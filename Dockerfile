FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY co_agent_recruitment/ ./co_agent_recruitment/
COPY main.py uv.lock pyproject.toml README.md ./



RUN adduser --disabled-password --gecos "" myuser && \
    chown -R myuser:myuser /app

USER myuser

RUN uv sync --frozen && uv pip install .


ENV PYTHONPATH=/app
ENV PATH="/home/myuser/.local/bin:$PATH"
CMD ["sh", "-c", "PYTHONPATH=/app:$PYTHONPATH uv run uvicorn main:app --host 0.0.0.0 --port $PORT"]