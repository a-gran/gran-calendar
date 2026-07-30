# Упаковка и локальная установка

Этот документ описывает, как собрать Calendar Planner и установить его как desktop-приложение
для текущего пользователя в Kali.

## Главная идея

Программа и пользовательские данные хранятся отдельно.

Установленная программа:

```text
~/.local/opt/calendar-planner/
```

Пользовательские события:

```text
~/.local/share/calendar-planner/calendar.db
```

При обновлении программы папка `~/.local/opt/calendar-planner/` пересоздается.
База `calendar.db` при этом не удаляется и не перезаписывается.

## Собрать приложение

```bash
make build-app
```

Сборка создается в папке:

```text
dist/CalendarPlanner/
```

В сборку не нужно добавлять `calendar.db`, тесты, документацию и служебные папки проекта.

## Установить или обновить приложение

Перед новой сборкой обновите версию в `pyproject.toml`:

```toml
version = "0.1.1"
```

```bash
make install-local
```

Команда:

- собирает приложение;
- копирует новую версию в `~/.local/opt/calendar-planner/`;
- записывает версию в `~/.local/opt/calendar-planner/VERSION`;
- устанавливает иконку;
- создает desktop-ярлык `~/.local/share/applications/calendar-planner.desktop`.

Версия также показывается в заголовке окна приложения.

После этого приложение можно запускать из меню рабочего стола или через desktop-ярлык.

## Проверить установленный файл

```bash
~/.local/opt/calendar-planner/CalendarPlanner
```

## Удалить установленную программу

```bash
make uninstall-local
```

Команда удаляет установленную программу, desktop-ярлык и иконку.
Файл `~/.local/share/calendar-planner/calendar.db` не удаляется.

## Где остаются события

События сохраняются в:

```text
~/.local/share/calendar-planner/calendar.db
```

Этот файл не входит в сборку и не должен удаляться при обновлении установленной программы.
