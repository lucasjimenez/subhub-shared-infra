"""
Snowflake database client with Azure Key Vault integration.

This module provides a direct extraction of the Snowflake connection logic
from subhub-ai with the same interface and behavior.
"""

from typing import Optional, Any
import snowflake.connector
from .azure_client import AzureKeyVaultClient


class SnowflakeClient:
    """
    Snowflake database client that matches the subhub-ai implementation exactly.
    
    Handles Snowflake database connections using credentials from Azure Key Vault
    with the same logic as the original subhub-ai implementation.
    """
    
    def __init__(self, azure_client: AzureKeyVaultClient):
        """
        Initialize the Snowflake client.
        
        Args:
            azure_client: The Azure Key Vault client for retrieving secrets
        """
        self.azure_client = azure_client
        self._connection: Optional[Any] = None
        self._cursor: Optional[Any] = None
    
    async def get_connection(self):
        """
        Get or create a Snowflake connection.
        
        This method replicates the exact connection logic from 
        subhub-ai/helpers/settings.py lines 60-70.
        
        Returns:
            snowflake.connector.SnowflakeConnection: The database connection
        """
        if self._connection is None:
            self._connection = snowflake.connector.connect(
                user=await self.azure_client.get_secret("snowflake-username"),
                password=await self.azure_client.get_secret("snowflake-password"), 
                account=await self.azure_client.get_secret("snowflake-account"),
                role=await self.azure_client.get_secret("snowflake-role"),
                warehouse=await self.azure_client.get_secret("snowflake-warehouse"),
                database=await self.azure_client.get_secret("snowflake-database"),
                schema=await self.azure_client.get_secret("snowflake-schema")
            )
        
        return self._connection
    
    async def get_cursor(self):
        """
        Get or create a Snowflake cursor.
        
        This method replicates the exact cursor creation logic from
        subhub-ai/helpers/settings.py line 71.
        
        Returns:
            snowflake.connector.cursor.SnowflakeCursor: The database cursor
        """
        if self._cursor is None:
            connection = await self.get_connection()
            self._cursor = connection.cursor()
        
        return self._cursor
    
    async def execute_query(self, sql_query: str, return_format: str = "json") -> str:
        """
        Execute a SQL query using the Snowflake connection.
        
        This method provides the same interface as subhub-ai's execute_sql_query
        function for easy migration.
        
        Args:
            sql_query: The SQL query to execute
            return_format: "json" (default) for JSON string, "raw" for plain text
            
        Returns:
            Results as JSON string (default) or plain text table format
        """
        cursor = await self.get_cursor()
        
        try:
            cursor.execute(sql_query)
            # Process results if successful
        except snowflake.connector.errors.ProgrammingError as e:
            print(f"SQL compilation error: {e.msg}")
            print(f"Error code: {e.errno}")
            print(f"SQL state: {e.sqlstate}")
            print(f"Query ID: {e.sfqid}")
            raise Exception(f"SQL execution error: {e}")
        except Exception as e:
            raise Exception(f"SQL execution error: {e}")
        
        # Get results (this logic matches subhub-ai exactly)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        
        # Format results based on requested format
        if return_format == "raw":
            return self._format_results_as_txt(columns, rows)
        else:  # Default JSON format
            return self._format_results_as_json(columns, rows)
    
    def _format_results_as_json(self, columns: list, rows: list) -> str:
        """Format SQL results as JSON string (matches subhub-ai exactly)."""
        import json
        import datetime
        import decimal
        
        def convert_decimal(obj):
            if isinstance(obj, decimal.Decimal):
                return float(obj)
            if isinstance(obj, datetime.date):
                return obj.isoformat()
            if isinstance(obj, datetime.datetime):
                return obj.isoformat()
            return obj

        results = [
            {col: convert_decimal(val) for col, val in zip(columns, row)}
            for row in rows
        ]
        return json.dumps(results, indent=2)
    
    def _format_results_as_txt(self, columns: list, rows: list) -> str:
        """Format SQL results as tab-separated text (matches subhub-ai exactly)."""
        if not rows:
            return "No results returned."
        
        # Build tab-separated output
        lines = ["\t".join(columns)]  # Header
        lines.extend("\t".join(str(val) if val is not None else "" for val in row) for row in rows)
        return "\n".join(lines)
    
    def close(self):
        """Close the Snowflake connection and cursor."""
        try:
            if self._cursor:
                self._cursor.close()
        except Exception as e:
            print(f"Error closing Snowflake cursor: {e}")
        
        try:
            if self._connection:
                self._connection.close()
        except Exception as e:
            print(f"Error closing Snowflake connection: {e}")
        
        self._cursor = None
        self._connection = None


def create_snowflake_client(azure_client: AzureKeyVaultClient) -> SnowflakeClient:
    """
    Factory function to create a Snowflake client.
    
    Args:
        azure_client: The Azure Key Vault client for retrieving secrets
        
    Returns:
        SnowflakeClient: Configured client instance
    """
    return SnowflakeClient(azure_client)