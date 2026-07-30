# Инструкции для агентов

Этот файл описывает правила работы с проектом Calendar Planner.
Его нужно читать перед любыми изменениями в коде или документации.

## Язык общения

Всегда отвечать пользователю на русском языке, если пользователь явно не попросил другой язык.

## Согласование изменений

Перед изменением файлов нужно изучить текущие файлы и понять затрагиваемую область.

Diff перед изменениями показывать не нужно, если пользователь отдельно не попросил об этом.

## Комментарии в коде

Комментарии писать над стркоами, подробно, как ребенку, что происходит в коде, но только тогда, когда
я отдельно явно указал это в запросе.

## Назначение проекта

Calendar Planner - desktop-приложение для личного планирования в форме календаря.

Проект не является плагином Obsidian.
Проект не использует Google Calendar.
Проект должен оставаться минималистичным и не превращаться в перегруженный календарный сервис.

## Текущий стек

- Python;
- PySide6;
- SQLite;
- uv для виртуального окружения и запуска;
- будущая синхронизация через GitLab.

## Текущая структура

- `main.py` - точка запуска приложения.
- `domain/event.py` - модель события.
- `domain/clock.py` - получение текущего времени.
- `domain/event_limits.py` - ограничения полей события.
- `domain/event_status.py` - статусы событий.
- `domain/event_factory.py` - создание новых событий и копий.
- `domain/event_index.py` - индексация, сортировка и поиск событий.
- `services/event_service.py` - операции добавления и удаления событий через storage.
- `storage/event_storage.py` - SQLite-хранилище.
- `ui/calendar_window.py` - главное окно календаря.
- `ui/calendar_window_state.py` - начальное состояние главного окна.
- `ui/calendar_window_widgets.py` - создание виджетов главного окна.
- `ui/calendar_window_connections.py` - подключения сигналов главного окна.
- `ui/calendar_window_layout.py` - сборка layout главного окна.
- `ui/calendar_shortcuts.py` - горячие клавиши главного окна.
- `ui/calendar_grid.py` - кастомная календарная сетка.
- `docs/` - пользовательская и техническая документация.
- `.agents/` - инструкции для агентов.
- `.codex/` - рабочий контекст Codex, который нужно проверять на актуальность.

## Документация, которую нужно учитывать

Перед разработкой читать:

- `README.md`;
- `docs/architecture.md`;
- `docs/usage.md`;
- `docs/hotkeys.md`;
- `docs/gitlab-sync.md`;
- `.agents/CODEX_RULES.md`;
- `.agents/WORKFLOW.md`;
- `.agents/STYLE_GUIDE.md`;
- `.agents/TESTING_POLICY.md`;
- `.agents/DOCUMENTATION_POLICY.md`;
- `.agents/CODEX_AUDIT.md`, если файл существует.

Документы из `.codex/` описывают рабочий контекст Calendar Planner.
Если содержимое `.codex/` и `docs/` расходится, нужно остановиться, указать расхождение пользователю и не угадывать.

## Правила разработки

- Сохранять простую архитектуру.
- Не добавлять лишние функции без явной необходимости.
- Предпочитать существующие слои проекта: `ui`, `domain`, `services`, `storage`.
- Не смешивать UI, доменную модель и SQLite-логику в одном файле.
- Обновлять документацию вместе с изменением поведения приложения.
- Не коммитить `calendar.db`, `__pycache__/`, `*.pyc`.
- Не удалять пользовательские изменения без прямого разрешения.

## Проверки после изменений

Минимальные проверки после изменения Python-кода:

```bash
uv run python -m py_compile main.py domain/__init__.py domain/clock.py domain/event.py domain/event_factory.py domain/event_index.py domain/event_limits.py domain/event_status.py domain/event_update.py domain/history_manager.py services/__init__.py services/event_service.py storage/__init__.py storage/event_storage.py ui/__init__.py ui/calendar_window.py ui/calendar_grid.py
```

Проверка создания окна без полноценного GUI:

```bash
QT_QPA_PLATFORM=offscreen uv run python -c "from PySide6.QtWidgets import QApplication; from ui.calendar_window import CalendarWindow; app = QApplication([]); window = CalendarWindow(); print(window.windowTitle())"
```

## Запуск приложения

Создать окружение:

```bash
uv venv
```

Активировать окружение:

```bash
source .venv/bin/activate
```

Установить зависимости:

```bash
uv sync
```

Запустить приложение:

```bash
uv run python main.py
```

Запуск без активации окружения:

```bash
uv run python main.py
```
