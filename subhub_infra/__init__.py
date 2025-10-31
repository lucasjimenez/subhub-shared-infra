"""
SubHub Infrastructure Shared Package

Provides shared infrastructure clients for Azure, Snowflake, and Looker
to be used across SubHub AI projects.
"""

from .main import (
    get_infrastructure_client,
    get_azure_client,
    get_snowflake_client,
    get_looker_client
)
from .azure_client import AzureKeyVaultClient
from .snowflake_client import SnowflakeClient
from .looker_client import LookerAPIClient

__version__ = "0.1.0"
__all__ = [
    "get_infrastructure_client",
    "get_azure_client",
    "get_snowflake_client", 
    "get_looker_client",
    "AzureKeyVaultClient", 
    "SnowflakeClient",
    "LookerAPIClient"
]