## K8S Command
```bash title="K8S command"
# Lists all pods across all namespaces in a cluster
kubectl get pods --all-namespaces

# Show details of all service
kubectl get svc

# Show details of nginx service
kubectl get service nginx

# Show all pods of nginx application
kubectl get pods -l app=nginx

# Show all nodes with details
kubectl get nodes -o wide

# Show nginx nodes with details
kubectl get pods -l app=nginx -o wide

# Show pod details of a specific name
kubectl get pods -l app=nginx
kubectl describe pod <pod-name>

# Delete nginx service
kubectl delete service nginx

# Delete nginx deployment
kubectl delete deployment nginx

# Check flannel pods
kubectl get pods -n kube-system -l app=flannel

# Check flannel pod log
kubectl get pods -n kube-system -l app=flannel
kubectl logs -n kube-system <flannel-pod-name> -c kube-flannel

# Check the current status of the containerd service using systemd
sudo systemctl status containerd

# Restart kubelet
sudo systemctl restart kubelet

# Check kubelet logs
journalctl -u kubelet -n 100 --no-pager
```
