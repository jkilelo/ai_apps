#!/usr/bin/env bash

# Spark environment configuration

# Java
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk

# Hadoop configuration
export HADOOP_CONF_DIR=/etc/hadoop/conf
export YARN_CONF_DIR=/etc/hadoop/conf
export HADOOP_HOME=/opt/cloudera/parcels/CDH

# Spark configuration
export SPARK_HOME=/opt/spark
export SPARK_CONF_DIR=$SPARK_HOME/conf
export PYSPARK_PYTHON=/usr/bin/python3.9
export PYSPARK_DRIVER_PYTHON=/usr/bin/python3.9

# Memory settings
export SPARK_DRIVER_MEMORY=4g
export SPARK_EXECUTOR_MEMORY=4g

# Master/Worker settings
export SPARK_MASTER_HOST=localhost
export SPARK_MASTER_PORT=7077
export SPARK_MASTER_WEBUI_PORT=8080
export SPARK_WORKER_CORES=4
export SPARK_WORKER_MEMORY=8g
export SPARK_WORKER_PORT=7078
export SPARK_WORKER_WEBUI_PORT=8081

# History Server
export SPARK_HISTORY_OPTS="-Dspark.history.fs.logDirectory=hdfs://localhost:9000/spark-events"

# Class path for CDH integration
export SPARK_DIST_CLASSPATH=$(hadoop classpath)

# Additional JARs
export SPARK_CLASSPATH=$SPARK_CLASSPATH:/opt/cloudera/parcels/CDH/lib/hive/lib/*