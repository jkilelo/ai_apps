# Python Version Update to 3.9.20

## Overview

All Python installations in the bigdata directory have been updated to **Python 3.9.20** for consistency and compatibility with PySpark 3.3.2.

## Why Python 3.9.20?

- **Stability**: Python 3.9.x is a mature, stable release with long-term support
- **Compatibility**: Fully compatible with PySpark 3.3.2
- **Performance**: Includes performance improvements over earlier versions
- **Security**: Latest patch release (3.9.20) includes all security updates

## Files Updated

### 1. Main PySpark Container
- **File**: `docker/Dockerfile.pyspark`
- **Change**: Base image updated from `python:3.11-slim` to `python:3.9.20-slim`

### 2. Simple PySpark Container
- **File**: `docker/Dockerfile.pyspark.simple`
- **Changes**: 
  - Base image updated to `python:3.9.20-slim`
  - Removed redundant Python installation (already in base image)
  - Updated pip commands to use `pip` instead of `pip3`

### 3. Cloudera CDH Container
- **File**: `cloudera/Dockerfile.cdh7-spark3`
- **Changes**:
  - Added Python 3.9.20 compilation from source
  - Set environment variables for PYSPARK_PYTHON
  - Updated all Python-related paths

### 4. Configuration Files
- **File**: `cloudera/spark-conf/spark-env.sh`
- **Changes**: Updated PYSPARK_PYTHON paths to use `/usr/bin/python3.9`

## Installation Methods

### Docker/Podman Images
Python 3.9.20 is installed via:
- **Main containers**: Official Python 3.9.20 Docker image
- **Cloudera container**: Compiled from source for CentOS 7 compatibility

## Rebuilding Containers

### Quick Rebuild All
```bash
cd bigdata/scripts
./rebuild-python-3.9.20.sh
```

### Manual Rebuild

#### Main PySpark Container
```bash
cd bigdata/docker
docker-compose -f docker-compose.pyspark.yml down
docker-compose -f docker-compose.pyspark.yml build
docker-compose -f docker-compose.pyspark.yml up -d
```

#### Cloudera CDH Container
```bash
cd bigdata/cloudera
podman-compose down
podman-compose build
./build-and-run.sh
```

## Verification

### Check Python Version
```bash
# Run verification script
cd bigdata/scripts
./verify-python-version.sh

# Or manually check
docker exec pyspark-app python --version
# Expected output: Python 3.9.20

docker exec cdh7-spark3 python --version
# Expected output: Python 3.9.20
```

### Test PySpark Compatibility
```bash
docker exec -it pyspark-app python -c "
import sys
import pyspark
print(f'Python: {sys.version}')
print(f'PySpark: {pyspark.__version__}')
spark = pyspark.sql.SparkSession.builder.appName('test').getOrCreate()
print('✓ PySpark session created successfully')
spark.stop()
"
```

## Environment Variables

The following environment variables are set in containers:
- `PYTHON_VERSION=3.9.20`
- `PYSPARK_PYTHON=/usr/bin/python3.9` (or `/usr/bin/python`)
- `PYSPARK_DRIVER_PYTHON=/usr/bin/python3.9` (or `/usr/bin/python`)

## Compatibility Matrix

| Component | Version | Python 3.9.20 Compatible |
|-----------|---------|-------------------------|
| PySpark | 3.3.2 | ✓ Yes |
| pandas | 2.0.3 | ✓ Yes |
| numpy | 1.24.3 | ✓ Yes |
| pyarrow | 12.0.1 | ✓ Yes |
| faker | 20.1.0 | ✓ Yes |
| jupyter | latest | ✓ Yes |

## Migration Notes

### From Python 3.11/3.12
- Most code will work without changes
- Some newer Python features (match/case statements) won't be available
- Type hints syntax might need minor adjustments

### From Python 3.7/3.8
- All code should work without changes
- Performance improvements will be automatic
- New features like dict merge operators are available

## Troubleshooting

### Issue: Python command not found
```bash
# Create symlinks
docker exec container_name ln -s /usr/bin/python3.9 /usr/bin/python
```

### Issue: pip not found
```bash
# Create pip symlink
docker exec container_name ln -s /usr/bin/pip3.9 /usr/bin/pip
```

### Issue: Module import errors
```bash
# Reinstall packages for Python 3.9
docker exec container_name pip install --upgrade --force-reinstall package_name
```

## Benefits

1. **Consistency**: All environments use the same Python version
2. **Stability**: Python 3.9.20 is a mature, well-tested release
3. **Compatibility**: Excellent compatibility with data science libraries
4. **Performance**: Optimized builds with --enable-optimizations flag
5. **Security**: Latest security patches included

## Next Steps

1. Rebuild all containers using the provided scripts
2. Test your existing Python/PySpark code
3. Update any Python 3.10+ specific code if necessary
4. Enjoy the consistent Python environment!