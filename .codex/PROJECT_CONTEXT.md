# Контекст проекта

Проект - Calendar Planner, desktop-приложение для личного планирования в форме календаря.

Цель проекта - сделать простой календарный планировщик без Obsidian, Google Calendar и лишних функций.

Основной стек:

- Python;
- PySide6;
- SQLite;
- uv;
- будущая синхронизация через GitLab.

Текущий режим работы - локальное desktop-приложение.

Ключевые файлы и папки:

- `main.py` - точка входа;
- `domain/clock.py` - получение текущего времени;
- `domain/event.py` - модель события;
- `domain/event_limits.py` - ограничения полей события;
- `domain/event_status.py` - статусы событий и связанные цвета;
- `domain/event_factory.py` - создание новых событий и копий;
- `domain/event_index.py` - индексация, сортировка и поиск событий;
- `domain/event_update.py` - применение снимка события к существующему событию;
- `domain/history_manager.py` - управление стеками undo и redo;
- `services/event_service.py` - операции добавления и удаления событий через storage;
- `storage/event_storage.py` - SQLite-хранилище событий;
- `ui/calendar_window.py` - главное окно календаря;
- `ui/calendar_window_state.py` - начальное состояние главного окна;
- `ui/calendar_window_widgets.py` - создание виджетов главного окна;
- `ui/calendar_window_connections.py` - подключения сигналов главного окна;
- `ui/calendar_window_layout.py` - сборка layout главного окна;
- `ui/calendar_shortcuts.py` - горячие клавиши главного окна;
- `ui/calendar_grid.py` - кастомная календарная сетка;
- `docs/` - документация проекта;
- `.agents/` - инструкции для агентов;
- `.codex/` - рабочий контекст Codex.
