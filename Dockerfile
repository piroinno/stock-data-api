FROM docker.io/python:3.11-alpine AS base

ARG EXTRA_INDEX_URL=${EXTRA_INDEX_URL}
ENV EXTRA_INDEX_URL=${EXTRA_INDEX_URL}
# Install dependencies

RUN apk update && \
    apk add --no-cache \
    musl-dev \
    libpq-dev \
    gcc

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url $EXTRA_INDEX_URL

FROM python:3.11-alpine

RUN apk update && \
    apk add --no-cache \
    libpq-dev

COPY --from=base /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY ./src/stock/data/api/*.py /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]