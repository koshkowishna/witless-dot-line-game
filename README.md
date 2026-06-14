# Игра "Witless"

Индивидуальный программный проект-головоломка на Python с использованием библиотеки Pygame.

## Архитектура проекта

├── .gitignore
├── .dockerignore
├── .pre-commit-config.yaml
├── Dockerfile
├── README.md
├── requirements.txt
└── src/
 ├── colors.py     # Цветовые палитры и константы
 ├── levels.py     # Матрицы игровых уровней
 ├── main.py       # Точка входа, игровой цикл и логика
 └── ui.py         # Отрисовка интерфейса и кнопок

## Требования
* Python 3.11+
* Pygame 2.6.0
* Docker (для запуска в контейнере)

## Запуск локально

1. Установите зависимости:
```bash
pip install -r requirements.txt