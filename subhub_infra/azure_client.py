"""
Azure Key Vault client for accessing secrets.

This module provides a direct extraction of the Azure Key Vault logic
from subhub-ai with the same interface and behavior.
"""

import platform
from typing import Optional
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.core.exceptions import ResourceNotFoundError, ClientAuthenticationError
from pydantic import SecretStr


class AzureKeyVaultClient:
    """
    Azure Key Vault client that matches the subhub-ai implementation exactly.
    
    Handles authentication and secret retrieval from Azure Key Vault
    using the same logic as the original subhub-ai implementation.
    """
    
    def __init__(self, vault_url: str = "https://walt-key-vault.vault.azure.net/"):
        """
        Initialize the Azure Key Vault client.
        
        Args:
            vault_url: The URL of the Azure Key Vault (default matches subhub-ai)
        """
        self.vault_url = vault_url
        self._client: Optional[SecretClient] = None
    
    def _get_credential(self):
        """
        Get Azure credential based on the system platform.
        Uses the exact same logic as subhub-ai main.py.
        """
        system = platform.system()
        
        if system == "Windows":
            try:
                credential = DefaultAzureCredential()
                # Test the credential to make sure it works
                credential.get_token("https://management.azure.com/.default")
                return credential
            except ClientAuthenticationError:
                print("DefaultAzureCredential failed")
                raise
        else:
            try:
                return InteractiveBrowserCredential()
            except ClientAuthenticationError:
                print("InteractiveBrowserCredential failed")
                raise
    
    def get_client(self) -> SecretClient:
        """
        Get or create the SecretClient instance.
        
        Returns:
            SecretClient: The Azure Key Vault secret client
        """
        if self._client is None:
            credential = self._get_credential()
            self._client = SecretClient(vault_url=self.vault_url, credential=credential)
        
        return self._client
    
    async def get_secret(self, name: str):
        """
        Get a secret from Azure Key Vault.
        
        This method replicates the exact behavior of the get_secret function
        from subhub-ai/helpers/get_secret.py.
        
        Args:
            name: The name of the secret to retrieve
            
        Returns:
            The secret value, with special handling for azure-openai-api-key
            
        Raises:
            ValueError: If the secret is not found or is None
        """
        try:
            client = self.get_client()
            secret = client.get_secret(name).value
            
            if secret is None:
                raise ValueError(f"Secret '{name}' not found in Key Vault.")
            
            # Special handling for OpenAI API key (matches subhub-ai behavior)
            if name == "azure-openai-api-key":
                secret = SecretStr(secret)
            
            return secret
        
        except ResourceNotFoundError:
            raise ValueError(f"Secret '{name}' not found in Key Vault.")


def create_key_vault_client(vault_url: str = "https://walt-key-vault.vault.azure.net/") -> AzureKeyVaultClient:
    """
    Factory function to create an Azure Key Vault client.
    
    Args:
        vault_url: The URL of the Azure Key Vault
        
    Returns:
        AzureKeyVaultClient: Configured client instance
    """
    return AzureKeyVaultClient(vault_url=vault_url)