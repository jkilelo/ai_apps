import asyncio
import pytest

from core.resilience import retry, RetryError, with_timeout, CircuitBreaker


@pytest.mark.asyncio
async def test_retry_eventual_success():
    calls = {"n": 0}

    async def op():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("boom")
        return 42

    val = await retry(op, attempts=5, retry_exceptions=(ValueError,))
    assert val == 42
    assert calls["n"] == 3


@pytest.mark.asyncio
async def test_retry_failure():
    async def op():
        raise RuntimeError("fail")

    with pytest.raises(RetryError):
        await retry(op, attempts=2, retry_exceptions=(RuntimeError,))


@pytest.mark.asyncio
async def test_with_timeout():
    async def op():
        await asyncio.sleep(0.05)
        return "ok"

    out = await with_timeout(op(), timeout_s=0.2)
    assert out == "ok"


@pytest.mark.asyncio
async def test_with_timeout_exceeds():
    async def op():
        await asyncio.sleep(0.2)
        return "late"

    with pytest.raises(asyncio.TimeoutError):
        await with_timeout(op(), timeout_s=0.05)


@pytest.mark.asyncio
async def test_circuit_breaker_open_and_reset():
    cb = CircuitBreaker(failure_threshold=2, reset_timeout=0.2)

    async def bad():
        raise ValueError("nope")

    # two failures -> open
    with pytest.raises(ValueError):
        await cb.run(bad)
    with pytest.raises(ValueError):
        await cb.run(bad)
    assert cb.state == "open"

    # while open it should raise circuit_open
    with pytest.raises(RuntimeError):
        await cb.run(bad)

    # after reset timeout it becomes half-open, one failure re-opens
    await asyncio.sleep(0.25)
    assert cb.state == "half-open"
    with pytest.raises(ValueError):
        await cb.run(bad)
    assert cb.state == "open"
