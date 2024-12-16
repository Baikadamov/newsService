# Используем Python образ
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект
COPY . .

# Открываем порт
EXPOSE 8000

# Команда для запуска Django приложения
CMD ["gunicorn", "NewsService.wsgi:application", "--bind", "0.0.0.0:8000"]