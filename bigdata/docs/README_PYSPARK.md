# PySpark 3.4 with Podman Setup

This setup provides PySpark 3.4 running in a Podman container with all necessary dependencies.

## Quick Start

### Option 1: Using the management script (Recommended)

```bash
# Build the container
./pyspark_container.sh build

# Start the container
./pyspark_container.sh run

# Test PySpark installation
./pyspark_container.sh test

# Open shell in container
./pyspark_container.sh shell

# Start Jupyter Lab
./pyspark_container.sh jupyter

# Check status
./pyspark_container.sh status

# Clean up
./pyspark_container.sh clean
```

### Option 2: Using Podman commands directly

```bash
# Build the container
podman build -f Dockerfile.pyspark -t pyspark-3.4 .

# Run the container
podman run -d \
  --name pyspark-app \
  -p 4040:4040 -p 8080:8080 -p 8081:8081 -p 7077:7077 -p 8888:8888 \
  -v /var/www/ai_apps:/workspace \
  pyspark-3.4 \
  tail -f /dev/null

# Execute commands in container
podman exec -it pyspark-app python pyspark_demo.py

# Start Jupyter Lab
podman exec -d pyspark-app \
  jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token=''
```

### Option 3: Using the simple pre-built image

```bash
# Build using Apache's official Spark image
podman build -f Dockerfile.pyspark.simple -t pyspark-simple .

# Run with the simple image
podman run -d \
  --name pyspark-simple \
  -p 4040:4040 -p 8888:8888 \
  -v /var/www/ai_apps:/workspace \
  pyspark-simple
```

## Access Points

- **Spark UI**: http://localhost:4040
- **Spark Master UI**: http://localhost:8080
- **Jupyter Lab**: http://localhost:8888

## Files Created

- `Dockerfile.pyspark` - Main Dockerfile with Java 11 and Spark 3.4.3
- `Dockerfile.pyspark.simple` - Simplified Dockerfile using Apache's pre-built image
- `requirements_pyspark.txt` - Python dependencies
- `pyspark_container.sh` - Container management script
- `pyspark_demo.py` - Demo script to test PySpark
- `docker-compose.pyspark.yml` - Docker Compose configuration

## Testing PySpark

Run the demo script to verify everything works:

```bash
# In the container
podman exec -it pyspark-app python pyspark_demo.py
```

Or use the management script:

```bash
./pyspark_container.sh test
```

## Features

- ✅ PySpark 3.4.3
- ✅ Java 11 OpenJDK
- ✅ Jupyter Lab
- ✅ Pandas, NumPy, Matplotlib
- ✅ Spark UI access
- ✅ Volume mounting for persistent work
- ✅ Port forwarding for web interfaces

## Troubleshooting

If the build fails, try the alternative simple image:
```bash
podman build -f Dockerfile.pyspark.simple -t pyspark-simple .
```

For memory issues, you can adjust Spark configuration:
```bash
podman exec -it pyspark-app pyspark --driver-memory 2g --executor-memory 2g
```
