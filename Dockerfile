FROM python:3.12-slim

RUN apt-get update && apt-get install -y ffmpeg curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN curl -Ls https://astral.sh/uv/install.sh | sh && \
    ln -s /root/.local/bin/uv /usr/local/bin/uv

COPY ./pyproject.toml ./
COPY ./uv.lock ./

COPY ./nest_pb2.py ./
COPY ./nest_pb2_grpc.py ./
COPY ./nest.proto ./

RUN uv venv && uv sync

COPY ./llm ./llm
COPY ./src ./src

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app:$PYTHONPATH"
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
