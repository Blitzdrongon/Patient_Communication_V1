"""
State management for Patient Comm
"""

from typing import Dict, List,Optional,Any
from datetime import datetime
from pydantic import BaseModel , Field
from enum import Enum
from loguru import logger

class MessageType(str,Enum):
    """Types of messages"""
    TEXT="text"
    AUDIO="audio"
    IMAGE="image"
    PDF="pdf"
    SYSTEM="system"


class Language(str,Enum):
    """Supported Languages"""
    KANNADA ="kn"
    ENGLISH = "en"
    HINDI = "hn"

class Message(BaseModel):
    """Individual message in conv"""
    id:str
    type:MessageType
    content:str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender: str
    metadata:Optional[dict[str,Any]] = None
    language: Language = Language.ENGLISH


class ConversationalState(BaseModel):
    """State of a conversation"""
    session_id:str
    user_id:str
    message:List[Message] = Field(default_factory=list)
    current_language: Language = Language.ENGLISH
    context:Dict[str,Any] = Field(default_factory=dict)
    created_at:datetime = Field(default_factory=datetime.utcnow)
    updated_at:datetime = Field(default_factory=datetime.utcnow)

    # Voice context
    voice_enabled: bool = True
    preferred_voice: Optional[str] = None


class UserProfile(BaseModel):
    """User profile information"""
    user_id:str
    name:str
    preferred_language: Language = Language.ENGLISH
    location:Optional[str]=None
    timezone: Optional[str] = None
    created_at:datetime = Field(default_factory=datetime.utcnow)
    last_active:datetime = Field(default_factory=datetime.utcnow)
    preferences:Dict[str,Any] = Field(default_factory=dict)



class GlobalState(BaseModel):
    """Global application state"""
    conversations: Dict[str,ConversationalState] = Field(default_factory=dict)
    user_profiles: Dict[str, UserProfile] = Field(default_factory=dict)
    active_session: Dict[str,str] = Field(default_factory=dict)

    def get_conversation(self, session_id:str) -> Optional[ConversationalState]:
        """Get conversation by session ID"""
        return self.conversations.get(session_id)
    
    def create_conversation(self, session_id:str, user_id:str) -> ConversationalState:
        """Create a new conversation"""
        conversation = ConversationalState(session_id=session_id,user_id=user_id)
        self.conversations[session_id]=conversation
        self.active_session[session_id]=user_id
        return conversation
    
    def add_message(self, session_id:str, message:Message) -> Optional[UserProfile]:
        """Add messaage to conversation"""
        conversation = self.get_conversation(session_id)
        if conversation:
            conversation.message.append(message)
            conversation.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_user_profile(self, user_id:str)-> Optional[UserProfile]:
        """Get user profile by user ID"""
        return self.user_profiles.get(user_id)
    
    def update_user_profile(self, user_id:str,**kwargs)-> bool:
        """Update user profile"""
        profile = self.get_user_profile(user_id)
        if profile:
            for key,value in kwargs.items():
                if hasattr(profile,key):
                    setattr(profile,key,value)
            profile.last_active=datetime.utcnow()
            return True
        return False
    


# Global state instance
global_state = GlobalState()


def get_global_state() -> GlobalState:
    """Get global state instance"""
    return global_state

