"""
Cloudflare Integration Module
Handles DNS and CDN operations via Cloudflare API
"""
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass


@dataclass
class ZoneInfo:
    """Cloudflare zone info"""
    id: str
    name: str
    status: str
    nameservers: List[str]
    created_on: str
    modified_on: str


@dataclass
class DNSRecord:
    """DNS record info"""
    id: str
    type: str
    name: str
    content: str
    ttl: int
    proxied: bool


class CloudflareIntegration:
    """
    Cloudflare API integration for DNS and CDN management
    
    Provides methods for:
    - Zone management
    - DNS record management
    - SSL/TLS configuration
    - Cache management
    """
    
    BASE_URL = "https://api.cloudflare.com/client/v4"
    
    def __init__(self, api_token: str):
        """
        Initialize Cloudflare integration
        
        Args:
            api_token: Cloudflare API token with Zone:Edit permissions
        """
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated request to Cloudflare API"""
        url = f"{self.BASE_URL}{endpoint}"
        response = requests.request(
            method,
            url,
            headers=self.headers,
            **kwargs
        )
        response.raise_for_status()
        return response
    
    def _get_result(self, response: requests.Response) -> Any:
        """Extract result from Cloudflare response"""
        data = response.json()
        if not data.get('success', False):
            errors = data.get('errors', [])
            raise Exception(f"Cloudflare API error: {errors}")
        return data.get('result')
    
    def get_zones(self) -> List[ZoneInfo]:
        """
        Get all zones
        
        Returns:
            List of ZoneInfo objects
        """
        response = self._request("GET", "/zones")
        zones = self._get_result(response)
        
        return [
            ZoneInfo(
                id=zone.get('id', ''),
                name=zone.get('name', ''),
                status=zone.get('status', 'unknown'),
                nameservers=zone.get('name_servers', []),
                created_on=zone.get('created_on', ''),
                modified_on=zone.get('modified_on', '')
            )
            for zone in zones
        ]
    
    def get_zone(self, zone_id: str) -> ZoneInfo:
        """
        Get zone by ID
        
        Args:
            zone_id: Zone ID
            
        Returns:
            ZoneInfo object
        """
        response = self._request("GET", f"/zones/{zone_id}")
        zone = self._get_result(response)
        
        return ZoneInfo(
            id=zone.get('id', ''),
            name=zone.get('name', ''),
            status=zone.get('status', 'unknown'),
            nameservers=zone.get('name_servers', []),
            created_on=zone.get('created_on', ''),
            modified_on=zone.get('modified_on', '')
        )
    
    def get_zone_by_name(self, zone_name: str) -> Optional[ZoneInfo]:
        """
        Get zone by name
        
        Args:
            zone_name: Zone name (domain)
            
        Returns:
            ZoneInfo object or None
        """
        response = self._request("GET", "/zones", params={"name": zone_name})
        zones = self._get_result(response)
        
        if zones:
            zone = zones[0]
            return ZoneInfo(
                id=zone.get('id', ''),
                name=zone.get('name', ''),
                status=zone.get('status', 'unknown'),
                nameservers=zone.get('name_servers', []),
                created_on=zone.get('created_on', ''),
                modified_on=zone.get('modified_on', '')
            )
        return None
    
    def get_dns_records(self, zone_id: str, record_type: Optional[str] = None) -> List[DNSRecord]:
        """
        Get DNS records for a zone
        
        Args:
            zone_id: Zone ID
            record_type: Optional filter by record type
            
        Returns:
            List of DNSRecord objects
        """
        params = {}
        if record_type:
            params["type"] = record_type
            
        response = self._request("GET", f"/zones/{zone_id}/dns_records", params=params)
        records = self._get_result(response)
        
        return [
            DNSRecord(
                id=record.get('id', ''),
                type=record.get('type', ''),
                name=record.get('name', ''),
                content=record.get('content', ''),
                ttl=record.get('ttl', 3600),
                proxied=record.get('proxied', False)
            )
            for record in records
        ]
    
    def create_dns_record(
        self,
        zone_id: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 3600,
        proxied: bool = False
    ) -> DNSRecord:
        """
        Create DNS record
        
        Args:
            zone_id: Zone ID
            record_type: Record type (A, AAAA, CNAME, MX, TXT, etc.)
            name: Record name
            content: Record value
            ttl: Time to live
            proxied: Whether to proxy through Cloudflare
            
        Returns:
            Created DNSRecord
        """
        response = self._request(
            "POST",
            f"/zones/{zone_id}/dns_records",
            json={
                "type": record_type,
                "name": name,
                "content": content,
                "ttl": ttl,
                "proxied": proxied
            }
        )
        record = self._get_result(response)
        
        return DNSRecord(
            id=record.get('id', ''),
            type=record.get('type', ''),
            name=record.get('name', ''),
            content=record.get('content', ''),
            ttl=record.get('ttl', 3600),
            proxied=record.get('proxied', False)
        )
    
    def update_dns_record(
        self,
        zone_id: str,
        record_id: str,
        record_type: str,
        name: str,
        content: str,
        ttl: int = 3600,
        proxied: bool = False
    ) -> DNSRecord:
        """
        Update DNS record
        
        Args:
            zone_id: Zone ID
            record_id: Record ID
            record_type: Record type
            name: Record name
            content: Record value
            ttl: Time to live
            proxied: Whether to proxy
            
        Returns:
            Updated DNSRecord
        """
        response = self._request(
            "PUT",
            f"/zones/{zone_id}/dns_records/{record_id}",
            json={
                "type": record_type,
                "name": name,
                "content": content,
                "ttl": ttl,
                "proxied": proxied
            }
        )
        record = self._get_result(response)
        
        return DNSRecord(
            id=record.get('id', ''),
            type=record.get('type', ''),
            name=record.get('name', ''),
            content=record.get('content', ''),
            ttl=record.get('ttl', 3600),
            proxied=record.get('proxied', False)
        )
    
    def delete_dns_record(self, zone_id: str, record_id: str) -> bool:
        """
        Delete DNS record
        
        Args:
            zone_id: Zone ID
            record_id: Record ID
            
        Returns:
            True if deleted
        """
        response = self._request(
            "DELETE",
            f"/zones/{zone_id}/dns_records/{record_id}"
        )
        return self._get_result(response).get('id') == record_id
    
    def set_ssl_mode(self, zone_id: str, mode: str = "full") -> Dict:
        """
        Set SSL/TLS mode for zone
        
        Args:
            zone_id: Zone ID
            mode: SSL mode (off, flexible, full, full_strict)
            
        Returns:
            Response dictionary
        """
        response = self._request(
            "PATCH",
            f"/zones/{zone_id}/settings/ssl",
            json={"value": mode}
        )
        return self._get_result(response)
    
    def get_ssl_mode(self, zone_id: str) -> str:
        """
        Get SSL/TLS mode for zone
        
        Args:
            zone_id: Zone ID
            
        Returns:
            SSL mode string
        """
        response = self._request("GET", f"/zones/{zone_id}/settings/ssl")
        result = self._get_result(response)
        return result.get('value', 'unknown')
    
    def purge_cache(self, zone_id: str, files: Optional[List[str]] = None) -> Dict:
        """
        Purge cache for zone
        
        Args:
            zone_id: Zone ID
            files: Optional list of specific files to purge (purges all if not provided)
            
        Returns:
            Response dictionary
        """
        if files:
            response = self._request(
                "POST",
                f"/zones/{zone_id}/purge_cache",
                json={"files": files}
            )
        else:
            response = self._request(
                "POST",
                f"/zones/{zone_id}/purge_cache",
                json={"purge_everything": True}
            )
        return self._get_result(response)
    
    def get_analytics(self, zone_id: str, since: str = "-24h") -> Dict:
        """
        Get zone analytics
        
        Args:
            zone_id: Zone ID
            since: Time range (e.g., -24h, -7d, -30d)
            
        Returns:
            Analytics dictionary
        """
        response = self._request(
            "GET",
            f"/zones/{zone_id}/analytics/dashboard",
            params={"since": since}
        )
        return self._get_result(response)
    
    def create_page_rule(
        self,
        zone_id: str,
        pattern: str,
        actions: List[Dict]
    ) -> Dict:
        """
        Create page rule
        
        Args:
            zone_id: Zone ID
            pattern: URL pattern for the rule
            actions: List of actions (e.g., {"id": "ssl", "value": "flexible"})
            
        Returns:
            Created page rule
        """
        response = self._request(
            "POST",
            f"/zones/{zone_id}/pagerules",
            json={
                "targets": [{"target": "url", "constraint": {"operator": "matches", "value": pattern}}],
                "actions": actions
            }
        )
        return self._get_result(response)
    
    def verify_token(self) -> bool:
        """
        Verify API token is valid
        
        Returns:
            True if token is valid
        """
        try:
            response = self._request("GET", "/user/tokens/verify")
            return response.json().get('success', False)
        except requests.exceptions.RequestException:
            return False
    
    def health_check(self) -> bool:
        """
        Check API connectivity
        
        Returns:
            True if API is accessible
        """
        return self.verify_token()