import pytest
from stealth.config import StealthConfig, StealthLevel


def test_config_defaults():
    cfg = StealthConfig()
    assert cfg.level == StealthLevel.MAXIMUM
    assert cfg.viewport_width == 1920
    assert cfg.timeout > 0


@pytest.mark.skip("Playwright environment not initialized yet for injector script test")
def test_injector_placeholder():
    # Placeholder until we have a mock Page or playwright fixture
    assert True
