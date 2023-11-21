# google-search-console-integrator
## How to Use

This code can be run both on local machine or GCP serverless service. Adjustments must be made on settings variables accordingly.

Start date must be set to current date for programatic usage. Otherwise it should indicate start and end date for backfill purposes.

## Functions Framework
To run locally, the package functions-framework should be installed via pip. At the same folder as the function code, the command functions_framework target=NAME-OF-FUNCTION is necessary to setup the service.

To start sending events, use curl or Postman whith the required payload along with the endpoint request.

## API
To query the API, the following endpoint is used:
  https://www.googleapis.com/webmasters/v3/sites/DOMAIN_OR_WEBADDRESS/searchAnalytics/query

The payload used is simply the stard and end date.

For further usage, check the following docs:
https://developers.google.com/webmaster-tools/v1/searchanalytics/query

## Authentication

For local usage, a JSON credential generated on IAM must be referenced. For cloud environment, the serverless service's service account must have permissions to write data in Big Query.
