#!/bin/bash

# PySpark Container Management Script
# Usage: ./pyspark_container.sh [build|run|stop|shell|jupyter|clean]

CONTAINER_NAME="pyspark-app"
IMAGE_NAME="pyspark-3.4"
WORKSPACE_DIR="/var/www/ai_apps"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to build the container
build_container() {
    print_status "Using Bitnami Spark 3.4.3 image directly..."
    print_status "No build needed - using pre-built image: docker.io/bitnami/spark:3.4.3"
    print_success "Ready to run container!"
}

# Function to run the container
run_container() {
    print_status "Starting PySpark container..."
    
    # Stop existing container if running
    podman stop $CONTAINER_NAME 2>/dev/null || true
    podman rm $CONTAINER_NAME 2>/dev/null || true
    
    # Use Bitnami Spark image directly
    podman run -d \
        --name $CONTAINER_NAME \
        -p 4040:4040 \
        -p 8082:8080 \
        -p 8081:8081 \
        -p 7077:7077 \
        -p 8888:8888 \
        -v $WORKSPACE_DIR:/workspace \
        docker.io/bitnami/spark:3.4.3 \
        tail -f /dev/null
    
    if [ $? -eq 0 ]; then
        # Install Python packages
        print_status "Installing Python packages..."
        podman exec $CONTAINER_NAME pip install py4j pandas numpy matplotlib jupyterlab
        
        print_success "Container started successfully!"
        print_status "Access Spark UI at: http://localhost:4040"
        print_status "Access Spark Master UI at: http://localhost:8082"
        print_status "Access Jupyter at: http://localhost:8888"
    else
        print_error "Failed to start container"
        exit 1
    fi
}

# Function to stop the container
stop_container() {
    print_status "Stopping PySpark container..."
    
    if podman stop $CONTAINER_NAME; then
        podman rm $CONTAINER_NAME
        print_success "Container stopped and removed!"
    else
        print_warning "Container might not be running"
    fi
}

# Function to open shell in container
shell_container() {
    print_status "Opening shell in PySpark container..."
    
    if podman exec -it $CONTAINER_NAME /bin/bash; then
        print_success "Shell session ended"
    else
        print_error "Failed to open shell. Is the container running?"
        exit 1
    fi
}

# Function to start Jupyter in container
jupyter_container() {
    print_status "Starting Jupyter Lab in container..."
    
    podman exec -d $CONTAINER_NAME \
        python /.local/bin/jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' --notebook-dir=/workspace
    
    if [ $? -eq 0 ]; then
        print_success "Jupyter Lab started!"
        print_status "Access Jupyter at: http://localhost:8888"
    else
        print_error "Failed to start Jupyter Lab"
        exit 1
    fi
}

# Function to clean up all containers and images
clean_all() {
    print_status "Cleaning up containers and images..."
    
    # Stop and remove container
    podman stop $CONTAINER_NAME 2>/dev/null || true
    podman rm $CONTAINER_NAME 2>/dev/null || true
    
    # Remove image
    podman rmi $IMAGE_NAME 2>/dev/null || true
    
    print_success "Cleanup completed!"
}

# Function to show container status
status_container() {
    print_status "Container Status:"
    echo
    podman ps -a --filter name=$CONTAINER_NAME
    echo
    
    if podman ps --filter name=$CONTAINER_NAME --format "table {{.Names}}" | grep -q $CONTAINER_NAME; then
        print_success "Container is running"
        echo
        print_status "Available endpoints:"
        echo "  - Spark UI: http://localhost:4040"
        echo "  - Jupyter Lab: http://localhost:8888"
        echo "  - Spark Master UI: http://localhost:8080"
    else
        print_warning "Container is not running"
    fi
}

# Function to run a PySpark test
test_pyspark() {
    print_status "Running PySpark test..."
    
    podman exec -it $CONTAINER_NAME python -c "
import pyspark
from pyspark.sql import SparkSession

print(f'PySpark version: {pyspark.__version__}')

# Create Spark session
spark = SparkSession.builder.appName('TestApp').getOrCreate()
print(f'Spark session created: {spark.version}')

# Create a simple DataFrame
data = [('Alice', 25), ('Bob', 30), ('Charlie', 35)]
df = spark.createDataFrame(data, ['name', 'age'])

print('Sample DataFrame:')
df.show()

# Stop the session
spark.stop()
print('Test completed successfully!')
"
    
    if [ $? -eq 0 ]; then
        print_success "PySpark test passed!"
    else
        print_error "PySpark test failed!"
    fi
}

# Main script logic
case "$1" in
    build)
        build_container
        ;;
    run)
        run_container
        ;;
    stop)
        stop_container
        ;;
    shell)
        shell_container
        ;;
    jupyter)
        jupyter_container
        ;;
    clean)
        clean_all
        ;;
    status)
        status_container
        ;;
    test)
        test_pyspark
        ;;
    *)
        echo "Usage: $0 {build|run|stop|shell|jupyter|clean|status|test}"
        echo
        echo "Commands:"
        echo "  build   - Build the PySpark container"
        echo "  run     - Start the PySpark container"
        echo "  stop    - Stop and remove the container"
        echo "  shell   - Open bash shell in the container"
        echo "  jupyter - Start Jupyter Lab in the container"
        echo "  clean   - Remove all containers and images"
        echo "  status  - Show container status"
        echo "  test    - Run a PySpark test"
        exit 1
        ;;
esac
