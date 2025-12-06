"""
Prompt templates for the medical assistant
"""

class SystemPrompt:
    """System prompt manager"""
    
    def __init__(self):
        self.base_prompt = """You are a helpful medical assistant. Please provide accurate and helpful medical information."""
    
    def describe_prompt(self) -> str:
        """Get prompt for image description"""
        return "Describe this image in detail. If it's a medical image, provide relevant medical observations."
    
    def medical_prompt(self) -> str:
        """Get prompt for medical queries"""
        return "You are a medical assistant. Please provide helpful medical information based on the user's query."
    
    def general_prompt(self) -> str:
        """Get prompt for general queries"""
        return "You are a helpful assistant. Please provide useful information based on the user's query."

# Global instance
system_prompt = SystemPrompt()

def get_system_prompt() -> SystemPrompt:
    """Get system prompt instance"""
    return system_prompt
