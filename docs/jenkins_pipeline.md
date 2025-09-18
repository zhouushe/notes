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

## Configure SMTP server on Jenkins Server
**Manage Jenkins** → **System**
- E-mail Notification
  - SMTP server (e.g., `smtp.xxx.com`)
  - Default user e-mail suffix (e.g., `@xxx.com`)

## Install Plugins on Jenkins Server
**Manage Jenkins** → **Plugins**
  - Generic Webhook Trigger
  - Lockable Resources

## Configure Jenkins Job `github_webhook_dispatcher` on Jenkins Server
- Discard old builds
  - Strategy (e.g., `Log Rotation`)
    - Days to keep builds (e.g., `30` days)
    - Max # of builds to keep (e.g., `500` records)
- This project is parameterized
  - String Parameter
    - Name (e.g., `payload`)
    - Default Value
    - Trim the string
- Triggers
  - Generic Webhook Trigger
    - Post content parameters
      - Variable (e.g., `payload`)
      - Expression (e.g., `$`)
      - JSONPath
    - Header parameters
      - Request header (e.g., `X-GitHub-Event`)
- Pipeline
  - Definition (Pipeline script)
    ```groovy title="pipeline script"
    /**在Jenkins Pipeline中引入共享库的指令，下划线_指示Groovy在解析代码时将库导入到当前命名空间中，允许调用该库中定义的步骤和函数。*/
    @Library('xxx-qe-jenkins@main') _
    /**Jenkins Pipeline的执行入口，this是Jenkins session实例。*/
    com.corp.product.jenkins.Launcher.launch(this)
    ```
