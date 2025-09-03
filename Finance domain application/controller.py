import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from tool_registry import ToolRegistry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ControllerPlanner:
    """
    Controller that parses user queries and plans the execution of tasks
    using available tools from the ToolRegistry.
    """
    
    def __init__(self, tool_registry: ToolRegistry, llm_client=None):
        self.tool_registry = tool_registry
        self.llm_client = llm_client
        self.task_parsing_prompt = self._load_task_parsing_prompt()
        
    def _load_task_parsing_prompt(self) -> str:
        """Load the task parsing prompt tailored for finance"""
        available_tasks = self.tool_registry.get_all_tasks()
        
        return f"""
        You are a financial assistant for students. Parse the user's query into a sequence of tasks.
        
        Available task types: {', '.join(available_tasks)}
        
        Task descriptions:
        - financial-sentiment-analysis: Analyze sentiment of financial text
        - conversational: Handle conversational follow-ups
        - summarization: Summarize financial information
        - financial-qa: Answer financial education questions
        - financial-explanation: Provide personalized financial explanations
        - stock-data: Fetch stock market data
        - economic-data: Fetch economic indicators
        - financial-news: Get financial news
        - crypto-data: Get cryptocurrency data
        - currency-conversion: Convert between currencies
        - education-data: Get college cost and ROI data
        - loan-information: Get student loan information
        
        For each task, specify:
        - task: the task type (must be one of the available types)
        - id: a unique identifier (integer)
        - dep: dependencies (list of task IDs this task depends on, use [-1] for no dependencies)
        - args: arguments needed for the task (as key-value pairs)
        
        Example output for "Should I invest my $500 summer internship earnings or save it?":
        [
            {{
                "task": "financial-sentiment-analysis",
                "id": 1,
                "dep": [-1],
                "args": {{"text": "current market sentiment for beginner investors"}}
            }},
            {{
                "task": "economic-data",
                "id": 2,
                "dep": [-1],
                "args": {{"indicator": "inflation rate"}}
            }},
            {{
                "task": "stock-data",
                "id": 3,
                "dep": [-1],
                "args": {{"symbol": "SPY", "function": "GLOBAL_QUOTE"}}
            }},
            {{
                "task": "financial-explanation",
                "id": 4,
                "dep": [1, 2, 3],
                "args": {{
                    "context": "investment vs savings decision for student with $500", 
                    "risk_profile": "conservative"
                }}
            }}
        ]
        
        Important: Only use available task types. If the query cannot be parsed into tasks, return an empty list [].
        """
    
    def parse_query(self, query: str, context: List[Dict] = None) -> List[Dict[str, Any]]:
        """
        Parse user query into a sequence of tasks.
        """
        try:
            # Prepare the prompt for the LLM
            prompt = f"{self.task_parsing_prompt}\n\nUser query: {query}"
            
            if context:
                prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
            
            # Use the LLM to parse the task
            if self.llm_client:
                response = self.llm_client.generate(prompt)
            else:
                # Fallback: simple rule-based parsing for demonstration
                response = self._fallback_parse_query(query)
            
            # Extract JSON from response
            tasks = self._extract_tasks_from_response(response)
            
            # Validate tasks
            valid_tasks = self._validate_tasks(tasks)
            
            logger.info(f"Parsed {len(valid_tasks)} tasks from query: {query}")
            return valid_tasks
            
        except Exception as e:
            logger.error(f"Error parsing query '{query}': {e}")
            return []
    
    def _fallback_parse_query(self, query: str) -> str:
        """
        Fallback method for parsing queries when no LLM is available.
        This is a simple rule-based approach for demonstration.
        """
        query_lower = query.lower()
        
        # Investment-related queries
        if any(word in query_lower for word in ["invest", "stock", "market", "portfolio"]):
            return json.dumps([
                {
                    "task": "stock-data",
                    "id": 1,
                    "dep": [-1],
                    "args": {"symbol": "SPY", "function": "overview"}
                },
                {
                    "task": "economic-data",
                    "id": 2,
                    "dep": [-1],
                    "args": {"indicator": "inflation rate"}
                },
                {
                    "task": "financial-explanation",
                    "id": 3,
                    "dep": [1, 2],
                    "args": {"context": query}
                }
            ])
        
        # Savings-related queries
        elif any(word in query_lower for word in ["save", "savings", "emergency fund"]):
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
                    "args": {"context": query}
                }
            ])
        
        # Loan-related queries
        elif any(word in query_lower for word in ["loan", "debt", "borrow"]):
            return json.dumps([
                {
                    "task": "loan-information",
                    "id": 1,
                    "dep": [-1],
                    "args": {"loan_type": "student"}
                },
                {
                    "task": "financial-explanation",
                    "id": 2,
                    "dep": [1],
                    "args": {"context": query}
                }
            ])
        
        # Inflation-related queries
        elif any(word in query_lower for word in ["inflation", "cpi", "consumer price"]):
            return json.dumps([
                {
                    "task": "economic-data",
                    "id": 1,
                    "dep": [-1],
                    "args": {"indicator": "CPIAUCSL"}
                },
                {
                    "task": "financial-explanation",
                    "id": 2,
                    "dep": [1],
                    "args": {"context": "explain inflation to a student"}
                }
            ])
        
        # General financial questions
        else:
            return json.dumps([
                {
                    "task": "financial-qa",
                    "id": 1,
                    "dep": [-1],
                    "args": {"question": query}
                }
            ])
    
    def _extract_tasks_from_response(self, response: str) -> List[Dict[str, Any]]:
        """
        Extract task list from LLM response.
        """
        try:
            # Try to find JSON in the response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                tasks = json.loads(json_match.group())
                return tasks
            else:
                logger.warning("No JSON array found in response")
                return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from response: {e}")
            return []
        except Exception as e:
            logger.error(f"Error extracting tasks from response: {e}")
            return []
    
    def _validate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate tasks to ensure they use available task types and have required fields.
        """
        if not isinstance(tasks, list):
            return []
        
        available_tasks = self.tool_registry.get_all_tasks()
        valid_tasks = []
        
        for task in tasks:
            # Check required fields
            if not all(key in task for key in ["task", "id", "dep", "args"]):
                logger.warning(f"Task missing required fields: {task}")
                continue
            
            # Check if task type is available
            if task["task"] not in available_tasks:
                logger.warning(f"Task type not available: {task['task']}")
                continue
            
            # Check if dependencies are valid
            if not isinstance(task["dep"], list) or not all(isinstance(d, int) for d in task["dep"]):
                logger.warning(f"Invalid dependencies format: {task['dep']}")
                continue
            
            # Check if args is a dictionary
            if not isinstance(task["args"], dict):
                logger.warning(f"Args should be a dictionary: {task['args']}")
                continue
            
            valid_tasks.append(task)
        
        return valid_tasks
    
    def select_tool(self, task: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Select the best tool for a given task.
        """
        try:
            available_tools = self.tool_registry.get_tools_by_task(task["task"])
            
            if not available_tools:
                logger.warning(f"No tools available for task: {task['task']}")
                return None
            
            # Simple selection logic - choose the first available tool
            selected_tool = available_tools[0]
            
            # Check if the tool has all required parameters
            required_params = self.tool_registry.get_required_params(selected_tool["id"])
            missing_params = [p for p in required_params if p not in task["args"]]
            
            if missing_params:
                logger.warning(f"Tool {selected_tool['id']} missing parameters: {missing_params}")
                # Try to find a tool that has the required parameters
                for tool in available_tools[1:]:
                    tool_params = self.tool_registry.get_required_params(tool["id"])
                    missing_params = [p for p in tool_params if p not in task["args"]]
                    if not missing_params:
                        selected_tool = tool
                        break
                else:
                    # No tool has all required parameters
                    logger.error(f"No tool for task {task['task']} has all required parameters")
                    return None
            
            logger.info(f"Selected tool {selected_tool['id']} for task {task['task']}")
            return selected_tool
            
        except Exception as e:
            logger.error(f"Error selecting tool for task {task}: {e}")
            return None
    
    def resolve_dependencies(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Resolve task dependencies and ensure valid execution order.
        """
        try:
            # Create a mapping of task IDs to tasks
            task_map = {task["id"]: task for task in tasks}
            
            # Check for circular dependencies
            for task in tasks:
                for dep_id in task["dep"]:
                    if dep_id != -1 and dep_id not in task_map:
                        logger.warning(f"Task {task['id']} depends on non-existent task {dep_id}")
                        task["dep"] = [-1]  # Remove invalid dependency
            
            # Ensure tasks are in an executable order
            # Simple approach: sort by dependency depth
            def get_dependency_depth(task_id, depth=0, visited=None):
                if visited is None:
                    visited = set()
                
                if task_id in visited:
                    logger.warning(f"Circular dependency detected for task {task_id}")
                    return depth
                
                visited.add(task_id)
                
                if task_id not in task_map:
                    return depth
                
                task = task_map[task_id]
                if task["dep"] == [-1]:
                    return depth
                
                max_depth = depth
                for dep_id in task["dep"]:
                    dep_depth = get_dependency_depth(dep_id, depth + 1, visited.copy())
                    max_depth = max(max_depth, dep_depth)
                
                return max_depth
            
            # Sort tasks by dependency depth
            tasks_with_depth = [(task, get_dependency_depth(task["id"])) for task in tasks]
            sorted_tasks = sorted(tasks_with_depth, key=lambda x: x[1])
            
            return [task for task, depth in sorted_tasks]
            
        except Exception as e:
            logger.error(f"Error resolving dependencies: {e}")
            return tasks