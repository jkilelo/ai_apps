# 🚀 Big Data Development Environment

## 📋 Complete Architecture

This setup provides a comprehensive big data development environment with the following components:

### 🏗️ Core Infrastructure
- **Hadoop HDFS**: Distributed file system (NameNode + 2 DataNodes)
- **YARN**: Resource management (ResourceManager + NodeManager)
- **History Server**: Job history tracking

### 🔥 Processing Engines
- **Apache Spark**: Distributed computing (Master + 2 Workers)
- **Apache Hive**: Data warehouse (HiveServer2 + Metastore)
- **Apache Flink**: Stream processing

### 📊 Data Storage
- **HDFS**: Distributed storage
- **MinIO**: S3-compatible object storage
- **PostgreSQL**: Hive Metastore database

### 🌊 Streaming & Messaging
- **Apache Kafka**: Message broker
- **Zookeeper**: Coordination service
- **Kafka UI**: Web interface for Kafka

### 🛠️ Development Tools
- **Jupyter Lab**: Interactive development
- **Hue**: SQL editor and HDFS browser
- **Beeline**: Hive CLI client

## 🚀 Quick Start

### 1. Install Dependencies
```bash
# Install podman-compose
pip3 install podman-compose

# Make scripts executable
chmod +x bigdata_env.sh
```

### 2. Start Environment

#### Option A: Core Services Only (Recommended for beginners)
```bash
./bigdata_env.sh core
```

#### Option B: Complete Environment
```bash
./bigdata_env.sh start
```

### 3. Access Services

After startup, access the web interfaces:

| Service | URL | Description |
|---------|-----|-------------|
| **Hadoop NameNode** | http://localhost:9870 | HDFS management |
| **YARN ResourceManager** | http://localhost:8088 | Job tracking |
| **Spark Master** | http://localhost:8080 | Spark cluster |
| **HiveServer2** | http://localhost:10002 | Hive web UI |
| **Jupyter Lab** | http://localhost:8889 | Development environment |
| **Hue** | http://localhost:8888 | SQL editor & file browser |
| **Kafka UI** | http://localhost:8090 | Message broker UI |
| **Flink Dashboard** | http://localhost:8091 | Stream processing |
| **MinIO Console** | http://localhost:9001 | Object storage |

## 📖 Usage Examples

### HDFS Operations
```bash
# List HDFS directories
./bigdata_env.sh hdfs dfs -ls /

# Create directory
./bigdata_env.sh hdfs dfs -mkdir /user/data

# Upload file
./bigdata_env.sh hdfs dfs -put local_file.txt /user/data/

# Download file
./bigdata_env.sh hdfs dfs -get /user/data/file.txt ./
```

### Hive Operations
```bash
# Connect with Beeline
./bigdata_env.sh beeline

# In Beeline:
CREATE DATABASE my_db;
USE my_db;
CREATE TABLE employees (id INT, name STRING, salary DOUBLE);
INSERT INTO employees VALUES (1, 'Alice', 75000);
SELECT * FROM employees;
```

### Spark Operations
```bash
# Start Spark Shell
./bigdata_env.sh spark

# In Spark Shell:
val df = spark.sql("SELECT * FROM my_db.employees")
df.show()
```

### Python Development
```bash
# Run demo script
podman exec -it bigdata-dev_spark-master_1 python /workspace/bigdata_demo.py

# Or use Jupyter Lab at http://localhost:8889
```

## 🔧 Management Commands

### Environment Control
```bash
./bigdata_env.sh start          # Start all services
./bigdata_env.sh core           # Start core services only
./bigdata_env.sh streaming      # Start streaming services
./bigdata_env.sh stop           # Stop all services
./bigdata_env.sh restart        # Restart all services
./bigdata_env.sh status         # Show container status
```

### Service Management
```bash
./bigdata_env.sh logs           # Show all logs
./bigdata_env.sh logs namenode  # Show specific service logs
./bigdata_env.sh scale spark-worker 3  # Scale Spark workers
```

### Data Operations
```bash
./bigdata_env.sh sample-data    # Create sample Hive tables
./bigdata_env.sh hdfs <cmd>     # Run HDFS commands
./bigdata_env.sh beeline        # Connect to HiveServer2
./bigdata_env.sh spark          # Start Spark shell
```

### Cleanup
```bash
./bigdata_env.sh clean          # Remove all containers and volumes
```

## 📊 Sample Data & Examples

### 1. Create Sample Data
```bash
./bigdata_env.sh sample-data
```

This creates a sample database with employee data in Hive.

### 2. Run Python Demo
```bash
podman exec -it bigdata-dev_spark-master_1 python /workspace/bigdata_demo.py
```

### 3. Jupyter Notebooks
- Access Jupyter at http://localhost:8889
- Examples available in `/notebooks` directory
- Pre-configured with Spark and Hive connections

## 🎯 Development Workflows

### 1. Data Engineering Pipeline
1. **Ingest**: Load data into HDFS or object storage
2. **Process**: Use Spark for ETL operations
3. **Store**: Save processed data to Hive tables
4. **Analyze**: Query with SQL or run ML models

### 2. Streaming Pipeline
1. **Produce**: Send data to Kafka topics
2. **Process**: Use Spark Streaming or Flink
3. **Store**: Write results to HDFS/Hive
4. **Monitor**: Use Kafka UI and Flink Dashboard

### 3. Analytics Workflow
1. **Explore**: Use Jupyter for data exploration
2. **Model**: Develop ML models with Spark MLlib
3. **Deploy**: Save models and create batch jobs
4. **Visualize**: Use built-in UIs or external tools

## 🔍 Troubleshooting

### Common Issues

1. **Port Conflicts**
   - Check for conflicting services: `podman ps`
   - Modify ports in `docker-compose.bigdata.yml`

2. **Memory Issues**
   - Reduce worker memory in compose file
   - Use core services only: `./bigdata_env.sh core`

3. **Storage Issues**
   - Check available disk space
   - Clean up: `./bigdata_env.sh clean`

4. **Connection Issues**
   - Wait for services to fully start (30-60 seconds)
   - Check logs: `./bigdata_env.sh logs <service>`

### Performance Tuning

1. **Resource Allocation**
   - Adjust worker memory and cores in compose file
   - Scale workers: `./bigdata_env.sh scale spark-worker 3`

2. **Storage Optimization**
   - Use external volumes for production
   - Configure appropriate replication factors

3. **Network Optimization**
   - Use dedicated network for production
   - Configure appropriate port mappings

## 🛡️ Security Considerations

### Development Environment
- Default passwords are used for simplicity
- All services run with minimal security
- Suitable for development and learning only

### Production Deployment
- Change all default passwords
- Enable authentication and authorization
- Use proper network segmentation
- Configure SSL/TLS encryption
- Implement proper backup strategies

## 📚 Learning Resources

### Official Documentation
- [Apache Hadoop](https://hadoop.apache.org/docs/)
- [Apache Spark](https://spark.apache.org/docs/)
- [Apache Hive](https://hive.apache.org/documentation.html)
- [Apache Kafka](https://kafka.apache.org/documentation/)
- [Apache Flink](https://flink.apache.org/documentation.html)

### Tutorials & Examples
- Check `/notebooks` directory for Jupyter examples
- Run `bigdata_demo.py` for comprehensive examples
- Use Hue web interface for interactive SQL queries

## 🤝 Contributing

Feel free to extend this environment with additional services:
- Add more Spark workers
- Include additional databases (Cassandra, MongoDB)
- Add monitoring tools (Prometheus, Grafana)
- Include data governance tools (Apache Atlas)

## 📄 License

This big data environment setup is provided as-is for educational and development purposes.
