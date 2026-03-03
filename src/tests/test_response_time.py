import urllib.error
from io import BytesIO
from unittest.mock import patch, MagicMock

import pytest

from src.utils.response_time import measure_response_time, ResponseTimeResult, _is_ru_domain


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_response(status: int) -> MagicMock:
    resp = MagicMock()
    resp.status = status
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def make_http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        url="https://example.com", code=code, msg="err", hdrs={}, fp=BytesIO()
    )


# ---------------------------------------------------------------------------
# _is_ru_domain
# ---------------------------------------------------------------------------

class TestIsRuDomain:
    def test_ru_tld(self):
        assert _is_ru_domain("https://mail.ru") is True

    def test_ru_subdomain(self):
        assert _is_ru_domain("https://www.yandex.ru") is True

    def test_com_tld(self):
        assert _is_ru_domain("https://example.com") is False

    def test_co_uk_tld(self):
        assert _is_ru_domain("https://google.co.uk") is False

    def test_org_tld(self):
        assert _is_ru_domain("https://wikipedia.org") is False


# ---------------------------------------------------------------------------
# Единицы измерения
# ---------------------------------------------------------------------------

class TestTimeUnits:
    def test_ru_domain_returns_ms(self):
        with patch("urllib.request.urlopen", return_value=make_response(200)):
            result = measure_response_time("https://mail.ru", attempts=1)
        assert result.time_unit == "ms"

    def test_non_ru_domain_returns_seconds(self):
        with patch("urllib.request.urlopen", return_value=make_response(200)):
            result = measure_response_time("https://example.com", attempts=1)
        assert result.time_unit == "s"

    def test_ru_response_time_in_ms_range(self):
        with patch("urllib.request.urlopen", return_value=make_response(200)):
            result = measure_response_time("https://mail.ru", attempts=1)
        # миллисекунды — значение >= 0
        assert result.response_time >= 0

    def test_non_ru_response_time_in_seconds_range(self):
        with patch("urllib.request.urlopen", return_value=make_response(200)):
            result = measure_response_time("https://example.com", attempts=1)
        # секунды — значение должно быть меньше, чем миллисекунды
        assert result.response_time < 1000


# ---------------------------------------------------------------------------
# Базовое поведение
# ---------------------------------------------------------------------------

class TestMeasureResponseTime:
    def test_returns_result_instance(self):
        with patch("urllib.request.urlopen", return_value=make_response(200)):
            result = measure_response_time("https://example.com", attempts=1)
        assert isinstance(result, ResponseTimeResult)

    def test_successful_request(self):
        with patch("urllib.request.urlopen", return_value=make_response(200)):
            result = measure_response_time("https://example.com", attempts=1)
        assert result.status_code == 200
        assert result.successful == 1
        assert result.error is None

    def test_attempts_count(self):
        with patch("urllib.request.urlopen", return_value=make_response(200)):
            result = measure_response_time("https://example.com", attempts=3)
        assert result.attempts == 3
        assert result.successful == 3

    def test_http_error_counted_as_successful(self):
        with patch("urllib.request.urlopen", side_effect=make_http_error(404)):
            result = measure_response_time("https://example.com", attempts=2)
        assert result.successful == 2
        assert result.status_code == 404

    def test_network_error_returns_error(self):
        exc = urllib.error.URLError(reason="Name not known")
        with patch("urllib.request.urlopen", side_effect=exc):
            result = measure_response_time("https://example.com", attempts=1)
        assert result.successful == 0
        assert result.response_time is None
        assert result.error is not None

    def test_timeout_error(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError):
            result = measure_response_time("https://example.com", attempts=1, timeout=5)
        assert result.successful == 0
        assert "5" in result.error

    def test_invalid_attempts_raises(self):
        with pytest.raises(ValueError, match="attempts"):
            measure_response_time("https://example.com", attempts=0)

    def test_response_time_is_none_on_full_failure(self):
        exc = urllib.error.URLError(reason="err")
        with patch("urllib.request.urlopen", side_effect=exc):
            result = measure_response_time("https://example.com", attempts=2)
        assert result.response_time is None
