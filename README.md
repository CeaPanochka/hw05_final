# hw05_final

[![CI](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml/badge.svg?branch=master)](https://github.com/yandex-praktikum/hw05_final/actions/workflows/python-app.yml)

# Yatube API
## Описание

Проект разработки социальной сети для публикации дневников. Разработана по MVT архитектуре. Используется пагинация постов, кеширование, и тесты, проверяющие работу сервиса. Регистрация реализована с верификацией данных, сменной и восстановлением пароля через почту.

### Технологии:
- Django
- Unittest
- Bootstrap

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке.

```sh
git clone https://github.com/CeaPanochka/hw05_final.git
cd hw05_final
```

Создать и активировать виртуальное окружение.

```sh
python -m venv venv
source venv/Scripts/activate
```

Установить зависимости.

```sh
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Выполнить миграции.

```sh
python manage.py migrate
```

Запустить проект.

```sh
python manage.py runsrver
```
