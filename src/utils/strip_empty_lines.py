# Created: 2026-03-03 16:44:10
#
# Plan:
# 1. Разбить текст на строки через splitlines()
# 2. Отфильтровать строки, состоящие только из пробельных символов
# 3. Собрать обратно через join с сохранением оригинального разделителя строк
# 4. Вернуть результат
# 5. Предоставить CLI-вывод при запуске как скрипт

import sys


def strip_empty_lines(text: str) -> str:
    """Удаляет пустые строки из текста.

    Строка считается пустой, если она содержит только пробельные символы
    (пробелы, табуляции и т.п.).

    Args:
        text: Исходный текст.

    Returns:
        Текст без пустых строк.
    """
    lines = text.splitlines(keepends=True)
    return "".join(line for line in lines if line.strip())


if __name__ == "__main__":
    text = sys.stdin.read()
    sys.stdout.write(strip_empty_lines(text))
