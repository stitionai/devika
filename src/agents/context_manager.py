import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from src.memory import KnowledgeBase
from src.bert.sentence import SentenceBert
from src.logger import Logger

class ContextManager:
    """Enhanced context management for better agent performance"""
    
    def __init__(self):
        self.knowledge_base = KnowledgeBase()
        self.logger = Logger()
        self.context_cache = {}
        self.context_history = {}
    
    def extract_context_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """Extract relevant keywords from text"""
        try:
            sentence_bert = SentenceBert(text)
            keywords = sentence_bert.extract_keywords(top_n=top_k)
            return [keyword[0] for keyword in keywords]
        except Exception as e:
            self.logger.error(f"Error extracting keywords: {str(e)}")
            return []
    
    def build_context(self, project_name: str, current_prompt: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Build comprehensive context for agent execution"""
        context = {
            "project_name": project_name,
            "current_prompt": current_prompt,
            "timestamp": datetime.now().isoformat(),
            "keywords": [],
            "related_knowledge": [],
            "conversation_summary": "",
            "technical_context": {},
            "project_context": {}
        }
        
        # Extract keywords from current prompt
        context["keywords"] = self.extract_context_keywords(current_prompt)
        
        # Build conversation summary
        context["conversation_summary"] = self._summarize_conversation(conversation_history)
        
        # Get related knowledge from knowledge base
        for keyword in context["keywords"][:5]:  # Top 5 keywords
            knowledge = self.knowledge_base.get_knowledge(keyword)
            if knowledge:
                context["related_knowledge"].append({
                    "keyword": keyword,
                    "knowledge": knowledge
                })
        
        # Build technical context
        context["technical_context"] = self._extract_technical_context(current_prompt, conversation_history)
        
        # Build project context
        context["project_context"] = self._build_project_context(project_name)
        
        # Cache context for future use
        self.context_cache[project_name] = context
        
        return context
    
    def _summarize_conversation(self, conversation_history: List[Dict]) -> str:
        """Summarize conversation history"""
        if not conversation_history:
            return "No previous conversation"
        
        # Take last 5 messages for summary
        recent_messages = conversation_history[-5:]
        summary_parts = []
        
        for msg in recent_messages:
            role = "User" if not msg.get("from_devika", False) else "Devika"
            content = msg.get("message", "")[:100]  # Truncate long messages
            summary_parts.append(f"{role}: {content}")
        
        return " | ".join(summary_parts)
    
    def _extract_technical_context(self, prompt: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Extract technical context from prompt and conversation"""
        technical_context = {
            "programming_languages": [],
            "frameworks": [],
            "technologies": [],
            "development_type": "general"
        }
        
        # Common patterns to detect
        languages = ["python", "javascript", "typescript", "java", "c++", "c#", "go", "rust", "php", "ruby"]
        frameworks = ["react", "vue", "angular", "django", "flask", "express", "spring", "laravel"]
        technologies = ["docker", "kubernetes", "aws", "azure", "gcp", "mongodb", "postgresql", "redis"]
        
        text_to_analyze = prompt.lower()
        for msg in conversation_history[-3:]:  # Last 3 messages
            text_to_analyze += " " + msg.get("message", "").lower()
        
        # Detect languages
        for lang in languages:
            if lang in text_to_analyze:
                technical_context["programming_languages"].append(lang)
        
        # Detect frameworks
        for framework in frameworks:
            if framework in text_to_analyze:
                technical_context["frameworks"].append(framework)
        
        # Detect technologies
        for tech in technologies:
            if tech in text_to_analyze:
                technical_context["technologies"].append(tech)
        
        # Determine development type
        if any(word in text_to_analyze for word in ["web", "website", "frontend", "backend", "api"]):
            technical_context["development_type"] = "web"
        elif any(word in text_to_analyze for word in ["mobile", "app", "android", "ios"]):
            technical_context["development_type"] = "mobile"
        elif any(word in text_to_analyze for word in ["data", "analysis", "ml", "ai", "machine learning"]):
            technical_context["development_type"] = "data_science"
        elif any(word in text_to_analyze for word in ["game", "unity", "unreal"]):
            technical_context["development_type"] = "game"
        
        return technical_context
    
    def _build_project_context(self, project_name: str) -> Dict[str, Any]:
        """Build project-specific context"""
        project_context = {
            "project_name": project_name,
            "creation_time": None,
            "last_activity": None,
            "file_count": 0,
            "main_language": "unknown",
            "project_type": "unknown"
        }
        
        # This would be enhanced with actual project analysis
        # For now, return basic structure
        return project_context
    
    def get_cached_context(self, project_name: str) -> Optional[Dict[str, Any]]:
        """Get cached context for a project"""
        return self.context_cache.get(project_name)
    
    def update_context_history(self, project_name: str, context: Dict[str, Any]):
        """Update context history for learning"""
        if project_name not in self.context_history:
            self.context_history[project_name] = []
        
        self.context_history[project_name].append({
            "timestamp": datetime.now().isoformat(),
            "context": context
        })
        
        # Keep only last 10 context entries
        self.context_history[project_name] = self.context_history[project_name][-10:]
    
    def get_context_trends(self, project_name: str) -> Dict[str, Any]:
        """Analyze context trends for a project"""
        history = self.context_history.get(project_name, [])
        if not history:
            return {}
        
        trends = {
            "common_keywords": {},
            "technical_evolution": [],
            "activity_pattern": []
        }
        
        # Analyze common keywords
        for entry in history:
            for keyword in entry["context"].get("keywords", []):
                trends["common_keywords"][keyword] = trends["common_keywords"].get(keyword, 0) + 1
        
        # Sort by frequency
        trends["common_keywords"] = dict(sorted(
            trends["common_keywords"].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10])
        
        return trends