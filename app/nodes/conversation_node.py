import uuid
from typing import Dict, Any, List
from datetime import datetime
from loguru import logger
import asyncio
import time
from app.core.state import Message, MessageType, Language
from app.core.memory import get_memory_manager
from app.services.OCR_vision import get_image_analysis
from app.services.medgemma import get_med_gemma3
from app.services.pdf import PDFRAGTemp
from app.services.elevenlabs_service import get_elevenlabs_service


class ConversationNodes:
    """Nodes for conversation flow"""

    def __init__(self):
        self.memory_manager = get_memory_manager()
        self.image_analysis = get_image_analysis()
        self.medgemma3 = get_med_gemma3()
        self.elevenlabs_service = get_elevenlabs_service()

    async def process_user_input(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not isinstance(state, dict):
                state = state.model_dump() if hasattr(state, "model_dump") else dict(state)

            user_input = state.get("user_input", "")
            session_id = state.get("session_id", "")
            user_id = state.get("user_id", "anonymous")
            language = state.get("language", "en")

            msg = Message(
                id=str(uuid.uuid4()),
                type=MessageType.TEXT,
                content=user_input,
                sender="user",
                language=Language(language)
            )

            state.setdefault("messages", [])
            state["messages"].append(msg.dict())

            # history + preferences
            state["conversation_history"] = self.memory_manager.get_conversation_history(session_id, limit=5)

            user_preferences = self.memory_manager.get_user_preferences(user_id)
            if user_preferences:
                state["user_preferences"] = user_preferences
                if user_preferences.get("language") and language != user_preferences["language"]:
                    language = user_preferences["language"]
                    state["language"] = language

            # ✅ Detect input type (text, pdf, image)
            user_input = await self._classify_input_type(
                text=user_input,
                language=language,
                image_url=state.get("image_url"),
                pdf_url=state.get("pdf_url")
            )
            state["user_input"] = user_input

            # ✅ Classify intent
            state["current_intent"] = await self._classify_intent(user_input, language)

            logger.info(f"Processed user input: {state['current_intent']}")
            return state

        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            state["error"] = str(e)
            return state

    async def generate_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not isinstance(state, dict):
                state = state.model_dump() if hasattr(state, "model_dump") else dict(state)

            intent = state.get("current_intent", "general")
            user_input = state.get("user_input", "")
            language = state.get("language", "en")
            conversation_history = state.get("conversation_history", [])
            user_preferences = state.get("user_preferences", {})

            context = self._build_context(user_input, conversation_history, user_preferences, language)

            if intent in ["prescription", "diagnostics", "insurance"]:
                response = await self.medgemma3.generate_raw_medical_advice(user_input, 250)
            elif intent == "memory_query":
                response = await self._handle_memory_query(user_input, language, context)
            else:
                response = await self.medgemma3.generate_raw_medical_advice(user_input, 250)

            response = (response or "").strip() or "Sorry, I couldn't generate a response."

            assistant_msg = Message(
                id=str(uuid.uuid4()),
                type=MessageType.TEXT,
                content=response,
                sender="assistant",
                language=Language(language)
            )

            state["assistant_response"] = response
            state["messages"].append(assistant_msg.dict())
            return state

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            state["assistant_response"] = "Sorry, an error occurred."
            return state

    async def generate_audio_response(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate audio response using TTS"""
        time.sleep(2)
        try:
            # Normalize state to mutable dict
            if not isinstance(state, dict):
                if hasattr(state, "model_dump"):
                    state = state.model_dump()
                else:
                    state = dict(state)
            response_text = state.get("assistant_response", "")
            language = state.get("language", "kn")
            
            if not response_text:
                return state
            
            # Generate audio
            audio_data = await self.elevenlabs_service.text_to_speech(
                text=response_text,
                language=language
            )
            
            if audio_data:
                # Save audio to file (Gemini TTS returns WAV bytes). Use .wav extension.
                audio_filename = f"response_{uuid.uuid4()}.mp3"
                audio_path = f"uploads/{audio_filename}"

                if self.elevenlabs_service.save_audio_to_file(audio_data, audio_path):
                    state["audio_response_path"] = audio_path
                    state["audio_generated"] = True
                else:
                    state["audio_generated"] = False
            
            return state
            
        except Exception as e:
            logger.error(f"Error generating audio response: {e}")
            state["audio_generated"] = False
            return state


    async def save_to_memory(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not isinstance(state, dict):
                state = state.model_dump() if hasattr(state, "model_dump") else dict(state)

            user_input = state.get("user_input", "")
            response = state.get("assistant_response", "")
            session_id = state.get("session_id", "")
            user_id = state.get("user_id", "anonymous")
            language = state.get("language", "en")

            if user_input and response:
                memory_id = self.memory_manager.add_conversation(
                    session_id=session_id,
                    user_id=user_id,
                    user_message=user_input,
                    assistant_response=response,
                    language=language,
                    metadata={
                        "intent": state.get("current_intent", "general"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

                state["memory_saved"] = bool(memory_id)
                if memory_id:
                    state["memory_id"] = memory_id
                    logger.info(f"Conversation saved to memory: {memory_id}")

            return state

        except Exception as e:
            logger.error(f"Error saving to memory: {e}")
            state["memory_saved"] = False
            return state

    # ✅ Detect input type
    async def _classify_input_type(self, text: str, language: str, image_url: str, pdf_url: str) -> str:
        try:
            text_lower = (text or "").lower()

            if pdf_url:
                return await self._handle_PDF_analysis(pdf_url, language)

            if image_url:
                return await self._handle_image_analysis(image_url, language)

            return text_lower

        except Exception as e:
            logger.error(f"Error classifying input type: {e}")
            

    # 1. Create a synchronous helper method to handle the whole job
    def _run_pdf_job_sync(self, pdf_path: str, query: str) -> str:
        # This acts as a wrapper so both initialization AND asking happen in the thread
        agent = PDFRAGTemp(pdf_path)
        return agent.ask(query)

    # 2. Your async handler
    async def _handle_PDF_analysis(self, pdf_url: str, language: str) -> str:
        try:
            query = f"Summarize this PDF in {language} within 500 token only."
            
            # Use get_running_loop (modern practice)
            loop = asyncio.get_running_loop()

            # ✅ PASS THE WRAPPER FUNCTION, NOT THE CLASS METHOD
            # This ensures the heavy __init__ happens in the background thread
            result = await loop.run_in_executor(
                None, 
                self._run_pdf_job_sync,  # The function to run
                pdf_url,                 # Arg 1
                query                    # Arg 2
            )

            return result

        except Exception as e:
            logger.error(f"PDF analysis error: {e}")
            return f"Error analyzing PDF: {str(e)}"

    # ✅ Image handler
    async def _handle_image_analysis(self, image_url: str, language: str) -> str:
        try:
            analysis = await self.image_analysis.analyze_image(
                image_path=image_url,
                language=language
            )
            return analysis or "Could not analyze the image."

        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return "Error analyzing image"

    # ✅ Intent detection unchanged
    async def _classify_intent(self, text: str, language: str) -> str:
        try:
            if not text:
                return "general"

            text_lower = text.lower()

            if any(k in text_lower for k in ["acute", "chronic", "benign"]):
                return "prescription"
            if any(k in text_lower for k in ["lab", "scan", "diagnosis"]):
                return "diagnostics"
            if any(k in text_lower for k in ["policy", "claim", "insurance"]):
                return "insurance"
            if any(k in text_lower for k in ["remember", "previous", "memory"]):
                return "memory_query"

            return "general"

        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            return "general"

    # ✅ Context builder unchanged
    def _build_context(self, user_input, conversation_history, user_preferences, language):
        parts = []

        if user_preferences.get("location"):
            parts.append(f"User location: {user_preferences['location']}")

        if conversation_history:
            recent = [
                f"Prev: {c['user_message']} -> {c['assistant_response']}"
                for c in conversation_history[:3]
            ]
            parts.append("Recent conversation:\n" + "\n".join(recent))

        return "\n\n".join(parts)

    async def _handle_memory_query(self, text: str, language: str, context: str):
        return f"I remember: {context or 'No memory found.'}"


# ✅ Global instance
conversation_nodes = ConversationNodes()


def get_conversation_nodes() -> ConversationNodes:
    return conversation_nodes
