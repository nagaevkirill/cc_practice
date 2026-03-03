import time
import pytest
from unittest.mock import patch, MagicMock

from src.utils.retry import retry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_flaky(fail_times: int, exc_type: type[Exception] = ValueError):
    """Returns a function that raises exc_type for the first `fail_times` calls."""
    calls = {"count": 0}

    def flaky():
        calls["count"] += 1
        if calls["count"] <= fail_times:
            raise exc_type(f"fail #{calls['count']}")
        return "ok"

    return flaky, calls


# ---------------------------------------------------------------------------
# Базовое поведение
# ---------------------------------------------------------------------------

class TestRetryBasic:
    def test_succeeds_on_first_attempt(self):
        func, calls = make_flaky(0)
        result = retry(max_attempts=3, base_delay=0, jitter=False)(func)()
        assert result == "ok"
        assert calls["count"] == 1

    def test_retries_and_succeeds(self):
        func, calls = make_flaky(2)
        result = retry(max_attempts=3, base_delay=0, jitter=False)(func)()
        assert result == "ok"
        assert calls["count"] == 3

    def test_raises_after_all_attempts(self):
        func, calls = make_flaky(5)
        with pytest.raises(ValueError, match="fail #3"):
            retry(max_attempts=3, base_delay=0, jitter=False)(func)()
        assert calls["count"] == 3

    def test_reraises_last_exception(self):
        """Должно пробрасываться именно последнее исключение."""
        counter = {"n": 0}

        @retry(max_attempts=3, base_delay=0, jitter=False)
        def func():
            counter["n"] += 1
            raise ValueError(f"attempt {counter['n']}")

        with pytest.raises(ValueError, match="attempt 3"):
            func()

    def test_preserves_function_metadata(self):
        @retry()
        def my_func():
            """docstring"""

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "docstring"

    def test_passes_args_and_kwargs(self):
        @retry(max_attempts=1, base_delay=0, jitter=False)
        def add(a, b, *, factor=1):
            return (a + b) * factor

        assert add(2, 3, factor=10) == 50


# ---------------------------------------------------------------------------
# Фильтрация исключений
# ---------------------------------------------------------------------------

class TestRetryExceptions:
    def test_retries_only_specified_exceptions(self):
        func, calls = make_flaky(2, exc_type=IOError)
        result = retry(
            max_attempts=5, base_delay=0, jitter=False, exceptions=(IOError,)
        )(func)()
        assert result == "ok"
        assert calls["count"] == 3

    def test_does_not_catch_unspecified_exception(self):
        @retry(max_attempts=3, base_delay=0, jitter=False, exceptions=(IOError,))
        def func():
            raise TypeError("not retried")

        with pytest.raises(TypeError, match="not retried"):
            func()

    def test_retries_on_multiple_exception_types(self):
        errors = [IOError("io"), ValueError("val"), None]

        @retry(max_attempts=3, base_delay=0, jitter=False,
               exceptions=(IOError, ValueError))
        def func():
            err = errors.pop(0)
            if err:
                raise err
            return "done"

        assert func() == "done"


# ---------------------------------------------------------------------------
# Задержки
# ---------------------------------------------------------------------------

class TestRetryDelays:
    def test_no_sleep_on_first_failure_then_success(self):
        func, _ = make_flaky(1)
        with patch("src.utils.retry.time.sleep") as mock_sleep:
            retry(max_attempts=3, base_delay=1.0, jitter=False)(func)()
        mock_sleep.assert_called_once_with(1.0)  # base * 2^0

    def test_exponential_backoff_delays(self):
        func, _ = make_flaky(3)
        with patch("src.utils.retry.time.sleep") as mock_sleep:
            with pytest.raises(ValueError):
                retry(max_attempts=3, base_delay=1.0, jitter=False)(func)()
        # попытки 0 и 1 — задержки 1.0 и 2.0; попытка 2 — последняя, сна нет
        calls = [c.args[0] for c in mock_sleep.call_args_list]
        assert calls == [1.0, 2.0]

    def test_delay_capped_at_max_delay(self):
        func, _ = make_flaky(5)
        with patch("src.utils.retry.time.sleep") as mock_sleep:
            with pytest.raises(ValueError):
                retry(
                    max_attempts=5, base_delay=10.0, max_delay=15.0, jitter=False
                )(func)()
        for call in mock_sleep.call_args_list:
            assert call.args[0] <= 15.0

    def test_no_sleep_after_last_attempt(self):
        func, _ = make_flaky(3)
        with patch("src.utils.retry.time.sleep") as mock_sleep:
            with pytest.raises(ValueError):
                retry(max_attempts=3, base_delay=1.0, jitter=False)(func)()
        # 3 попытки → 2 паузы (после 0-й и 1-й)
        assert mock_sleep.call_count == 2

    def test_jitter_stays_within_bounds(self):
        func, _ = make_flaky(2)
        delays = []

        def fake_sleep(d):
            delays.append(d)

        with patch("src.utils.retry.time.sleep", side_effect=fake_sleep):
            with patch("src.utils.retry.random.random", return_value=0.0):
                retry(max_attempts=3, base_delay=2.0, jitter=True)(func)()

        # random() == 0.0 → множитель 0.5 → delay = base * 0.5
        assert delays[0] == pytest.approx(1.0)

    def test_jitter_upper_bound(self):
        func, _ = make_flaky(2)
        delays = []

        def fake_sleep(d):
            delays.append(d)

        with patch("src.utils.retry.time.sleep", side_effect=fake_sleep):
            with patch("src.utils.retry.random.random", return_value=1.0):
                retry(max_attempts=3, base_delay=2.0, jitter=True)(func)()

        # random() == 1.0 → множитель 1.5 → delay = base * 1.5
        assert delays[0] == pytest.approx(3.0)
