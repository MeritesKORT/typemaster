#!/bin/bash

echo "🚀 Настройка TypeMaster Docker"

# Создаем .env если нет
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Создан файл .env"
fi

# Даем права на скрипты
chmod +x docker/entrypoint.sh
chmod +x scripts/*.py

echo "📦 Сборка Docker образов..."
docker-compose build

echo "🚀 Запуск контейнеров..."
docker-compose up -d

echo "⏳ Ожидание запуска сервисов..."
sleep 10

echo "📦 Применение миграций..."
docker-compose exec web python manage.py migrate

echo "🎨 Сбор статики..."
docker-compose exec web python manage.py collectstatic --noinput

echo "📝 Добавление тестовых данных..."
docker-compose exec web python scripts/add_samples.py

echo "✅ Готово!"
echo "🌐 Приложение доступно по адресу: http://localhost:8000"
echo "🗄️ База данных: localhost:1433"
echo "📊 PGAdmin: http://localhost:5050 (логин: admin@typemaster.com, пароль: admin123)"