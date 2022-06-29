[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API) [![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Bugs](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=bugs)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=coverage)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)

[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-white.svg)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)
# Umbrella-ERP-API

Umbrella Enterprise Resource Planning web app's backend.

# Azure Cloud Infrastructure Architectural Diagram

![Azure Cloud infrastructure architectural diagram](https://umbrellaerpdevelopment.blob.core.windows.net/public/Infrastructure%20Architectural%20Diagram.svg)

|Infrastructure|Cloud service
|--|--|
|`Client`|Azure Static Website
|`API`|Azure Functions
|`Storage`|Azure Storage
|`Database`|Azure Cosmos DB API for MongoDB

# Base Endpoints

|Environment|URL
|--|--|
|`Development`|https://umbrella-backend-development.azurewebsites.net/
|`SIT`|https://umbrella-backend-sit.azurewebsites.net/
|`Production`|https://umbrella-backend-production.azurewebsites.net/

# Configuration

Setup the following environmental variables for running the application:

|Name|Description|Use
|--|--|--|
|`KEY_VAULT_NAME`|Azure Key Vault Name|Connect to the Azure Key Vault
|`AZURE_TENANT_ID`|Azure Tenant ID|Connect to the Azure Key Vault
|`AZURE_CLIENT_ID`|Azure Client ID|Connect to the Azure Key Vault
|`AZURE_CLIENT_SECRET`|Azure Client Secret|Connect to the Azure Key Vault


Setup the following secrets in the key vault:

|Name|Description|Use
|--|--|--|
|`MONGO-DB-URI`|MongoDB compatible NoSQL Database URI String|Connect to the NoSQL Database
|`AZURE-STORAGE-CONNECTION-STRING`|Azure Storage Connection String|Connect to the Azure Storage Containers
