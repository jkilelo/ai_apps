#!/bin/bash

echo "Starting Cloudera CDH and Spark services..."

# Source environment
source /opt/spark/conf/spark-env.sh

# Initialize and start HDFS
/opt/init-scripts/init-hdfs.sh

# Start YARN services
echo "Starting YARN services..."
yarn --daemon start resourcemanager
yarn --daemon start nodemanager

# Wait for YARN to be ready
sleep 10

# Initialize Hive metastore
echo "Initializing Hive metastore..."
schematool -dbType derby -initSchema || true

# Start Hive metastore
echo "Starting Hive metastore..."
hive --service metastore &

# Wait for metastore to be ready
sleep 10

# Start Hive server2
echo "Starting HiveServer2..."
hive --service hiveserver2 &

# Start Spark master
echo "Starting Spark master..."
$SPARK_HOME/sbin/start-master.sh

# Start Spark worker
echo "Starting Spark worker..."
$SPARK_HOME/sbin/start-worker.sh spark://localhost:7077

# Start Spark history server
echo "Starting Spark History Server..."
$SPARK_HOME/sbin/start-history-server.sh

# Start Jupyter Lab
echo "Starting Jupyter Lab..."
jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root --NotebookApp.token='' &

# Show service status
echo "Waiting for services to stabilize..."
sleep 15

echo "==================================="
echo "Services Status:"
echo "==================================="
jps

echo ""
echo "==================================="
echo "Web UIs Available:"
echo "==================================="
echo "HDFS NameNode:      http://localhost:9870"
echo "YARN ResourceMgr:   http://localhost:8088"
echo "Spark Master:       http://localhost:8080"
echo "Spark Worker:       http://localhost:8081"
echo "Spark History:      http://localhost:18080"
echo "Jupyter Lab:        http://localhost:8888"
echo "==================================="

# Keep container running
tail -f /dev/null