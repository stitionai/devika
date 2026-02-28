import os
import subprocess
from typing import List, Dict, Optional
from src.config import Config
from src.logger import Logger

class GitIntegration:
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.repos_dir = self.config.get_repos_dir()

    def clone_repository(self, repo_url: str, project_name: str) -> Dict[str, str]:
        """Clone a Git repository to the project directory"""
        try:
            project_path = os.path.join(self.config.get_projects_dir(), project_name.lower().replace(" ", "-"))
            
            # Create project directory if it doesn't exist
            os.makedirs(project_path, exist_ok=True)
            
            # Clone the repository
            result = subprocess.run(
                ["git", "clone", repo_url, project_path],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                self.logger.info(f"Successfully cloned repository {repo_url} to {project_path}")
                return {
                    "status": "success",
                    "message": f"Repository cloned successfully to {project_path}",
                    "path": project_path
                }
            else:
                self.logger.error(f"Failed to clone repository: {result.stderr}")
                return {
                    "status": "error",
                    "message": f"Failed to clone repository: {result.stderr}"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "error",
                "message": "Repository cloning timed out"
            }
        except Exception as e:
            self.logger.error(f"Error cloning repository: {str(e)}")
            return {
                "status": "error",
                "message": f"Error cloning repository: {str(e)}"
            }

    def get_repository_info(self, project_path: str) -> Dict[str, str]:
        """Get information about a Git repository"""
        try:
            # Check if it's a git repository
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {"status": "error", "message": "Not a Git repository"}
            
            # Get repository information
            info = {}
            
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            if branch_result.returncode == 0:
                info["current_branch"] = branch_result.stdout.strip()
            
            # Get remote URL
            remote_result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            if remote_result.returncode == 0:
                info["remote_url"] = remote_result.stdout.strip()
            
            # Get last commit
            commit_result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%H %s %an %ad", "--date=short"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            if commit_result.returncode == 0:
                info["last_commit"] = commit_result.stdout.strip()
            
            # Get repository status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            if status_result.returncode == 0:
                info["has_changes"] = bool(status_result.stdout.strip())
                info["status"] = "clean" if not info["has_changes"] else "modified"
            
            return {"status": "success", "info": info}
            
        except Exception as e:
            self.logger.error(f"Error getting repository info: {str(e)}")
            return {"status": "error", "message": str(e)}

    def create_commit(self, project_path: str, message: str, files: Optional[List[str]] = None) -> Dict[str, str]:
        """Create a Git commit"""
        try:
            # Add files
            if files:
                for file in files:
                    subprocess.run(
                        ["git", "add", file],
                        cwd=project_path,
                        check=True
                    )
            else:
                subprocess.run(
                    ["git", "add", "."],
                    cwd=project_path,
                    check=True
                )
            
            # Create commit
            result = subprocess.run(
                ["git", "commit", "-m", message],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "message": "Commit created successfully",
                    "commit_hash": result.stdout.strip()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to create commit: {result.stderr}"
                }
                
        except Exception as e:
            self.logger.error(f"Error creating commit: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_commit_history(self, project_path: str, limit: int = 10) -> Dict[str, any]:
        """Get commit history"""
        try:
            result = subprocess.run(
                ["git", "log", f"--max-count={limit}", "--pretty=format:%H|%s|%an|%ad|%ar", "--date=short"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                commits = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split('|')
                        if len(parts) >= 5:
                            commits.append({
                                "hash": parts[0],
                                "message": parts[1],
                                "author": parts[2],
                                "date": parts[3],
                                "relative_date": parts[4]
                            })
                
                return {"status": "success", "commits": commits}
            else:
                return {"status": "error", "message": result.stderr}
                
        except Exception as e:
            self.logger.error(f"Error getting commit history: {str(e)}")
            return {"status": "error", "message": str(e)}