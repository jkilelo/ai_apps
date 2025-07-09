#!/bin/bash

# Big Data Environment Management Script
# Usage: ./bigdata_env.sh [command] [options]

set -e

# Configuration
COMPOSE_FILE="docker-compose.bigdata.yml"
PROJECT_NAME="bigdata-dev"
WORKSPACE_DIR="/var/www/ai_apps"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                    Big Data Environment                      ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
}

print_status() {
    echo -e "${CYAN}[INFO]${NC} $1"
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

print_section() {
    echo -e "${PURPLE}=== $1 ===${NC}"
}

# Function to check if podman-compose is available
check_dependencies() {
    if ! command -v podman-compose &> /dev/null; then
        print_error "podman-compose is required but not installed."
        print_status "Installing podman-compose..."
        pip3 install podman-compose || {
            print_error "Failed to install podman-compose"
            print_status "Please install manually: pip3 install podman-compose"
            exit 1
        }
    fi
}

# Function to start the entire environment
start_full() {
    print_header
    print_status "Starting complete Big Data environment..."
    
    check_dependencies
    
    # Create necessary directories
    mkdir -p data notebooks apps
    
    podman-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d
    
    if [ $? -eq 0 ]; then
        print_success "Big Data environment started successfully!"
        show_urls
    else
        print_error "Failed to start environment"
        exit 1
    fi
}

# Function to start core services only
start_core() {
    print_header
    print_status "Starting core Big Data services (Hadoop + Spark + Hive)..."
    
    check_dependencies
    mkdir -p data notebooks apps
    
    podman-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d \
        namenode datanode1 datanode2 resourcemanager nodemanager historyserver \
        postgres-hive hive-metastore hiveserver2 \
        spark-master spark-worker1
    
    if [ $? -eq 0 ]; then
        print_success "Core services started successfully!"
        show_core_urls
    else
        print_error "Failed to start core services"
        exit 1
    fi
}

# Function to start streaming services
start_streaming() {
    print_status "Starting streaming services (Kafka + Flink)..."
    
    podman-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d \
        zookeeper kafka kafka-ui flink-jobmanager flink-taskmanager
    
    if [ $? -eq 0 ]; then
        print_success "Streaming services started!"
        show_streaming_urls
    else
        print_error "Failed to start streaming services"
        exit 1
    fi
}

# Function to stop the environment
stop_env() {
    print_status "Stopping Big Data environment..."
    
    podman-compose -f $COMPOSE_FILE -p $PROJECT_NAME down
    
    print_success "Environment stopped successfully!"
}

# Function to show service URLs
show_urls() {
    print_section "Service URLs"
    echo -e "${GREEN}Hadoop Ecosystem:${NC}"
    echo "  • Namenode Web UI:       http://localhost:9870"
    echo "  • DataNode 1 Web UI:     http://localhost:9864"
    echo "  • DataNode 2 Web UI:     http://localhost:9865"
    echo "  • Resource Manager:      http://localhost:8088"
    echo "  • Node Manager:          http://localhost:8042"
    echo "  • History Server:        http://localhost:8188"
    echo
    echo -e "${GREEN}Spark:${NC}"
    echo "  • Spark Master UI:       http://localhost:8080"
    echo "  • Spark Worker 1:        http://localhost:8081"
    echo "  • Spark Worker 2:        http://localhost:8082"
    echo
    echo -e "${GREEN}Hive:${NC}"
    echo "  • HiveServer2 Web UI:    http://localhost:10002"
    echo "  • Hive Metastore:        thrift://localhost:9083"
    echo "  • HiveServer2 Thrift:    jdbc:hive2://localhost:10000"
    echo
    echo -e "${GREEN}Development Tools:${NC}"
    echo "  • Jupyter Lab:           http://localhost:8889"
    echo "  • Hue (SQL Editor):      http://localhost:8888"
    echo
    echo -e "${GREEN}Streaming & Messaging:${NC}"
    echo "  • Kafka UI:              http://localhost:8090"
    echo "  • Flink Dashboard:       http://localhost:8091"
    echo
    echo -e "${GREEN}Storage:${NC}"
    echo "  • MinIO Console:         http://localhost:9001"
    echo "  • MinIO API:             http://localhost:9000"
    echo
}

show_core_urls() {
    print_section "Core Service URLs"
    echo -e "${GREEN}Hadoop:${NC}"
    echo "  • Namenode Web UI:       http://localhost:9870"
    echo "  • Resource Manager:      http://localhost:8088"
    echo
    echo -e "${GREEN}Spark:${NC}"
    echo "  • Spark Master UI:       http://localhost:8080"
    echo "  • Spark Worker:          http://localhost:8081"
    echo
    echo -e "${GREEN}Hive:${NC}"
    echo "  • HiveServer2 Web UI:    http://localhost:10002"
    echo "  • Beeline connection:    beeline -u jdbc:hive2://localhost:10000"
    echo
}

show_streaming_urls() {
    print_section "Streaming Service URLs"
    echo -e "${GREEN}Kafka:${NC}"
    echo "  • Kafka UI:              http://localhost:8090"
    echo
    echo -e "${GREEN}Flink:${NC}"
    echo "  • Flink Dashboard:       http://localhost:8091"
    echo
}

# Function to show status
show_status() {
    print_header
    print_section "Container Status"
    
    podman-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps
    
    echo
    print_section "Resource Usage"
    podman stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" \
        $(podman-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps -q 2>/dev/null || echo "")
}

# Function to run beeline
run_beeline() {
    print_status "Connecting to HiveServer2 with Beeline..."
    
    podman exec -it ${PROJECT_NAME}_hiveserver2_1 beeline -u jdbc:hive2://localhost:10000
}

# Function to run hdfs commands
run_hdfs() {
    if [ $# -eq 0 ]; then
        print_error "Please provide HDFS command. Example: $0 hdfs dfs -ls /"
        exit 1
    fi
    
    print_status "Running HDFS command: $*"
    podman exec -it ${PROJECT_NAME}_namenode_1 hdfs "$@"
}

# Function to run spark-shell
run_spark_shell() {
    print_status "Starting Spark Shell..."
    
    podman exec -it ${PROJECT_NAME}_spark-master_1 spark-shell \
        --master spark://spark-master:7077 \
        --conf spark.sql.warehouse.dir=hdfs://namenode:8020/user/hive/warehouse
}

# Function to clean up everything
clean_all() {
    print_warning "This will remove all containers and volumes. Are you sure? (y/N)"
    read -r confirm
    
    if [[ $confirm =~ ^[Yy]$ ]]; then
        print_status "Cleaning up Big Data environment..."
        
        podman-compose -f $COMPOSE_FILE -p $PROJECT_NAME down -v
        podman system prune -f
        
        print_success "Environment cleaned up!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to show logs
show_logs() {
    if [ $# -eq 0 ]; then
        print_status "Showing logs for all services..."
        podman-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f
    else
        print_status "Showing logs for: $1"
        podman-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f "$1"
    fi
}

# Function to scale services
scale_service() {
    if [ $# -ne 2 ]; then
        print_error "Usage: $0 scale <service> <count>"
        print_status "Example: $0 scale spark-worker 3"
        exit 1
    fi
    
    local service=$1
    local count=$2
    
    print_status "Scaling $service to $count instances..."
    podman-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d --scale $service=$count
}

# Function to create sample data
create_sample_data() {
    print_status "Creating sample data in HDFS and Hive..."
    
    # Wait for services to be ready
    sleep 30
    
    # Create HDFS directories
    podman exec ${PROJECT_NAME}_namenode_1 hdfs dfs -mkdir -p /user/hive/warehouse
    podman exec ${PROJECT_NAME}_namenode_1 hdfs dfs -mkdir -p /tmp
    podman exec ${PROJECT_NAME}_namenode_1 hdfs dfs -chmod 777 /tmp
    
    # Create sample Hive table
    podman exec ${PROJECT_NAME}_hiveserver2_1 hive -e "
        CREATE DATABASE IF NOT EXISTS sample_db;
        USE sample_db;
        
        CREATE TABLE IF NOT EXISTS employees (
            id INT,
            name STRING,
            department STRING,
            salary DOUBLE
        ) STORED AS PARQUET;
        
        INSERT INTO employees VALUES
        (1, 'Alice', 'Engineering', 75000),
        (2, 'Bob', 'Sales', 65000),
        (3, 'Charlie', 'Engineering', 85000),
        (4, 'Diana', 'Marketing', 60000),
        (5, 'Eve', 'Engineering', 90000);
    "
    
    print_success "Sample data created in Hive table: sample_db.employees"
}

# Main script logic
case "$1" in
    start|up)
        start_full
        ;;
    start-core|core)
        start_core
        ;;
    start-streaming|streaming)
        start_streaming
        ;;
    stop|down)
        stop_env
        ;;
    restart)
        stop_env
        sleep 5
        start_full
        ;;
    status|ps)
        show_status
        ;;
    urls|url)
        show_urls
        ;;
    beeline)
        run_beeline
        ;;
    hdfs)
        shift
        run_hdfs "$@"
        ;;
    spark-shell|spark)
        run_spark_shell
        ;;
    logs)
        shift
        show_logs "$@"
        ;;
    scale)
        shift
        scale_service "$@"
        ;;
    sample-data|sample)
        create_sample_data
        ;;
    clean)
        clean_all
        ;;
    *)
        echo "Big Data Environment Manager"
        echo
        echo "Usage: $0 [command] [options]"
        echo
        echo "Commands:"
        echo "  start, up              Start complete Big Data environment"
        echo "  start-core, core       Start core services (Hadoop + Spark + Hive)"
        echo "  start-streaming        Start streaming services (Kafka + Flink)"
        echo "  stop, down             Stop all services"
        echo "  restart                Restart all services"
        echo "  status, ps             Show container status"
        echo "  urls, url              Show service URLs"
        echo "  beeline                Connect to HiveServer2 with Beeline"
        echo "  hdfs <command>         Run HDFS commands"
        echo "  spark-shell, spark     Start Spark Shell"
        echo "  logs [service]         Show logs for all or specific service"
        echo "  scale <service> <count> Scale a service to N instances"
        echo "  sample-data, sample    Create sample data in Hive"
        echo "  clean                  Remove all containers and volumes"
        echo
        echo "Examples:"
        echo "  $0 start               # Start full environment"
        echo "  $0 core                # Start only core services"
        echo "  $0 hdfs dfs -ls /      # List HDFS root directory"
        echo "  $0 logs namenode       # Show namenode logs"
        echo "  $0 scale spark-worker 3 # Scale to 3 Spark workers"
        exit 1
        ;;
esac
