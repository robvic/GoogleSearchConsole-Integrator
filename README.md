# google-search-console-integrator
## How to Use

This code can be run both on local machine or GCP serverless service. Adjustments must be made on settings variables accordingly.

Start date must be set to current date for programatic usage. Otherwise it should indicate start and end date for backfill purposes.

## Authentication

For local usage, a JSON credential generated on IAM must be referenced. For cloud environment, the serverless service's service account must have permissions to write data in Big Query.