FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

WORKDIR /app

COPY src /app/src
COPY pyproject.toml /app/pyproject.toml

RUN pip install --no-cache-dir .

CMD ["uvicorn", "happiness_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
