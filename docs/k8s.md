!!! note
    Perform these steps on **all nodes** (`control-plane` and `workers`).

# Prerequisites

## Update System and Install Dependencies
```bash title="Update the system and install required tools"
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl gpg
```

## Disable Swap (Required)
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

# Install Container Runtime (containerd)

## Install containerd
```bash title="Install containerd"
# Install containerd
sudo apt update
sudo apt install -y containerd
```

# Configure containerd
```bash title="Configure containerd"
sudo mkdir -p /etc/containerd
containerd config default | sudo tee /etc/containerd/config.toml
```

# Enable systemd cgroup driver
```bash title="Enable systemd cgroup driver"
sudo sed -i 's/SystemdCgroup\s*=\s*false/SystemdCgroup = true/i' /etc/containerd/config.toml
```

# Restart containerd
```bash title="Restart containerd"
sudo systemctl restart containerd
sudo systemctl enable containerd
```

# Install Kubernetes Components

## Add Kubernetes APT repository
```bash title="Add Kubernetes APT repository"
curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.32/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg
echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list
```

## Install Kubernetes tools
```bash title="Install Kubernetes tools"
sudo apt update
sudo apt install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl  # Prevent auto-upgrades
```

!!! note
    Perform these steps **only on the control-plane node**.

# Initialize the Control Plane (Master Node)

## Set Hostname
```bash title="Set Hostname"
# Set a unique hostname
sudo hostnamectl set-hostname k8s-control-plane

# View hostname information
hostnamectl status

# Clear the hostname, the system will use the default value
hostnamectl set-hostname ""
```

## Initialize the Cluster
```bash title="Initialize the Cluster"
# sudo kubeadm init --pod-network-cidr=<cidr> --control-plane-endpoint=<control-plane-ip>
sudo kubeadm init --pod-network-cidr=10.227.0.0/16 --control-plane-endpoint=10.227.224.235
```
!!! error 
    [ERROR FileContent--proc-sys-net-ipv4-ip_forward]: /proc/sys/net/ipv4/ip_forward contents are not set to 1

    ```bash title="Enable IPv4 forward"
    sudo sed -i 's/^#*net.ipv4.ip_forward=1/net.ipv4.ip_forward = 1/' /etc/sysctl.conf
    sudo sysctl -p
    ```

## Configure kubectl
