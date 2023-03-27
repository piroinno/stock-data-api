# Stock Data API

> NOTICE: This is purly development code. Please my further notices here: NOTICE.md 
This API serves EDO stock data. and will serve historical price delta when completed.

A very temporary implementation - (I will decom it soon) is here https://stockdata-dev.piroinno.com/

# Stack

- FastAPI: Serves EOD data if given a ticker symbol 
  - stock-data-api code repo and buile workflows:  https://github.com/piroinno/stock-data-api
- Data ingestion microservices: Written in Python, get data from a privider on daily schedule. The python controller creates batch jobs on an azure queue. The python worker services pickup essages from the queue, downloads the data into blob as defined in the message oayload.
  - stock-data-ingestor code repo and build workflows: https://github.com/piroinno/stock-data-ingestor
- AKS: the API and microservices are hosted on a secure AKS server within a hub and spoke vnet network
- Flagsmith: This is a feature control tool which I used to disbale the historical analysis endpoint in the API in a given environment. Feature flags are great at preventing unintended feature breakout into enviromrnts like production.

## Storage

- The simple data model used as part of the databse interaction is stored here, stock-data-model: https://github.com/piroinno/stock-data-model
- Postgres Database: Using alembic the database is versioned, so changes to the schema can be rolled back or forward
- ADLS to store the partitioned histoorical files: Data downloade is stored here

## IaC / CICD Ochestration

To keep things DRY, I used composite templates so tha I could reuse code and generally its better to have 1 place to make changes.

I also used tags when possible to ensure workflows are pinned to a given snapshot in time and no tto day the dev or main branch.

- Terraform was used to version and deploy infrastructure.
  - infra code repo and ochestration templates: https://github.com/piroinno/stock-data-infra-mngt, https://github.com/piroinno/stock-data-infra-tf-automation
- CICD ochestration was implemented using 2 different patterns - DevOps and GitOps.
  - application ochestration action templates: https://github.com/piroinno/stock-data-app-automation 
  - DevOps: Build agents (both managed and self hosted) were used to test + build + deploy
  - GitOps: BUild agents (both managed and self hosted) were used to build + test only. Deployment of the Application code and manifiests to the AKS cluster was implemented with flux
    - FLux: Adter testing and building the application code, chnages to the dev and prd branches were merged into state.dev and state.prd via a PR.
    - state.xxx: is the golden source of truth fo the AKS clusters. Any changes in these branches are automatically reconcilled by flux into AKS.
