# Created: 2026-03-03 16:44:10
#
# Plan:
# 1. Отправить HTTP HEAD-запрос к указанному URL
# 2. Замерить время от отправки до получения ответа через time.perf_counter()
# 3. Вернуть датакласс ResponseTimeResult с url, response_time_ms, status_code, error
# 4. Поддержать несколько замеров с усреднением (параметр attempts)
# 5. CLI-вывод при запуске как скрипт

import sys
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class ResponseTimeResult:
    url: str
    response_time: float | None  # значение в единицах time_unit
    time_unit: str               # "ms" для .ru, "s" для остальных
    status_code: int | None
    attempts: int
    successful: int
    error: str | None = None


def _is_ru_domain(url: str) -> bool:
    """Возвращает True, если TLD домена — ru."""
    hostname = urlparse(url).hostname or ""
    return hostname.lower().rstrip(".").rsplit(".", 1)[-1] == "ru"


def measure_response_time(
    url: str,
    attempts: int = 3,
    timeout: int = 10,
) -> ResponseTimeResult:
    """Измеряет время отклика сайта через HEAD-запрос.

    Для доменов .ru возвращает время в миллисекундах, для остальных — в секундах.

    Args:
        url: URL для проверки.
        attempts: Количество замеров для усреднения.
        timeout: Таймаут одного запроса в секундах.

    Returns:
        ResponseTimeResult со средним временем отклика и статус-кодом.
    """
    if attempts < 1:
        raise ValueError("attempts должно быть >= 1")

    times = []
    status_code = None
    last_error = None

    for _ in range(attempts):
        request = urllib.request.Request(url, method="HEAD")
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                elapsed_ms = (time.perf_counter() - start) * 1000
                times.append(elapsed_ms)
                status_code = response.status
        except urllib.error.HTTPError as exc:
            elapsed_ms = (time.perf_counter() - start) * 1000
            times.append(elapsed_ms)
            status_code = exc.code
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc.reason) if isinstance(exc, urllib.error.URLError) else f"Timeout after {timeout}s"

    avg_ms = sum(times) / len(times) if times else None

    if avg_ms is not None and not _is_ru_domain(url):
        response_time = round(avg_ms / 1000, 3)
        time_unit = "s"
    else:
        response_time = round(avg_ms, 1) if avg_ms is not None else None
        time_unit = "ms"

    return ResponseTimeResult(
        url=url,
        response_time=response_time,
        time_unit=time_unit,
        status_code=status_code,
        attempts=attempts,
        successful=len(times),
        error=last_error if not times else None,
    )


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Использование: python -m src.utils.response_time <url> [attempts]")
        print("Пример: python -m src.utils.response_time https://example.com 3")
        sys.exit(1)

    url = args[0]
    attempts = int(args[1]) if len(args) > 1 else 3

    result = measure_response_time(url, attempts=attempts)

    if result.error:
        print(f"[ERROR] {result.url}")
        print(f"  Ошибка : {result.error}")
    else:
        print(f"[OK] {result.url}")
        print(f"  Статус      : {result.status_code}")
        print(f"  Среднее     : {result.response_time} {result.time_unit}")
        print(f"  Замеров     : {result.successful}/{result.attempts}")
