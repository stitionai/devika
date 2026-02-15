"""
Coolify Integration Module
Handles deployment operations via Coolify API
"""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ApplicationInfo:
    """Coolify application info"""
    id: str
    uuid: str
    name: str
    fqdn: str
    status: str
    created_at: str
    updated_at: str


@dataclass
class DeploymentInfo:
    """Deployment status info"""
    id: str
    uuid: str
    status: str
    created_at: str
    updated_at: str
    application_name: str


class CoolifyIntegration:
    """
    Coolify API integration for deployment management
    
    Provides methods for:
    - Application management
    - Deployment triggering and monitoring
    - Server and project listing
    - Webhook-based deployments
    """
    
    def __init__(self, base_url: str, api_token: str):
        """
        Initialize Coolify integration
        
        Args:
            base_url: Coolify instance URL (e.g., https://coolify.example.com)
            api_token: Coolify API token
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request to Coolify API"""
        url = f"{self.base_url}/api/v1{endpoint}"
        response = requests.request(
            method,
            url,
            headers=self.headers,
            **kwargs
        )
        response.raise_for_status()
        return response
    
    def get_applications(self) -> List[ApplicationInfo]:
        """
        Get all applications
        
        Returns:
            List of ApplicationInfo objects
        """
        response = self._request("GET", "/applications")
        applications = response.json()
        
        return [
            ApplicationInfo(
                id=app.get('id', ''),
                uuid=app.get('uuid', ''),
                name=app.get('name', ''),
                fqdn=app.get('fqdn', ''),
                status=app.get('status', 'unknown'),
                created_at=app.get('created_at', ''),
                updated_at=app.get('updated_at', '')
            )
            for app in applications
        ]
    
    def get_application(self, app_uuid: str) -> ApplicationInfo:
        """
        Get application by UUID
        
        Args:
            app_uuid: Application UUID
            
        Returns:
            ApplicationInfo object
        """
        response = self._request("GET", f"/applications/{app_uuid}")
        app = response.json()
        
        return ApplicationInfo(
            id=app.get('id', ''),
            uuid=app.get('uuid', ''),
            name=app.get('name', ''),
            fqdn=app.get('fqdn', ''),
            status=app.get('status', 'unknown'),
            created_at=app.get('created_at', ''),
            updated_at=app.get('updated_at', '')
        )
    
    def deploy_application(self, app_uuid: str) -> Dict[str, Any]:
        """
        Trigger application deployment
        
        Args:
            app_uuid: Application UUID
            
        Returns:
            Deployment response
        """
        response = self._request("GET", f"/deploy", params={"uuid": app_uuid})
        return response.json()
    
    def get_deployments(self, app_uuid: str, limit: int = 10) -> List[DeploymentInfo]:
        """
        Get deployments for an application
        
        Args:
            app_uuid: Application UUID
            limit: Maximum number of deployments
            
        Returns:
            List of DeploymentInfo objects
        """
        response = self._request(
            "GET",
            f"/applications/{app_uuid}/deployments",
            params={"limit": limit}
        )
        deployments = response.json()
        
        return [
            DeploymentInfo(
                id=dep.get('id', ''),
                uuid=dep.get('uuid', ''),
                status=dep.get('status', 'unknown'),
                created_at=dep.get('created_at', ''),
                updated_at=dep.get('updated_at', ''),
                application_name=dep.get('application_name', '')
            )
            for dep in deployments
        ]
    
    def get_deployment(self, deployment_uuid: str) -> DeploymentInfo:
        """
        Get deployment status
        
        Args:
            deployment_uuid: Deployment UUID
            
        Returns:
            DeploymentInfo object
        """
        response = self._request("GET", f"/deployments/{deployment_uuid}")
        dep = response.json()
        
        return DeploymentInfo(
            id=dep.get('id', ''),
            uuid=dep.get('uuid', ''),
            status=dep.get('status', 'unknown'),
            created_at=dep.get('created_at', ''),
            updated_at=dep.get('updated_at', ''),
            application_name=dep.get('application_name', '')
        )
    
    def get_servers(self) -> List[Dict]:
        """
        Get all servers
        
        Returns:
            List of server dictionaries
        """
        response = self._request("GET", "/servers")
        return response.json()
    
    def get_server(self, server_uuid: str) -> Dict:
        """
        Get server by UUID
        
        Args:
            server_uuid: Server UUID
            
        Returns:
            Server dictionary
        """
        response = self._request("GET", f"/servers/{server_uuid}")
        return response.json()
    
    def get_projects(self) -> List[Dict]:
        """
        Get all projects
        
        Returns:
            List of project dictionaries
        """
        response = self._request("GET", "/projects")
        return response.json()
    
    def get_project(self, project_uuid: str) -> Dict:
        """
        Get project by UUID
        
        Args:
            project_uuid: Project UUID
            
        Returns:
            Project dictionary
        """
        response = self._request("GET", f"/projects/{project_uuid}")
        return response.json()
    
    def trigger_webhook(self, webhook_url: str) -> Dict:
        """
        Trigger deployment via webhook
        
        Args:
            webhook_url: Full webhook URL
            
        Returns:
            Webhook response
        """
        response = requests.get(webhook_url)
        response.raise_for_status()
        return response.json()
    
    def get_resources(self) -> Dict[str, Any]:
        """
        Get all resources (applications, databases, services)
        
        Returns:
            Resources dictionary
        """
        response = self._request("GET", "/resources")
        return response.json()
    
    def health_check(self) -> bool:
        """
        Check Coolify instance health
        
        Returns:
            True if healthy
        """
        try:
            response = self._request("GET", "/health")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_version(self) -> str:
        """
        Get Coolify version
        
        Returns:
            Version string
        """
        response = self._request("GET", "/version")
        return response.json().get('version', 'unknown')
    
    def create_database(self, db_type: str, name: str, server_uuid: str) -> Dict:
        """
        Create a database
        
        Args:
            db_type: Database type (postgresql, mysql, redis, etc.)
            name: Database name
            server_uuid: Server UUID
            
        Returns:
            Created database info
        """
        # Note: This is a simplified version - actual API may differ
        response = self._request(
            "POST",
            f"/databases",
            json={
                "type": db_type,
                "name": name,
                "server_uuid": server_uuid
            }
        )
        return response.json()
    
    def get_logs(self, resource_uuid: str, limit: int = 100) -> List[str]:
        """
        Get logs for a resource
        
        Args:
            resource_uuid: Resource UUID
            limit: Number of log lines
            
        Returns:
            List of log lines
        """
        response = self._request(
            "GET",
            f"/resources/{resource_uuid}/logs",
            params={"limit": limit}
        )
        return response.json()