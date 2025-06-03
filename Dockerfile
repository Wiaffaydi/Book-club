# Використовуємо офіційний Python образ як базовий
FROM python:3.12-slim

# Встановлюємо змінні середовища
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Встановлюємо робочу директорію
WORKDIR /app

# Копіюємо файли requirements.txt (якщо є) та встановлюємо залежності
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь проект у контейнер
COPY . /app/

# Відкриваємо порт для доступу до додатку
EXPOSE 8000

# Команда для запуску сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
