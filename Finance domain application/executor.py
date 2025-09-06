import requests
import json
import logging
import time
from typing import Dict, Any, Optional, List
from tool_registry import ToolRegistry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Executor:
    """
    Executes tasks using the appropriate tools from the ToolRegistry.
    Handles API calls to both Hugging Face models and external financial APIs.
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.tool_registry = ToolRegistry()
        self.api_keys = self._load_api_keys()
        self.session = requests.Session()
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from configuration"""
        try:
            return {
                "huggingface": self.config.get("huggingface", {}).get("token", ""),
                "alpha-vantage": self.config.get("apis", {}).get("alpha-vantage", {}).get("key", ""),
                "fred": self.config.get("apis", {}).get("fred", {}).get("key", ""),
                "newsapi": self.config.get("apis", {}).get("newsapi", {}).get("key", ""),
                "coingecko": self.config.get("apis", {}).get("coingecko", {}).get("key", ""),
                "exchangerate-api": self.config.get("apis", {}).get("exchangerate-api", {}).get("key", ""),
                "college-scorecard": self.config.get("apis", {}).get("college-scorecard", {}).get("key", ""),
                "student-aid-api": self.config.get("apis", {}).get("student-aid-api", {}).get("key", ""),
                "openexchangerates": self.config.get("apis", {}).get("openexchangerates", {}).get("key", ""),
                "financialmodelingprep": self.config.get("apis", {}).get("financialmodelingprep", {}).get("key", "")
            }
        except Exception as e:
            logger.error(f"Error loading API keys: {e}")
            return {}
    
    def execute(self, task: Dict[str, Any], tool: Dict[str, Any], dependencies: Dict[int, Any] = None) -> Any:
        """
        Execute a task using the specified tool.
        
        Args:
            task: The task to execute
            tool: The tool to use for execution
            dependencies: Results from dependent tasks
            
        Returns:
            Result of the execution
        """
        try:
            # Resolve dependencies
            resolved_args = self._resolve_dependencies(task["args"], dependencies or {})
            
            # Execute based on tool provider
            provider = tool.get("provider", "")
            
            if provider == "huggingface":
                return self._execute_huggingface_model(tool, resolved_args, task["task"])
            else:
                return self._execute_external_api(tool, resolved_args)
                
        except Exception as e:
            logger.error(f"Error executing task {task.get('id', 'unknown')} with tool {tool.get('id', 'unknown')}: {e}")
            return {"error": str(e)}
    
    def _resolve_dependencies(self, args: Dict[str, Any], dependencies: Dict[int, Any]) -> Dict[str, Any]:
        """
        Resolve dependencies by replacing placeholders with actual results.
        
        Args:
            args: Task arguments
            dependencies: Results from dependent tasks
            
        Returns:
            Resolved arguments
        """
        try:
            resolved_args = args.copy()
            
            for key, value in args.items():
                if isinstance(value, str) and value.startswith("$dep:"):
                    dep_id = int(value.split(":")[1])
                    if dep_id in dependencies:
                        # Use the entire dependency result or a specific field
                        resolved_args[key] = dependencies[dep_id]
                    else:
                        logger.warning(f"Dependency {dep_id} not found for key {key}")
                        resolved_args[key] = f"MISSING_DEPENDENCY_{dep_id}"
            
            return resolved_args
            
        except Exception as e:
            logger.error(f"Error resolving dependencies: {e}")
            return args
    
    def _execute_huggingface_model(self, tool: Dict[str, Any], args: Dict[str, Any], task: str) -> Any:
        """
        Execute a Hugging Face model via their Inference API.
        
        Args:
            tool: The Hugging Face tool
            args: Arguments for the tool
            task: The task type
            
        Returns:
            Model inference result
        """
        try:
            endpoint = tool["endpoint"]
            api_key = self.api_keys.get("huggingface")
            
            if not api_key:
                return {"error": "Hugging Face API key not configured"}
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            # Format input based on task type
            payload = self._format_huggingface_payload(task, args)
            
            # Execute with retries
            for attempt in range(self.max_retries):
                try:
                    response = self.session.post(endpoint, headers=headers, json=payload, timeout=30)
                    
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 503:
                        # Model is loading, wait and retry
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (attempt + 1)
                            logger.info(f"Model loading, waiting {wait_time}s before retry...")
                            time.sleep(wait_time)
                            continue
                        else:
                            return {"error": "Model is loading, try again later"}
                    else:
                        return {"error": f"API error: {response.status_code} - {response.text}"}
                        
                except requests.exceptions.Timeout:
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                        time.sleep(self.retry_delay)
                    else:
                        return {"error": "Request timeout"}
                except requests.exceptions.ConnectionError:
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Connection error on attempt {attempt + 1}, retrying...")
                        time.sleep(self.retry_delay)
                    else:
                        return {"error": "Connection error"}
            
            return {"error": "Max retries exceeded"}
            
        except Exception as e:
            logger.error(f"Error executing Hugging Face model {tool['id']}: {e}")
            return {"error": str(e)}
    
    def _format_huggingface_payload(self, task: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the payload for Hugging Face API based on task type.
        
        Args:
            task: The task type
            args: Task arguments
            
        Returns:
            Formatted payload
        """
        if task == "financial-sentiment-analysis":
            return {"inputs": args.get("text", "")}
        elif task == "summarization":
            return {"inputs": args.get("text", "")}
        elif task == "financial-qa":
            return {
                "question": args.get("question", ""),
                "context": args.get("context", "")
            }
        elif task == "financial-explanation":
            return {"inputs": args.get("context", "")}
        elif task == "conversational":
            return {"inputs": args.get("text", "")}
        else:
            # Default payload format
            return {"inputs": args}
    
    def _execute_external_api(self, tool: Dict[str, Any], args: Dict[str, Any]) -> Any:
        """
        Execute an external API call.
        
        Args:
            tool: The API tool
            args: Arguments for the API
            
        Returns:
            API response
        """
        try:
            endpoint = tool["endpoint"]
            provider = tool["provider"]
            api_key = self.api_keys.get(provider, "")
            
            # Add API key to arguments if needed
            if api_key:
                # Different APIs have different parameter names for the API key
                key_param = self._get_api_key_param(provider)
                args[key_param] = api_key
            
            # Execute with retries
            for attempt in range(self.max_retries):
                try:
                    # Determine if this is a GET or POST request
                    if provider in ["huggingface", "newsapi", "alpha-vantage", "fred", "coingecko"]:
                        # These typically use GET requests
                        response = self.session.get(endpoint, params=args, timeout=30)
                    else:
                        # Others might use POST
                        response = self.session.post(endpoint, json=args, timeout=30)
                    
                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 429:
                        # Rate limited, wait and retry
                        if attempt < self.max_retries - 1:
                            wait_time = self.retry_delay * (attempt + 1)
                            logger.info(f"Rate limited, waiting {wait_time}s before retry...")
                            time.sleep(wait_time)
                            continue
                        else:
                            return {"error": "Rate limited, try again later"}
                    else:
                        return {"error": f"API error: {response.status_code} - {response.text}"}
                        
                except requests.exceptions.Timeout:
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Timeout on attempt {attempt + 1}, retrying...")
                        time.sleep(self.retry_delay)
                    else:
                        return {"error": "Request timeout"}
                except requests.exceptions.ConnectionError:
                    if attempt < self.max_retries - 1:
                        logger.warning(f"Connection error on attempt {attempt + 1}, retrying...")
                        time.sleep(self.retry_delay)
                    else:
                        return {"error": "Connection error"}
            
            return {"error": "Max retries exceeded"}
            
        except Exception as e:
            logger.error(f"Error executing external API {tool['id']}: {e}")
            return {"error": str(e)}
    
    def _get_api_key_param(self, provider: str) -> str:
        """
        Get the parameter name for the API key based on the provider.
        
        Args:
            provider: The API provider
            
        Returns:
            Parameter name for the API key
        """
        key_params = {
            "alpha-vantage": "apikey",
            "fred": "api_key",
            "newsapi": "apiKey",
            "coingecko": "x_cg_demo_api_key",  # CoinGecko uses header for API key
            "college-scorecard": "api_key",
            "student-aid-api": "api_key",
            "openexchangerates": "app_id",
            "financialmodelingprep": "apikey"
        }
        
        return key_params.get(provider, "api_key")
    
    def execute_task_sequence(self, tasks: List[Dict[str, Any]], task_results: Dict[int, Any] = None) -> Dict[int, Any]:
        """
        Execute a sequence of tasks in dependency order.
        
        Args:
            tasks: List of tasks to execute
            task_results: Existing task results (for incremental execution)
            
        Returns:
            Dictionary of task results
        """
        if task_results is None:
            task_results = {}
        
        try:
            # Create a copy of tasks to avoid modifying the original list
            remaining_tasks = tasks.copy()
            
            while remaining_tasks:
                executed_this_round = False
                
                for task in remaining_tasks[:]:
                    # Check if all dependencies are satisfied
                    dependencies_satisfied = all(
                        dep_id in task_results or dep_id == -1
                        for dep_id in task["dep"]
                    )
                    
                    if dependencies_satisfied:
                        # Get dependency results
                        dep_results = {
                            dep_id: task_results[dep_id] 
                            for dep_id in task["dep"] 
                            if dep_id != -1
                        }
                        
                        # Select appropriate tool
                        tool_registry = ToolRegistry()
                        tool = tool_registry.get_tool_by_id(task.get("tool_id", ""))
                        
                        if not tool:
                            # If no specific tool specified, select one
                            available_tools = tool_registry.get_tools_by_task(task["task"])
                            if available_tools:
                                tool = available_tools[0]
                            else:
                                task_results[task["id"]] = {"error": "No suitable tool found"}
                                remaining_tasks.remove(task)
                                executed_this_round = True
                                continue
                        
                        # Execute the task
                        result = self.execute(task, tool, dep_results)
                        task_results[task["id"]] = result
                        remaining_tasks.remove(task)
                        executed_this_round = True
                
                if not executed_this_round:
                    logger.error("Cannot execute remaining tasks due to unmet dependencies")
                    break
            
            return task_results
            
        except Exception as e:
            logger.error(f"Error executing task sequence: {e}")
            return task_results

# Example usage
if __name__ == "__main__":
    # Mock configuration
    config = {
        "huggingface": {
            "token": "your_huggingface_token_here"
        },
        "apis": {
            "alpha-vantage": {
                "key": "your_alpha_vantage_key_here"
            },
            "newsapi": {
                "key": "your_newsapi_key_here"
            }
        }
    }
    
    # Create executor
    executor = Executor(config)
    
    # Test task execution
    test_tasks = [
        {
            "id": 1,
            "task": "stock-data",
            "dep": [-1],
            "args": {"symbol": "AAPL", "function": "GLOBAL_QUOTE"},
            "tool_id": "alpha-vantage"
        },
        {
            "id": 2,
            "task": "financial-sentiment-analysis",
            "dep": [-1],
            "args": {"text": "Apple stock is performing well today"},
            "tool_id": "ProsusAI/finbert"
        }
    ]
    
    print("Testing task execution...")
    results = executor.execute_task_sequence(test_tasks)
    
    print("Execution results:")
    for task_id, result in results.items():
        print(f"Task {task_id}: {json.dumps(result, indent=2)[:200]}...")