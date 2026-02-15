"""
Vercel CLI Integration for Bambu Agent System
Enables immediate updates and deployments
"""

import os
import subprocess
import json
from typing import Optional, Dict, Any


class VercelIntegration:
    """Vercel CLI integration for automated deployments"""
    
    def __init__(self):
        self.token = os.getenv("VERCEL_TOKEN")
        self.project_id = os.getenv("VERCEL_PROJECT_ID")
        self.project_name = os.getenv("VERCEL_PROJECT_NAME")
        
    def is_authenticated(self) -> bool:
        """Check if Vercel CLI is authenticated"""
        try:
            result = subprocess.run(
                ["vercel", "whoami"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def login_with_token(self) -> bool:
        """Login using environment token"""
        if not self.token:
            return False
        try:
            # Set token as environment variable for Vercel CLI
            os.environ["VERCEL_ORG_ID"] = ""
            return True
        except Exception as e:
            print(f"Vercel login error: {e}")
            return False
    
    def deploy(self, path: str = ".", prod: bool = False) -> Dict[str, Any]:
        """Deploy to Vercel"""
        cmd = ["vercel", "--yes"]
        if prod:
            cmd.append("--prod")
        
        try:
            result = subprocess.run(
                cmd,
                cwd=path,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # Extract deployment URL from output
                lines = result.stdout.strip().split("\n")
                url = lines[-1] if lines else None
                return {
                    "success": True,
                    "url": url,
                    "output": result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_deployments(self) -> Dict[str, Any]:
        """List recent deployments"""
        try:
            result = subprocess.run(
                ["vercel", "list", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "deployments": json.loads(result.stdout)
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_deployment_logs(self, deployment_id: str) -> Dict[str, Any]:
        """Get logs for a specific deployment"""
        try:
            result = subprocess.run(
                ["vercel", "logs", deployment_id],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": result.returncode == 0,
                "logs": result.stdout if result.returncode == 0 else result.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def set_env_var(self, key: str, value: str, env: str = "production") -> bool:
        """Set environment variable in Vercel project"""
        try:
            result = subprocess.run(
                ["vercel", "env", "add", key, env],
                input=value,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def link_project(self, project_name: Optional[str] = None) -> bool:
        """Link current directory to Vercel project"""
        name = project_name or self.project_name
        if not name:
            return False
            
        try:
            result = subprocess.run(
                ["vercel", "link", "--yes", "--project", name],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False


# CLI commands
def deploy_now(path: str = ".", prod: bool = False):
    """Immediate deployment to Vercel"""
    vercel = VercelIntegration()
    return vercel.deploy(path, prod)


def get_status():
    """Get Vercel deployment status"""
    vercel = VercelIntegration()
    return vercel.list_deployments()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python vercel.py [deploy|status|logs]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "deploy":
        prod = "--prod" in sys.argv
        result = deploy_now(prod=prod)
        print(json.dumps(result, indent=2))
    elif command == "status":
        result = get_status()
        print(json.dumps(result, indent=2))
    else:
        print(f"Unknown command: {command}")
