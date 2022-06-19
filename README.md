![Known Vulnerabilities](https://snyk.io/test/github/JaKTR/Umbrella-ERP-API/badge.svg)
[![Maintainability](https://api.codeclimate.com/v1/badges/1455525ce4f602db9f48/maintainability)](https://codeclimate.com/github/JaKTR/Umbrella-ERP-API/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/1455525ce4f602db9f48/test_coverage)](https://codeclimate.com/github/JaKTR/Umbrella-ERP-API/test_coverage)

# Umbrella-ERP-API  
Umbrella Enterprise Resource Planning web app's backend. 

# Infrastructure Architecture
![Umbrella Enterprise Resource Planning web app's infrastructure architectural diagram.](https://umbrellaerpdevelopment.blob.core.windows.net/public/Infrastructure%20Architectural%20Diagram.svg)

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
Setup the following environmental variables:

|Name|Description|Use
|--|--|--|
|`MONGO_DB_URI`|MongoDB compatible NoSQL Database URI|Connect to the database
