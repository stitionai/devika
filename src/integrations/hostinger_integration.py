"""
Hostinger Integration Module
Handles VPS and hosting operations via Hostinger API
"""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class VPSInfo:
    """VPS server info"""
    id: int
    name: str
    status: str
    ip: str
    cores: int
    memory: int
    disk: int
    bandwidth: int
    location: str
    created_at: str
    expires_at: str


@dataclass
class DomainInfo:
    """Domain info"""
    domain: str
    status: str
    expires_at: str
    nameservers: List[str]


class HostingerIntegration:
    """
    Hostinger API integration for VPS and hosting management
    
    Provides methods for:
    - VPS management
    - Domain management
    - DNS configuration
    - SSL certificates
    """
    
    BASE_URL = "https://developers.hostinger.com"
    
    def __init__(self, api_token: str):
        """
        Initialize Hostinger integration
        
        Args:
            api_token: Hostinger API token
        """
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request to Hostinger API"""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(
            method,
            url,
            headers=self.headers,
            **kwargs
        )
        response.raise_for_status()
        return response
    
    def get_vps_list(self) -> List[VPSInfo]:
        """
        Get all VPS servers
        
        Returns:
            List of VPSInfo objects
        """
        response = self._request("GET", "/api/v3/vps")
        vps_list = response.json()
        
        return [
            VPSInfo(
                id=vps.get('id', 0),
                name=vps.get('hostname', ''),
                status=vps.get('status', 'unknown'),
                ip=vps.get('ip', {}).get('address', '') if isinstance(vps.get('ip'), dict) else '',
                cores=vps.get('plan', {}).get('cores', 0),
                memory=vps.get('plan', {}).get('memory', 0),
                disk=vps.get('plan', {}).get('disk', 0),
                bandwidth=vps.get('plan', {}).get('bandwidth', 0),
                location=vps.get('location', {}).get('name', '') if isinstance(vps.get('location'), dict) else '',
                created_at=vps.get('created_at', ''),
                expires_at=vps.get('expires_at', '')
            )
            for vps in vps_list
        ]
    
    def get_vps(self, vps_id: int) -> VPSInfo:
        """
        Get VPS by ID
        
        Args:
            vps_id: VPS ID
            
        Returns:
            VPSInfo object
        """
        response = self._request("GET", f"/api/v3/vps/{vps_id}")
        vps = response.json()
        
        return VPSInfo(
            id=vps.get('id', 0),
            name=vps.get('hostname', ''),
            status=vps.get('status', 'unknown'),
            ip=vps.get('ip', {}).get('address', '') if isinstance(vps.get('ip'), dict) else '',
            cores=vps.get('plan', {}).get('cores', 0),
            memory=vps.get('plan', {}).get('memory', 0),
            disk=vps.get('plan', {}).get('disk', 0),
            bandwidth=vps.get('plan', {}).get('bandwidth', 0),
            location=vps.get('location', {}).get('name', '') if isinstance(vps.get('location'), dict) else '',
            created_at=vps.get('created_at', ''),
            expires_at=vps.get('expires_at', '')
        )
    
    def start_vps(self, vps_id: int) -> Dict:
        """
        Start VPS server
        
        Args:
            vps_id: VPS ID
            
        Returns:
            Response dictionary
        """
        response = self._request("POST", f"/api/v3/vps/{vps_id}/start")
        return response.json()
    
    def stop_vps(self, vps_id: int) -> Dict:
        """
        Stop VPS server
        
        Args:
            vps_id: VPS ID
            
        Returns:
            Response dictionary
        """
        response = self._request("POST", f"/api/v3/vps/{vps_id}/stop")
        return response.json()
    
    def restart_vps(self, vps_id: int) -> Dict:
        """
        Restart VPS server
        
        Args:
            vps_id: VPS ID
            
        Returns:
            Response dictionary
        """
        response = self._request("POST", f"/api/v3/vps/{vps_id}/restart")
        return response.json()
    
    def get_vps_metrics(self, vps_id: int) -> Dict:
        """
        Get VPS metrics (CPU, RAM, disk usage)
        
        Args:
            vps_id: VPS ID
            
        Returns:
            Metrics dictionary
        """
        response = self._request("GET", f"/api/v3/vps/{vps_id}/metrics")
        return response.json()
    
    def get_domains(self) -> List[DomainInfo]:
        """
        Get all domains
        
        Returns:
            List of DomainInfo objects
        """
        response = self._request("GET", "/api/v3/domains")
        domains = response.json()
        
        return [
            DomainInfo(
                domain=domain.get('domain', ''),
                status=domain.get('status', 'unknown'),
                expires_at=domain.get('expires_at', ''),
                nameservers=domain.get('nameservers', [])
            )
            for domain in domains
        ]
    
    def get_domain(self, domain_name: str) -> DomainInfo:
        """
        Get domain by name
        
        Args:
            domain_name: Domain name
            
        Returns:
            DomainInfo object
        """
        response = self._request("GET", f"/api/v3/domains/{domain_name}")
        domain = response.json()
        
        return DomainInfo(
            domain=domain.get('domain', ''),
            status=domain.get('status', 'unknown'),
            expires_at=domain.get('expires_at', ''),
            nameservers=domain.get('nameservers', [])
        )
    
    def get_dns_records(self, domain_name: str) -> List[Dict]:
        """
        Get DNS records for a domain
        
        Args:
            domain_name: Domain name
            
        Returns:
            List of DNS records
        """
        response = self._request("GET", f"/api/v3/domains/{domain_name}/dns")
        return response.json()
    
    def create_dns_record(
        self, 
        domain_name: str, 
        record_type: str, 
        name: str, 
        value: str,
        ttl: int = 3600
    ) -> Dict:
        """
        Create DNS record
        
        Args:
            domain_name: Domain name
            record_type: Record type (A, AAAA, CNAME, MX, TXT, etc.)
            name: Record name
            value: Record value
            ttl: Time to live
            
        Returns:
            Created record
        """
        response = self._request(
            "POST",
            f"/api/v3/domains/{domain_name}/dns",
            json={
                "type": record_type,
                "name": name,
                "value": value,
                "ttl": ttl
            }
        )
        return response.json()
    
    def delete_dns_record(self, domain_name: str, record_id: str) -> Dict:
        """
        Delete DNS record
        
        Args:
            domain_name: Domain name
            record_id: Record ID
            
        Returns:
            Response dictionary
        """
        response = self._request(
            "DELETE",
            f"/api/v3/domains/{domain_name}/dns/{record_id}"
        )
        return response.json()
    
    def get_web_servers(self, vps_id: int) -> List[Dict]:
        """
        Get web servers installed on VPS
        
        Args:
            vps_id: VPS ID
            
        Returns:
            List of web servers
        """
        response = self._request("GET", f"/api/v3/vps/{vps_id}/web-servers")
        return response.json()
    
    def get_databases(self, vps_id: int) -> List[Dict]:
        """
        Get databases on VPS
        
        Args:
            vps_id: VPS ID
            
        Returns:
            List of databases
        """
        response = self._request("GET", f"/api/v3/vps/{vps_id}/databases")
        return response.json()
    
    def install_panel(self, vps_id: int, panel_type: str = "coolify") -> Dict:
        """
        Install control panel on VPS
        
        Args:
            vps_id: VPS ID
            panel_type: Panel type (coolify, plesk, cpanel, etc.)
            
        Returns:
            Installation response
        """
        response = self._request(
            "POST",
            f"/api/v3/vps/{vps_id}/install-panel",
            json={"panel": panel_type}
        )
        return response.json()
    
    def health_check(self) -> bool:
        """
        Check API connectivity
        
        Returns:
            True if API is accessible
        """
        try:
            response = self._request("GET", "/api/v3/domains")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False