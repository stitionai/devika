"""
Canonical Logging System
Maintains structured, queryable logs of all agent operations
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from uuid import uuid4
from dataclasses import dataclass, asdict
from enum import Enum


class LogLevel(str, Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(str, Enum):
    """Log categories for organization"""
    AGENT = "agent"
    REPOS = "repos"
    PRDS = "prds"
    DEPLOYMENTS = "deployments"
    SECRETS = "secrets"
    ERRORS = "errors"


@dataclass
class LogEntry:
    """Structured log entry"""
    timestamp: str
    level: str
    correlation_id: str
    action: str
    details: Dict[str, Any]
    category: str = "agent"
    repo: Optional[str] = None
    agent_id: str = "github-secretary"
    duration_ms: Optional[int] = None
    model_used: Optional[str] = None
    tokens_consumed: Optional[int] = None
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(asdict(self))


class CanonicalLogger:
    """
    Structured logging with correlation IDs and category-based storage
    
    Logs are stored in JSONL format (one JSON object per line) for easy
    parsing and querying.
    """
    
    _instance = None
    
    def __new__(cls, log_dir: str = "logs"):
        """Singleton pattern to ensure single instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, log_dir: str = "logs"):
        if self._initialized:
            return
            
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create category directories
        for category in LogCategory:
            (self.log_dir / category.value).mkdir(exist_ok=True)
        
        self._initialized = True
    
    def _get_log_path(self, category: str, date: Optional[str] = None) -> Path:
        """Get log file path for category and date"""
        if date is None:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        return self.log_dir / category / f"{date}.jsonl"
    
    def log(
        self,
        category: str,
        action: str,
        details: Dict[str, Any],
        level: str = "INFO",
        correlation_id: Optional[str] = None,
        repo: Optional[str] = None,
        duration_ms: Optional[int] = None,
        model_used: Optional[str] = None,
        tokens_consumed: Optional[int] = None
    ) -> str:
        """
        Write a structured log entry
        
        Args:
            category: Log category (agent, repos, prds, deployments, secrets, errors)
            action: Action being performed
            details: Additional details dictionary
            level: Log level (DEBUG, INFO, WARN, ERROR, CRITICAL)
            correlation_id: Optional correlation ID for tracking
            repo: Optional repository context
            duration_ms: Optional duration in milliseconds
            model_used: Optional LLM model used
            tokens_consumed: Optional token count
            
        Returns:
            Correlation ID for tracking
        """
        if correlation_id is None:
            correlation_id = str(uuid4())
        
        entry = LogEntry(
            timestamp=datetime.utcnow().isoformat(),
            level=level,
            correlation_id=correlation_id,
            action=action,
            details=details,
            category=category,
            repo=repo,
            duration_ms=duration_ms,
            model_used=model_used,
            tokens_consumed=tokens_consumed
        )
        
        log_path = self._get_log_path(category)
        with open(log_path, 'a') as f:
            f.write(entry.to_json() + "\n")
        
        return correlation_id
    
    def log_agent_action(
        self,
        action: str,
        details: Dict[str, Any],
        correlation_id: Optional[str] = None,
        level: str = "INFO"
    ) -> str:
        """Log agent action"""
        return self.log(
            LogCategory.AGENT.value, 
            action, 
            details, 
            correlation_id=correlation_id,
            level=level
        )
    
    def log_repo_scan(
        self,
        repo_url: str,
        action: str,
        details: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Log repository scan"""
        return self.log(
            LogCategory.REPOS.value, 
            action, 
            details, 
            repo=repo_url, 
            correlation_id=correlation_id
        )
    
    def log_prd_change(
        self,
        prd_id: str,
        action: str,
        details: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Log PRD change"""
        details["prd_id"] = prd_id
        return self.log(
            LogCategory.PRDS.value, 
            action, 
            details, 
            correlation_id=correlation_id
        )
    
    def log_deployment(
        self,
        action: str,
        details: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Log deployment action"""
        return self.log(
            LogCategory.DEPLOYMENTS.value, 
            action, 
            details, 
            correlation_id=correlation_id
        )
    
    def log_secret_access(
        self,
        key: str,
        action: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """Log secret access (key name only, never value)"""
        return self.log(
            LogCategory.SECRETS.value, 
            action, 
            {"key": key}, 
            correlation_id=correlation_id
        )
    
    def log_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        correlation_id: Optional[str] = None,
        repo: Optional[str] = None
    ) -> str:
        """Log error with context"""
        details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        return self.log(
            LogCategory.ERRORS.value, 
            "error", 
            details, 
            level=LogLevel.ERROR.value, 
            correlation_id=correlation_id,
            repo=repo
        )
    
    def query(
        self,
        category: str,
        date: Optional[str] = None,
        action: Optional[str] = None,
        correlation_id: Optional[str] = None,
        level: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query logs by criteria
        
        Args:
            category: Log category
            date: Date string (YYYY-MM-DD)
            action: Filter by action
            correlation_id: Filter by correlation ID
            level: Filter by log level
            limit: Maximum number of results
            
        Returns:
            List of matching log entries
        """
        log_path = self._get_log_path(category, date)
        if not log_path.exists():
            return []
        
        results = []
        with open(log_path, 'r') as f:
            for line in f:
                if len(results) >= limit:
                    break
                    
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                if action and entry.get("action") != action:
                    continue
                if correlation_id and entry.get("correlation_id") != correlation_id:
                    continue
                if level and entry.get("level") != level:
                    continue
                
                results.append(entry)
        
        return results
    
    def get_correlation_chain(self, correlation_id: str) -> List[Dict[str, Any]]:
        """
        Get all log entries for a correlation ID across all categories
        
        Args:
            correlation_id: Correlation ID to search for
            
        Returns:
            List of all entries with the correlation ID
        """
        results = []
        
        for category in LogCategory:
            log_path = self._get_log_path(category.value)
            if not log_path.exists():
                continue
            
            with open(log_path, 'r') as f:
                for line in f:
                    try:
                        entry = json.loads(line)
                        if entry.get("correlation_id") == correlation_id:
                            results.append(entry)
                    except json.JSONDecodeError:
                        continue
        
        # Sort by timestamp
        results.sort(key=lambda x: x.get("timestamp", ""))
        return results
    
    def get_recent_errors(self, hours: int = 24, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent errors
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of results
            
        Returns:
            List of recent error entries
        """
        return self.query(
            LogCategory.ERRORS.value, 
            level=LogLevel.ERROR.value,
            limit=limit
        )
    
    def get_stats(self, category: str = "agent", date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a category
        
        Args:
            category: Log category
            date: Date string (YYYY-MM-DD)
            
        Returns:
            Statistics dictionary
        """
        entries = self.query(category, date, limit=10000)
        
        if not entries:
            return {"total": 0}
        
        stats = {
            "total": len(entries),
            "by_level": {},
            "by_action": {},
            "total_tokens": 0,
            "avg_duration_ms": 0
        }
        
        durations = []
        for entry in entries:
            # Count by level
            level = entry.get("level", "UNKNOWN")
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            
            # Count by action
            action = entry.get("action", "unknown")
            stats["by_action"][action] = stats["by_action"].get(action, 0) + 1
            
            # Sum tokens
            if entry.get("tokens_consumed"):
                stats["total_tokens"] += entry["tokens_consumed"]
            
            # Collect durations
            if entry.get("duration_ms"):
                durations.append(entry["duration_ms"])
        
        if durations:
            stats["avg_duration_ms"] = sum(durations) / len(durations)
        
        return stats


# Global singleton instance
canonical_logger = CanonicalLogger()
