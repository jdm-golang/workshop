import os
import boto3
from typing import Optional
from dotenv import load_dotenv
from strands import models

# Load environment variables from .env file
load_dotenv()

class Config:
    """Simple configuration management for Strands agents"""
    
    @property
    def aws_region(self) -> str:
        """Get AWS region from environment variables"""
        return os.getenv('AWS_REGION', 'us-east-1')
    
    @property 
    def aws_profile(self) -> Optional[str]:
        """Get AWS profile from environment variables"""
        return os.getenv('AWS_PROFILE')
    
    @property
    def model_id(self) -> str:
        """Get model ID from environment variables"""
        return os.getenv('MODEL_ID', 'us.anthropic.claude-sonnet-4-20250514-v1:0')
    
    @property
    def reasoning_enabled(self) -> bool:
        """Get reasoning setting from environment variables"""
        return os.getenv('REASONING_ENABLED', 'false').lower() == 'true'
    
    def get_boto_session(self) -> boto3.Session:
        """Create configured boto3 session"""
        session_kwargs = {'region_name': self.aws_region}
        
        if self.aws_profile:
            session_kwargs['profile_name'] = self.aws_profile
            
        return boto3.Session(**session_kwargs)
    
    def create_bedrock_model(self, model_id: Optional[str] = None, reasoning: Optional[bool] = None) -> models.BedrockModel:
        """Create a configured BedrockModel instance"""
        model_id = model_id or self.model_id
        reasoning = reasoning if reasoning is not None else self.reasoning_enabled
        boto_session = self.get_boto_session()
        
        return models.BedrockModel(
            model_id=model_id,
            boto_session=boto_session
        )
    
    def get_agent_model_id(self, agent_name: str) -> str:
        """Get model ID for specific agent, falling back to global default"""
        agent_key = f"{agent_name.upper()}_AGENT_MODEL_ID"
        return os.getenv(agent_key, self.model_id)
    
    def get_agent_reasoning_enabled(self, agent_name: str) -> bool:
        """Get reasoning setting for specific agent, falling back to global default"""
        agent_key = f"{agent_name.upper()}_AGENT_REASONING_ENABLED"
        return os.getenv(agent_key, str(self.reasoning_enabled)).lower() == 'true'
    
    def create_bedrock_model_for_agent(self, agent_name: str, model_id: Optional[str] = None, reasoning: Optional[bool] = None) -> models.BedrockModel:
        """Create a configured BedrockModel instance for specific agent"""
        if model_id is None:
            model_id = self.get_agent_model_id(agent_name)
        if reasoning is None:
            reasoning = self.get_agent_reasoning_enabled(agent_name)
        
        return self.create_bedrock_model(model_id=model_id, reasoning=reasoning)

# Global configuration instance
config = Config()

def get_bedrock_model_for_agent(agent_name: str, model_id: Optional[str] = None, reasoning: Optional[bool] = None) -> models.BedrockModel:
    """Convenience function to get a configured model for specific agent"""
    return config.create_bedrock_model_for_agent(agent_name=agent_name, model_id=model_id, reasoning=reasoning)
