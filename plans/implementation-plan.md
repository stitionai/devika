# GitHub Agent Secretary - Implementation Plan

## Overview

This document provides the step-by-step implementation plan for building the GitHub Agent Secretary. It includes all configuration templates, code structures, and deployment instructions.

---

## Phase 1: Foundation Setup

### 1.1 Environment Configuration

Create `.env` file from the following template:

```bash
# =============================================================================
# CORE LLM API KEYS
# =============================================================================

# Anthropic (Claude)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
ANTHROPIC_API_KEY_2=your-secondary-anthropic-key-here

# OpenAI (GPT-4, etc.)
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_ORG_ID=your-openai-org-id

# Google (Gemini)
GOOGLE_API_KEY=your-google-api-key-here

# =============================================================================
# CLOUD SERVICES
# =============================================================================

# GitHub
GH_PAT=your-github-personal-access-token

# Coolify
COOLIFY_URL=https://your-coolify-instance.com
COOLIFY_API_TOKEN=your-coolify-api-token
COOLIFY_WEBHOOK_URL=https://your-coolify-instance.com/api/v1/deploy/webhook/webhook-id
COOLIFY_PROJECT_ID=your-project-uuid

# Hostinger
HOSTINGER_API_TOKEN=your-hostinger-api-token

# Cloudflare
CLOUDFLARE_API_TOKEN=your-cloudflare-api-token

# =============================================================================
# COMMUNICATION
# =============================================================================

TELEGRAM_BOT_TOKEN=your-telegram-bot-token
NOTION_API_TOKEN=your-notion-api-token

# =============================================================================
# DATABASE
# =============================================================================

SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key

# =============================================================================
# AGENT ZERO
# =============================================================================

AZ_BASE_URL=your-agent-zero-url
AZ_API_KEY=your-agent-zero-api-key
```

### 1.2 Update .gitignore

Add the following entries to `.gitignore`:

```gitignore
# Secrets - NEVER COMMIT
.env
.env.local
.env.*.local
*.pem
*.key
secrets/

# Logs
logs/
*.log

# Database
*.db
*.sqlite
*.sqlite3

# Generated files
data/
projects/
screenshots/
pdfs/
```

### 1.3 Project Structure

Create the following directory structure:

```
/github-agent-secretary/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── repo_scanner.py
│   │   ├── prd_generator.py
│   │   └── report_engine.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── websocket.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── commands.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   └── config.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   ├── github.py
│   │   ├── coolify.py
│   │   ├── hostinger.py
│   │   └── cloudflare.py
│   ├── secrets/
│   │   ├── __init__.py
│   │   └── manager.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       └── crypto.py
├── logs/
│   ├── agent/
│   ├── repos/
│   ├── prds/
│   └── deployments/
├── ui/
│   └── dashboard/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env
├── .gitignore
├── config.toml
├── requirements.txt
├── AGENTS.md
└── README.md
```

---

## Phase 2: Core Modules

### 2.1 Secrets Manager (src/secrets/manager.py)

```python
"""
Secrets Management Module
Handles secure loading and access of API keys and tokens
"""
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from datetime import datetime

class SecretsManager:
    """
    Secure secrets management with encryption and audit logging
    """
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = Path(env_file)
        self._secrets: Dict[str, str] = {}
        self._audit_log: list = []
        self._load_secrets()
    
    def _load_secrets(self) -> None:
        """Load secrets from environment file"""
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self._secrets[key.strip()] = value.strip()
        
        # Also load from environment variables (take precedence)
        for key in self._secrets:
            env_value = os.environ.get(key)
            if env_value:
                self._secrets[key] = env_value
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a secret value with audit logging
        
        Args:
            key: Secret key name
            default: Default value if not found
            
        Returns:
            Secret value or default
        """
        self._log_access(key)
        return self._secrets.get(key, default)
    
    def require(self, key: str) -> str:
        """
        Get a required secret, raise error if not found
        
        Args:
            key: Secret key name
            
        Returns:
            Secret value
            
        Raises:
            ValueError: If secret not found
        """
        value = self.get(key)
        if value is None:
            raise ValueError(f"Required secret '{key}' not found")
        return value
    
    def set(self, key: str, value: str) -> None:
        """
        Set a secret value (in memory only, not persisted)
        
        Args:
            key: Secret key name
            value: Secret value
        """
        self._secrets[key] = value
        self._log_access(key, action="set")
    
    def _log_access(self, key: str, action: str = "get") -> None:
        """Log secret access for audit trail"""
        self._audit_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "key": key,
            "action": action
        })
    
    def get_audit_log(self) -> list:
        """Get audit log of all secret accesses"""
        return self._audit_log.copy()
    
    def list_keys(self) -> list:
        """List all available secret keys (not values)"""
        return list(self._secrets.keys())
    
    def validate_required_secrets(self, required: list) -> Dict[str, bool]:
        """
        Validate that all required secrets are present
        
        Args:
            required: List of required secret keys
            
        Returns:
            Dict mapping keys to presence status
        """
        return {key: key in self._secrets for key in required}


# Global instance
secrets = SecretsManager()
```

### 2.2 Canonical Logger (src/utils/logging.py)

```python
"""
Canonical Logging System
Maintains structured, queryable logs of all agent operations
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from uuid import uuid4

class CanonicalLogger:
    """
    Structured logging with correlation IDs and category-based storage
    """
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create category directories
        for category in ["agent", "repos", "prds", "deployments", "secrets", "errors"]:
            (self.log_dir / category).mkdir(exist_ok=True)
    
    def _get_log_path(self, category: str) -> Path:
        """Get log file path for category and date"""
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        return self.log_dir / category / f"{date_str}.jsonl"
    
    def log(
        self,
        category: str,
        action: str,
        details: Dict[str, Any],
        level: str = "INFO",
        correlation_id: Optional[str] = None,
        repo: Optional[str] = None
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
            
        Returns:
            Correlation ID for tracking
        """
        if correlation_id is None:
            correlation_id = str(uuid4())
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "correlation_id": correlation_id,
            "action": action,
            "details": details
        }
        
        if repo:
            entry["repo"] = repo
        
        log_path = self._get_log_path(category)
        with open(log_path, 'a') as f:
            f.write(json.dumps(entry) + "\n")
        
        return correlation_id
    
    def log_agent_action(
        self,
        action: str,
        details: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Log agent action"""
        return self.log("agent", action, details, correlation_id=correlation_id)
    
    def log_repo_scan(
        self,
        repo_url: str,
        details: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Log repository scan"""
        return self.log("repos", "scan", details, repo=repo_url, correlation_id=correlation_id)
    
    def log_prd_change(
        self,
        prd_id: str,
        action: str,
        details: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Log PRD change"""
        details["prd_id"] = prd_id
        return self.log("prds", action, details, correlation_id=correlation_id)
    
    def log_deployment(
        self,
        action: str,
        details: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Log deployment action"""
        return self.log("deployments", action, details, correlation_id=correlation_id)
    
    def log_secret_access(
        self,
        key: str,
        action: str,
        correlation_id: Optional[str] = None
    ) -> str:
        """Log secret access (key name only, never value)"""
        return self.log("secrets", action, {"key": key}, correlation_id=correlation_id)
    
    def log_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Log error with context"""
        details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context
        }
        return self.log("errors", "error", details, level="ERROR", correlation_id=correlation_id)
    
    def query(
        self,
        category: str,
        date: Optional[str] = None,
        action: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> list:
        """
        Query logs by criteria
        
        Args:
            category: Log category
            date: Date string (YYYY-MM-DD)
            action: Filter by action
            correlation_id: Filter by correlation ID
            
        Returns:
            List of matching log entries
        """
        if date is None:
            date = datetime.utcnow().strftime("%Y-%m-%d")
        
        log_path = self._get_log_path(category)
        if not log_path.exists():
            return []
        
        results = []
        with open(log_path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                
                if action and entry.get("action") != action:
                    continue
                if correlation_id and entry.get("correlation_id") != correlation_id:
                    continue
                
                results.append(entry)
        
        return results


# Global instance
logger = CanonicalLogger()
```

### 2.3 GitHub Integration (src/integrations/github.py)

```python
"""
GitHub Integration Module
Handles repository operations via GitHub API
"""
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

class GitHubIntegration:
    """
    GitHub API integration for repository operations
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_repo(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get repository metadata
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository metadata dictionary
        """
        response = requests.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_repo_contents(self, owner: str, repo: str, path: str = "") -> List[Dict]:
        """
        Get repository contents at path
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Path within repository
            
        Returns:
            List of file/directory metadata
        """
        response = requests.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_readme(self, owner: str, repo: str) -> Optional[str]:
        """
        Get repository README content
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            README content or None
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/readme",
                headers=self.headers
            )
            response.raise_for_status()
            import base64
            content = response.json()
            return base64.b64decode(content['content']).decode('utf-8')
        except requests.exceptions.HTTPError:
            return None
    
    def get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """
        Get content of a specific file
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            
        Returns:
            File content or None
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{path}",
                headers=self.headers
            )
            response.raise_for_status()
            import base64
            content = response.json()
            if content.get('type') == 'file':
                return base64.b64decode(content['content']).decode('utf-8')
            return None
        except requests.exceptions.HTTPError:
            return None
    
    def list_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        List languages used in repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary of language -> bytes
        """
        response = requests.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/languages",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_tree(self, owner: str, repo: str, branch: str = "main") -> List[Dict]:
        """
        Get repository file tree
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            
        Returns:
            List of tree entries
        """
        # First get the branch to find the tree SHA
        response = requests.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/branches/{branch}",
            headers=self.headers
        )
        response.raise_for_status()
        tree_sha = response.json()['commit']['commit']['tree']['sha']
        
        # Get the tree recursively
        response = requests.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get('tree', [])
    
    def get_issues(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """
        Get repository issues
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            
        Returns:
            List of issues
        """
        response = requests.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/issues",
            headers=self.headers,
            params={"state": state}
        )
        response.raise_for_status()
        return response.json()
    
    def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> List[Dict]:
        """
        Get repository pull requests
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state (open, closed, all)
            
        Returns:
            List of pull requests
        """
        response = requests.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/pulls",
            headers=self.headers,
            params={"state": state}
        )
        response.raise_for_status()
        return response.json()
    
    def get_workflow_runs(self, owner: str, repo: str) -> List[Dict]:
        """
        Get GitHub Actions workflow runs
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of workflow runs
        """
        response = requests.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/actions/runs",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get('workflow_runs', [])
    
    def scan_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Perform comprehensive repository scan
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Complete scan results
        """
        result = {
            "metadata": self.get_repo(owner, repo),
            "languages": self.list_languages(owner, repo),
            "readme": self.get_readme(owner, repo),
            "tree": self.get_tree(owner, repo),
            "issues": self.get_issues(owner, repo),
            "pull_requests": self.get_pull_requests(owner, repo),
            "workflows": self.get_workflow_runs(owner, repo),
            "scanned_at": datetime.utcnow().isoformat()
        }
        
        return result
```

### 2.4 Coolify Integration (src/integrations/coolify.py)

```python
"""
Coolify Integration Module
Handles deployment operations via Coolify API
"""
import requests
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

class CoolifyIntegration:
    """
    Coolify API integration for deployment management
    """
    
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def get_applications(self) -> List[Dict]:
        """Get all applications"""
        response = requests.get(
            f"{self.base_url}/api/v1/applications",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_application(self, app_id: str) -> Dict:
        """Get application by ID"""
        response = requests.get(
            f"{self.base_url}/api/v1/applications/{app_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def deploy_application(self, app_id: str) -> Dict:
        """Trigger application deployment"""
        response = requests.get(
            f"{self.base_url}/api/v1/deploy",
            headers=self.headers,
            params={"uuid": app_id}
        )
        response.raise_for_status()
        return response.json()
    
    def get_deployment_status(self, deployment_id: str) -> Dict:
        """Get deployment status"""
        response = requests.get(
            f"{self.base_url}/api/v1/deployments/{deployment_id}",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_servers(self) -> List[Dict]:
        """Get all servers"""
        response = requests.get(
            f"{self.base_url}/api/v1/servers",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def get_projects(self) -> List[Dict]:
        """Get all projects"""
        response = requests.get(
            f"{self.base_url}/api/v1/projects",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()
    
    def trigger_webhook(self, webhook_url: str) -> Dict:
        """Trigger deployment via webhook"""
        response = requests.get(webhook_url)
        response.raise_for_status()
        return response.json()
```

### 2.5 Repository Scanner Agent (src/agents/repo_scanner.py)

```python
"""
Repository Scanner Agent
Analyzes GitHub repositories and generates reports
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

from src.integrations.github import GitHubIntegration
from src.utils.logging import CanonicalLogger

@dataclass
class ScanResult:
    """Repository scan result"""
    repo_url: str
    metadata: Dict[str, Any]
    languages: Dict[str, int]
    structure: List[Dict]
    issues: List[Dict]
    pull_requests: List[Dict]
    workflows: List[Dict]
    readme: Optional[str]
    recommendations: List[str]
    scanned_at: str

class RepoScannerAgent:
    """
    Agent for scanning and analyzing GitHub repositories
    """
    
    def __init__(self, github_token: str):
        self.github = GitHubIntegration(github_token)
        self.logger = CanonicalLogger()
    
    def scan(self, repo_url: str) -> ScanResult:
        """
        Scan a repository and generate analysis
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            ScanResult with complete analysis
        """
        correlation_id = self.logger.log_repo_scan(
            repo_url, 
            {"status": "started"}
        )
        
        try:
            # Parse owner/repo from URL
            parts = repo_url.rstrip('/').split('/')
            owner, repo = parts[-2], parts[-1]
            
            # Perform scan
            scan_data = self.github.scan_repository(owner, repo)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(scan_data)
            
            result = ScanResult(
                repo_url=repo_url,
                metadata=scan_data['metadata'],
                languages=scan_data['languages'],
                structure=scan_data['tree'],
                issues=scan_data['issues'],
                pull_requests=scan_data['pull_requests'],
                workflows=scan_data['workflows'],
                readme=scan_data['readme'],
                recommendations=recommendations,
                scanned_at=datetime.utcnow().isoformat()
            )
            
            self.logger.log_repo_scan(
                repo_url,
                {"status": "completed", "recommendations_count": len(recommendations)},
                correlation_id
            )
            
            return result
            
        except Exception as e:
            self.logger.log_error(e, {"repo_url": repo_url}, correlation_id)
            raise
    
    def _generate_recommendations(self, scan_data: Dict) -> List[str]:
        """Generate recommendations based on scan data"""
        recommendations = []
        
        # Check for README
        if not scan_data.get('readme'):
            recommendations.append("Add a README.md file to document the project")
        
        # Check for CI/CD
        has_ci = any(
            '.github/workflows' in str(item.get('path', ''))
            for item in scan_data.get('tree', [])
        )
        if not has_ci:
            recommendations.append("Add CI/CD workflows for automated testing and deployment")
        
        # Check for tests
        has_tests = any(
            'test' in str(item.get('path', '')).lower()
            for item in scan_data.get('tree', [])
        )
        if not has_tests:
            recommendations.append("Add test files to improve code quality")
        
        # Check for open issues
        open_issues = [i for i in scan_data.get('issues', []) if i.get('state') == 'open']
        if len(open_issues) > 10:
            recommendations.append(f"Consider addressing {len(open_issues)} open issues")
        
        # Check for language diversity
        languages = scan_data.get('languages', {})
        if len(languages) > 5:
            recommendations.append("Consider consolidating languages for maintainability")
        
        return recommendations
    
    def generate_report(self, scan_result: ScanResult) -> str:
        """
        Generate markdown report from scan result
        
        Args:
            scan_result: ScanResult object
            
        Returns:
            Markdown formatted report
        """
        report = f"""# Repository Analysis Report

## Metadata

| Property | Value |
|----------|-------|
| **Repository** | [{scan_result.metadata.get('full_name', 'N/A')}]({scan_result.metadata.get('html_url', '#')}) |
| **Description** | {scan_result.metadata.get('description', 'No description')} |
| **Primary Language** | {scan_result.metadata.get('language', 'N/A')} |
| **Stars** | {scan_result.metadata.get('stargazers_count', 0)} |
| **Forks** | {scan_result.metadata.get('forks_count', 0)} |
| **Open Issues** | {scan_result.metadata.get('open_issues_count', 0)} |
| **Last Updated** | {scan_result.metadata.get('updated_at', 'N/A')} |
| **Scanned At** | {scan_result.scanned_at} |

## Languages

| Language | Bytes |
|----------|-------|
"""
        for lang, bytes_count in sorted(scan_result.languages.items(), key=lambda x: x[1], reverse=True):
            report += f"| {lang} | {bytes_count:,} |\n"
        
        report += f"""
## Structure

Total files: {len([i for i in scan_result.structure if i.get('type') == 'blob'])}
Total directories: {len([i for i in scan_result.structure if i.get('type') == 'tree'])}

## Issues

Open issues: {len([i for i in scan_result.issues if i.get('state') == 'open'])}

## Pull Requests

Open PRs: {len([pr for pr in scan_result.pull_requests if pr.get('state') == 'open'])}

## CI/CD

Workflow runs: {len(scan_result.workflows)}

## Recommendations

"""
        for i, rec in enumerate(scan_result.recommendations, 1):
            report += f"{i}. {rec}\n"
        
        return report
```

---

## Phase 3: API Server

### 3.1 REST API Routes (src/api/routes.py)

```python
"""
API Routes
REST endpoints for agent operations
"""
from flask import Blueprint, request, jsonify
from typing import Dict, Any

from src.agents.repo_scanner import RepoScannerAgent
from src.utils.logging import CanonicalLogger
from src.secrets.manager import secrets

api_bp = Blueprint('api', __name__)
logger = CanonicalLogger()

# Initialize agents
scanner = None

def get_scanner():
    """Get or create scanner instance"""
    global scanner
    if scanner is None:
        github_token = secrets.require('GH_PAT')
        scanner = RepoScannerAgent(github_token)
    return scanner

@api_bp.route('/status', methods=['GET'])
def status():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "agent": "github-secretary"})

@api_bp.route('/repo/scan', methods=['POST'])
def scan_repo():
    """Scan a repository"""
    data = request.json
    repo_url = data.get('repo_url')
    
    if not repo_url:
        return jsonify({"error": "repo_url required"}), 400
    
    try:
        scanner = get_scanner()
        result = scanner.scan(repo_url)
        report = scanner.generate_report(result)
        
        return jsonify({
            "success": True,
            "report": report,
            "metadata": {
                "repo_url": result.repo_url,
                "languages": result.languages,
                "recommendations": result.recommendations,
                "scanned_at": result.scanned_at
            }
        })
    except Exception as e:
        logger.log_error(e, {"repo_url": repo_url})
        return jsonify({"error": str(e)}), 500

@api_bp.route('/repo/report', methods=['GET'])
def get_report():
    """Get cached report for repository"""
    repo_url = request.args.get('repo_url')
    # TODO: Implement report caching
    return jsonify({"error": "Not implemented"}), 501

@api_bp.route('/prd/create', methods=['POST'])
def create_prd():
    """Create a new PRD"""
    data = request.json
    # TODO: Implement PRD creation
    return jsonify({"error": "Not implemented"}), 501

@api_bp.route('/prd/list', methods=['GET'])
def list_prds():
    """List all PRDs"""
    # TODO: Implement PRD listing
    return jsonify({"prds": []})

@api_bp.route('/deploy/trigger', methods=['POST'])
def trigger_deploy():
    """Trigger deployment"""
    data = request.json
    # TODO: Implement deployment trigger
    return jsonify({"error": "Not implemented"}), 501

@api_bp.route('/logs', methods=['GET'])
def get_logs():
    """Get canonical logs"""
    category = request.args.get('category', 'agent')
    date = request.args.get('date')
    
    logs = logger.query(category, date)
    return jsonify({"logs": logs})

@api_bp.route('/secrets/audit', methods=['GET'])
def secrets_audit():
    """Get secret access audit log"""
    logs = logger.query('secrets')
    return jsonify({"audit": logs})
```

---

## Phase 4: Docker Configuration

### 4.1 Dockerfile

```dockerfile
# GitHub Agent Secretary Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs/agent logs/repos logs/prds logs/deployments logs/secrets logs/errors

# Create non-root user
RUN useradd -m -u 1000 agent && chown -R agent:agent /app
USER agent

# Expose port
EXPOSE 1337

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:1337/api/status || exit 1

# Start command
CMD ["python", "-m", "src.api.routes"]
```

### 4.2 docker-compose.yml

```yaml
version: "3.9"

services:
  agent-api:
    build:
      context: .
      dockerfile: docker/Dockerfile
    ports:
      - "1337:1337"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - GH_PAT=${GH_PAT}
      - COOLIFY_URL=${COOLIFY_URL}
      - COOLIFY_API_TOKEN=${COOLIFY_API_TOKEN}
      - HOSTINGER_API_TOKEN=${HOSTINGER_API_TOKEN}
      - CLOUDFLARE_API_TOKEN=${CLOUDFLARE_API_TOKEN}
    volumes:
      - agent-logs:/app/logs
      - agent-data:/app/data
    networks:
      - agent-network
    restart: unless-stopped

volumes:
  agent-logs:
  agent-data:

networks:
  agent-network:
    driver: bridge
```

---

## Phase 5: CLI Tool

### 5.1 CLI Commands (src/cli/commands.py)

```python
"""
CLI Commands
Command-line interface for agent operations
"""
import click
import json
from typing import Optional

from src.agents.repo_scanner import RepoScannerAgent
from src.utils.logging import CanonicalLogger
from src.secrets.manager import secrets

@click.group()
def cli():
    """GitHub Agent Secretary CLI"""
    pass

# Repository commands
@cli.group()
def repo():
    """Repository operations"""
    pass

@repo.command()
@click.argument('url')
def scan(url):
    """Scan a repository"""
    click.echo(f"Scanning repository: {url}")
    
    try:
        scanner = RepoScannerAgent(secrets.require('GH_PAT'))
        result = scanner.scan(url)
        report = scanner.generate_report(result)
        
        click.echo(report)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@repo.command()
def list():
    """List monitored repositories"""
    click.echo("Monitored repositories:")
    # TODO: Implement from database
    click.echo("  (none configured)")

# PRD commands
@cli.group()
def prd():
    """PRD operations"""
    pass

@prd.command()
@click.argument('repo_url')
def create(repo_url):
    """Create a new PRD for repository"""
    click.echo(f"Creating PRD for: {repo_url}")
    # TODO: Implement PRD creation

@prd.command()
def list():
    """List all PRDs"""
    click.echo("PRDs:")
    # TODO: Implement from database
    click.echo("  (none created)")

# Deployment commands
@cli.group()
def deploy():
    """Deployment operations"""
    pass

@deploy.command()
def status():
    """Check deployment status"""
    click.echo("Deployment status: Not deployed")

@deploy.command()
def trigger():
    """Trigger deployment"""
    click.echo("Triggering deployment...")
    # TODO: Implement deployment trigger

# Secret commands
@cli.group()
def secrets_cmd():
    """Secret operations"""
    pass

@secrets_cmd.command('list')
def list_secrets():
    """List secret keys"""
    keys = secrets.list_keys()
    click.echo("Configured secrets:")
    for key in keys:
        click.echo(f"  - {key}")

@secrets_cmd.command('audit')
def audit_secrets():
    """View secret access audit"""
    logger = CanonicalLogger()
    logs = logger.query('secrets')
    click.echo("Secret access audit:")
    for entry in logs:
        click.echo(f"  {entry['timestamp']}: {entry['details']['key']} ({entry['details']['action']})")

# Agent commands
@cli.command()
def status():
    """Agent health status"""
    click.echo("Agent Status: Healthy")
    click.echo(f"Configured secrets: {len(secrets.list_keys())}")

@cli.command()
@click.option('--category', default='agent', help='Log category')
@click.option('--date', default=None, help='Date (YYYY-MM-DD)')
def logs(category, date):
    """View agent logs"""
    logger = CanonicalLogger()
    entries = logger.query(category, date)
    
    for entry in entries:
        click.echo(json.dumps(entry, indent=2))

if __name__ == '__main__':
    cli()
```

### 5.2 CLI Entry Point (setup.py addition)

```python
# Add to setup.py console_scripts:
# 'agent = src.cli.commands:cli'
```

---

## Phase 6: Requirements

### requirements.txt

```
# Core
flask>=2.3.0
flask-cors>=4.0.0
flask-socketio>=5.3.0
gevent>=23.9.0

# LLM
anthropic>=0.18.0
openai>=1.0.0
google-generativeai>=0.3.0
tiktoken>=0.5.0

# Integrations
requests>=2.31.0
PyGithub>=2.0.0

# Database
sqlmodel>=0.0.14
supabase>=2.0.0

# Browser Automation
playwright>=1.40.0
markdownify>=0.11.0
pdfminer.six>=20221105

# Security
cryptography>=41.0.0
python-dotenv>=1.0.0

# CLI
click>=8.1.0

# Utilities
toml>=0.10.2
pydantic>=2.0.0

# Logging
structlog>=23.1.0
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Copy `.env.template` to `.env`
- [ ] Fill in all required secrets
- [ ] Verify `.env` is in `.gitignore`
- [ ] Test locally with `python devika.py`
- [ ] Build Docker image: `docker build -t github-agent-secretary .`
- [ ] Test Docker: `docker run -p 1337:1337 github-agent-secretary`

### Coolify Deployment

- [ ] Create new application in Coolify
- [ ] Connect to GitHub repository
- [ ] Set environment variables from `.env`
- [ ] Configure domain and SSL
- [ ] Deploy and verify health check

### Post-Deployment

- [ ] Verify API status endpoint
- [ ] Test repository scan functionality
- [ ] Configure Cloudflare DNS
- [ ] Set up monitoring and alerts
- [ ] Document deployment URL

---

*Document Version: 1.0.0*
*Last Updated: 2024-02-14*
