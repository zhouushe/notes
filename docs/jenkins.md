# Jenkins Notes

## Jenkins Doc
https://www.jenkins.io/doc/

### **Jenkins Code Samples**
- Jenkins Get Computer
```groovy title="This is an example get computer"
import jenkins.model.Jenkins

println(Jenkins.getInstance().getComputer("agent-node-1").getDescription())
println(Jenkins.getInstance().getComputer("agent-node-1").getNode().getLabelString())

for(computer in Jenkins.getInstance().getComputers()) {
    println(computer.getName())
    println(computer.getDisplayName())
    println(computer.getNode())
    println(computer.getDescription())
    println("--------------------------------")
}
```
