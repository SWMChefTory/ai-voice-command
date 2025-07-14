FROM python:3.12-slim

RUN apt-get update && apt-get install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN curl -Ls https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv

COPY ./pyproject.toml ./
COPY ./pdm.lock ./

RUN uv venv && uv sync --all

COPY ./app ./app

CMD ["uvicorn", "app.main:app"]
