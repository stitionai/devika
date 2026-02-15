#!/usr/bin/env python3
"""
Repository Scanner Cron Job for Bambu Agent System
Scans all repositories for updates and security issues
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, List
import subprocess


class RepoScanner:
    """Scan all repositories for updates"""
    
    def __init__(self):
        self.github_token = os.getenv("GH_PAT")
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.log_file = "logs/repo_scans.jsonl"
        
    def get_all_repos(self, username: str = "executiveusa") -> List[Dict]:
        """Get all repositories for a user"""
        repos = []
        page = 1
        
        while True:
            response = requests.get(
                f"https://api.github.com/users/{username}/repos",
                headers=self.headers,
                params={"page": page, "per_page": 100}
            )
            
            if response.status_code != 200:
                break
                
            page_repos = response.json()
            if not page_repos:
                break
                
            repos.extend(page_repos)
            page += 1
            
        return repos
    
    def get_org_repos(self, org: str = "THE-PAULI-EFFECT") -> List[Dict]:
        """Get all repositories for an organization"""
        repos = []
        page = 1
        
        while True:
            response = requests.get(
                f"https://api.github.com/orgs/{org}/repos",
                headers=self.headers,
                params={"page": page, "per_page": 100}
            )
            
            if response.status_code != 200:
                break
                
            page_repos = response.json()
            if not page_repos:
                break
                
            repos.extend(page_repos)
            page += 1
            
        return repos
    
    def check_repo_updates(self, repo_name: str) -> Dict[str, Any]:
        """Check for recent updates in a repository"""
        response = requests.get(
            f"https://api.github.com/repos/{repo_name}/commits",
            headers=self.headers,
            params={"per_page": 5}
        )
        
        if response.status_code == 200:
            commits = response.json()
            return {
                "repo": repo_name,
                "latest_commits": [
                    {
                        "sha": c["sha"][:7],
                        "message": c["commit"]["message"],
                        "date": c["commit"]["author"]["date"],
                        "author": c["commit"]["author"]["name"]
                    }
                    for c in commits
                ]
            }
        return {"repo": repo_name, "error": response.status_code}
    
    def check_security_issues(self, repo_name: str) -> Dict[str, Any]:
        """Check for security vulnerabilities"""
        response = requests.get(
            f"https://api.github.com/repos/{repo_name}/vulnerability-alerts",
            headers={**self.headers, "Accept": "application/vnd.github.dorian-preview+json"}
        )
        
        return {
            "repo": repo_name,
            "vulnerability_alerts_enabled": response.status_code == 204
        }
    
    def scan_local_repos(self, repos_dir: str = "repos") -> List[Dict]:
        """Scan locally cloned repositories for changes"""
        results = []
        
        if not os.path.exists(repos_dir):
            return results
            
        for repo_name in os.listdir(repos_dir):
            repo_path = os.path.join(repos_dir, repo_name)
            if os.path.isdir(repo_path) and os.path.isdir(os.path.join(repo_path, ".git")):
                try:
                    # Check git status
                    result = subprocess.run(
                        ["git", "status", "--porcelain"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    # Get last commit
                    last_commit = subprocess.run(
                        ["git", "log", "-1", "--format=%H %s %ci"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    results.append({
                        "repo": repo_name,
                        "path": repo_path,
                        "has_changes": bool(result.stdout.strip()),
                        "last_commit": last_commit.stdout.strip()
                    })
                except Exception as e:
                    results.append({
                        "repo": repo_name,
                        "error": str(e)
                    })
                    
        return results
    
    def log_scan(self, results: Dict[str, Any]):
        """Log scan results"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "scan_type": "repo_scanner",
            "results": results
        }
        
        with open(self.log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def run_full_scan(self) -> Dict[str, Any]:
        """Run a full scan of all repositories"""
        results = {
            "user_repos": [],
            "org_repos": [],
            "local_repos": [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Scan user repos
        print("Scanning user repositories...")
        user_repos = self.get_all_repos("executiveusa")
        results["user_repos_count"] = len(user_repos)
        
        # Scan org repos
        print("Scanning organization repositories...")
        org_repos = self.get_org_repos("THE-PAULI-EFFECT")
        results["org_repos_count"] = len(org_repos)
        
        # Scan local repos
        print("Scanning local repositories...")
        results["local_repos"] = self.scan_local_repos()
        
        # Log results
        self.log_scan(results)
        
        return results


def main():
    """Main entry point for cron job"""
    scanner = RepoScanner()
    results = scanner.run_full_scan()
    
    print(f"Scan complete:")
    print(f"  User repos: {results.get('user_repos_count', 0)}")
    print(f"  Org repos: {results.get('org_repos_count', 0)}")
    print(f"  Local repos: {len(results.get('local_repos', []))}")
    
    return results


if __name__ == "__main__":
    main()
