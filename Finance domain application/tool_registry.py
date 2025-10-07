import json
import logging
from typing import Dict, List, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Registry for all available tools (Hugging Face models and external APIs)
    for the Student Finance AI Orchestrator - API Only Version.
    """
    
    def __init__(self):
        self.models = self._load_models()
        self.apis = self._load_apis()
        self._validate_tools()
        
    def _load_models(self) -> List[Dict[str, Any]]:
        """Load finance-specific Hugging Face models (API endpoints only)"""
        try:
            return [
                {
                    "id": "ProsusAI/finbert",
                    "name": "FinBERT",
                    "task": "financial-sentiment-analysis",
                    "description": "Financial sentiment analysis model",
                    "endpoint": "https://api-inference.huggingface.co/models/ProsusAI/finbert",
                    "input_type": "text",
                    "output_type": "sentiment-score",
                    "provider": "huggingface",
                    "required_params": ["inputs"]
                },
                {
                    "id": "microsoft/DialoGPT-large",
                    "name": "DialoGPT",
                    "task": "conversational",
                    "description": "Conversational AI for follow-up questions",
                    "endpoint": "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large",
                    "input_type": "text",
                    "output_type": "text",
                    "provider": "huggingface",
                    "required_params": ["inputs"]
                },
                {
                    "id": "facebook/bart-large-cnn",
                    "name": "BART",
                    "task": "summarization",
                    "description": "Text summarization model",
                    "endpoint": "https://api-inference.huggingface.co/models/facebook/bart-large-cnn",
                    "input_type": "text",
                    "output_type": "text",
                    "provider": "huggingface",
                    "required_params": ["inputs"]
                },
                {
                    "id": "deepset/roberta-base-squad2",
                    "name": "Financial QA",
                    "task": "financial-qa",
                    "description": "Question answering for financial education",
                    "endpoint": "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2",
                    "input_type": "text",
                    "output_type": "text",
                    "provider": "huggingface",
                    "required_params": ["inputs"]
                },
                {
                    "id": "google/flan-t5-large",
                    "name": "FLAN-T5",
                    "task": "financial-explanation",
                    "description": "General purpose text generation for financial explanations",
                    "endpoint": "https://api-inference.huggingface.co/models/google/flan-t5-large",
                    "input_type": "text",
                    "output_type": "text",
                    "provider": "huggingface",
                    "required_params": ["inputs"]
                }
            ]
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return []
    # Add this method to the ToolRegistry class in tool_registry.py
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools (both models and APIs)"""
        return self.models + self.apis
    
    def _load_apis(self) -> List[Dict[str, Any]]:
        """Load financial APIs"""
        try:
            return [
                {
                    "id": "alpha-vantage",
                    "name": "Alpha Vantage",
                    "task": "stock-data",
                    "description": "Stock market data API",
                    "endpoint": "https://www.alphavantage.co/query",
                    "input_type": "symbol",
                    "output_type": "stock-data",
                    "provider": "alpha-vantage",
                    "required_params": ["function", "symbol"]
                },
                {
                    "id": "fred",
                    "name": "FRED",
                    "task": "economic-data",
                    "description": "Federal Reserve Economic Data",
                    "endpoint": "https://api.stlouisfed.org/fred/series/observations",
                    "input_type": "indicator",
                    "output_type": "economic-data",
                    "provider": "fred",
                    "required_params": ["series_id", "file_type"]
                },
                {
                    "id": "newsapi",
                    "name": "NewsAPI",
                    "task": "financial-news",
                    "description": "Financial news API",
                    "endpoint": "https://newsapi.org/v2/everything",
                    "input_type": "query",
                    "output_type": "news-articles",
                    "provider": "newsapi",
                    "required_params": ["q"]
                },
                {
                    "id": "coingecko",
                    "name": "CoinGecko",
                    "task": "crypto-data",
                    "description": "Cryptocurrency data API",
                    "endpoint": "https://api.coingecko.com/api/v3/simple/price",
                    "input_type": "coin-id",
                    "output_type": "crypto-data",
                    "provider": "coingecko",
                    "required_params": ["ids", "vs_currencies"]
                },
                {
                    "id": "exchangerate-api",
                    "name": "ExchangeRate-API",
                    "task": "currency-conversion",
                    "description": "Currency conversion API",
                    "endpoint": "https://api.exchangerate-api.com/v4/latest",
                    "input_type": "currency",
                    "output_type": "exchange-rate",
                    "provider": "exchangerate-api",
                    "required_params": ["base"]
                },
                {
                    "id": "college-scorecard",
                    "name": "College Scorecard",
                    "task": "education-data",
                    "description": "College cost and ROI data",
                    "endpoint": "https://api.data.gov/ed/collegescorecard/v1/schools",
                    "input_type": "school-name",
                    "output_type": "education-data",
                    "provider": "college-scorecard",
                    "required_params": ["school.name", "api_key"]
                },
                {
                    "id": "student-aid-api",
                    "name": "Student Aid API",
                    "task": "loan-information",
                    "description": "Student loan information API",
                    "endpoint": "https://api.studentaid.gov/services",
                    "input_type": "loan-type",
                    "output_type": "loan-data",
                    "provider": "student-aid",
                    "required_params": ["service"]
                },
                {
                    "id": "openexchangerates",
                    "name": "Open Exchange Rates",
                    "task": "currency-conversion",
                    "description": "Alternative currency conversion API",
                    "endpoint": "https://openexchangerates.org/api/latest.json",
                    "input_type": "currency",
                    "output_type": "exchange-rate",
                    "provider": "openexchangerates",
                    "required_params": ["app_id", "base"]
                },
                {
                    "id": "financialmodelingprep",
                    "name": "Financial Modeling Prep",
                    "task": "financial-data",
                    "description": "Comprehensive financial data API",
                    "endpoint": "https://financialmodelingprep.com/api/v3",
                    "input_type": "symbol",
                    "output_type": "financial-data",
                    "provider": "fmp",
                    "required_params": ["apikey"]
                }
            ]
        except Exception as e:
            logger.error(f"Error loading APIs: {e}")
            return []
    
    def _validate_tools(self) -> None:
        """Validate that all tools have required fields"""
        required_fields = ["id", "name", "task", "description", "endpoint", "provider", "required_params"]
        
        for model in self.models:
            for field in required_fields:
                if field not in model:
                    logger.warning(f"Model {model.get('id', 'unknown')} missing required field: {field}")
        
        for api in self.apis:
            for field in required_fields:
                if field not in api:
                    logger.warning(f"API {api.get('id', 'unknown')} missing required field: {field}")
    
    def get_tools_by_task(self, task: str) -> List[Dict[str, Any]]:
        """Get all tools that can handle a specific task"""
        try:
            model_tools = [model for model in self.models if model["task"] == task]
            api_tools = [api for api in self.apis if api["task"] == task]
            return model_tools + api_tools
        except Exception as e:
            logger.error(f"Error getting tools by task {task}: {e}")
            return []
    
    def get_tool_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific tool by ID"""
        try:
            for model in self.models:
                if model["id"] == tool_id:
                    return model
            for api in self.apis:
                if api["id"] == tool_id:
                    return api
            logger.warning(f"Tool with ID {tool_id} not found")
            return None
        except Exception as e:
            logger.error(f"Error getting tool by ID {tool_id}: {e}")
            return None
    
    def get_all_tasks(self) -> List[str]:
        """Get a list of all available tasks"""
        try:
            model_tasks = [model["task"] for model in self.models]
            api_tasks = [api["task"] for api in self.apis]
            return list(set(model_tasks + api_tasks))
        except Exception as e:
            logger.error(f"Error getting all tasks: {e}")
            return []
    
    def get_tool_metadata(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific tool"""
        tool = self.get_tool_by_id(tool_id)
        if not tool:
            return None
        
        # Return a subset of fields for metadata
        metadata_fields = ["id", "name", "task", "description", "input_type", "output_type", "provider"]
        return {field: tool.get(field) for field in metadata_fields}
    
    def get_tools_by_provider(self, provider: str) -> List[Dict[str, Any]]:
        """Get all tools from a specific provider"""
        try:
            model_tools = [model for model in self.models if model.get("provider") == provider]
            api_tools = [api for api in self.apis if api.get("provider") == provider]
            return model_tools + api_tools
        except Exception as e:
            logger.error(f"Error getting tools by provider {provider}: {e}")
            return []
    
    def get_required_params(self, tool_id: str) -> List[str]:
        """Get required parameters for a specific tool"""
        tool = self.get_tool_by_id(tool_id)
        if not tool:
            return []
        return tool.get("required_params", [])
    
    def to_json(self) -> str:
        """Serialize the tool registry to JSON"""
        try:
            return json.dumps({
                "models": self.models,
                "apis": self.apis,
                "total_tools": len(self.models) + len(self.apis)
            }, indent=2)
        except Exception as e:
            logger.error(f"Error serializing tool registry to JSON: {e}")
            return "{}"

# Example usage
if __name__ == "__main__":
    registry = ToolRegistry()
    
    print("=" * 60)
    print("STUDENT FINANCE AI ORCHESTRATOR - TOOL REGISTRY")
    print("=" * 60)
    
    print(f"\nTotal Tools: {len(registry.models) + len(registry.apis)}")
    print(f"Models: {len(registry.models)}")
    print(f"APIs: {len(registry.apis)}")
    
    print(f"\nAvailable tasks: {registry.get_all_tasks()}")
    
    print(f"\nTools for financial-sentiment-analysis:")
    for tool in registry.get_tools_by_task("financial-sentiment-analysis"):
        print(f"  - {tool['name']} ({tool['provider']})")
    
    print(f"\nAlpha Vantage tool details:")
    alpha_vantage = registry.get_tool_by_id("alpha-vantage")
    if alpha_vantage:
        print(f"  Required params: {alpha_vantage.get('required_params', [])}")
    
    print(f"\nHuggingFace tools:")
    hf_tools = registry.get_tools_by_provider("huggingface")
    for tool in hf_tools:
        print(f"  - {tool['name']}: {tool['task']}")