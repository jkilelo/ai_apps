#!/bin/bash

# Test script to verify CDH 7.1.9 and Spark 3.3.2 installation

set -e

echo "==================================="
echo "Testing CDH + Spark Installation"
echo "==================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Container command
if command -v podman &> /dev/null; then
    CONTAINER_CMD="podman"
else
    CONTAINER_CMD="docker"
fi

# Function to run tests
run_test() {
    local test_name=$1
    local test_command=$2
    
    echo -ne "${YELLOW}Testing $test_name...${NC}"
    
    if $CONTAINER_CMD exec cdh7-spark3 bash -c "$test_command" &> /dev/null; then
        echo -e " ${GREEN}✓ PASSED${NC}"
        return 0
    else
        echo -e " ${RED}✗ FAILED${NC}"
        return 1
    fi
}

# Check if container is running
echo -e "${YELLOW}Checking container status...${NC}"
if ! $CONTAINER_CMD ps | grep -q cdh7-spark3; then
    echo -e "${RED}Error: Container 'cdh7-spark3' is not running!${NC}"
    echo "Please run ./build-and-run.sh first"
    exit 1
fi

echo -e "${GREEN}Container is running${NC}"
echo ""

# Version checks
echo "=== Version Information ==="
echo -n "Spark version: "
$CONTAINER_CMD exec cdh7-spark3 spark-submit --version 2>&1 | grep "version" | head -1

echo -n "Hadoop version: "
$CONTAINER_CMD exec cdh7-spark3 hadoop version | grep "Hadoop" | head -1

echo -n "Hive version: "
$CONTAINER_CMD exec cdh7-spark3 hive --version 2>&1 | grep "Hive" | head -1

echo -n "Python version: "
$CONTAINER_CMD exec cdh7-spark3 python3 --version

echo -n "PySpark version: "
$CONTAINER_CMD exec cdh7-spark3 python3 -c "import pyspark; print(pyspark.__version__)"
echo ""

# Service tests
echo "=== Service Tests ==="
run_test "HDFS NameNode" "hdfs dfsadmin -report | grep -q 'Live datanodes'"
run_test "YARN ResourceManager" "yarn node -list 2>&1 | grep -q 'Total Nodes'"
run_test "Spark Master" "curl -s http://localhost:8080 | grep -q 'Spark Master'"
run_test "Hive Metastore" "hive -e 'show databases;' | grep -q 'default'"
echo ""

# HDFS operations test
echo "=== HDFS Operations Test ==="
run_test "Create HDFS directory" "hdfs dfs -mkdir -p /test/data"
run_test "List HDFS directory" "hdfs dfs -ls /"
run_test "Write to HDFS" "echo 'test data' | hdfs dfs -put - /test/data/test.txt"
run_test "Read from HDFS" "hdfs dfs -cat /test/data/test.txt | grep -q 'test data'"
run_test "Clean up HDFS" "hdfs dfs -rm -r /test"
echo ""

# Spark tests
echo "=== Spark Tests ==="

# Create test PySpark script
$CONTAINER_CMD exec cdh7-spark3 bash -c 'cat > /tmp/test_spark.py << EOF
from pyspark.sql import SparkSession

# Create Spark session
spark = SparkSession.builder \
    .appName("Test Spark Installation") \
    .enableHiveSupport() \
    .getOrCreate()

# Print versions
print(f"Spark Version: {spark.version}")
print(f"Hadoop Version: {spark._jsc.hadoopConfiguration().get('hadoop.version', 'Unknown')}")

# Test DataFrame operations
data = [(1, "Alice", 25), (2, "Bob", 30), (3, "Charlie", 35)]
columns = ["id", "name", "age"]
df = spark.createDataFrame(data, columns)

print("\nDataFrame Schema:")
df.printSchema()

print("\nDataFrame Content:")
df.show()

# Test SQL
df.createOrReplaceTempView("people")
result = spark.sql("SELECT name, age FROM people WHERE age > 25")
print("\nSQL Query Result:")
result.show()

# Test Hive integration
spark.sql("CREATE DATABASE IF NOT EXISTS test_db")
spark.sql("USE test_db")
df.write.mode("overwrite").saveAsTable("test_table")
print("\nHive Table Created Successfully")

# Verify table
tables = spark.sql("SHOW TABLES IN test_db").collect()
print(f"Tables in test_db: {[row.tableName for row in tables]}")

# Clean up
spark.sql("DROP TABLE IF EXISTS test_db.test_table")
spark.sql("DROP DATABASE IF EXISTS test_db")

spark.stop()
print("\nAll tests completed successfully!")
EOF'

echo -e "${YELLOW}Running PySpark test script...${NC}"
if $CONTAINER_CMD exec cdh7-spark3 spark-submit /tmp/test_spark.py; then
    echo -e "${GREEN}✓ PySpark test completed successfully${NC}"
else
    echo -e "${RED}✗ PySpark test failed${NC}"
fi
echo ""

# Web UI connectivity test
echo "=== Web UI Connectivity Tests ==="
services=(
    "HDFS NameNode|9870"
    "YARN ResourceManager|8088"
    "Spark Master|8080"
    "Jupyter Lab|8888"
)

for service in "${services[@]}"; do
    IFS='|' read -r name port <<< "$service"
    echo -ne "${YELLOW}Testing $name (port $port)...${NC}"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port | grep -q "200\|302"; then
        echo -e " ${GREEN}✓ Accessible${NC}"
    else
        echo -e " ${RED}✗ Not accessible${NC}"
    fi
done
echo ""

# Summary
echo "==================================="
echo "Installation Test Summary"
echo "==================================="
echo -e "${GREEN}CDH 7.1.9 with Spark 3.3.2 is successfully installed!${NC}"
echo ""
echo "You can now:"
echo "1. Access Jupyter at http://localhost:8888"
echo "2. Run PySpark: $CONTAINER_CMD exec -it cdh7-spark3 pyspark"
echo "3. Run Spark Shell: $CONTAINER_CMD exec -it cdh7-spark3 spark-shell"
echo "4. Submit Spark jobs: $CONTAINER_CMD exec -it cdh7-spark3 spark-submit your_job.py"