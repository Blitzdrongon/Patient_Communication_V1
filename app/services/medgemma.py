from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import asyncio
from typing import Optional
from loguru import logger
from app.core.config import get_settings


class Medgemma:
    def __init__(self):
        self.settings = get_settings()
        self.model_id = "ContactDoctor/Bio-Medical-Llama-3-2-1B-CoT-012025"

        logger.info("Loading Bio-Medical Llama model...")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_id,
            trust_remote_code=True,
            cache_dir="d:/mini/huggingface_model"
        )

        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            dtype=torch.float16,     # safer for GPU
            device_map="auto",
            trust_remote_code=True,
            cache_dir="d:/mini/huggingface_model"
        )

        logger.info("✅ Bio-Medical Llama model loaded successfully")


    # ✅ Helper: format chat prompts
    def _build_prompt(self, user_input: str) -> str:
        messages = [
            {"role": "system", "content": "You are a AI Assestent who is expect in medicine."},
            {"role": "user", "content": user_input}
        ]

        return self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )


    # ✅ Simple response
    async def generate_simple(self, user_input: str, max_new_tokens: int = 100) -> str:
        try:
            prompt = self._build_prompt(user_input)
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

            with torch.no_grad():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=500,
                    do_sample=True,
                    temperature=0.8,
                    top_p=0.9
                )

            decoded = self.tokenizer.decode(output[0], skip_special_tokens=True)
            logger.info(f"decode:{decoded}")
            return decoded

        except Exception as e:
            logger.error(f"Error in generate_simple: {e}")
            return f"Error: {str(e)}"


    # ✅ Context response
    async def generate_medical_response(self, query: str, context: str = "", language: str = "en", max_new_tokens: int = 300) -> str:
        try:
            if context:
                final_input = f"Context: {context}\nQuestion: {query}"
            else:
                final_input = query

            return await self.generate_simple(final_input, max_new_tokens)

        except Exception as e:
            logger.error(f"Error in generate_medical_response: {e}")
            return f"Error: {str(e)}"


    async def generate_prescription_advice(self, query: str, language: str = "en") -> str:
        return await self.generate_medical_response(query, "", language, 200)

    async def generate_diagnostic_info(self, query: str, language: str = "en") -> str:
        return await self.generate_medical_response(query, "", language, 250)

    async def generate_insurance_help(self, query: str, language: str = "en") -> str:
        return await self.generate_medical_response(query, "", language, 150)

    async def generate_raw_medical_advice(self, query: str, max_new_tokens: int = 300) -> str:
        return await self.generate_simple(query, max_new_tokens)


# Global instance
medgemma = Medgemma()

def get_med_gemma3() -> Medgemma:
    return medgemma


# ✅ Test function
async def test_medgemma():
    model = get_med_gemma3()
    test_query = "What are the causes of headache?"
    response = await model.generate_simple(test_query)
    print("Test Query:", test_query)
    print("Raw Response:", response)


if __name__ == "__main__":
    asyncio.run(test_medgemma())

