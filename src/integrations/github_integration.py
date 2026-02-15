"""
GitHub Integration Module
Handles repository operations via GitHub API
"""
import requests
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class RepositoryInfo:
    """Repository metadata"""
    owner: str
    name: str
    full_name: str
    description: str
    url: str
    stars: int
    forks: int
    open_issues: int
    language: str
    topics: List[str]
    created_at: str
    updated_at: str
    license: Optional[str]
    is_fork: bool
    is_archived: bool


@dataclass
class FileNode:
    """File or directory in repository"""
    path: str
    type: str  # 'file' or 'dir'
    size: Optional[int]
    sha: str


class GitHubIntegration:
    """
    GitHub API integration for repository operations
    
    Provides methods for:
    - Repository metadata retrieval
    - File content access
    - Issue and PR listing
    - Workflow run monitoring
    - Comprehensive repository scanning
    """
    
    BASE_URL = "https://api.github.com"
    
    def __init__(self, token: str):
        """
        Initialize GitHub integration
        
        Args:
            token: GitHub Personal Access Token with appropriate scopes
        """
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Agent-Secretary/1.0"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request to GitHub API"""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(
            method, 
            url, 
            headers=self.headers,
            **kwargs
        )
        response.raise_for_status()
        return response
    
    def _parse_repo_url(self, repo_url: str) -> tuple:
        """Parse owner and repo name from URL"""
        # Handle various URL formats
        repo_url = repo_url.rstrip('/')
        if 'github.com' in repo_url:
            parts = repo_url.split('github.com/')[-1].split('/')
        else:
            parts = repo_url.split('/')
        
        if len(parts) >= 2:
            return parts[0], parts[1]
        raise ValueError(f"Invalid repository URL: {repo_url}")
    
    def get_repo(self, owner: str, repo: str) -> RepositoryInfo:
        """
        Get repository metadata
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            RepositoryInfo object
        """
        response = self._request("GET", f"/repos/{owner}/{repo}")
        data = response.json()
        
        return RepositoryInfo(
            owner=data.get("owner", {}).get("login", ""),
            name=data.get("name", ""),
            full_name=data.get("full_name", ""),
            description=data.get("description", "") or "",
            url=data.get("html_url", ""),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            open_issues=data.get("open_issues_count", 0),
            language=data.get("language", "") or "Unknown",
            topics=data.get("topics", []),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            license=data.get("license", {}).get("spdx_id") if data.get("license") else None,
            is_fork=data.get("fork", False),
            is_archived=data.get("archived", False)
        )
    
    def get_repo_by_url(self, repo_url: str) -> RepositoryInfo:
        """
        Get repository metadata by URL
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            RepositoryInfo object
        """
        owner, repo = self._parse_repo_url(repo_url)
        return self.get_repo(owner, repo)
    
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
            response = self._request("GET", f"/repos/{owner}/{repo}/readme")
            data = response.json()
            return base64.b64decode(data['content']).decode('utf-8')
        except requests.exceptions.HTTPError:
            return None
    
    def get_file_content(self, owner: str, repo: str, path: str, ref: str = "main") -> Optional[str]:
        """
        Get content of a specific file
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: File path
            ref: Branch or commit reference
            
        Returns:
            File content or None
        """
        try:
            response = self._request(
                "GET", 
                f"/repos/{owner}/{repo}/contents/{path}",
                params={"ref": ref}
            )
            data = response.json()
            if data.get('type') == 'file':
                return base64.b64decode(data['content']).decode('utf-8')
            return None
        except requests.exceptions.HTTPError:
            return None
    
    def get_directory_contents(self, owner: str, repo: str, path: str = "", ref: str = "main") -> List[FileNode]:
        """
        Get contents of a directory
        
        Args:
            owner: Repository owner
            repo: Repository name
            path: Directory path (empty for root)
            ref: Branch or commit reference
            
        Returns:
            List of FileNode objects
        """
        try:
            response = self._request(
                "GET",
                f"/repos/{owner}/{repo}/contents/{path}",
                params={"ref": ref}
            )
            data = response.json()
            
            return [
                FileNode(
                    path=item['path'],
                    type=item['type'],
                    size=item.get('size'),
                    sha=item['sha']
                )
                for item in data
            ]
        except requests.exceptions.HTTPError:
            return []
    
    def list_languages(self, owner: str, repo: str) -> Dict[str, int]:
        """
        List languages used in repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Dictionary of language -> bytes
        """
        response = self._request("GET", f"/repos/{owner}/{repo}/languages")
        return response.json()
    
    def get_tree(self, owner: str, repo: str, branch: str = "main") -> List[FileNode]:
        """
        Get complete repository file tree
        
        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            
        Returns:
            List of FileNode objects for all files
        """
        try:
            # Get branch to find tree SHA
            response = self._request("GET", f"/repos/{owner}/{repo}/branches/{branch}")
            tree_sha = response.json()['commit']['commit']['tree']['sha']
            
            # Get tree recursively
            response = self._request(
                "GET",
                f"/repos/{owner}/{repo}/git/trees/{tree_sha}",
                params={"recursive": "1"}
            )
            
            return [
                FileNode(
                    path=item['path'],
                    type=item['type'],
                    size=item.get('size'),
                    sha=item['sha']
                )
                for item in response.json().get('tree', [])
            ]
        except requests.exceptions.HTTPError:
            return []
    
    def get_issues(self, owner: str, repo: str, state: str = "open", limit: int = 30) -> List[Dict]:
        """
        Get repository issues
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state (open, closed, all)
            limit: Maximum number of issues to return
            
        Returns:
            List of issue dictionaries
        """
        response = self._request(
            "GET",
            f"/repos/{owner}/{repo}/issues",
            params={"state": state, "per_page": limit}
        )
        return response.json()
    
    def get_pull_requests(self, owner: str, repo: str, state: str = "open", limit: int = 30) -> List[Dict]:
        """
        Get repository pull requests
        
        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state (open, closed, all)
            limit: Maximum number of PRs to return
            
        Returns:
            List of PR dictionaries
        """
        response = self._request(
            "GET",
            f"/repos/{owner}/{repo}/pulls",
            params={"state": state, "per_page": limit}
        )
        return response.json()
    
    def get_workflow_runs(self, owner: str, repo: str, limit: int = 10) -> List[Dict]:
        """
        Get GitHub Actions workflow runs
        
        Args:
            owner: Repository owner
            repo: Repository name
            limit: Maximum number of runs to return
            
        Returns:
            List of workflow run dictionaries
        """
        response = self._request(
            "GET",
            f"/repos/{owner}/{repo}/actions/runs",
            params={"per_page": limit}
        )
        return response.json().get('workflow_runs', [])
    
    def get_contributors(self, owner: str, repo: str, limit: int = 30) -> List[Dict]:
        """
        Get repository contributors
        
        Args:
            owner: Repository owner
            repo: Repository name
            limit: Maximum number of contributors
            
        Returns:
            List of contributor dictionaries
        """
        response = self._request(
            "GET",
            f"/repos/{owner}/{repo}/contributors",
            params={"per_page": limit}
        )
        return response.json()
    
    def get_releases(self, owner: str, repo: str, limit: int = 10) -> List[Dict]:
        """
        Get repository releases
        
        Args:
            owner: Repository owner
            repo: Repository name
            limit: Maximum number of releases
            
        Returns:
            List of release dictionaries
        """
        response = self._request(
            "GET",
            f"/repos/{owner}/{repo}/releases",
            params={"per_page": limit}
        )
        return response.json()
    
    def scan_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Perform comprehensive repository scan
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Complete scan results dictionary
        """
        owner, repo = self._parse_repo_url(repo_url)
        
        # Get all data
        repo_info = self.get_repo(owner, repo)
        languages = self.list_languages(owner, repo)
        readme = self.get_readme(owner, repo)
        tree = self.get_tree(owner, repo, repo_info.default_branch if hasattr(repo_info, 'default_branch') else 'main')
        issues = self.get_issues(owner, repo)
        pull_requests = self.get_pull_requests(owner, repo)
        workflows = self.get_workflow_runs(owner, repo)
        contributors = self.get_contributors(owner, repo)
        releases = self.get_releases(owner, repo)
        
        return {
            "metadata": {
                "owner": owner,
                "repo": repo,
                "full_name": repo_info.full_name,
                "description": repo_info.description,
                "url": repo_info.url,
                "stars": repo_info.stars,
                "forks": repo_info.forks,
                "open_issues": repo_info.open_issues,
                "language": repo_info.language,
                "topics": repo_info.topics,
                "license": repo_info.license,
                "is_fork": repo_info.is_fork,
                "is_archived": repo_info.is_archived,
                "created_at": repo_info.created_at,
                "updated_at": repo_info.updated_at
            },
            "languages": languages,
            "readme": readme,
            "tree": [
                {"path": node.path, "type": node.type, "size": node.size}
                for node in tree
            ],
            "issues": issues,
            "pull_requests": pull_requests,
            "workflows": workflows,
            "contributors": contributors,
            "releases": releases,
            "scanned_at": datetime.utcnow().isoformat()
        }
    
    def list_user_repos(self, limit: int = 100) -> List[str]:
        """
        List repositories accessible to the authenticated user
        
        Args:
            limit: Maximum number of repos
            
        Returns:
            List of repository full names
        """
        response = self._request(
            "GET",
            "/user/repos",
            params={"per_page": limit, "sort": "updated"}
        )
        return [repo["full_name"] for repo in response.json()]
    
    def list_org_repos(self, org: str, limit: int = 100) -> List[str]:
        """
        List repositories in an organization
        
        Args:
            org: Organization name
            limit: Maximum number of repos
            
        Returns:
            List of repository full names
        """
        response = self._request(
            "GET",
            f"/orgs/{org}/repos",
            params={"per_page": limit}
        )
        return [repo["full_name"] for repo in response.json()]
