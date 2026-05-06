FROM python:3.12-alpine AS builder

WORKDIR /app

RUN apk update && apk add --no-cache \
    curl \
    gcc \
    musl-dev \
    postgresql-dev \
    && rm -rf /var/cache/apk/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-alpine AS production

RUN apk update && apk add --no-cache \
    curl \
    gcc \
    musl-dev \
    postgresql-dev \
    && rm -rf /var/cache/apk/*


WORKDIR /app

RUN adduser -D -u 1000 appuser && chown -R appuser:appuser /app


COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY . .

USER appuser

EXPOSE 5000


HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:5000/api/gifts || exit 1


CMD ["python", "-m", "app"]