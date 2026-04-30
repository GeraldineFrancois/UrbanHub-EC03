FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-interaction --no-ansi

COPY src/ ./src/

EXPOSE 8006

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8006/health || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8006"]
