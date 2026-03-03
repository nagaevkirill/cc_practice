# Plan:
# 1. Отправить HEAD-запрос на https://mail.ru (HEAD легче GET — не тянет тело)
# 2. Считать сайт доступным при HTTP 200-399
# 3. При сетевой ошибке или таймауте — недоступен
# 4. Вернуть структуру с флагом доступности, статус-кодом и временем ответа
# 5. Предоставить удобный CLI-вывод при запуске как скрипт

import time
import urllib.request
import urllib.error
from dataclasses import dataclass


TARGET_URL = "https://mail.ru"
TIMEOUT = 10  # секунд


@dataclass
class CheckResult:
    available: bool
    status_code: int | None
    response_time_ms: float | None
    error: str | None = None


def check_status(url: str = TARGET_URL, timeout: int = TIMEOUT) -> CheckResult:
    """Проверяет доступность сайта через HEAD-запрос.

    Args:
        url: URL для проверки.
        timeout: Таймаут соединения в секундах.

    Returns:
        CheckResult с флагом доступности, статус-кодом и временем ответа.
    """
    request = urllib.request.Request(url, method="HEAD")
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            elapsed_ms = (time.perf_counter() - start) * 1000
            return CheckResult(
                available=True,
                status_code=response.status,
                response_time_ms=round(elapsed_ms, 1),
            )
    except urllib.error.HTTPError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        available = exc.code < 400
        return CheckResult(
            available=available,
            status_code=exc.code,
            response_time_ms=round(elapsed_ms, 1),
            error=str(exc) if not available else None,
        )
    except urllib.error.URLError as exc:
        return CheckResult(
            available=False,
            status_code=None,
            response_time_ms=None,
            error=str(exc.reason),
        )
    except TimeoutError:
        return CheckResult(
            available=False,
            status_code=None,
            response_time_ms=None,
            error=f"Timeout after {timeout}s",
        )


if __name__ == "__main__":
    result = check_status()
    status = "UP" if result.available else "DOWN"
    print(f"[{status}] {TARGET_URL}")
    if result.status_code:
        print(f"  HTTP status : {result.status_code}")
    if result.response_time_ms is not None:
        print(f"  Response    : {result.response_time_ms} ms")
    if result.error:
        print(f"  Error       : {result.error}")
