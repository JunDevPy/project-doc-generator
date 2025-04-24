# 🔍 Project Documentation Generator

## 📝 Описание

**Project Documentation Generator** - мощный Python-скрипт для автоматической генерации comprehensive документации вашего проекта, идеально подходящий для:

- 🔒 Анализа безопасности проектов
- 📋 Быстрого обзора структуры проекта
- 🤖 Подготовки материалов для AI-анализа

## ✨ Возможности

- 🌳 Полное отображение структуры проекта
- 📄 Листинг содержимого всех текстовых файлов
- 🔍 Поддержка .gitignore и .mapignore
- 🌐 Автоматическое определение кодировки файлов
- 🔒 Гибкое исключение конфиденциальных файлов
- 📊 Генерация Markdown-документации

## 🚀 Установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/your_username/project-doc-generator.git
cd project-doc-generator
```

### Рекомендуется использовать виртуальное окружение для Linux/macOS
python3 -m venv venv
source venv/bin/activate  
### или для Windows
venv\Scripts\activate  

### Установка зависимостей
pip install -r requirements.txt

## 🛠️ Использование

### Базовое использование

```bash
python generate_project_doc.py /path/to/your/project
```

### Используем опции командной строки

```bash
# Указать custom имя выходного файла
python generate_project_doc.py /path/to/project -o my_project_docs.md

# Игнорировать дополнительные директории
python generate_project_doc.py /path/to/project --ignore-dirs build dist

# Игнорировать дополнительные расширения файлов
python generate_project_doc.py /path/to/project --ignore-exts .log .tmp

# Отключить использование .gitignore
python generate_project_doc.py /path/to/project --no-gitignore

# Отключить использование .mapignore
python generate_project_doc.py /path/to/project --no-mapignore
```

## 🗂️ Использование файла .mapignore

Создайте .mapignore в корне проекта для тонкой настройки игнорируемых файлов:

```txt
# Игнорировать все логи
*.log

# Игнорировать временные файлы
*.tmp
.DS_Store

# Игнорировать директории
node_modules/
__pycache__/

# Исключить конкретные файлы
secrets.json
.env

# Можно использовать negation для включения
!important.txt
```

## 📦 Зависимости

- Python 3.7+
- chardet
- argparse (встроенный)

## 🛡️ Безопасность
### ⚠️ Важно:
    ```Всегда проверяйте содержимое сгенерированного файла документации перед публикацией или распространением.```


## 🤝 Вклад в проект
1. Fork репозитория
2. Создайте свою ветку (git checkout -b feature/AmazingFeature)
3. Commit изменений (git commit -m 'Add some AmazingFeature')
4. Push в ветку (git push origin feature/AmazingFeature)
5. Откройте Pull Request

## 📄 Лицензия
Распространяется под MIT License.

## 🌟 Поддержка
Если у вас возникли проблемы или есть предложения, пожалуйста, откройте Issues в репозитории.

