# Foodgram
Продуктовый помощник - сервис на котором пользователи могут публиковать рецепты, подписываться на любимых авторов, добавлять рецепты в избранное и список покупок.

Проект реализован с помощью Django, Django Rest Framework, Nginx, Docker и Postgresql.

## Запуск на локальном сервере

- Скачайте репозиторий проекта
- Установите Docker и Docker compose
- Создайте .env файл в директории проекта в соотвествии с примером (env.example)
- В директории проекта выполните команду ```sudo docker compose up```
- При необходимости можно импортировать заранее заготовленный данные из папки data с помощью команд ```sudo docker compose cp data/ingredients.csv foodgram_db:/ingredients.csv``` > ```sudo docker compose exec foodgram_db psql -d foodgram -U <имя_пользователя_базы_данных_из_env> -c "COPY foodgram_ingredient(name, measurement_unit) FROM '/ingredients.csv' WITH DELIMITER ',' CSV;"```

## Автор

Максимов Сергей