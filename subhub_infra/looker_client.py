"""
Looker API client with Azure Key Vault integration.

This module provides a direct extraction of the Looker API logic
from subhub-ai with the same interface and behavior.
"""

import json
from typing import Optional, Dict, Any
import httpx
from .azure_client import AzureKeyVaultClient


class LookerAPIClient:
    """
    Looker API client that matches the subhub-ai implementation exactly.
    
    Handles Looker API authentication and query execution using credentials 
    from Azure Key Vault with the same logic as the original subhub-ai implementation.
    """
    
    def __init__(self, azure_client: AzureKeyVaultClient):
        """
        Initialize the Looker API client.
        
        Args:
            azure_client: The Azure Key Vault client for retrieving secrets
        """
        self.azure_client = azure_client
        self._access_token: Optional[str] = None
        self._base_url: Optional[str] = None
        self._client_id: Optional[str] = None
        self._client_secret: Optional[str] = None
    
    async def _load_credentials(self):
        """Load Looker credentials from Azure Key Vault."""
        if self._base_url is None:
            self._base_url = await self.azure_client.get_secret("looker-api-base-url")
            self._client_id = await self.azure_client.get_secret("looker-service-account-client-id")
            self._client_secret = await self.azure_client.get_secret("looker-service-account-client-secret")
    
    async def authenticate(self) -> str:
        """
        Authenticate with Looker API and get access token.
        
        This method replicates the exact authentication logic from 
        subhub-ai/helpers/settings.py lines 115-132.
        
        Returns:
            str: The access token
        """
        await self._load_credentials()
        
        looker_login_url = f"{self._base_url}/api/4.0/login"
        payload = {
            'client_id': self._client_id,
            'client_secret': self._client_secret
        }
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        async with httpx.AsyncClient() as client:
            looker_login_raw_response = await client.post(
                looker_login_url,
                headers=headers,
                data=payload,
                timeout=300
            )
            
            if looker_login_raw_response.status_code != 200:
                raise Exception(f"Looker authentication failed: {looker_login_raw_response.text}")
            
            looker_login_json = looker_login_raw_response.json()
            self._access_token = looker_login_json['access_token']
        
        return self._access_token
    
    async def execute_query(self, query_json: Dict[str, Any]) -> str:
        """
        Execute a Looker query using JSON format.
        
        This method replicates the exact query execution logic from 
        subhub-ai/helpers/analytic_utils/sql_operations.py execute_sql_query_via_looker function.
        
        Args:
            query_json: The Looker query in JSON format
            
        Returns:
            str: JSON string containing query results
        """
        await self._load_credentials()
        
        # Ensure we have an access token
        if not self._access_token:
            await self.authenticate()
        
        # CONNECT TO THE LOOKER API (matches subhub-ai exactly)
        looker_base_url = f"{self._base_url}/api/4.0/queries/run/json"
        looker_base_headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self._access_token}'
        }
        
        async with httpx.AsyncClient() as client:
            looker_api_raw_response = await client.post(
                looker_base_url,
                headers=looker_base_headers,
                json=query_json,
                timeout=300
            )
            
            looker_api_response = looker_api_raw_response.json()
        
        # Handle authentication expiration (matches subhub-ai exactly)
        if looker_api_raw_response.status_code == 401:
            print("Looker API Authentication expired. Reauthorizing...")
            
            # Re-authenticate and retry
            await self.authenticate()
            
            looker_retry_headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self._access_token}'
            }
            
            async with httpx.AsyncClient() as client:
                looker_api_raw_response = await client.post(
                    looker_base_url,
                    headers=looker_retry_headers,
                    json=query_json,
                    timeout=300
                )
                
                looker_api_response = looker_api_raw_response.json()
        
        # Check for API errors
        if looker_api_raw_response.status_code != 200:
            raise Exception(f"Looker query execution failed: {looker_api_response}")
        
        return json.dumps(looker_api_response, indent=2)
    
    async def execute_sql_via_looker(self, sql_query: str, model: str = "subscriber_analytics", 
                                   view: str = "service_subscriber_metric_agg_subhub") -> str:
        """
        Execute a SQL query via Looker (placeholder for future SQL translation).
        
        For the MVP, this is a simplified interface. The full SQL-to-Looker translation
        logic from turn_sf_sql_into_looker_sql would be implemented here in the future.
        
        Args:
            sql_query: The SQL query to execute
            model: The Looker model name (default matches subhub-ai)
            view: The Looker view name (default matches subhub-ai)
            
        Returns:
            str: JSON string containing query results
        """
        # For MVP, this is a placeholder that would need the SQL translation logic
        # from subhub-ai's turn_sf_sql_into_looker_sql function
        raise NotImplementedError(
            "SQL-to-Looker translation not implemented in MVP. "
            "Use execute_query() with pre-built JSON queries instead."
        )
    
    @property
    def access_token(self) -> Optional[str]:
        """Get the current access token."""
        return self._access_token
    
    @property
    def base_url(self) -> Optional[str]:
        """Get the base URL."""
        return self._base_url


def create_looker_client(azure_client: AzureKeyVaultClient) -> LookerAPIClient:
    """
    Factory function to create a Looker API client.
    
    Args:
        azure_client: The Azure Key Vault client for retrieving secrets
        
    Returns:
        LookerAPIClient: Configured client instance
    """
    return LookerAPIClient(azure_client)