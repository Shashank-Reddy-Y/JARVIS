import requests
import logging
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenRouterClient:
    """
    Client for interacting with OpenRouter API for free LLM access.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.api_key = config.get("openrouter", {}).get("api_key", "")
        self.model = config.get("openrouter", {}).get("model", "google/gemini-2.0-flash-thinking-exp:free")
        self.base_url = config.get("openrouter", {}).get("base_url", "https://openrouter.ai/api/v1")
        self.temperature = config.get("openrouter", {}).get("temperature", 0.1)
        self.max_tokens = config.get("openrouter", {}).get("max_tokens", 1000)
        
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate a response using OpenRouter API.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            
        Returns:
            Generated response text
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/your-username/student-finance-ai",
                "X-Title": "Student Finance AI"
            }
        
            messages = []
        
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                # ✅ FIX: Properly handle the response format
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    return response_data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Unexpected response format: {response_data}")
                    return "Error: Unexpected response format from AI service"
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text}")
                return f"Error: API returned status {response.status_code}"
                
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return f"Error: {str(e)}"
    
    def get_available_models(self) -> Optional[Dict[str, Any]]:
        """
        Get list of available models from OpenRouter.
        
        Returns:
            Dictionary of available models or None if error
        """
        try:
            response = requests.get(
                "https://openrouter.ai/api/v1/models",
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error fetching models: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching available models: {e}")
            return None

# Fallback client for when OpenRouter is not available
class FallbackLLMClient:
    """Fallback LLM client that uses simple rule-based responses"""
    
    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """Generate a fallback response"""
        # Simple rule-based responses for critical functions
        if "task parsing" in prompt.lower() or "parse" in prompt.lower():
            # Fallback task parsing for common student finance questions
            if any(term in prompt.lower() for term in ["invest", "stock", "market"]):
                return json.dumps([
                    {
                        "task": "stock-data",
                        "id": 1,
                        "dep": [-1],
                        "args": {"symbol": "SPY", "function": "GLOBAL_QUOTE"}
                    },
                    {
                        "task": "economic-data",
                        "id": 2,
                        "dep": [-1],
                        "args": {"indicator": "CPIAUCSL"}
                    },
                    {
                        "task": "financial-explanation",
                        "id": 3,
                        "dep": [1, 2],
                        "args": {"context": "investment decision for student"}
                    }
                ])
            elif any(term in prompt.lower() for term in ["save", "savings", "emergency"]):
                return json.dumps([
                    {
                        "task": "economic-data",
                        "id": 1,
                        "dep": [-1],
                        "args": {"indicator": "interest rates"}
                    },
                    {
                        "task": "financial-explanation",
                        "id": 2,
                        "dep": [1],
                        "args": {"context": "savings strategy for student"}
                    }
                ])
            else:
                return json.dumps([
                    {
                        "task": "financial-qa",
                        "id": 1,
                        "dep": [-1],
                        "args": {"question": "general financial advice for students"}
                    }
                ])
        else:
            # Fallback response synthesis
            return "Based on financial analysis, I recommend a balanced approach for students. " \
                   "Consider saving a portion of your money for emergencies and investing the rest " \
                   "in low-cost index funds. Always prioritize education and skill development " \
                   "as your best investment."