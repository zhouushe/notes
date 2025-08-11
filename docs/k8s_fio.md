## Prepare fio image
- Use an official or community-provided fio image (e.g., `ubuntu:fio`, ensuring fio is pre-installed in the image).
- Build a custom image containing fio.
```dockerfile title="FIO Dockerfile"
# Use Alpine Linux as the base image
FROM alpine:latest

# Install dependencies and FIO
RUN apk add --no-cache fio

# Set working directory
WORKDIR /data

# Define the default command to run fio
CMD ["fio"]
```

```bash title="Build FIO Docker image"
docker build -t alpine:fio -f fio_dockerfile .
```

## Create fio-test.yaml
*To test persistent storage performance, add volumes and volumeMounts to the Pod configuration, and mount the test directory to a Persistent Volume Claim (PVC).*
```yaml title="fio-test.yaml"
apiVersion: v1
kind: Pod
metadata:
  name: fio-test
  namespace: default
spec:
  containers:
  - name: fio-container
    image: alpine:fio
    command: ["fio"]
    args:
      - "--name=test"        # Specifies the name of the test
      - "--ioengine=libaio"  # Sets the I/O engine to libaio (Linux native asynchronous I/O)
      - "--rw=read"          # I/O mode: sequential read (other options: write, randread, randwrite, etc.)
      - "--bs=4k"            # Block size for I/O operations (4 KiB in this case)
      - "--size=1G"          # Total size of the test file (1 GiB in this case)
      - "--numjobs=1"        # Number of parallel jobs/processes (1 job in this case)
      - "--runtime=60"       # Test runtime in seconds (60 seconds in this case)
      - "--direct=1"         # Enables direct I/O, bypassing the cache (1 = enabled)
  restartPolicy: Never       # The container will not restart automatically after the FIO job completes or fails
```

## Deploy Pod & Run Test
- Deploy Pod
```bash title="Deploy pod and run test"
kubectl apply -f fio-test.yaml
```

- View Logs
*View results (such as IOPS, bandwidth, etc) after test complete.*
```bash title="View test results"
kubectl logs -f fio-test
```

- Describe Pod
```bash title="Describe pod details"
kubectl describe pod fio-test
```

## Clean Up
- Delete Pod
```bash title="Delete pod after test complete"
kubectl delete pod fio-test
```
