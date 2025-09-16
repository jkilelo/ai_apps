#!/usr/bin/env python3
"""
Test file for NEXUS Browser File Manager Module.

Comprehensive tests for ENV-008 file_manager.py.
Verifies all functionality and quality requirements.
"""

import tempfile
from pathlib import Path
from typing import Final

from file_manager import (
    FileManager,
    FileMetadata,
    FileSearchCriteria,
    BackupConfiguration,
    FileLock,
    CompressionType,
    FileOperation,
    FileType,
    safe_read,
    safe_write,
    ensure_directory,
    atomic_write,
)

# Test constants
TEST_PASSED: Final[str] = "[PASSED]"
TEST_FAILED: Final[str] = "[FAILED]"


def test_file_operations() -> None:
    """Test basic file operations."""
    print("\n[TEST] Testing File Operations...")
    manager = FileManager()

    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = Path(tmp_dir) / "test_ops.txt"
        test_content = "File operations test content"

        # Test write
        result = manager.write_file(test_file, test_content)
        assert result.success, "Write operation failed"
        assert result.operation == FileOperation.WRITE
        print(f"  Write operation: {TEST_PASSED}")

        # Test read
        content = manager.read_file(test_file)
        assert content == test_content, "Read content mismatch"
        print(f"  Read operation: {TEST_PASSED}")

        # Test copy
        copy_file = Path(tmp_dir) / "copy.txt"
        result = manager.copy_file(test_file, copy_file)
        assert result.success, "Copy operation failed"
        assert copy_file.exists(), "Copy file doesn't exist"
        print(f"  Copy operation: {TEST_PASSED}")

        # Test move
        move_file = Path(tmp_dir) / "moved.txt"
        result = manager.move_file(copy_file, move_file)
        assert result.success, "Move operation failed"
        assert move_file.exists(), "Moved file doesn't exist"
        assert not copy_file.exists(), "Original file still exists"
        print(f"  Move operation: {TEST_PASSED}")

        # Test delete
        result = manager.delete_file(move_file)
        assert result.success, "Delete operation failed"
        assert not move_file.exists(), "File still exists after delete"
        print(f"  Delete operation: {TEST_PASSED}")


def test_file_metadata() -> None:
    """Test file metadata extraction."""
    print("\n[TEST] Testing File Metadata...")
    manager = FileManager()

    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = Path(tmp_dir) / "metadata_test.json"
        test_content = '{"test": "data"}'

        manager.write_file(test_file, test_content)
        metadata = manager.get_metadata(test_file)

        assert isinstance(metadata, FileMetadata)
        assert metadata.name == "metadata_test.json"
        assert metadata.extension == ".json"
        assert metadata.file_type == FileType.JSON
        assert metadata.is_file
        assert not metadata.is_directory
        assert metadata.size_bytes > 0
        assert metadata.checksum is not None
        print(f"  Metadata extraction: {TEST_PASSED}")


def test_file_search() -> None:
    """Test file search functionality."""
    print("\n[TEST] Testing File Search...")
    manager = FileManager()

    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create test files
        for i in range(5):
            test_file = Path(tmp_dir) / f"test_{i}.txt"
            manager.write_file(test_file, f"Content {i}")

        # Create a different extension file
        other_file = Path(tmp_dir) / "other.log"
        manager.write_file(other_file, "Log content")

        # Search for txt files
        criteria = FileSearchCriteria(
            root_directory=tmp_dir,
            extensions=[".txt"],
        )
        results = manager.search_files(criteria)
        assert len(results) == 5, f"Expected 5 txt files, found {len(results)}"
        print(f"  Extension filter: {TEST_PASSED}")

        # Search with pattern
        criteria = FileSearchCriteria(
            root_directory=tmp_dir,
            pattern="test_[0-2]\\.txt",
        )
        results = manager.search_files(criteria)
        assert len(results) == 3, f"Expected 3 matching files, found {len(results)}"
        print(f"  Pattern matching: {TEST_PASSED}")


def test_compression() -> None:
    """Test file compression and decompression."""
    print("\n[TEST] Testing Compression...")
    manager = FileManager()

    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = Path(tmp_dir) / "compress_test.txt"
        test_content = "Content to compress" * 100

        manager.write_file(test_file, test_content)

        # Test GZIP compression
        result = manager.compress_file(test_file, compression=CompressionType.GZIP)
        assert result.success, "GZIP compression failed"
        compressed_file = Path(f"{test_file}.gz")
        assert compressed_file.exists(), "Compressed file doesn't exist"
        print(f"  GZIP compression: {TEST_PASSED}")

        # Test decompression
        decompressed_file = Path(tmp_dir) / "decompressed.txt"
        result = manager.decompress_file(compressed_file, decompressed_file)
        assert result.success, "Decompression failed"

        content = manager.read_file(decompressed_file)
        assert content == test_content, "Decompressed content mismatch"
        print(f"  GZIP decompression: {TEST_PASSED}")

        # Test ZIP compression
        test_dir = Path(tmp_dir) / "test_dir"
        test_dir.mkdir()
        for i in range(3):
            file_path = test_dir / f"file_{i}.txt"
            manager.write_file(file_path, f"File {i} content")

        result = manager.compress_file(test_dir, compression=CompressionType.ZIP)
        assert result.success, "ZIP compression failed"
        zip_file = Path(f"{test_dir}.zip")
        assert zip_file.exists(), "ZIP file doesn't exist"
        print(f"  ZIP compression: {TEST_PASSED}")


def test_backup_restore() -> None:
    """Test backup and restore operations."""
    print("\n[TEST] Testing Backup/Restore...")
    manager = FileManager()

    with tempfile.TemporaryDirectory() as tmp_dir:
        source_file = Path(tmp_dir) / "original.txt"
        backup_dir = Path(tmp_dir) / "backups"
        backup_dir.mkdir()

        original_content = "Original file content"
        manager.write_file(source_file, original_content)

        # Create backup
        config = BackupConfiguration(
            source_path=str(source_file),
            backup_directory=str(backup_dir),
            compression=CompressionType.GZIP,
            versioning=True,
        )
        result = manager.create_backup(config)
        assert result.success, "Backup creation failed"
        print(f"  Backup creation: {TEST_PASSED}")

        # Delete original
        manager.delete_file(source_file)
        assert not source_file.exists()

        # Restore from backup
        backup_files = list(backup_dir.glob("backup_*.gz"))
        assert len(backup_files) > 0, "No backup files found"

        result = manager.restore_backup(backup_files[0], source_file)
        assert result.success, "Restore failed"
        assert source_file.exists(), "Restored file doesn't exist"

        content = manager.read_file(source_file)
        assert content == original_content, "Restored content mismatch"
        print(f"  Backup restore: {TEST_PASSED}")


def test_file_locking() -> None:
    """Test file locking mechanism."""
    print("\n[TEST] Testing File Locking...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = Path(tmp_dir) / "lock_test.txt"
        test_file.touch()

        # Test lock acquisition
        acquired = FileLock.acquire(str(test_file))
        assert acquired, "Failed to acquire lock"
        print(f"  Lock acquisition: {TEST_PASSED}")

        # Release lock
        FileLock.release(str(test_file))
        print(f"  Lock release: {TEST_PASSED}")

        # Test context manager
        with FileLock.lock_context(str(test_file)):
            # Lock is held here
            pass
        print(f"  Lock context manager: {TEST_PASSED}")


def test_convenience_functions() -> None:
    """Test convenience functions."""
    print("\n[TEST] Testing Convenience Functions...")

    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = Path(tmp_dir) / "convenience.txt"
        test_content = "Convenience test"

        # Test safe_write
        success = safe_write(test_file, test_content)
        assert success, "safe_write failed"
        print(f"  safe_write: {TEST_PASSED}")

        # Test safe_read
        content = safe_read(test_file)
        assert content == test_content, "safe_read content mismatch"
        print(f"  safe_read: {TEST_PASSED}")

        # Test safe_read with non-existent file
        content = safe_read(Path(tmp_dir) / "nonexistent.txt", default="default")
        assert content == "default", "safe_read default not returned"
        print(f"  safe_read with default: {TEST_PASSED}")

        # Test ensure_directory
        new_dir = Path(tmp_dir) / "new" / "nested" / "dir"
        success = ensure_directory(new_dir)
        assert success, "ensure_directory failed"
        assert new_dir.exists(), "Directory not created"
        print(f"  ensure_directory: {TEST_PASSED}")

        # Test atomic_write
        atomic_file = Path(tmp_dir) / "atomic.txt"
        result = atomic_write(atomic_file, "Atomic content")
        assert result.success, "atomic_write failed"
        assert atomic_file.exists(), "Atomic file not created"
        print(f"  atomic_write: {TEST_PASSED}")


def test_pydantic_models() -> None:
    """Test Pydantic model validation."""
    print("\n[TEST] Testing Pydantic Models...")

    # Test FileSearchCriteria validation
    try:
        FileSearchCriteria(
            root_directory="/nonexistent/path",
            max_size=100,
            min_size=200,  # Invalid: min > max
        )
        assert False, "Should have raised validation error"
    except ValueError:
        print(f"  FileSearchCriteria validation: {TEST_PASSED}")

    # Test BackupConfiguration validation
    try:
        BackupConfiguration(
            source_path="/nonexistent/file",
            backup_directory="/tmp",
        )
        assert False, "Should have raised validation error"
    except ValueError:
        print(f"  BackupConfiguration validation: {TEST_PASSED}")


def run_all_tests() -> None:
    """Run all tests."""
    print("=" * 60)
    print("NEXUS File Manager Test Suite")
    print("=" * 60)

    test_functions = [
        test_file_operations,
        test_file_metadata,
        test_file_search,
        test_compression,
        test_backup_restore,
        test_file_locking,
        test_convenience_functions,
        test_pydantic_models,
    ]

    for test_func in test_functions:
        try:
            test_func()
        except Exception as e:
            print(f"\n{TEST_FAILED} {test_func.__name__}: {e}")
            raise

    print("\n" + "=" * 60)
    print("All tests passed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
