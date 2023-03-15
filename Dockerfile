FROM docker.io/python:3.11-alpine

ARG EXTRA_INDEX_URL=${EXTRA_INDEX_URL}
ENV EXTRA_INDEX_URL=${EXTRA_INDEX_URL}
# Install dependencies

RUN apk add --no-cache \
    libpq-dev \
    python3-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url $EXTRA_INDEX_URL && \
    rm -f requirements.txt

# Copy the rest of the code
RUN mkdir /app
COPY ./src/stock/data/api/*.py /app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]