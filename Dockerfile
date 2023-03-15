FROM docker.io/python:3.11-alpine

ARG EXTRA_INDEX_URL=${EXTRA_INDEX_URL}
ENV EXTRA_INDEX_URL=${EXTRA_INDEX_URL}
# Install dependencies

RUN apt-get update 
RUN apt-get install \
    libpq-dev \
    python3-dev
    
COPY requirements.txt .
RUN pip install -r requirements.txt --extra-index-url $EXTRA_INDEX_URL && \
    rm -f requirements.txt

# Copy the rest of the code
RUN mkdir /app
COPY ./src/stock/data/api/*.py /app/
