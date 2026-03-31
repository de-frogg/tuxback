# Используем легковесный Python образ
FROM python:3.12-slim
# Отключаем создание .pyc файлов
ENV PYTHONDONTWRITEBYTECODE=1
# Логи сразу выводятся в stdout/stderr (без буферизации)
ENV PYTHONUNBUFFERED=1
# XDG директории (как в основной программе)
ENV XDG_DATA_HOME=/home/app/.local/share \
    XDG_CONFIG_HOME=/home/app/.config \
    XDG_STATE_HOME=/home/app/.local/state

# Не запускает приложение от root — это best practice
RUN useradd -m app

# Рабочая директория приложения
WORKDIR /app

# Копирует requirements отдельно (кеш Docker)
COPY requirements.txt .
# Устанавливает зависимости
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Создаёт XDG директории для пользователя
RUN mkdir -p \
    /home/app/.local/share/tuxback/backups \
    /home/app/.config/tuxback \
    /home/app/.local/state/tuxback

# Даём права пользователю
RUN chown -R app:app /home/app /app

# Делает CLI исполняемым
RUN chmod +x /app/tuxback

# Переключается на обычного пользователя
USER app

# По умолчанию показывает help
CMD ["./tuxback", "--help"]