
|Badge|Source
|--|--|
|![Known Vulnerabilities](https://snyk.io/test/github/JaKTR/Umbrella-ERP-API/badge.svg)|[Synk Developer Security](https://snyk.io)|
|[![codecov](https://codecov.io/gh/JaKTR/Umbrella-ERP-API/branch/main-dev/graph/badge.svg?token=ZB9ZG2KH3O)](https://codecov.io/gh/JaKTR/Umbrella-ERP-API)|[CodeCov](https://app.codecov.io/gh/JaKTR/Umbrella-ERP-API)
|[![Total alerts](https://img.shields.io/lgtm/alerts/g/JaKTR/Umbrella-ERP-API.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/JaKTR/Umbrella-ERP-API/alerts/)|[LGTM Code Analysis](https://lgtm.com/projects/g/JaKTR/Umbrella-ERP-API/alerts/)
|[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/JaKTR/Umbrella-ERP-API.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/JaKTR/Umbrella-ERP-API/context:python)|[LGTM Code Analysis](https://lgtm.com/projects/g/JaKTR/Umbrella-ERP-API/context:python)
|[![Maintainability](https://api.codeclimate.com/v1/badges/1455525ce4f602db9f48/maintainability)](https://codeclimate.com/github/JaKTR/Umbrella-ERP-API/maintainability)|[Code Climate](https://codeclimate.com/github/JaKTR/Umbrella-ERP-API/maintainability)
|[![Foresight Docs](https://foresight.service.thundra.io/public/api/v1/badge/test?repoId=b232bf7b-2c03-4700-9acd-74024edca0a8)](https://foresight.docs.thundra.io/)|[Thundra Foresight](https://www.thundra.io/foresight)
|[![Foresight Docs](https://foresight.service.thundra.io/public/api/v1/badge/success?repoId=b232bf7b-2c03-4700-9acd-74024edca0a8)](https://foresight.docs.thundra.io/)|[Thundra Foresight](https://www.thundra.io/foresight)
|[![Foresight Docs](https://foresight.service.thundra.io/public/api/v1/badge/utilization?repoId=b232bf7b-2c03-4700-9acd-74024edca0a8)](https://foresight.docs.thundra.io/)|[Thundra Foresight](https://www.thundra.io/foresight)


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
