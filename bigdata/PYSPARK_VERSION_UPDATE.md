# PySpark Version Standardization to 3.3.2

## Summary of Changes

All PySpark installations in the bigdata directory have been standardized to **version 3.3.2** to match the Cloudera CDH 7.1.9 setup.

## Files Updated

### 1. Main PySpark Docker Configuration
- **File**: `docker/Dockerfile.pyspark`
- **Changes**: 
  - Updated from PySpark 3.4.3 to 3.3.2
  - Changed base image from Python 3.12 to Python 3.11 for better compatibility
  - Updated py4j version to 0.10.9.5 (matching Spark 3.3.2)

### 2. Requirements Files
- **File**: `requirements_pyspark.txt`
- **Changes**: Updated PySpark version from 3.4.3 to 3.3.2

- **File**: `data_generator/requirements.txt`
- **Changes**: 
  - Updated PySpark from 3.5.0 to 3.3.2
  - Adjusted pandas to 2.0.3 (compatible version)
  - Adjusted pyarrow to 12.0.1 (compatible version)

### 3. Simple PySpark Dockerfile
- **File**: `docker/Dockerfile.pyspark.simple`
- **Changes**: Complete rewrite to use PySpark 3.3.2 with minimal dependencies

### 4. Docker Compose
- **File**: `docker/docker-compose.pyspark.yml`
- **Changes**: Added comment noting PySpark 3.3.2 usage

## Compatibility Notes

### Python Version
- Using Python 3.11 for better compatibility with Spark 3.3.2
- All containers now use consistent Python version

### Library Versions
Adjusted to ensure compatibility with PySpark 3.3.2:
- pandas: 2.0.3
- numpy: 1.24.3
- pyarrow: 12.0.1
- py4j: 0.10.9.5

## Rebuilding Containers

To rebuild all containers with the new PySpark version:

```bash
# Option 1: Use the rebuild script
cd bigdata/scripts
./rebuild-pyspark-3.3.2.sh

# Option 2: Manual rebuild
cd bigdata/docker
docker-compose -f docker-compose.pyspark.yml down
docker-compose -f docker-compose.pyspark.yml build
docker-compose -f docker-compose.pyspark.yml up -d
```

## Verification

Verify the PySpark version in any container:

```bash
# Check PySpark version
docker exec pyspark-app python -c "import pyspark; print(pyspark.__version__)"

# Or for Cloudera container
docker exec cdh7-spark3 python -c "import pyspark; print(pyspark.__version__)"
```

Expected output: `3.3.2`

## Benefits of Standardization

1. **Consistency**: All environments use the same PySpark version
2. **Compatibility**: Matches Cloudera CDH 7.1.9 requirements
3. **Stability**: Version 3.3.2 is a stable, well-tested release
4. **Integration**: Better integration with Hadoop 3.x ecosystem

## Migration Notes

If you have existing code or notebooks:
- Most PySpark 3.4/3.5 code will work with 3.3.2
- Some newer features from 3.4+ may not be available
- Check Spark 3.3.2 documentation for specific API differences

## Rollback

If you need to rollback to previous versions, the original files are in git history.

## Next Steps

1. Rebuild all containers using the script
2. Test your existing PySpark applications
3. Update any code that relies on PySpark 3.4+ specific features