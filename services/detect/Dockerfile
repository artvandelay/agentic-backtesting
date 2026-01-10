FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "nlbt.services.detect:app", "--host", "0.0.0.0", "--port", "8000"]
