# cc_practice

Добро пожаловать! Это учебный проект с набором вспомогательных утилит на Python 3.11+.
Здесь вы найдёте примеры работы с HTTP-запросами, декораторами и тестированием.

---

## check_status_mailru

Проверяет доступность сайта https://mail.ru через HTTPS HEAD-запрос.

### Запуск из командной строки

```bash
python -m src.utils.check_status_mailru
```

Пример вывода, когда сайт доступен:

```
[UP] https://mail.ru
  HTTP status : 200
  Response    : 143.7 ms
```

Пример вывода, когда сайт недоступен:

```
[DOWN] https://mail.ru
  Error       : [Errno -2] Name or service not known
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

Проверка произвольного URL с кастомным таймаутом:

```python
result = check_status(url="https://example.com", timeout=5)
print(result.status_code)  # например, 200
```

### Возвращаемый объект `CheckResult`

| Поле               | Тип            | Описание                                      |
|--------------------|----------------|-----------------------------------------------|
| `available`        | `bool`         | `True`, если HTTP-статус < 400                |
| `status_code`      | `int \| None`  | HTTP-статус ответа, `None` при сетевой ошибке |
| `response_time_ms` | `float \| None`| Время ответа в миллисекундах                  |
| `error`            | `str \| None`  | Описание ошибки, `None` при успехе            |

### Запуск тестов

```bash
python -m pytest src/tests/test_check_status_mailru.py -v
```

---

## Контакты

Автор: **Ivan Petrov**
Email: ivan.petrov@example.com
GitHub: https://github.com/ivan-petrov
