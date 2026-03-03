# Created: 2026-03-03 16:44:10
#
# Plan:
# 1. Принять месяц (1-12) и год на вход
# 2. Учесть високосный год для февраля (делится на 4, кроме 100, кроме 400)
# 3. Вернуть количество дней
# 4. Валидировать входные данные — бросать ValueError при некорректных значениях
# 5. Предоставить CLI-вывод при запуске как скрипт

import sys
import calendar


def days_in_month(month: int, year: int) -> int:
    """Возвращает количество дней в указанном месяце.

    Args:
        month: Номер месяца (1-12).
        year: Год (например, 2026).

    Returns:
        Количество дней в месяце.

    Raises:
        ValueError: Если month не в диапазоне 1-12 или year <= 0.
    """
    if not 1 <= month <= 12:
        raise ValueError(f"Некорректный месяц: {month}. Ожидается значение от 1 до 12.")
    if year <= 0:
        raise ValueError(f"Некорректный год: {year}. Ожидается положительное число.")

    return calendar.monthrange(month=month, year=year)[1]


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 2:
        print("Использование: python -m src.utils.days_in_month <месяц> <год>")
        print("Пример: python -m src.utils.days_in_month 2 2026")
        sys.exit(1)

    try:
        month, year = int(args[0]), int(args[1])
        days = days_in_month(month, year)
        print(f"{year}-{month:02d}: {days} дней")
    except ValueError as e:
        print(f"Ошибка: {e}")
        sys.exit(1)
