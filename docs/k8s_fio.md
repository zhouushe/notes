## Prepare fio image
- Use an official or community-provided fio image (e.g., `ubuntu:fio`, ensuring fio is pre-installed in the image)
- Build a custom image containing fio
```dockerfile title="FIO Dockerfile"
# Use Alpine Linux as the base image
FROM alpine:latest

# Install dependencies and FIO
RUN apk add --no-cache fio

# Set FIO working directory
WORKDIR /data

# Expose FIO server port (default 8765)
EXPOSE 8765

# Define the default command to run fio
CMD ["fio"]
```

```bash title="Build FIO Docker image"
docker build -t alpine:fio -f fio_dockerfile .
```

```bash title="Verify FIO Docker image"
docker run -it --rm --network=host alpine:fio fio --version
```

- Ensure k8s nodes can access local image
```bash title="Use local registry for multi-node clusters"
# Run a Docker registry container in detached mode
# -d: Runs the container in the background (detached mode)
# -p 5000:5000: Maps port 5000 on the host to port 5000 in the container, allowing access to the registry
# --restart=always: Automatically restarts the container if it stops or the host reboots
# --name registry: Names the container "registry" for easy reference
# registry:2: Uses the official Docker registry image (version 2)
docker run -d -p 5000:5000 --restart=always --name registry registry:2

# Tag the local alpine:fio image for pushing to the local registry
# alpine:fio - The source image name (built locally on your machine)
# localhost:5000/alpine-fio - The new tag, indicating the image will be pushed to the local registry at localhost:5000
docker tag alpine:fio localhost:5000/alpine-fio

# Push the tagged image to the local registry
# localhost:5000/alpine-fio: The target registry and image name
# This uploads the image to the registry running at localhost:5000, making it accessible to Kubernetes nodes
docker push localhost:5000/alpine-fio
```

## Deploy FIO Server
- Create fio-server.yaml
```yaml title="fio-server.yaml"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fio-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: fio-server
  template:
    metadata:
      labels:
        app: fio-server
    spec:
      containers:
      - name: fio-server
        image: localhost:5000/alpine-fio
        command: ["fio"]
        args: ["--server", "--port=8765"]
        ports:
        - containerPort: 8765
        volumeMounts:
        - name: test-volume
          mountPath: /test
      volumes:
      - name: test-volume
        hostPath:
          path: /mnt/fio-test
          type: DirectoryOrCreate
```
- Deploy FIO Server
```bash title="Deploy fio server"
kubectl apply -f fio-server.yaml
```

## Wait for FIO Server Ready
```bash title="Wait for FIO server to be ready"
kubectl wait --for=condition=available deployment/fio-server --timeout=300s
```

## Deploy FIO Service
- Create fio-server-service.yaml
```yaml title="fio-server-service.yaml"
apiVersion: v1
kind: Service
metadata:
  name: fio-server-service
spec:
  selector:
    app: fio-server-service
  ports:
    - protocol: TCP
      port: 8765
      targetPort: 8765
```
- Deploy FIO Service
```bash title="Deploy fio service"
kubectl apply -f fio-server-service.yaml
```

## Create fio-client.yaml
-  Create fio-client.yaml
*To test persistent storage performance, add volumes and volumeMounts to the Pod configuration, and mount the test directory to a Persistent Volume Claim (PVC).*
```yaml title="fio-client.yaml"
apiVersion: batch/v1
kind: Job
metadata:
  name: fio-client
spec:
  template:
    spec:
      containers:
      - name: fio-client
        image: localhost:5000/alpine-fio
        imagePullPolicy: Always
        command: ["fio", "--server=fio-server:8765"]
        args:
          - "--name=test"        # Specifies the name of the test
          - "--ioengine=libaio"  # Sets the I/O engine to libaio (Linux native asynchronous I/O)
          - "--rw=read"          # I/O mode: sequential read (other options: write, randread, randwrite, etc.)
          - "--bs=4k"            # Block size for I/O operations (4 KiB in this case)
          - "--size=1G"          # Total size of the test file (1 GiB in this case)
          - "--numjobs=1"        # Number of parallel jobs/processes (1 job in this case)
          - "--runtime=60"       # Test runtime in seconds (60 seconds in this case)
          - "--direct=1"         # Enables direct I/O, bypassing the cache (1 = enabled)
        volumeMounts:
        - name: fio-volume
          mountPath: /test
      volumes:
      - name: fio-volume
        hostPath:
          path: /mnt/fio-test      # Test this storage path
          type: DirectoryOrCreate  # Creates if doesn't exist
      restartPolicy: Never         # Don't restart after completion
  backoffLimit: 0
```
- Deploy FIO Client
```bash title="Deploy fio client"
kubectl apply -f fio-client.yaml
```

## Monitor FIO Progress
```bash title="Monitor FIO server and client progress"
kubectl get pods -w
```

## View FIO Log
- View FIO Client Log
```bash title="View client logs"
kubectl logs -f job/fio-client
```
- View FIO Server Log
```bash title="View server logs"
kubectl logs -f deployment/fio-server
```

## Retrieve Results
```bash title="Retrieve results"
# Get detailed JSON output
kubectl logs job/fio-client > fio-results.json

# Parse results
kubectl logs job/fio-client | jq '.jobs[] | {jobname: .jobname, read: .read, write: .write}'
```

## Clean Up
- Delete Client
```bash title="Delete client"
kubectl delete job fio-client -n default
```
- Delete Server
```bash title="Delete server"
kubectl delete deployment fio-server -n default
kubectl delete svc fio-server-service -n default
```
