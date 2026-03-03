import urllib.error
from io import BytesIO
from unittest.mock import patch, MagicMock

from src.utils.check_status_mailru import check_status, CheckResult, TARGET_URL


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_response(status: int) -> MagicMock:
    """Фейковый urllib response с атрибутом status."""
    resp = MagicMock()
    resp.status = status
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


def make_http_error(code: int) -> urllib.error.HTTPError:
    return urllib.error.HTTPError(
        url=TARGET_URL, code=code, msg="err", hdrs={}, fp=BytesIO()
    )


# ---------------------------------------------------------------------------
# Успешные ответы
# ---------------------------------------------------------------------------

class TestCheckStatusSuccess:
    def test_returns_available_on_200(self):
        with patch("urllib.request.urlopen", return_value=make_response(200)):
            result = check_status()
        assert result.available is True
        assert result.status_code == 200
        assert result.error is None

    def test_response_time_populated(self):
        with patch("urllib.request.urlopen", return_value=make_response(200)):
            result = check_status()
        assert result.response_time_ms is not None
        assert result.response_time_ms >= 0

    def test_returns_available_on_301(self):
        with patch("urllib.request.urlopen", return_value=make_response(301)):
            result = check_status()
        assert result.available is True
        assert result.status_code == 301

    def test_custom_url_passed_to_request(self):
        custom_url = "https://example.com"
        captured = {}

        def fake_urlopen(req, timeout):
            captured["url"] = req.full_url
            return make_response(200)

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            check_status(url=custom_url)

        assert captured["url"] == custom_url


# ---------------------------------------------------------------------------
# HTTP-ошибки
# ---------------------------------------------------------------------------

class TestCheckStatusHTTPError:
    def test_404_returns_unavailable(self):
        with patch("urllib.request.urlopen", side_effect=make_http_error(404)):
            result = check_status()
        assert result.available is False
        assert result.status_code == 404
        assert result.error is not None

    def test_500_returns_unavailable(self):
        with patch("urllib.request.urlopen", side_effect=make_http_error(500)):
            result = check_status()
        assert result.available is False
        assert result.status_code == 500

    def test_301_via_http_error_returns_available(self):
        """HTTPError с кодом < 400 считается доступным (редирект без follow)."""
        with patch("urllib.request.urlopen", side_effect=make_http_error(301)):
            result = check_status()
        assert result.available is True
        assert result.error is None

    def test_http_error_response_time_populated(self):
        with patch("urllib.request.urlopen", side_effect=make_http_error(503)):
            result = check_status()
        assert result.response_time_ms is not None


# ---------------------------------------------------------------------------
# Сетевые ошибки
# ---------------------------------------------------------------------------

class TestCheckStatusNetworkError:
    def test_url_error_returns_unavailable(self):
        exc = urllib.error.URLError(reason="Name or service not known")
        with patch("urllib.request.urlopen", side_effect=exc):
            result = check_status()
        assert result.available is False
        assert result.status_code is None
        assert result.response_time_ms is None
        assert "Name or service not known" in result.error

    def test_timeout_returns_unavailable(self):
        with patch("urllib.request.urlopen", side_effect=TimeoutError):
            result = check_status(timeout=5)
        assert result.available is False
        assert result.status_code is None
        assert result.response_time_ms is None
        assert "5" in result.error


# ---------------------------------------------------------------------------
# Возвращаемый тип
# ---------------------------------------------------------------------------

class TestCheckResult:
    def test_returns_check_result_instance(self):
        with patch("urllib.request.urlopen", return_value=make_response(200)):
            result = check_status()
        assert isinstance(result, CheckResult)

    def test_error_is_none_on_success(self):
        with patch("urllib.request.urlopen", return_value=make_response(200)):
            result = check_status()
        assert result.error is None
