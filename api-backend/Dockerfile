FROM python:3.12-alpine

# Setting up Python dependencies - experimenting with uv
WORKDIR /app
RUN apk add --no-cache curl postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv ~/.local/bin/uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync

# Running app as a non-priv user
COPY . .

# Running application
EXPOSE 5000
CMD ["uv", "run", "app.py"]