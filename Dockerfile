FROM python:3.11-slim

# Установка системных зависимостей для корректной работы Pygame (SDL2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Установка зависимостей Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY src/ ./src/

# Настройка дисплея по умолчанию для GUI
ENV DISPLAY=:0

# Точка входа для запуска игры
CMD ["python", "src/main.py"]