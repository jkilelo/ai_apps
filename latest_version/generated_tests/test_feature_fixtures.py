# Test Fixtures

import pytest

@pytest.fixture
def test_data():
    """Test data for scenarios"""
    return {
    }

@pytest.fixture
def test_user():
    """Test user credentials"""
    return {
        "username": "testuser@example.com",
        "password": "TestPassword123!",
    }

