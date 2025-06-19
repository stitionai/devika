import json
from typing import List, Dict, Any
from jinja2 import Environment, BaseLoader
from src.llm import LLM
from src.services.utils import retry_wrapper, validate_responses
from src.browser.search import BingSearch, GoogleSearch, DuckDuckGoSearch

PROMPT = open("src/agents/smart_researcher/prompt.jinja2", "r").read().strip()

class SmartResearcher:
    """Enhanced researcher with intelligent query generation and filtering"""
    
    def __init__(self, base_model: str, search_engine: str = "bing"):
        self.llm = LLM(model_id=base_model)
        self.search_engine = search_engine
        
        if search_engine == "bing":
            self.search = BingSearch()
        elif search_engine == "google":
            self.search = GoogleSearch()
        else:
            self.search = DuckDuckGoSearch()

    def render(self, step_by_step_plan: str, contextual_keywords: List[str], context: Dict[str, Any] = None) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(PROMPT)
        return template.render(
            step_by_step_plan=step_by_step_plan,
            contextual_keywords=contextual_keywords,
            context=context or {}
        )

    @validate_responses
    def validate_response(self, response: str) -> dict:
        required_fields = ["queries", "ask_user", "research_strategy", "priority_queries"]
        
        for field in required_fields:
            if field not in response:
                return False
        
        return response

    def filter_queries(self, queries: List[str], context: Dict[str, Any]) -> List[str]:
        """Filter and prioritize search queries based on context"""
        if not queries:
            return []
        
        # Remove duplicates while preserving order
        unique_queries = []
        seen = set()
        for query in queries:
            if query.lower() not in seen:
                unique_queries.append(query)
                seen.add(query.lower())
        
        # Prioritize based on technical context
        technical_context = context.get("technical_context", {})
        languages = technical_context.get("programming_languages", [])
        frameworks = technical_context.get("frameworks", [])
        
        prioritized = []
        regular = []
        
        for query in unique_queries:
            query_lower = query.lower()
            is_priority = False
            
            # Prioritize queries related to detected technologies
            for lang in languages:
                if lang in query_lower:
                    is_priority = True
                    break
            
            if not is_priority:
                for framework in frameworks:
                    if framework in query_lower:
                        is_priority = True
                        break
            
            if is_priority:
                prioritized.append(query)
            else:
                regular.append(query)
        
        # Return prioritized queries first, then regular ones
        return (prioritized + regular)[:5]  # Limit to 5 queries max

    def generate_smart_queries(self, plan: str, keywords: List[str], context: Dict[str, Any]) -> List[str]:
        """Generate intelligent search queries based on plan and context"""
        # Extract technical context
        technical_context = context.get("technical_context", {})
        languages = technical_context.get("programming_languages", [])
        frameworks = technical_context.get("frameworks", [])
        dev_type = technical_context.get("development_type", "general")
        
        # Generate context-aware queries
        smart_queries = []
        
        # Add language-specific queries
        for lang in languages[:2]:  # Top 2 languages
            for keyword in keywords[:3]:  # Top 3 keywords
                smart_queries.append(f"{keyword} {lang} best practices")
                smart_queries.append(f"{lang} {keyword} tutorial")
        
        # Add framework-specific queries
        for framework in frameworks[:2]:  # Top 2 frameworks
            smart_queries.append(f"{framework} documentation")
            smart_queries.append(f"{framework} examples")
        
        # Add development-type specific queries
        if dev_type == "web":
            smart_queries.extend([
                "modern web development practices",
                "responsive design patterns",
                "web performance optimization"
            ])
        elif dev_type == "mobile":
            smart_queries.extend([
                "mobile app development best practices",
                "mobile UI/UX patterns"
            ])
        elif dev_type == "data_science":
            smart_queries.extend([
                "data analysis techniques",
                "machine learning implementation"
            ])
        
        return smart_queries[:10]  # Limit to 10 queries

    @retry_wrapper
    def execute(self, step_by_step_plan: str, contextual_keywords: List[str], context: Dict[str, Any] = None, project_name: str = "") -> dict:
        # Generate smart queries based on context
        smart_queries = self.generate_smart_queries(step_by_step_plan, contextual_keywords, context or {})
        
        # Render prompt with enhanced context
        prompt = self.render(step_by_step_plan, contextual_keywords + smart_queries, context)
        response = self.llm.inference(prompt, project_name)
        
        valid_response = self.validate_response(response)
        
        # Filter and prioritize queries
        filtered_queries = self.filter_queries(valid_response["queries"], context or {})
        
        return {
            "queries": filtered_queries,
            "ask_user": valid_response["ask_user"],
            "research_strategy": valid_response.get("research_strategy", "comprehensive"),
            "priority_queries": valid_response.get("priority_queries", []),
            "smart_queries": smart_queries[:5]  # Include generated smart queries
        }