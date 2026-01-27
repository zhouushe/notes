# Add a Jenkins apt repository entry
curl https://pkg.jenkins.io/debian/jenkins.io-2026.key -o /etc/apt/keyrings/jenkins-keyring.asc \
echo "deb [signed-by=/etc/apt/keyrings/jenkins-keyring.asc]" https://pkg.jenkins.io/debian binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

# Install JDK and Jenkins
sudo apt-get update \
sudo apt-get install fontconfig openjdk-21-jre (sudo apt install openjdk-21-jdk) \
sudo apt-get install jenkins

# Configure Jenkins Service
sudo systemctl start jenkins   # Start Jenkins service \
sudo systemctl enable jenkins  # Enable automatic startup on boot \
sudo systemctl status jenkins  # Check the service status 

# Check Jenkins Port
sudo netstat -tlnp | grep 8080

# Jenkins Home
ll /var/lib/jenkins

# Retrieve the initial admin password for Jenkins setup
sudo cat /var/lib/jenkins/secrets/initialAdminPassword

# Visit Jenkins (shuai/******)
http://<jenkins-server>:8080

# Jenkins Plugins:
AnsiColor \
Environment Injector \
Generic Webhook Trigger \
lockable-resources \
Nested View \
Extended Choice Parameter \
Active Choices \
SSH Pipeline Steps \
docker-workflow \
Docker

# Configure HTML Publisher
Manage Jenkins -> Security -> Markup Formatter: Safe HTML

# Set Property via Script Console
Manage Jenkins --> Script Console: \
System.setProperty("hudson.model.DirectoryBrowserSupport.CSP", "default-src * 'unsafe-inline' 'unsafe-eval'; script-src * 'unsafe-inline' 'unsafe-eval'; connect-src * 'unsafe-inline'; img-src * data: blob: 'unsafe-inline'; frame-src *; style-src * 'unsafe-inline';")

# Install Plugin via CLI
curl -O http://localhost:8080/jnlpJars/jenkins-cli.jar \
java -jar jenkins-cli.jar -s http://localhost:8080/ -auth shuai:****** install-plugin ansicolor \
java -jar jenkins-cli.jar -s http://localhost:8080/ -auth shuai:****** install-plugin generic-webhook-trigger \
java -jar jenkins-cli.jar -s http://localhost:8080/ -auth shuai:****** safe-restart

# Configure Encoding
vi /etc/default/jenkins \
JAVA_ARGS="-Djava.awt.headless=true -Dfile.encoding=UTF-8 -Dsun.jnu.encoding=UTF-8 -Dmail.mime.charset=UTF-8" \
service jenkins restart \
service jenkins status

# GitHub Raw Content Rest API
https://raw.githubusercontent.com/<owner>/<repo>/main/mkdocs.yml \
Accept: application/vnd.github.v3.raw \
Authorization: token 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

# Simulate GitHub Payload
http://shuai:******@<jenkins-server>:8080/generic-webhook-trigger/invoke \
curl -X POST -H "Content-Type: application/json" -d '{"test": "value"}' http://shuai:110f292fb5d1ac78c5d03a6764b87a7aec@<jenkins-server>:8080/generic-webhook-trigger/invoke

# Uninstall Jenkins
sudo systemctl stop jenkins \
sudo apt remove --purge jenkins \
sudo rm -rf /var/lib/jenkins
