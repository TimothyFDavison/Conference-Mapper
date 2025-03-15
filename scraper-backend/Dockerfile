FROM python:3.12-slim

# Install cron
RUN apt-get update && apt-get install -y cron

# Install Python requirements; experimenting with uv
WORKDIR /app
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    gcc \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv ~/.local/bin/uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync

# Run scraper. Cron file contains reboot directive to run on startup
COPY . .
COPY scraper.cron /etc/cron.d/scraper-cron
RUN chmod 0644 /etc/cron.d/scraper-cron
RUN crontab /etc/cron.d/scraper-cron

# Log output to file
RUN touch /var/log/cron.log

# Start cron in the foreground
CMD ["cron", "-f"]
