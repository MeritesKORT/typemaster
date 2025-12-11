#!/bin/bash

set -e

echo "🚀 Запуск TypeMaster..."

# Ждем SQL Server
echo "⏳ Ожидание SQL Server..."
while ! nc -z db 1433; do
  sleep 0.1
done
echo "✅ SQL Server доступен"

# Применяем миграции
echo "📦 Применение миграций..."
python manage.py migrate --noinput

# Создаем суперпользователя если нужно
if [ -z "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "⚠️ Суперпользователь не создан (установите DJANGO_SUPERUSER_* переменные)"
else
    python manage.py createsuperuser --noinput || true
fi

# Собираем статику
echo "🎨 Сбор статических файлов..."
python manage.py collectstatic --noinput

# Запускаем сервер
echo "🚀 Запуск Django сервера..."
exec "$@"