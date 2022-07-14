[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API) [![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Bugs](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=bugs)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=coverage)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)    [![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=JaKTR_Umbrella-ERP-API&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)

[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-white.svg)](https://sonarcloud.io/summary/new_code?id=JaKTR_Umbrella-ERP-API)

# Ozone-ERP-API

Ozone Enterprise Resource Planning web app's backend.

# Azure Cloud Infrastructure Architectural Diagram

![Azure Cloud Infrastructure Architectural Diagram](https://raw.githubusercontent.com/JaKTR/Umbrella-ERP-API/main-dev/media/Infrastructure%20Architecture%20Diagram.svg?sanitize=true)

# Endpoints

## Base

|Environment|URL  
|--|--|  
|*Development*|`https://ozone-api-development.azurewebsites.net/`  
|*SIT*|`https://ozone-api-sit.azurewebsites.net/`  
|*Production*|`https://ozone-api-production.azurewebsites.net/`

## Microservice

|Microservice|URL  
|--|--|  
|*Super Admin*|`/super-admin`  
|*Identity Access Management*|`/iam`  
|*RACS*|`/racs`  
|*The Hydrant*|`/the-hydrant`

# Configuration

## Step 1: Environment Variables

Setup the following environmental variables for running the application:

|Name|Description|Use|Notes  
|--|--|--|--|  
|`KEY_VAULT_NAME`|Azure Key Vault Name|Connect to the Azure Key Vault|  
|`AZURE_TENANT_ID`|Azure Tenant ID|Connect to the Azure Key Vault|[Guide](https://www.inkoop.io/blog/how-to-get-azure-api-credentials/)  
|`AZURE_CLIENT_ID`|Azure Client ID|Connect to the Azure Key Vault|[Guide](https://www.inkoop.io/blog/how-to-get-azure-api-credentials/)  
|`AZURE_CLIENT_SECRET`|Azure Client Secret|Connect to the Azure Key Vault (periodic renewal needed)|[Guide](https://www.inkoop.io/blog/how-to-get-azure-api-credentials/)

## Step 2: Secrets

Setup the following secrets in the key vault:

|Name|Description|Use  
|--|--|--|  
|`MONGO-DB-URI`|MongoDB compatible NoSQL Database URI String|Connect to the NoSQL Database  
|`AZURE-STORAGE-CONNECTION-STRING`|Azure Storage Connection String|Connect to the Azure Storage Containers  
|`ALLOWED-ORIGINS`|The allowed CORS origins, comma seperated <br>(e.g. "`http://localhost:4200,https://agreeable-pond-0a5f40c10.1.azurestaticapps.net`")|Sets the `allow_origins` settings in the middleware settings

## Step 3: Azure Configurations

1. Add the the function to the Key Vault's Access Policy with all the `Secrets` permissions and the application *(created in the above step)* as the principal.

2. Enable CORS in the function app's `CORS` settings

3. Enable `Access-Control-Allow-Credentials` in the CORS settings and set the relevant allowed origins