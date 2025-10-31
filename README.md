# SubHub Infrastructure Shared

Shared infrastructure components for SubHub and TrueNorth AI projects.

## Overview

This package provides shared infrastructure clients for:
- **Azure Key Vault**: Authentication and secret management
- **Snowflake**: Database connections with automatic credential retrieval
- **Looker API**: Authentication and query execution

## Installation

Install directly from the repository:

```bash
pip install git+https://github.com/your-org/subhub-infra-shared.git
```

Or install in development mode (for local development):

```bash
git clone https://github.com/your-org/subhub-infra-shared.git
cd subhub-infra-shared
pip install -e .
```

## Quick Start

### Basic Usage

```python
from subhub_infra import get_infrastructure_client

# Initialize with Azure Key Vault
client = await get_infrastructure_client()

# Get Snowflake connection
snowflake_conn = await client.snowflake.get_connection()
cursor = await client.snowflake.get_cursor()

# Get Looker client and execute query
looker_client = client.looker
results = await looker_client.execute_query(query_json)
```

### Direct Client Access

```python
from subhub_infra import get_azure_client, get_looker_client

# Get specific clients directly
azure_client = await get_azure_client()
looker_client = await get_looker_client()

# Retrieve secrets
api_key = await azure_client.get_secret("my-secret-key")

# Execute Looker queries
query = {
    "model": "subscriber_analytics",
    "view": "service_subscriber_metric_agg_subhub",
    "fields": ["service_subscriber_metric_agg_subhub.signups"],
    "filters": {"service_subscriber_metric_agg_subhub.business_date": "7 days"},
    "limit": 100
}
results = await looker_client.execute_query(query)
```

## Components

### Azure Key Vault Client
- Handles authentication using system-appropriate credentials
- Retrieves secrets with the same interface as the original implementation
- Special handling for OpenAI API keys

### Snowflake Client  
- Manages database connections using Azure Key Vault credentials
- Provides query execution with JSON and text output formats
- Automatic connection management and cleanup

### Looker API Client
- Handles API authentication and token refresh
- Executes queries using Looker's JSON query format
- Automatic retry on authentication failures

## Configuration

The package uses Azure Key Vault for all credential management. Ensure your environment has access to the configured Key Vault and the following secrets are available:

- `azure-endpoint`
- `snowflake-username`, `snowflake-password`, `snowflake-account`, etc.
- `looker-api-base-url`, `looker-service-account-client-id`, `looker-service-account-client-secret`

## Architecture

This package extracts and modularizes infrastructure logic while maintaining exact compatibility with existing implementations. It enables:

- **Code Reuse**: Share infrastructure across multiple projects
- **Consistent Behavior**: Same interfaces and logic as original implementations  
- **Independent Evolution**: Projects can adopt at their own pace
- **Resource Sharing**: Common Azure, Snowflake, and Looker resources

## Requirements

- Python 3.9+
- Azure Key Vault access
- Snowflake account access
- Looker instance access

## Contributing

This package is designed as a stable infrastructure layer. Changes should maintain backward compatibility with existing consumers.