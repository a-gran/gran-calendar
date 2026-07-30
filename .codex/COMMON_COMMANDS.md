# Частые команды

Создать виртуальное окружение:

```bash
uv venv
```

Установить зависимости из `pyproject.toml` и `uv.lock`:

```bash
uv sync
```

Запустить приложение:

```bash
uv run python main.py
```

Проверить компиляцию Python-файлов:

```bash
uv run python -m py_compile main.py domain/__init__.py domain/clock.py domain/event.py domain/event_factory.py domain/event_index.py domain/event_limits.py domain/event_status.py domain/event_update.py domain/history_manager.py services/__init__.py services/event_service.py storage/__init__.py storage/event_storage.py ui/__init__.py ui/calendar_window.py ui/calendar_grid.py
```

Проверить создание окна без полноценного GUI:

```bash
QT_QPA_PLATFORM=offscreen uv run python -c "from PySide6.QtWidgets import QApplication; from ui.calendar_window import CalendarWindow; app = QApplication([]); window = CalendarWindow(); print(window.windowTitle())"
```

Если `uv` не может писать в кеш в ограниченной среде:

```bash
UV_CACHE_DIR=/tmp/uv-cache uv run python -m py_compile main.py domain/__init__.py domain/clock.py domain/event.py domain/event_factory.py domain/event_index.py domain/event_limits.py domain/event_status.py domain/event_update.py domain/history_manager.py services/__init__.py services/event_service.py storage/__init__.py storage/event_storage.py ui/__init__.py ui/calendar_window.py ui/calendar_grid.py
```

Проверить статус git:

```bash
git status --short
```

Запустить полный локальный набор проверок:

```bash
make check
```
