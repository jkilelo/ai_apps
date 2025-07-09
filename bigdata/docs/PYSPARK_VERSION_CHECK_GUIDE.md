# PySpark Version Check Guide

This guide provides comprehensive methods to check PySpark version across different environments.

## Quick Reference

### Command Line Methods

```bash
# Method 1: Direct Python command
python -c "import pyspark; print(pyspark.__version__)"

# Method 2: Using pip
pip show pyspark | grep Version

# Method 3: Using spark-submit
spark-submit --version

# Method 4: Using pyspark shell
pyspark --version

# Method 5: In conda environment
conda list pyspark
```

### Python/PySpark Environment

```python
# Method 1: Direct import
import pyspark
print(pyspark.__version__)

# Method 2: Using SparkSession
from pyspark.sql import SparkSession
spark = SparkSession.builder.getOrCreate()
print(spark.version)

# Method 3: Using SparkContext
from pyspark import SparkContext
sc = SparkContext.getOrCreate()
print(sc.version)
```

### Docker Container Methods

```bash
# Check in running container
docker exec <container_name> python -c "import pyspark; print(pyspark.__version__)"

# Using pip in container
docker exec <container_name> pip show pyspark

# Using spark-submit in container
docker exec <container_name> spark-submit --version

# Interactive check
docker exec -it <container_name> pyspark
>>> spark.version
```

## Available Scripts

1. **Python Script**: `/var/www/ai_apps/bigdata/scripts/check_pyspark_version.py`
   - Comprehensive version checking with 10 different methods
   - Run: `python check_pyspark_version.py`

2. **Shell Script**: `/var/www/ai_apps/bigdata/scripts/check_pyspark_version.sh`
   - Command-line version checking methods
   - Run: `./check_pyspark_version.sh`

3. **Jupyter Notebook**: `/var/www/ai_apps/bigdata/notebooks/check_pyspark_version.ipynb`
   - Interactive version checking with detailed explanations
   - Includes compatibility checks and system information

## Environment Variables

Important environment variables for PySpark:
- `SPARK_HOME`: Path to Spark installation
- `PYSPARK_PYTHON`: Python executable for PySpark
- `PYSPARK_DRIVER_PYTHON`: Python executable for driver
- `PYTHONPATH`: Should include PySpark libraries

## Version Compatibility Matrix

| PySpark Version | Compatible Python Versions |
|----------------|---------------------------|
| 3.5.x          | 3.10, 3.11               |
| 3.4.x          | 3.8, 3.9, 3.10, 3.11     |
| 3.3.x          | 3.7, 3.8, 3.9, 3.10      |
| 3.2.x          | 3.6, 3.7, 3.8, 3.9       |
| 3.1.x          | 3.6, 3.7, 3.8, 3.9       |
| 3.0.x          | 3.6, 3.7, 3.8            |
| 2.4.x          | 2.7, 3.4, 3.5, 3.6, 3.7  |

## Troubleshooting

### PySpark Not Found
If PySpark is not found, check:
1. Is PySpark installed? `pip list | grep pyspark`
2. Is PYTHONPATH set correctly?
3. Is SPARK_HOME set?
4. Are you in the correct virtual environment?

### Version Mismatch
If you see different versions:
1. Check which Python executable is being used
2. Verify virtual environment activation
3. Check for multiple PySpark installations
4. Ensure Docker container has correct image

### Docker-specific Issues
1. Container not running: `docker ps`
2. Wrong container name: List containers with `docker ps -a`
3. PySpark not installed in image: Check Dockerfile

## Best Practices

1. **Always verify version** before running production workloads
2. **Match Python and PySpark versions** according to compatibility matrix
3. **Use virtual environments** to isolate PySpark installations
4. **Document versions** in your project requirements
5. **Test thoroughly** when upgrading versions