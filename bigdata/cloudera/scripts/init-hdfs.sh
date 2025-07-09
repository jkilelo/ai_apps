#!/bin/bash

echo "Initializing HDFS..."

# Format namenode if not already formatted
if [ ! -d "/data/hdfs/namenode/current" ]; then
    echo "Formatting HDFS namenode..."
    hdfs namenode -format -force -nonInteractive
fi

# Start HDFS services
echo "Starting HDFS services..."
hdfs --daemon start namenode
hdfs --daemon start datanode

# Wait for HDFS to be ready
sleep 10

# Create necessary HDFS directories
echo "Creating HDFS directories..."
hdfs dfs -mkdir -p /user
hdfs dfs -mkdir -p /user/hive
hdfs dfs -mkdir -p /user/hive/warehouse
hdfs dfs -mkdir -p /user/spark
hdfs dfs -mkdir -p /spark-events
hdfs dfs -mkdir -p /tmp
hdfs dfs -mkdir -p /tmp/hive

# Set permissions
hdfs dfs -chmod 777 /tmp
hdfs dfs -chmod 777 /tmp/hive
hdfs dfs -chmod 777 /user/hive/warehouse
hdfs dfs -chmod 777 /spark-events

echo "HDFS initialization complete!"