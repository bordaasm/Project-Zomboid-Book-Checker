# PZ Build 42 Book Checker

## English

A small Windows checklist for Project Zomboid Build 42 skill books.

For normal use, download the ready-made executable from Releases and run:

```text
PZBookChecker.exe
```

You do not need Python to run the executable.

Features:
- mark found volumes I-V;
- light and dark themes;
- English by default, with RU/EN language switch;
- incomplete-topic filter and search;
- saves progress, theme, and language automatically;
- uses Project Zomboid-style book images from `Src/img`.

Saved data location:

```text
C:\Users\<your user name>\Zomboid\Book Checker\pz_books_progress.json
```

Emoji cache location:

```text
C:\Users\<your user name>\Zomboid\Book Checker\emoji_cache
```

Book data source:
https://pzwiki.net/wiki/Skill_book

Developer run:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Developer build:

```powershell
python build_exe.py
python -m PyInstaller --noconfirm --clean --windowed --onefile --name PZBookChecker --icon assets\app.ico --add-data "Src;Src" --add-data "assets;assets" main.py
```

The built executable appears in:

```text
dist\PZBookChecker.exe
```

## Русский

Небольшой Windows-чеклист книг навыков для Project Zomboid Build 42.

Для обычного использования скачайте готовый файл из Releases и запустите:

```text
PZBookChecker.exe
```

Python для запуска exe не нужен.

Возможности:
- отметка найденных томов I-V;
- светлая и темная тема;
- английский язык по умолчанию, переключение RU/EN;
- фильтр неполных тем и поиск;
- автоматическое сохранение прогресса, темы и языка;
- картинки книг в стиле Project Zomboid из `Src/img`.

Файл с данными находится здесь:

```text
C:\Users\<имя пользователя>\Zomboid\Book Checker\pz_books_progress.json
```

Кэш emoji находится здесь:

```text
C:\Users\<имя пользователя>\Zomboid\Book Checker\emoji_cache
```

Источник данных по книгам:
https://pzwiki.net/wiki/Skill_book

Запуск для разработки:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Сборка для разработки:

```powershell
python build_exe.py
python -m PyInstaller --noconfirm --clean --windowed --onefile --name PZBookChecker --icon assets\app.ico --add-data "Src;Src" --add-data "assets;assets" main.py
```

Готовый exe после сборки:

```text
dist\PZBookChecker.exe
```
