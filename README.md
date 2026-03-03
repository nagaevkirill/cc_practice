# cc_practice

Добро пожаловать! Это учебный проект с набором вспомогательных утилит на Python 3.11+.
Здесь вы найдёте примеры работы с HTTP-запросами, декораторами и тестированием.

---

## Утилиты

| Утилита | Описание |
|---|---|
| `check_status_mailru` | Проверка доступности сайта mail.ru |
| `response_time` | Измерение времени отклика сайта |
| `retry` | Декоратор повторных попыток с экспоненциальным backoff |
| `text_stats` | Подсчёт символов, слов и строк в тексте |
| `strip_empty_lines` | Удаление пустых строк из текста |
| `days_in_month` | Количество дней в месяце с учётом високосного года |

---

## check_status_mailru

Проверяет доступность сайта https://mail.ru через HTTPS HEAD-запрос.

### Запуск из командной строки

```bash
python -m src.utils.check_status_mailru
```

Пример вывода:

```
[UP] https://mail.ru
  HTTP status : 200
  Response    : 143.7 ms
```

### Использование в коде

```python
from src.utils.check_status_mailru import check_status

result = check_status()

if result.available:
    print(f"Сайт доступен, ответил за {result.response_time_ms} мс")
else:
    print(f"Сайт недоступен: {result.error}")
```

### Возвращаемый объект `CheckResult`

| Поле               | Тип             | Описание                                      |
|--------------------|-----------------|-----------------------------------------------|
| `available`        | `bool`          | `True`, если HTTP-статус < 400                |
| `status_code`      | `int \| None`   | HTTP-статус ответа, `None` при сетевой ошибке |
| `response_time_ms` | `float \| None` | Время ответа в миллисекундах                  |
| `error`            | `str \| None`   | Описание ошибки, `None` при успехе            |

### Запуск тестов

```bash
python -m pytest src/tests/test_check_status_mailru.py -v
```

---

## response_time

Измеряет время отклика сайта через HEAD-запрос с усреднением по нескольким замерам.
Для доменов `.ru` возвращает время в миллисекундах, для остальных — в секундах.

### Запуск из командной строки

```bash
python -m src.utils.response_time https://example.com 3
```

Пример вывода:

```
[OK] https://example.com
  Статус      : 200
  Среднее     : 0.213 s
  Замеров     : 3/3
```

### Использование в коде

```python
from src.utils.response_time import measure_response_time

result = measure_response_time("https://mail.ru", attempts=3)
print(f"{result.response_time} {result.time_unit}")  # например: 142.5 ms
```

### Возвращаемый объект `ResponseTimeResult`

| Поле            | Тип             | Описание                                  |
|-----------------|-----------------|-------------------------------------------|
| `url`           | `str`           | Проверяемый URL                           |
| `response_time` | `float \| None` | Среднее время отклика                     |
| `time_unit`     | `str`           | Единица измерения: `"ms"` или `"s"`       |
| `status_code`   | `int \| None`   | HTTP-статус последнего ответа             |
| `attempts`      | `int`           | Запрошенное количество замеров            |
| `successful`    | `int`           | Количество успешных замеров               |
| `error`         | `str \| None`   | Описание ошибки, `None` при успехе        |

### Запуск тестов

```bash
python -m pytest src/tests/test_response_time.py -v
```

---

## retry

Декоратор для повторного вызова функции при ошибке с экспоненциальным backoff и jitter.

### Использование в коде

```python
from src.utils.retry import retry

@retry(max_attempts=5, base_delay=1.0, exceptions=(IOError, TimeoutError))
def fetch_data(url: str) -> bytes:
    ...
```

### Параметры декоратора

| Параметр      | По умолчанию    | Описание                                       |
|---------------|-----------------|------------------------------------------------|
| `max_attempts`| `3`             | Максимальное число попыток (включая первую)    |
| `base_delay`  | `1.0`           | Начальная задержка в секундах                  |
| `max_delay`   | `60.0`          | Максимальная задержка в секундах               |
| `exceptions`  | `(Exception,)`  | Типы исключений для перехвата                  |
| `jitter`      | `True`          | Случайный разброс задержки ±50%                |

### Запуск тестов

```bash
python -m pytest src/tests/test_retry.py -v
```

---

## text_stats

Подсчитывает количество символов, слов и строк в тексте.

### Запуск из командной строки

```bash
echo "Привет мир" | python -m src.utils.text_stats
```

Пример вывода:

```
Символов (с пробелами)  : 10
Символов (без пробелов) : 9
Слов                    : 2
Строк                   : 1
```

### Использование в коде

```python
from src.utils.text_stats import analyze

result = analyze("Привет мир\nКак дела?")
print(result.word_count)        # 4
print(result.char_count)        # 20
print(result.line_count)        # 2
```

### Возвращаемый объект `TextStats`

| Поле                   | Тип   | Описание                        |
|------------------------|-------|---------------------------------|
| `char_count`           | `int` | Символов всего (с пробелами)    |
| `char_count_no_spaces` | `int` | Символов без пробельных знаков  |
| `word_count`           | `int` | Количество слов                 |
| `line_count`           | `int` | Количество строк                |

### Запуск тестов

```bash
python -m pytest src/tests/test_text_stats.py -v
```

---

## strip_empty_lines

Удаляет пустые строки из текста. Строка считается пустой, если содержит только пробельные символы.

### Запуск из командной строки

```bash
cat file.txt | python -m src.utils.strip_empty_lines
```

### Использование в коде

```python
from src.utils.strip_empty_lines import strip_empty_lines

text = "line one\n\nline two\n   \nline three\n"
print(strip_empty_lines(text))
# line one
# line two
# line three
```

### Запуск тестов

```bash
python -m pytest src/tests/test_strip_empty_lines.py -v
```

---

## days_in_month

Возвращает количество дней в указанном месяце с учётом високосного года.

### Запуск из командной строки

```bash
python -m src.utils.days_in_month 2 2024
```

Пример вывода:

```
2024-02: 29 дней
```

### Использование в коде

```python
from src.utils.days_in_month import days_in_month

print(days_in_month(2, 2024))  # 29 (високосный год)
print(days_in_month(2, 2026))  # 28
print(days_in_month(12, 2026)) # 31
```

### Запуск тестов

```bash
python -m pytest src/tests/test_days_in_month.py -v
```

---

## Запуск всех тестов

```bash
python -m pytest src/tests/ -v
```

---

## Контакты

Автор: **Ivan Petrov**
Email: ivan.petrov@example.com
GitHub: https://github.com/ivan-petrov
