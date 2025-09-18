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
  - Description (e.g., `GitHub token for service account xxx`)

## Configure Environment on Jenkins Server
**Manage Jenkins** → **System**
- Global properties
  - Environment variables
    - Name (e.g., `CFG_JENKINS_ENV`)
    - Value (e.g., `test` or `product`)

## Configure Library on Jenkins Server
**Manage Jenkins** → **System**
- Library
  - Name (e.g., `xxx-qe-jenkins`)
  - Default version (e.g., `main`)
- Allow default version to be overridden
- Include @Library changes in job recent changes
- Retrieval method (`Modern SCM`)
  - Source Code Management (`Git`)
    - Project Repository (e.g., `https://<GitHub-server>/<owner>/<repo>.git`)
    - Credentials (e.g., `GitHub token for service account xxx`)
  - Library Path (optional) (e.g., `./`)
