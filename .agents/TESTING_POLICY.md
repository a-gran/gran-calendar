# Правила проверок

Проверки выбираются по типу изменения.

## Только документация

Достаточно:

- проверить `git status --short`;
- убедиться, какие файлы изменены;
- явно указать, что код не менялся.

## Python-код

Минимальная проверка синтаксиса:

```bash
uv run python -m py_compile main.py domain/__init__.py domain/clock.py domain/event.py domain/event_factory.py domain/event_index.py domain/event_limits.py domain/event_status.py domain/event_update.py domain/history_manager.py services/__init__.py services/event_service.py storage/__init__.py storage/event_storage.py ui/__init__.py ui/calendar_window.py ui/calendar_grid.py
```

Проверка создания окна без полноценного GUI:

```bash
QT_QPA_PLATFORM=offscreen uv run python -c "from PySide6.QtWidgets import QApplication; from ui.calendar_window import CalendarWindow; app = QApplication([]); window = CalendarWindow(); print(window.windowTitle())"
```

## Если `uv` не может писать в кеш

В ограниченной среде можно временно указать кеш в `/tmp`:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m py_compile main.py domain/__init__.py domain/clock.py domain/event.py domain/event_factory.py domain/event_index.py domain/event_limits.py domain/event_status.py domain/event_update.py domain/history_manager.py services/__init__.py services/event_service.py storage/__init__.py storage/event_storage.py ui/__init__.py ui/calendar_window.py ui/calendar_grid.py
```

Обязательные линтеры и автотесты:

```bash
QT_QPA_PLATFORM=offscreen UV_CACHE_DIR=/tmp/uv-cache uv run ruff check .
QT_QPA_PLATFORM=offscreen UV_CACHE_DIR=/tmp/uv-cache uv run ruff format --check .
QT_QPA_PLATFORM=offscreen UV_CACHE_DIR=/tmp/uv-cache uv run pytest
```

## Автотесты проекта

Основная команда автотестов:

```bash
QT_QPA_PLATFORM=offscreen UV_CACHE_DIR=/tmp/uv-cache uv run pytest
```

## Узкие изменения

Если изменение маленькое и затрагивает один модуль, можно запускать ближайшую релевантную проверку.

Если проверку невозможно запустить, нужно явно написать причину.
