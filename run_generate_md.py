import os
import argparse
import re
from pathlib import Path
from fnmatch import fnmatch
import datetime
import chardet


def detect_encoding(file_path):
    """Определяет кодировку файла"""
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result['encoding'] or 'utf-8'


def is_text_file(file_path):
    """Проверяет, является ли файл текстовым"""
    try:
        # Список расширений, которые всегда считаются текстовыми
        text_extensions = [
            '.txt', '.py', '.json', '.yml', '.yaml', '.md',
            '.html', '.css', '.js', '.csv', '.log',
            '.ini', '.cfg', '.conf', '.xml', '.toml',
            '.rst', '.requirements', '.dockerignore', '.gitignore',
            '.env', '.sh', '.bat', '.cmd'
        ]

        # Проверяем расширение файла
        if Path(file_path).suffix.lower() in text_extensions:
            return True

        # Проверяем специфические имена файлов
        text_filenames = [
            'requirements.txt', 'Dockerfile', 'docker-compose.yml',
            '.env', 'README', 'CHANGELOG', 'CONTRIBUTING'
        ]
        if os.path.basename(file_path) in text_filenames:
            return True

        # Пытаемся прочитать файл
        encoding = detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding) as f:
            # Пробуем прочитать первые 1024 символа
            content = f.read(1024)

            # Проверяем на наличие печатных символов
            printable_chars = sum(1 for char in content if char.isprintable() or char.isspace())
            return printable_chars / len(content) > 0.8
    except (UnicodeDecodeError, IOError, ZeroDivisionError):
        return False


def parse_ignore_file(file_path):
    """Разбирает файл .gitignore или .mapignore и возвращает список шаблонов"""
    if not os.path.exists(file_path):
        return []

    patterns = []
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        for line in f:
            # Убираем комментарии и пробелы
            line = line.split('#')[0].strip()
            if line:
                # Преобразуем шаблон gitignore в регулярное выражение
                patterns.append(line)

    return patterns


def should_ignore(path, root_path, patterns):
    """Проверяет, должен ли файл или директория быть проигнорирован"""
    if not patterns:
        return False

    # Получаем относительный путь
    rel_path = str(Path(path).relative_to(root_path))
    # Также проверяем только имя файла/директории
    name = os.path.basename(path)

    for pattern in patterns:
        # Обрабатываем негативные шаблоны (которые начинаются с !)
        if pattern.startswith('!'):
            neg_pattern = pattern[1:]
            if fnmatch(rel_path, neg_pattern) or fnmatch(name, neg_pattern):
                return False
        # Обрабатываем обычные шаблоны
        elif fnmatch(rel_path, pattern) or fnmatch(name, pattern):
            return True

    return False


def generate_project_doc(root_path, output_file, ignore_dirs=None, ignore_exts=None, use_gitignore=True,
                         use_mapignore=True):
    """Генерирует Markdown документ с описанием проекта"""
    if ignore_dirs is None:
        ignore_dirs = ['.git', '__pycache__', 'node_modules', 'venv', '.idea', '.vscode']

    if ignore_exts is None:
        ignore_exts = ['.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.obj', '.class']

    root_path = Path(root_path).resolve()

    # Загружаем шаблоны из .gitignore и .mapignore
    ignore_patterns = []

    if use_gitignore:
        gitignore_path = root_path / '.gitignore'
        gitignore_patterns = parse_ignore_file(gitignore_path)
        ignore_patterns.extend(gitignore_patterns)

    if use_mapignore:
        mapignore_path = root_path / '.mapignore'
        mapignore_patterns = parse_ignore_file(mapignore_path)
        ignore_patterns.extend(mapignore_patterns)

    # Создаем выходной файл
    with open(output_file, 'w', encoding='utf-8') as f:
        # Добавляем заголовок
        project_name = root_path.name
        f.write(f"# Документация проекта {project_name}\n\n")

        # Добавляем информацию о проекте
        f.write("## Информация о проекте\n\n")
        f.write(f"- **Имя проекта**: {project_name}\n")
        f.write(f"- **Путь**: {root_path}\n")

        # Корректный вывод текущей даты
        current_date = datetime.datetime.now().strftime("%d.%m.%Y")
        f.write(f"- **Дата создания документации**: {current_date}\n\n")

        # Если есть readme, добавляем его содержимое
        readme_paths = [
            root_path / 'README.md',
            root_path / 'README.txt',
            root_path / 'Readme.md',
            root_path / 'readme.md'
        ]

        for readme_path in readme_paths:
            if readme_path.exists():
                f.write("## README\n\n")
                try:
                    readme_encoding = detect_encoding(readme_path)
                    with open(readme_path, 'r', encoding=readme_encoding) as readme_file:
                        f.write(readme_file.read() + "\n\n")
                except Exception as e:
                    f.write(f"Ошибка чтения README файла: {e}\n\n")
                break

        # Генерируем структуру дерева файлов
        f.write("## Структура проекта\n\n")
        f.write("```\n")

        # Функция для рекурсивного обхода и создания дерева
        tree_content = []

        def add_to_tree(_path, prefix=""):
            entries = sorted(os.listdir(_path))
            _files = []
            _dirs = []

            for entry in entries:
                full_path = _path / entry

                # Проверяем, нужно ли пропустить этот файл/директорию
                if should_ignore(full_path, root_path, ignore_patterns):
                    continue

                # Пропускаем игнорируемые директории
                if full_path.is_dir() and entry in ignore_dirs:
                    continue

                # Пропускаем файлы с игнорируемыми расширениями
                if full_path.is_file() and any(entry.endswith(ext) for ext in ignore_exts):
                    continue

                if full_path.is_dir():
                    _dirs.append(entry)
                else:
                    _files.append(entry)

            # Обрабатываем файлы
            for i, _file in enumerate(_files):
                is_last_file = (i == len(_files) - 1) and not _dirs
                tree_content.append(f"{prefix}{'└── ' if is_last_file else '├── '}{_file}")

            # Обрабатываем директории
            for i, dir_name in enumerate(_dirs):
                is_last_dir = (i == len(_dirs) - 1)
                tree_content.append(f"{prefix}{'└── ' if is_last_dir else '├── '}{dir_name}/")

                if is_last_dir:
                    add_to_tree(_path / dir_name, prefix + "    ")
                else:
                    add_to_tree(_path / dir_name, prefix + "│   ")

        add_to_tree(root_path)
        f.write("\n".join(tree_content))
        f.write("\n```\n\n")

        # Добавляем листинги кода
        f.write("## Листинги файлов\n\n")

        for path, dirs, files in os.walk(root_path):
            path_obj = Path(path)

            # Пропускаем директории на основе шаблонов игнорирования
            dirs[:] = [d for d in dirs if not (
                    d in ignore_dirs or
                    should_ignore(path_obj / d, root_path, ignore_patterns)
            )]

            # Сортируем файлы для удобства чтения
            files = sorted(files)

            for file in files:
                file_path = path_obj / file

                # Пропускаем файлы на основе расширений и шаблонов игнорирования
                if any(file.endswith(ext) for ext in ignore_exts) or should_ignore(file_path, root_path,
                                                                                   ignore_patterns):
                    continue

                rel_file_path = file_path.relative_to(root_path)

                # Определяем, является ли файл текстовым
                if not is_text_file(file_path):
                    f.write(f"### {rel_file_path}\n\n")
                    f.write("```\n[Бинарный файл]\n```\n\n")
                    continue

                # Определяем тип файла для подсветки синтаксиса
                file_ext = file_path.suffix.lstrip('.')
                if not file_ext:
                    file_ext = ""

                # Записываем содержимое файла
                f.write(f"### {rel_file_path}\n\n")
                f.write(f"```{file_ext}\n")

                try:
                    file_encoding = detect_encoding(file_path)
                    with open(file_path, 'r', encoding=file_encoding) as code_file:
                        content = code_file.read()
                        f.write(content)
                except Exception as e:
                    f.write(f"[Ошибка чтения файла: {str(e)}]")

                f.write("\n```\n\n")

        # Добавляем заключение
        f.write("## Заключение\n\n")
        f.write("Данная документация автоматически сгенерирована для анализа безопасности проекта.\n")

        # Добавляем информацию об исключенных файлах
        if ignore_patterns:
            f.write("\n### Исключенные файлы и директории\n\n")
            f.write("При генерации документации были применены следующие правила исключения:\n\n")
            f.write("```\n")
            for pattern in ignore_patterns:
                f.write(f"{pattern}\n")
            f.write("```\n")


def main():
    parser = argparse.ArgumentParser(description='Генератор документации проекта для анализа безопасности')
    parser.add_argument('path', help='Путь к проекту для анализа')
    parser.add_argument('-o', '--output', default='project_analysis.md', help='Имя выходного файла')
    parser.add_argument('--ignore-dirs', nargs='+', help='Дополнительные директории для игнорирования')
    parser.add_argument('--ignore-exts', nargs='+', help='Дополнительные расширения для игнорирования')
    parser.add_argument('--no-gitignore', action='store_true', help='Не использовать .gitignore')
    parser.add_argument('--no-mapignore', action='store_true', help='Не использовать .mapignore')

    args = parser.parse_args()

    ignore_dirs = ['.git', '__pycache__', 'node_modules', 'venv', '.idea', '.vscode']
    if args.ignore_dirs:
        ignore_dirs.extend(args.ignore_dirs)

    _ignore_exts = ['.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.obj', '.class']
    if args.ignore_exts:
        _ignore_exts.extend(args.ignore_exts)

    generate_project_doc(
        args.path,
        args.output,
        ignore_dirs,
        _ignore_exts,
        not args.no_gitignore,
        not args.no_mapignore
    )

    print(f"Документация успешно сгенерирована в файле {args.output}")
    print(f"Путь к файлу: {os.path.abspath(args.output)}")


if __name__ == "__main__":
    main()