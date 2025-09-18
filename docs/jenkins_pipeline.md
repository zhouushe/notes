# Prerequisites

## Configure Webhooks on GitHub Repo
**Settings** → **Hooks** → **Webhooks**
- Payload URL  
  - `https://<username>:<token>@<jenkins-server>/generic-webhook-trigger/invoke`
- Content type  
  - `application/json`
- SSL verification  
  - `Enable SSL verification`
- Which events would you like to trigger this webhook?  
  - Issue comments
  - Labels
  - Pull requests
  - Pushes

## Configure Credentials on Jenkins Server
