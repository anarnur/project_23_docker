# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder
 
WORKDIR /app
 
# Зависимости отдельным слоем — кешируются если requirements.txt не менялся
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -r requirements.txt
 
# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11-slim
 
WORKDIR /app
 
COPY --from=builder /install /usr/local
 
# Копируем только код приложения
COPY app/ ./app/
 
# Путь к модели — через переменную окружения, не захардкожен
ENV MODEL_PATH=gpt2
ENV PORT=8000
 
EXPOSE 8000
 
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
 
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]