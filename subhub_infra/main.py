"""
Main interface for SubHub Infrastructure Shared Package.

This module provides a simple interface that replicates the functionality
of subhub-ai's settings while using the shared infrastructure clients.
"""

from typing import Optional
from .azure_client import AzureKeyVaultClient, create_key_vault_client
from .snowflake_client import SnowflakeClient, create_snowflake_client
from .looker_client import LookerAPIClient, create_looker_client


class InfrastructureClient:
    """
    Main infrastructure client that provides access to all shared services.
    
    This class provides the same interface as subhub-ai's settings but using
    the shared infrastructure clients.
    """
    
    def __init__(self, vault_url: str = "https://walt-key-vault.vault.azure.net/"):
        """
        Initialize the infrastructure client.
        
        Args:
            vault_url: The URL of the Azure Key Vault (default matches subhub-ai)
        """
        self.vault_url = vault_url
        self._azure_client: Optional[AzureKeyVaultClient] = None
        self._snowflake_client: Optional[SnowflakeClient] = None
        self._looker_client: Optional[LookerAPIClient] = None
    
    @property
    def azure(self) -> AzureKeyVaultClient:
        """Get the Azure Key Vault client."""
        if self._azure_client is None:
            self._azure_client = create_key_vault_client(self.vault_url)
        return self._azure_client
    
    @property
    def snowflake(self) -> SnowflakeClient:
        """Get the Snowflake client."""
        if self._snowflake_client is None:
            self._snowflake_client = create_snowflake_client(self.azure)
        return self._snowflake_client
    
    @property
    def looker(self) -> LookerAPIClient:
        """Get the Looker API client."""
        if self._looker_client is None:
            self._looker_client = create_looker_client(self.azure)
        return self._looker_client
    
    async def initialize(self):
        """
        Initialize all clients (optional).
        
        This method can be called to pre-initialize all clients,
        but it's not required as clients are lazy-loaded.
        """
        # Pre-load Azure credentials
        _ = self.azure.get_client()
        
        # Pre-authenticate with Looker
        await self.looker.authenticate()
        
        # Pre-establish Snowflake connection
        await self.snowflake.get_connection()
    
    async def cleanup(self):
        """
        Clean up all client connections.
        
        This method should be called when shutting down to properly
        close all connections.
        """
        if self._snowflake_client:
            self._snowflake_client.close()


# Global instance cache (matches subhub-ai pattern)
_infrastructure_client_cache: Optional[InfrastructureClient] = None


async def get_infrastructure_client(vault_url: str = "https://walt-key-vault.vault.azure.net/") -> InfrastructureClient:
    """
    Get or create the global infrastructure client instance.
    
    This function provides the same pattern as subhub-ai's get_settings() function.
    
    Args:
        vault_url: The URL of the Azure Key Vault
        
    Returns:
        InfrastructureClient: The global client instance
    """
    global _infrastructure_client_cache
    
    if _infrastructure_client_cache is None:
        _infrastructure_client_cache = InfrastructureClient(vault_url)
        await _infrastructure_client_cache.initialize()
    
    return _infrastructure_client_cache


async def cleanup_infrastructure_client():
    """
    Clean up the global infrastructure client.
    
    This function provides the same pattern as subhub-ai's cleanup_settings() function.
    """
    global _infrastructure_client_cache
    
    if _infrastructure_client_cache is not None:
        await _infrastructure_client_cache.cleanup()
        _infrastructure_client_cache = None


# Convenience functions for direct access (matches subhub-ai patterns)
async def get_azure_client(vault_url: str = "https://walt-key-vault.vault.azure.net/") -> AzureKeyVaultClient:
    """Get the Azure Key Vault client directly."""
    client = await get_infrastructure_client(vault_url)
    return client.azure


async def get_snowflake_client(vault_url: str = "https://walt-key-vault.vault.azure.net/") -> SnowflakeClient:
    """Get the Snowflake client directly."""
    client = await get_infrastructure_client(vault_url)
    return client.snowflake


async def get_looker_client(vault_url: str = "https://walt-key-vault.vault.azure.net/") -> LookerAPIClient:
    """Get the Looker API client directly."""
    client = await get_infrastructure_client(vault_url)
    return client.looker