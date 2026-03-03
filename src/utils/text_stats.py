# Plan:
# 1. Принять строку текста на вход
# 2. Подсчитать общее число символов (с пробелами и без)
# 3. Подсчитать число слов (split по пробельным символам)
# 4. Подсчитать число строк
# 5. Вернуть структуру TextStats с результатами
# 6. Предоставить CLI-вывод при запуске как скрипт

import sys
from dataclasses import dataclass


@dataclass
class TextStats:
    char_count: int          # символов всего (включая пробелы)
    char_count_no_spaces: int  # символов без пробелов
    word_count: int          # слов
    line_count: int          # строк


def analyze(text: str) -> TextStats:
    """Возвращает статистику по тексту.

    Args:
        text: Произвольная строка для анализа.

    Returns:
        TextStats с количеством символов, слов и строк.
    """
    return TextStats(
        char_count=len(text),
        char_count_no_spaces=sum(1 for c in text if not c.isspace()),
        word_count=len(text.split()),
        line_count=len(text.splitlines()) if text else 0,
    )


if __name__ == "__main__":
    if not sys.stdin.isatty():
        text = sys.stdin.read()
    else:
        print("Введите текст (Ctrl+D для завершения):")
        text = sys.stdin.read()

    stats = analyze(text)
    print(f"Символов (с пробелами)  : {stats.char_count}")
    print(f"Символов (без пробелов) : {stats.char_count_no_spaces}")
    print(f"Слов                    : {stats.word_count}")
    print(f"Строк                   : {stats.line_count}")
