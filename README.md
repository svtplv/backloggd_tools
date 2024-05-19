# Backloggd_tools
## Описание:

[Backloggd](https://www.backloggd.com/) - сайт, на котором пользователи могут добавить игры с указанием оценки, статуса прохождения, количество потраченных часов, указать платформу, на которой играли и т.д. 

Данный асинхронный парсер позволяет собрать информацию по всем логам пользователя, а также на основе game_id получить дополнительную информацию по самим играм (разработчики, издатели, год выхода, жанры и тд) с помощью [IGDB API](https://api-docs.igdb.com/#getting-started) и сохранить это в два json файла, в одном из которых содержатся логи пользователя, а в другом информация по играм. В дальнейшем при желании можно сделать соединение этих двух коллекций по game_id, чтобы поиграться со статистикой.

Пример полученных объектов json у коллекции логов: 

```json
  {
    "username": "example_user",
    "game_id": 999,
    "slug": "example_slug",
    "user_rating": 10,
    "status": "Completed",
    "hours_played": 10.25,
    "platforms_played": [
      "Windows PC"
    ]
  },
```

Пример полученных объектов json у коллекции игр:
```json
  {
    "game_id": 14593,
    "title": "Hollow Knight",
    "release_year": 2017,
    "genres": [
      "Platform",
      "Adventure",
      "Indie"
    ],
    "developers": [
      "Team Cherry"
    ],
    "publishers": [
      "Team Cherry"
    ],
    "platforms": [
      "Linux",
      "PC (Microsoft Windows)",
      "Mac",
      "Wii U",
      "Nintendo Switch"
    ],
    "series": [
      "Hollow Knight"
    ]
  },
```

### Стек технологий:
* Python 3.12
* Aiohttp
* Beautiful Soup 4

### Подготовка:

Перед использованием для взаимодействия с IGDB API необходимо указать CLIENT ID и ACCESS TOKEN в .env файле как в примере .env.example.
Для этого потребуется регистрация на Twitch с обязательной двухфакторной аутентификацией. Подробности можно узнать на [IGDB](https://api-docs.igdb.com/#account-creation).


### Установка:

1. Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:svtplv/backloggd_tools.git
```

2. Cоздать и активировать виртуальное окружение:
* Linux/macOS:
```
python3 -m venv venv
source venv/bin/activate
```
* Windows:
```
python -m venv venv
source env/scripts/activate
```

3. Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```

4. Создать .env файл в корне по образцу .env example.

5. Запустить проект:
``` 
py main.py
```

### Авторы:
[Святослав Поляков](https://github.com/svtplv)
