# Cloudera CDH 7.1.9 with Spark 3.3.2 Container Setup

This setup provides a fully integrated big data environment with Cloudera CDH 7.1.9 and Apache Spark 3.3.2 running in a Podman/Docker container.

## Components Included

- **Cloudera CDH 7.1.9**
  - HDFS (Hadoop Distributed File System)
  - YARN (Resource Manager)
  - Hive 3.1.0
  - Zookeeper
  
- **Apache Spark 3.3.2**
  - Spark Core
  - Spark SQL
  - PySpark
  - Spark Streaming
  
- **Additional Tools**
  - Jupyter Lab
  - Python 3 with data science libraries
  - Faker for synthetic data generation

## Prerequisites

- Podman or Docker installed
- At least 16GB RAM (container limited to 16GB)
- 20GB+ free disk space
- Linux/macOS (Windows with WSL2)

## Quick Start

1. **Build and Run**
   ```bash
   cd bigdata/cloudera
   ./build-and-run.sh
   ```

2. **Verify Installation**
   ```bash
   ./test-installation.sh
   ```

## Accessing Services

### Web UIs

| Service | URL | Description |
|---------|-----|-------------|
| HDFS NameNode | http://localhost:9870 | HDFS management and monitoring |
| YARN ResourceManager | http://localhost:8088 | Cluster resource management |
| Spark Master | http://localhost:8080 | Spark cluster status |
| Spark Worker | http://localhost:8081 | Spark worker status |
| Spark History | http://localhost:18080 | Completed Spark applications |
| Jupyter Lab | http://localhost:8888 | Interactive notebooks |

### Command Line Access

```bash
# Access container shell
podman exec -it cdh7-spark3 /bin/bash

# Run PySpark shell
podman exec -it cdh7-spark3 pyspark

# Run Spark Shell (Scala)
podman exec -it cdh7-spark3 spark-shell

# Run Spark SQL CLI
podman exec -it cdh7-spark3 spark-sql

# Submit a Spark job
podman exec -it cdh7-spark3 spark-submit /workspace/your_job.py
```

## Working with Data

### HDFS Commands

```bash
# List files
podman exec cdh7-spark3 hdfs dfs -ls /

# Create directory
podman exec cdh7-spark3 hdfs dfs -mkdir -p /data/input

# Upload file
podman exec cdh7-spark3 hdfs dfs -put /workspace/data.csv /data/input/

# Download file
podman exec cdh7-spark3 hdfs dfs -get /data/output/results.csv /workspace/

# View file content
podman exec cdh7-spark3 hdfs dfs -cat /data/file.txt
```

### Hive Commands

```bash
# Access Hive CLI
podman exec -it cdh7-spark3 hive

# Or run Hive commands directly
podman exec cdh7-spark3 hive -e "SHOW DATABASES;"
podman exec cdh7-spark3 hive -e "CREATE DATABASE IF NOT EXISTS mydb;"
```

### PySpark Example

```python
# Create a simple PySpark application
from pyspark.sql import SparkSession

# Initialize Spark with Hive support
spark = SparkSession.builder \
    .appName("CDH Spark Example") \
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    .enableHiveSupport() \
    .getOrCreate()

# Read data from HDFS
df = spark.read.csv("hdfs://localhost:9000/data/input/data.csv", header=True)

# Process data
result = df.groupBy("category").count()

# Save to Hive table
result.write.mode("overwrite").saveAsTable("mydb.results")

# Save to HDFS
result.write.mode("overwrite").parquet("hdfs://localhost:9000/data/output/results")

spark.stop()
```

## Configuration Files

Configuration files are located in:
- Hadoop: `/etc/hadoop/conf/`
- Spark: `/opt/spark/conf/`
- Hive: `/etc/hive/conf/`

### Key Configuration Parameters

**Spark Memory Settings** (spark-defaults.conf):
- `spark.driver.memory`: 4g
- `spark.executor.memory`: 4g
- `spark.executor.cores`: 2

**YARN Resources** (yarn-site.xml):
- `yarn.nodemanager.resource.memory-mb`: 8192
- `yarn.nodemanager.resource.cpu-vcores`: 4

## Synthetic Data Generation

Use the included data generators:

```bash
# Copy data generator to container
podman cp ../data_generator/synthetic_data_generator.py cdh7-spark3:/workspace/

# Run data generation
podman exec -it cdh7-spark3 spark-submit /workspace/synthetic_data_generator.py
```

## Monitoring and Logs

### View Service Logs

```bash
# HDFS logs
podman exec cdh7-spark3 tail -f /var/log/hadoop-hdfs/*.log

# YARN logs
podman exec cdh7-spark3 tail -f /var/log/hadoop-yarn/*.log

# Spark logs
podman exec cdh7-spark3 tail -f /opt/spark/logs/*.out

# Container logs
podman logs -f cdh7-spark3
```

### Check Service Status

```bash
# List Java processes
podman exec cdh7-spark3 jps

# Check HDFS health
podman exec cdh7-spark3 hdfs dfsadmin -report

# Check YARN nodes
podman exec cdh7-spark3 yarn node -list
```

## Troubleshooting

### Container Won't Start

```bash
# Check container logs
podman logs cdh7-spark3

# Verify port availability
ss -tulpn | grep -E '(9870|8088|8080|8888)'

# Increase system limits (if needed)
sudo sysctl -w vm.max_map_count=262144
```

### Services Not Starting

```bash
# Restart specific service
podman exec cdh7-spark3 hdfs --daemon stop namenode
podman exec cdh7-spark3 hdfs --daemon start namenode

# Check service logs
podman exec cdh7-spark3 cat /opt/spark/logs/spark-*.out
```

### Out of Memory

```bash
# Increase container memory limit
podman update cdh7-spark3 --memory="20g" --memory-swap="20g"

# Or modify docker-compose.yml and recreate container
```

## Performance Tuning

### Spark Optimization

```python
# Optimal Spark configuration
spark = SparkSession.builder \
    .appName("Optimized App") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()
```

### YARN Queue Configuration

Configure YARN queues for better resource allocation:
```xml
<!-- capacity-scheduler.xml -->
<property>
  <name>yarn.scheduler.capacity.root.queues</name>
  <value>default,spark,batch</value>
</property>
```

## Backup and Restore

### Backup HDFS Data

```bash
# Create backup
podman exec cdh7-spark3 hdfs dfs -cp /data /backup/data_$(date +%Y%m%d)

# Export to local filesystem
podman exec cdh7-spark3 hdfs dfs -copyToLocal /data /workspace/backup/
```

### Backup Hive Metadata

```bash
# Export Hive metadata
podman exec cdh7-spark3 mysqldump -h mysql-metastore -u hive -p metastore > hive_metadata_backup.sql
```

## Stopping and Cleanup

```bash
# Stop container
podman-compose down

# Remove container and volumes (WARNING: deletes all data)
podman-compose down -v

# Clean up images
podman rmi cdh7-spark3
```

## Known Issues

1. **First startup takes time**: Services need 1-2 minutes to fully initialize
2. **Port conflicts**: Ensure ports 9870, 8088, 8080, 8888 are available
3. **Memory requirements**: Container needs at least 8GB RAM to run smoothly

## Support

For issues or questions:
1. Check container logs: `podman logs cdh7-spark3`
2. Verify service status: `./test-installation.sh`
3. Review configuration files in the container