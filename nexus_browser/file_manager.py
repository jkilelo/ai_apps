#!/usr/bin/env python3
"""
NEXUS Browser File Manager Module.

Task: ENV-008
Comprehensive file management operations for the NEXUS Browser system.
Full compliance with mypy --strict, flake8, and 100% type coverage.
Uses Pydantic v2 for all data structures.
"""

import os
import shutil
import tempfile
import hashlib
import gzip
import zipfile
import threading
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    Final,
    Iterator,
)
from datetime import datetime
from enum import Enum
from contextlib import contextmanager
import time
import re
from pydantic import BaseModel, Field, field_validator, ConfigDict

from exceptions import FileSystemError


# Module constants
TASK_ID: Final[str] = "ENV-008"
MODULE_NAME: Final[str] = "file_manager"
QUALITY_ENFORCED: Final[bool] = True

# File operation constants
DEFAULT_ENCODING: Final[str] = "utf-8"
BUFFER_SIZE: Final[int] = 8192
MAX_BACKUP_VERSIONS: Final[int] = 10


class FileOperation(str, Enum):
    """Types of file operations."""

    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    COPY = "copy"
    MOVE = "move"
    RENAME = "rename"
    COMPRESS = "compress"
    DECOMPRESS = "decompress"
    BACKUP = "backup"
    RESTORE = "restore"


class CompressionType(str, Enum):
    """Supported compression types."""

    GZIP = "gzip"
    ZIP = "zip"
    NONE = "none"


class FileType(str, Enum):
    """File type classification."""

    TEXT = "text"
    BINARY = "binary"
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    CONFIG = "config"
    LOG = "log"
    UNKNOWN = "unknown"


class FileMetadata(BaseModel):
    """File metadata information."""

    model_config = ConfigDict(frozen=True)

    path: str
    name: str
    extension: str
    size_bytes: int = Field(ge=0)
    created_time: datetime
    modified_time: datetime
    accessed_time: datetime
    is_file: bool
    is_directory: bool
    is_symlink: bool
    is_readable: bool
    is_writable: bool
    is_executable: bool
    mime_type: Optional[str] = None
    encoding: Optional[str] = None
    checksum: Optional[str] = None
    file_type: FileType = FileType.UNKNOWN

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate file path."""
        if not v:
            raise ValueError("Path cannot be empty")
        return str(Path(v).resolve())


class FileSearchCriteria(BaseModel):
    """Criteria for file searching."""

    model_config = ConfigDict(frozen=True)

    root_directory: str
    pattern: Optional[str] = None
    extensions: List[str] = Field(default_factory=list)
    min_size: Optional[int] = Field(None, ge=0)
    max_size: Optional[int] = Field(None, ge=0)
    modified_after: Optional[datetime] = None
    modified_before: Optional[datetime] = None
    recursive: bool = True
    include_hidden: bool = False
    follow_symlinks: bool = False
    max_results: Optional[int] = Field(None, ge=1)

    @field_validator("root_directory")
    @classmethod
    def validate_root_directory(cls, v: str) -> str:
        """Validate root directory exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Root directory does not exist: {v}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {v}")
        return str(path.resolve())

    @field_validator("max_size")
    @classmethod
    def validate_max_size(cls, v: Optional[int], info: Any) -> Optional[int]:
        """Validate max_size is greater than min_size."""
        if v is not None and "min_size" in info.data:
            min_size = info.data.get("min_size")
            if min_size is not None and v < min_size:
                raise ValueError("max_size must be greater than min_size")
        return v


class BackupConfiguration(BaseModel):
    """Configuration for backup operations."""

    model_config = ConfigDict(frozen=True)

    source_path: str
    backup_directory: str
    compression: CompressionType = CompressionType.GZIP
    versioning: bool = True
    max_versions: int = Field(default=MAX_BACKUP_VERSIONS, ge=1, le=100)
    include_timestamp: bool = True
    backup_name_prefix: str = "backup"
    exclude_patterns: List[str] = Field(default_factory=list)

    @field_validator("source_path")
    @classmethod
    def validate_source_path(cls, v: str) -> str:
        """Validate source path exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Source path does not exist: {v}")
        return str(path.resolve())

    @field_validator("backup_directory")
    @classmethod
    def validate_backup_directory(cls, v: str) -> str:
        """Validate backup directory."""
        path = Path(v)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        return str(path.resolve())


class FileOperationResult(BaseModel):
    """Result of a file operation."""

    model_config = ConfigDict(frozen=True)

    operation: FileOperation
    success: bool
    source_path: Optional[str] = None
    target_path: Optional[str] = None
    bytes_processed: int = Field(default=0, ge=0)
    duration_seconds: float = Field(default=0.0, ge=0.0)
    message: str = ""
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FileWatchEvent(BaseModel):
    """File system watch event."""

    model_config = ConfigDict(frozen=True)

    event_type: str
    path: str
    is_directory: bool
    timestamp: datetime
    old_path: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FileLock:
    """Thread-safe file locking mechanism."""

    _locks: Dict[str, threading.Lock] = {}
    _lock_mutex: threading.Lock = threading.Lock()

    @classmethod
    def acquire(cls, file_path: str, timeout: Optional[float] = None) -> bool:
        """
        Acquire a lock for a file.

        Args:
            file_path: Path to the file
            timeout: Maximum time to wait for lock

        Returns:
            bool: True if lock acquired, False otherwise
        """
        path_str = str(Path(file_path).resolve())

        with cls._lock_mutex:
            if path_str not in cls._locks:
                cls._locks[path_str] = threading.Lock()
            lock = cls._locks[path_str]

        if timeout is None:
            return lock.acquire(blocking=True)
        else:
            return lock.acquire(blocking=True, timeout=timeout)

    @classmethod
    def release(cls, file_path: str) -> None:
        """
        Release a lock for a file.

        Args:
            file_path: Path to the file
        """
        path_str = str(Path(file_path).resolve())

        with cls._lock_mutex:
            if path_str in cls._locks:
                cls._locks[path_str].release()

    @classmethod
    @contextmanager
    def lock_context(
        cls, file_path: str, timeout: Optional[float] = None
    ) -> Iterator[None]:
        """
        Context manager for file locking.

        Args:
            file_path: Path to the file
            timeout: Maximum time to wait for lock

        Yields:
            None

        Raises:
            FileSystemError: If lock cannot be acquired
        """
        if not cls.acquire(file_path, timeout):
            raise FileSystemError(
                f"Could not acquire lock for file: {file_path}",
                file_path=file_path,
                operation="lock",
            )
        try:
            yield
        finally:
            cls.release(file_path)


class FileManager:
    """Comprehensive file management operations."""

    def __init__(self, default_encoding: str = DEFAULT_ENCODING) -> None:
        """
        Initialize FileManager.

        Args:
            default_encoding: Default text encoding
        """
        self.default_encoding = default_encoding
        self._watchers: Dict[str, Any] = {}

    def read_file(
        self,
        file_path: Union[str, Path],
        encoding: Optional[str] = None,
        binary: bool = False,
    ) -> Union[str, bytes]:
        """
        Read file contents safely.

        Args:
            file_path: Path to the file
            encoding: Text encoding (if not binary)
            binary: Whether to read in binary mode

        Returns:
            Union[str, bytes]: File contents

        Raises:
            FileSystemError: If file cannot be read
        """
        path = Path(file_path)
        if not path.exists():
            raise FileSystemError(
                f"File does not exist: {file_path}",
                file_path=str(file_path),
                operation="read",
            )

        if not path.is_file():
            raise FileSystemError(
                f"Path is not a file: {file_path}",
                file_path=str(file_path),
                operation="read",
            )

        try:
            with FileLock.lock_context(str(path)):
                if binary:
                    with open(path, "rb") as f:
                        return f.read()
                else:
                    with open(
                        path, "r", encoding=encoding or self.default_encoding
                    ) as f:
                        return f.read()
        except Exception as e:
            raise FileSystemError(
                f"Failed to read file: {file_path}",
                file_path=str(file_path),
                operation="read",
                cause=e,
            )

    def write_file(
        self,
        file_path: Union[str, Path],
        content: Union[str, bytes],
        encoding: Optional[str] = None,
        create_parents: bool = True,
        atomic: bool = True,
    ) -> FileOperationResult:
        """
        Write content to file safely.

        Args:
            file_path: Path to the file
            content: Content to write
            encoding: Text encoding (for string content)
            create_parents: Create parent directories if needed
            atomic: Use atomic write operation

        Returns:
            FileOperationResult: Operation result

        Raises:
            FileSystemError: If file cannot be written
        """
        path = Path(file_path)
        start_time = time.time()

        try:
            if create_parents:
                path.parent.mkdir(parents=True, exist_ok=True)

            bytes_content: bytes
            if isinstance(content, str):
                bytes_content = content.encode(encoding or self.default_encoding)
            else:
                bytes_content = content

            if atomic:
                # Write to temporary file first
                with tempfile.NamedTemporaryFile(
                    mode="wb",
                    dir=path.parent,
                    delete=False,
                ) as tmp_file:
                    tmp_file.write(bytes_content)
                    tmp_path = Path(tmp_file.name)

                # Atomic rename
                tmp_path.replace(path)
            else:
                with FileLock.lock_context(str(path)):
                    with open(path, "wb") as f:
                        f.write(bytes_content)

            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.WRITE,
                success=True,
                target_path=str(path),
                bytes_processed=len(bytes_content),
                duration_seconds=duration,
                message=f"Successfully wrote {len(bytes_content)} bytes",
            )

        except Exception as e:
            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.WRITE,
                success=False,
                target_path=str(path),
                duration_seconds=duration,
                message=f"Failed to write file: {e}",
                error=str(e),
            )

    def delete_file(
        self, file_path: Union[str, Path], force: bool = False
    ) -> FileOperationResult:
        """
        Delete a file safely.

        Args:
            file_path: Path to the file
            force: Force deletion even if file is read-only

        Returns:
            FileOperationResult: Operation result
        """
        path = Path(file_path)
        start_time = time.time()

        try:
            if not path.exists():
                return FileOperationResult(
                    operation=FileOperation.DELETE,
                    success=True,
                    source_path=str(path),
                    duration_seconds=0.0,
                    message="File does not exist",
                )

            if force and not os.access(path, os.W_OK):
                os.chmod(path, 0o777)

            with FileLock.lock_context(str(path)):
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()

            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.DELETE,
                success=True,
                source_path=str(path),
                duration_seconds=duration,
                message="File deleted successfully",
            )

        except Exception as e:
            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.DELETE,
                success=False,
                source_path=str(path),
                duration_seconds=duration,
                message=f"Failed to delete file: {e}",
                error=str(e),
            )

    def copy_file(
        self,
        source: Union[str, Path],
        destination: Union[str, Path],
        overwrite: bool = False,
        preserve_metadata: bool = True,
    ) -> FileOperationResult:
        """
        Copy a file or directory.

        Args:
            source: Source path
            destination: Destination path
            overwrite: Overwrite if destination exists
            preserve_metadata: Preserve file metadata

        Returns:
            FileOperationResult: Operation result
        """
        src_path = Path(source)
        dst_path = Path(destination)
        start_time = time.time()

        try:
            if not src_path.exists():
                raise FileSystemError(
                    f"Source does not exist: {source}",
                    file_path=str(source),
                    operation="copy",
                )

            if dst_path.exists() and not overwrite:
                raise FileSystemError(
                    f"Destination already exists: {destination}",
                    file_path=str(destination),
                    operation="copy",
                )

            if src_path.is_dir():
                if preserve_metadata:
                    shutil.copytree(
                        src_path, dst_path, dirs_exist_ok=overwrite
                    )
                else:
                    shutil.copytree(
                        src_path,
                        dst_path,
                        dirs_exist_ok=overwrite,
                        copy_function=shutil.copy,
                    )
            else:
                if preserve_metadata:
                    shutil.copy2(src_path, dst_path)
                else:
                    shutil.copy(src_path, dst_path)

            duration = time.time() - start_time
            size = (
                src_path.stat().st_size if src_path.is_file() else 0
            )

            return FileOperationResult(
                operation=FileOperation.COPY,
                success=True,
                source_path=str(src_path),
                target_path=str(dst_path),
                bytes_processed=size,
                duration_seconds=duration,
                message="Copy completed successfully",
            )

        except Exception as e:
            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.COPY,
                success=False,
                source_path=str(src_path),
                target_path=str(dst_path),
                duration_seconds=duration,
                message=f"Copy failed: {e}",
                error=str(e),
            )

    def move_file(
        self,
        source: Union[str, Path],
        destination: Union[str, Path],
        overwrite: bool = False,
    ) -> FileOperationResult:
        """
        Move a file or directory.

        Args:
            source: Source path
            destination: Destination path
            overwrite: Overwrite if destination exists

        Returns:
            FileOperationResult: Operation result
        """
        src_path = Path(source)
        dst_path = Path(destination)
        start_time = time.time()

        try:
            if not src_path.exists():
                raise FileSystemError(
                    f"Source does not exist: {source}",
                    file_path=str(source),
                    operation="move",
                )

            if dst_path.exists() and not overwrite:
                raise FileSystemError(
                    f"Destination already exists: {destination}",
                    file_path=str(destination),
                    operation="move",
                )

            shutil.move(str(src_path), str(dst_path))

            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.MOVE,
                success=True,
                source_path=str(src_path),
                target_path=str(dst_path),
                duration_seconds=duration,
                message="Move completed successfully",
            )

        except Exception as e:
            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.MOVE,
                success=False,
                source_path=str(src_path),
                target_path=str(dst_path),
                duration_seconds=duration,
                message=f"Move failed: {e}",
                error=str(e),
            )

    def get_metadata(self, file_path: Union[str, Path]) -> FileMetadata:
        """
        Extract file metadata.

        Args:
            file_path: Path to the file

        Returns:
            FileMetadata: File metadata information

        Raises:
            FileSystemError: If metadata cannot be retrieved
        """
        path = Path(file_path)

        if not path.exists():
            raise FileSystemError(
                f"Path does not exist: {file_path}",
                file_path=str(file_path),
                operation="metadata",
            )

        try:
            stat = path.stat()
            file_type = self._detect_file_type(path)

            # Calculate checksum for files
            checksum: Optional[str] = None
            if path.is_file() and stat.st_size < 100 * 1024 * 1024:  # 100MB limit
                checksum = self._calculate_checksum(path)

            return FileMetadata(
                path=str(path.resolve()),
                name=path.name,
                extension=path.suffix,
                size_bytes=stat.st_size,
                created_time=datetime.fromtimestamp(stat.st_ctime),
                modified_time=datetime.fromtimestamp(stat.st_mtime),
                accessed_time=datetime.fromtimestamp(stat.st_atime),
                is_file=path.is_file(),
                is_directory=path.is_dir(),
                is_symlink=path.is_symlink(),
                is_readable=os.access(path, os.R_OK),
                is_writable=os.access(path, os.W_OK),
                is_executable=os.access(path, os.X_OK),
                file_type=file_type,
                checksum=checksum,
            )

        except Exception as e:
            raise FileSystemError(
                f"Failed to get metadata: {file_path}",
                file_path=str(file_path),
                operation="metadata",
                cause=e,
            )

    def search_files(
        self, criteria: FileSearchCriteria
    ) -> List[FileMetadata]:
        """
        Search for files matching criteria.

        Args:
            criteria: Search criteria

        Returns:
            List[FileMetadata]: Matching files
        """
        results: List[FileMetadata] = []
        root_path = Path(criteria.root_directory)

        try:
            if criteria.recursive:
                iterator = root_path.rglob("*")
            else:
                iterator = root_path.glob("*")

            for path in iterator:
                # Skip if max results reached
                if criteria.max_results and len(results) >= criteria.max_results:
                    break

                # Skip hidden files if not included
                if not criteria.include_hidden and path.name.startswith("."):
                    continue

                # Skip symlinks if not following
                if path.is_symlink() and not criteria.follow_symlinks:
                    continue

                # Skip directories
                if not path.is_file():
                    continue

                # Check pattern match
                if criteria.pattern:
                    if not re.match(criteria.pattern, path.name):
                        continue

                # Check extensions
                if criteria.extensions:
                    if path.suffix not in criteria.extensions:
                        continue

                # Check file size
                try:
                    size = path.stat().st_size
                    if criteria.min_size and size < criteria.min_size:
                        continue
                    if criteria.max_size and size > criteria.max_size:
                        continue

                    # Check modification time
                    mtime = datetime.fromtimestamp(path.stat().st_mtime)
                    if criteria.modified_after and mtime < criteria.modified_after:
                        continue
                    if criteria.modified_before and mtime > criteria.modified_before:
                        continue

                    # Add to results
                    results.append(self.get_metadata(path))

                except (OSError, PermissionError):
                    continue

        except Exception as e:
            raise FileSystemError(
                f"Search failed in directory: {criteria.root_directory}",
                file_path=criteria.root_directory,
                operation="search",
                cause=e,
            )

        return results

    def compress_file(
        self,
        source: Union[str, Path],
        output: Optional[Union[str, Path]] = None,
        compression: CompressionType = CompressionType.GZIP,
    ) -> FileOperationResult:
        """
        Compress a file or directory.

        Args:
            source: Source path
            output: Output path (auto-generated if None)
            compression: Compression type

        Returns:
            FileOperationResult: Operation result
        """
        src_path = Path(source)
        start_time = time.time()

        if not src_path.exists():
            raise FileSystemError(
                f"Source does not exist: {source}",
                file_path=str(source),
                operation="compress",
            )

        try:
            if output is None:
                if compression == CompressionType.GZIP:
                    output = Path(f"{src_path}.gz")
                elif compression == CompressionType.ZIP:
                    output = Path(f"{src_path}.zip")
                else:
                    output = src_path
            else:
                output = Path(output)

            bytes_processed = 0

            if compression == CompressionType.GZIP:
                if src_path.is_file():
                    with open(src_path, "rb") as f_in:
                        with gzip.open(output, "wb") as f_out:
                            shutil.copyfileobj(f_in, f_out)
                            bytes_processed = src_path.stat().st_size
                else:
                    raise ValueError("GZIP compression only supports single files")

            elif compression == CompressionType.ZIP:
                with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
                    if src_path.is_file():
                        zf.write(src_path, src_path.name)
                        bytes_processed = src_path.stat().st_size
                    else:
                        for file_path in src_path.rglob("*"):
                            if file_path.is_file():
                                zf.write(
                                    file_path,
                                    file_path.relative_to(src_path.parent),
                                )
                                bytes_processed += file_path.stat().st_size

            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.COMPRESS,
                success=True,
                source_path=str(src_path),
                target_path=str(output),
                bytes_processed=bytes_processed,
                duration_seconds=duration,
                message=f"Compressed to {compression.value} format",
            )

        except Exception as e:
            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.COMPRESS,
                success=False,
                source_path=str(src_path),
                target_path=str(output) if output else None,
                duration_seconds=duration,
                message=f"Compression failed: {e}",
                error=str(e),
            )

    def decompress_file(
        self,
        source: Union[str, Path],
        output: Optional[Union[str, Path]] = None,
    ) -> FileOperationResult:
        """
        Decompress a file.

        Args:
            source: Compressed file path
            output: Output directory (auto-generated if None)

        Returns:
            FileOperationResult: Operation result
        """
        src_path = Path(source)
        start_time = time.time()

        if not src_path.exists():
            raise FileSystemError(
                f"Source does not exist: {source}",
                file_path=str(source),
                operation="decompress",
            )

        try:
            bytes_processed = 0

            if src_path.suffix == ".gz":
                if output is None:
                    output = Path(str(src_path).removesuffix(".gz"))
                else:
                    output = Path(output)

                with gzip.open(src_path, "rb") as f_in:
                    with open(output, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                        bytes_processed = output.stat().st_size

            elif src_path.suffix == ".zip":
                if output is None:
                    output = src_path.parent / src_path.stem
                else:
                    output = Path(output)

                output.mkdir(parents=True, exist_ok=True)

                with zipfile.ZipFile(src_path, "r") as zf:
                    zf.extractall(output)
                    for info in zf.filelist:
                        bytes_processed += info.file_size

            else:
                raise ValueError(f"Unsupported compression format: {src_path.suffix}")

            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.DECOMPRESS,
                success=True,
                source_path=str(src_path),
                target_path=str(output),
                bytes_processed=bytes_processed,
                duration_seconds=duration,
                message="Decompression completed successfully",
            )

        except Exception as e:
            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.DECOMPRESS,
                success=False,
                source_path=str(src_path),
                target_path=str(output) if output else None,
                duration_seconds=duration,
                message=f"Decompression failed: {e}",
                error=str(e),
            )

    def create_backup(
        self, config: BackupConfiguration
    ) -> FileOperationResult:
        """
        Create a backup of files.

        Args:
            config: Backup configuration

        Returns:
            FileOperationResult: Operation result
        """
        start_time = time.time()
        src_path = Path(config.source_path)
        backup_dir = Path(config.backup_directory)

        try:
            # Generate backup name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if config.include_timestamp:
                backup_name = f"{config.backup_name_prefix}_{timestamp}"
            else:
                backup_name = config.backup_name_prefix

            # Handle versioning
            if config.versioning:
                existing_backups = sorted(
                    backup_dir.glob(f"{config.backup_name_prefix}*")
                )
                if len(existing_backups) >= config.max_versions:
                    # Remove oldest backups
                    for old_backup in existing_backups[: -config.max_versions + 1]:
                        if old_backup.is_dir():
                            shutil.rmtree(old_backup)
                        else:
                            old_backup.unlink()

            # Create backup
            backup_path = backup_dir / backup_name

            if src_path.is_file():
                shutil.copy2(src_path, backup_path)
            else:
                shutil.copytree(
                    src_path,
                    backup_path,
                    ignore=shutil.ignore_patterns(*config.exclude_patterns),
                )

            # Apply compression if needed
            if config.compression != CompressionType.NONE:
                compress_result = self.compress_file(
                    backup_path,
                    compression=config.compression,
                )
                if compress_result.success:
                    # Remove uncompressed backup
                    if backup_path.is_dir():
                        shutil.rmtree(backup_path)
                    else:
                        backup_path.unlink()
                    backup_path = Path(compress_result.target_path or "")

            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.BACKUP,
                success=True,
                source_path=str(src_path),
                target_path=str(backup_path),
                duration_seconds=duration,
                message=f"Backup created: {backup_name}",
                metadata={"timestamp": timestamp, "compression": config.compression},
            )

        except Exception as e:
            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.BACKUP,
                success=False,
                source_path=str(src_path),
                duration_seconds=duration,
                message=f"Backup failed: {e}",
                error=str(e),
            )

    def restore_backup(
        self,
        backup_path: Union[str, Path],
        restore_path: Union[str, Path],
        overwrite: bool = False,
    ) -> FileOperationResult:
        """
        Restore from a backup.

        Args:
            backup_path: Path to backup
            restore_path: Path to restore to
            overwrite: Overwrite existing files

        Returns:
            FileOperationResult: Operation result
        """
        backup = Path(backup_path)
        restore = Path(restore_path)
        start_time = time.time()

        try:
            if not backup.exists():
                raise FileSystemError(
                    f"Backup does not exist: {backup_path}",
                    file_path=str(backup_path),
                    operation="restore",
                )

            if restore.exists() and not overwrite:
                raise FileSystemError(
                    f"Restore target already exists: {restore_path}",
                    file_path=str(restore_path),
                    operation="restore",
                )

            # Check if backup is compressed
            if backup.suffix in [".gz", ".zip"]:
                decompress_result = self.decompress_file(backup, restore)
                if not decompress_result.success:
                    raise FileSystemError(
                        f"Failed to decompress backup: {decompress_result.message}",
                        file_path=str(backup_path),
                        operation="restore",
                    )
            else:
                # Direct copy
                if backup.is_file():
                    shutil.copy2(backup, restore)
                else:
                    shutil.copytree(backup, restore, dirs_exist_ok=overwrite)

            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.RESTORE,
                success=True,
                source_path=str(backup),
                target_path=str(restore),
                duration_seconds=duration,
                message="Restore completed successfully",
            )

        except Exception as e:
            duration = time.time() - start_time
            return FileOperationResult(
                operation=FileOperation.RESTORE,
                success=False,
                source_path=str(backup),
                target_path=str(restore),
                duration_seconds=duration,
                message=f"Restore failed: {e}",
                error=str(e),
            )

    def _detect_file_type(self, path: Path) -> FileType:
        """
        Detect file type based on extension and content.

        Args:
            path: File path

        Returns:
            FileType: Detected file type
        """
        if path.is_dir():
            return FileType.UNKNOWN

        extension = path.suffix.lower()

        # Check by extension
        text_extensions = {".txt", ".md", ".rst", ".csv"}
        json_extensions = {".json", ".jsonl"}
        xml_extensions = {".xml", ".xhtml", ".svg"}
        yaml_extensions = {".yaml", ".yml"}
        config_extensions = {".ini", ".cfg", ".conf", ".config", ".env"}
        log_extensions = {".log", ".out", ".err"}

        if extension in text_extensions:
            return FileType.TEXT
        elif extension in json_extensions:
            return FileType.JSON
        elif extension in xml_extensions:
            return FileType.XML
        elif extension in yaml_extensions:
            return FileType.YAML
        elif extension in config_extensions:
            return FileType.CONFIG
        elif extension in log_extensions:
            return FileType.LOG

        # Try to detect by content
        try:
            with open(path, "rb") as f:
                chunk = f.read(1024)
                # Check if text
                try:
                    chunk.decode("utf-8")
                    return FileType.TEXT
                except UnicodeDecodeError:
                    return FileType.BINARY
        except Exception:
            return FileType.UNKNOWN

    def _calculate_checksum(
        self, path: Path, algorithm: str = "sha256"
    ) -> str:
        """
        Calculate file checksum.

        Args:
            path: File path
            algorithm: Hash algorithm

        Returns:
            str: Hex digest of checksum
        """
        hash_obj = hashlib.new(algorithm)

        with open(path, "rb") as f:
            while chunk := f.read(BUFFER_SIZE):
                hash_obj.update(chunk)

        return hash_obj.hexdigest()


# Convenience functions
def safe_read(
    file_path: Union[str, Path],
    default: Optional[Union[str, bytes]] = None,
    encoding: str = DEFAULT_ENCODING,
) -> Union[str, bytes, None]:
    """
    Safely read a file with default fallback.

    Args:
        file_path: Path to file
        default: Default value if read fails
        encoding: Text encoding

    Returns:
        Union[str, bytes, None]: File contents or default
    """
    try:
        manager = FileManager()
        return manager.read_file(file_path, encoding=encoding)
    except Exception:
        return default


def safe_write(
    file_path: Union[str, Path],
    content: Union[str, bytes],
    encoding: str = DEFAULT_ENCODING,
) -> bool:
    """
    Safely write to a file.

    Args:
        file_path: Path to file
        content: Content to write
        encoding: Text encoding

    Returns:
        bool: True if successful
    """
    try:
        manager = FileManager()
        result = manager.write_file(file_path, content, encoding=encoding)
        return result.success
    except Exception:
        return False


def ensure_directory(
    directory: Union[str, Path], parents: bool = True
) -> bool:
    """
    Ensure a directory exists.

    Args:
        directory: Directory path
        parents: Create parent directories

    Returns:
        bool: True if directory exists or was created
    """
    try:
        path = Path(directory)
        path.mkdir(parents=parents, exist_ok=True)
        return True
    except Exception:
        return False


def atomic_write(
    file_path: Union[str, Path],
    content: Union[str, bytes],
    encoding: str = DEFAULT_ENCODING,
) -> FileOperationResult:
    """
    Perform atomic file write operation.

    Args:
        file_path: Path to file
        content: Content to write
        encoding: Text encoding

    Returns:
        FileOperationResult: Operation result
    """
    manager = FileManager()
    return manager.write_file(
        file_path,
        content,
        encoding=encoding,
        atomic=True,
    )


if __name__ == "__main__":
    print(f"[FILE_MANAGER] NEXUS Browser File Manager Module (Task: {TASK_ID})")
    print(f"[FILE_MANAGER] Quality Enforcement: {QUALITY_ENFORCED}")

    # Test basic functionality
    manager = FileManager()

    # Test file operations with temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = Path(tmp_dir) / "test.txt"
        test_content = "NEXUS Browser File Manager Test"

        # Test write
        write_result = manager.write_file(test_file, test_content)
        print(f"\n[FILE_MANAGER] Write test: {write_result.success}")

        # Test read
        if write_result.success:
            content = manager.read_file(test_file)
            print(f"[FILE_MANAGER] Read test: {content == test_content}")

            # Test metadata
            metadata = manager.get_metadata(test_file)
            print(f"[FILE_MANAGER] Metadata test: {metadata.name}")

            # Test search
            criteria = FileSearchCriteria(
                root_directory=tmp_dir,
                pattern=".*\\.txt$",
            )
            search_results = manager.search_files(criteria)
            print(f"[FILE_MANAGER] Search test: Found {len(search_results)} files")

            # Test backup
            backup_config = BackupConfiguration(
                source_path=str(test_file),
                backup_directory=tmp_dir,
                compression=CompressionType.GZIP,
            )
            backup_result = manager.create_backup(backup_config)
            print(f"[FILE_MANAGER] Backup test: {backup_result.success}")

    print("\n[FILE_MANAGER] Module initialized successfully")
