# Prepare All Nodes (Master Node & Worker Nodes)
!!! note
    Perform these steps on **all nodes** (`control-plane` and `workers`).

## Prerequisites
- Update System and Install Dependencies
```bash title="Update the system and install required tools"
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
```

- Disable Swap (Required)
```bash title="Kubernetes requires swap to be disabled"
# Backup the fstab file
sudo cp /etc/fstab /etc/fstab.bak

# Comment out the swap line
sudo sed -i '/swap/s/^/#/' /etc/fstab  # Permanent disable

# Disable all swap spaces
sudo swapoff -a

# View swap space status
sudo swapon --show
```

- Enable IPv4 forward
```bash title="Enable IPv4 forward"
sudo sed -i 's/^#*net.ipv4.ip_forward=1/net.ipv4.ip_forward = 1/' /etc/sysctl.conf
sudo sysctl -p
```

## Install Container Runtime (containerd)
- Install containerd
```bash title="Install containerd"
# Install containerd
sudo apt update
sudo apt install -y containerd
```

- Configure containerd
```bash title="Configure containerd"
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
```

- Enable systemd cgroup driver
```bash title="Enable systemd cgroup driver"
sudo sed -i 's/SystemdCgroup\s*=\s*false/SystemdCgroup = true/i' /etc/containerd/config.toml
```

- Restart containerd
```bash title="Restart containerd"
sudo systemctl restart containerd
sudo systemctl enable containerd
```

## Install Kubernetes Components
- Add Kubernetes APT repository
```bash title="Add Kubernetes APT repository"
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
```

- Install Kubernetes tools
```bash title="Install Kubernetes tools"
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl  # Prevent auto-upgrades
```

# Initialize Cluster (Master Node)
!!! note
    Perform these steps **only on the control-plane node**.

## Set Hostname
Set unique hostnames (e.g., `k8s-control-plane`)
```bash title="Set Hostname"
# Set a unique hostname
sudo hostnamectl set-hostname k8s-control-plane

# View hostname information
hostnamectl status

# Clear the hostname, the system will use the default value
hostnamectl set-hostname ""
```

## Initialize Cluster
- Initialize the control-plane with `kubeadm`
```bash title="Initialize the control-plane with kubeadm"
# sudo kubeadm init --pod-network-cidr=<cidr> --control-plane-endpoint=<control-plane-ip>
sudo kubeadm init --pod-network-cidr=10.227.0.0/16 --control-plane-endpoint=10.227.224.235
```

- `/etc/kubernetes/` directory structure
```text title="/etc/kubernetes/ Directory Structure"
/etc/kubernetes/
├── admin.conf               # Cluster configuration file with admin privileges
├── controller-manager.conf  # Configuration file for the controller manager
├── kubelet.conf             # Configuration file for the kubelet component
├── scheduler.conf           # Configuration file for the scheduler
├── manifests/               # Directory for static Pod manifests
└── pki/                     # Directory for certificates and keys
```

## Configure kubectl
- Set up the admin configuration
```bash title="Set up the admin configuration"
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

## Install CNI Plugin (Flannel)
- Apply the Flannel network
```bash title="Apply the Flannel network"
kubectl apply -f https://raw.githubusercontent.com/flannel-io/flannel/master/Documentation/kube-flannel.yml
```

- Wait for pods to be ready
```bash title="Wait for pods to be ready"
kubectl get pods -n kube-system
```

# Join Cluster (Worker Nodes)
!!! note
    Perform these steps on **each worker node**.

## Set Hostname
Set unique hostnames (e.g., `k8s-worker1`, `k8s-worker2`)
```bash title="Set unique hostname"
sudo hostnamectl set-hostname k8s-worker1
```

## Join Cluster
Run the `kubeadm join` command from the control-plane node’s `kubeadm init` output.
```bash title="Join cluster"
# sudo kubeadm join <control-plane-ip>:6443 --token <token> --discovery-token-ca-cert-hash sha256:<hash>
sudo kubeadm join 10.227.224.235:6443 --token mckgmt.bls3e4rnpj8mtllm --discovery-token-ca-cert-hash sha256:468406b3769e708098b5290806c9b0ff3ce9620a2c358e729566acd6b0bbf932
```

# Verify Cluster (Master Node)
!!! note
    Perform these steps **only on the control-plane node**.

## Verify Cluster
On the **control-plane node**, check `node` status.
```bash title="Verify cluster"
kubectl get nodes
```
All nodes should appear in the `Ready` state.

## Test Cluster
- Deploy a sample `nginx` application
```bash title="Deploy nginx"
kubectl create deployment nginx --image=nginx
kubectl scale deployment nginx --replicas=3
kubectl expose deployment nginx --port=80 --type=NodePort
```

- Get the service details
```bash title="Get details"
kubectl get svc
```
