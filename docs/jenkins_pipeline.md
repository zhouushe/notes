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
**Credentials** → **System** → **Global credentials (unrestricted)** → **Add Credentials**
- Credentials
  - Scope (e.g., `Global (Jenkins, nodes, items, all child items, etc)`)
  - Username
  - Treat username as secret
  - Password
  - ID (e.g., `GIT_BUILDER`)
  - Description (e.g., `GitHub Token for service account xxxxxx`)
## Configure Library on Jenkins Server
  - 
