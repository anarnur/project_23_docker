# Project 23 — Контейнеризация и облачное развертывание ИИ-приложения

## 1. Описание проекта

FastAPI-приложение, обслуживающее языковую модель GPT-2. Принимает текстовый промпт и возвращает сгенерированный текст. Модель загружается автоматически с HuggingFace Hub при старте контейнера.

## 2. Архитектура

```
Пользователь → HTTP запрос
    → FastAPI (app/main.py)
        → Model Inference (app/inference.py) ← GPT-2 (HuggingFace Hub)
    → JSON ответ

FastAPI → Docker-образ → GitHub Actions (CI/CD) → Railway (облако)
```

## 3. Переменные окружения

| Переменная   | Описание                                   | Пример        |
|--------------|--------------------------------------------|---------------|
| `MODEL_PATH` | Путь к локальным весам или название модели | `gpt2`        |
| `PORT`       | Порт запуска сервера                       | `8000`        |

## 4. Локальный запуск (без Docker)

```bash
python -m venv venv
venv\Scripts\activate         # Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 5. Запуск через Docker

```bash
# Сборка образа
docker build -t genai-api .

# Запуск контейнера
docker run -p 8000:8000 -e MODEL_PATH=gpt2 genai-api
```

## 6. Ссылка на деплой

🌐 **https://project23docker-production.up.railway.app**

- Swagger UI: https://project23docker-production.up.railway.app/docs
- Health check: https://project23docker-production.up.railway.app/health

## 7. Описание CI/CD

Пайплайн запускается автоматически при каждом пуше в ветку `main`:

1. **test** — устанавливает зависимости, запускает `ruff` (линтер) и `pytest` (6 тестов)
2. **build** — собирает Docker-образ для проверки корректности Dockerfile
3. **deploy** — автоматический деплой на Railway с использованием Railway CLI и флага --service.
4. **smoke test** — после деплоя делает `curl /health` для проверки живости сервиса

## 8. Пример запроса и ответа

```bash
# Health check
curl https://project23docker-production.up.railway.app/health
# {"status":"ok"}

# Информация о сервисе
curl https://project23docker-production.up.railway.app/
# {"service":"AI Production API","version":"1.0.0","description":"Fine-tuned LLM inference API"}

# Генерация текста
curl -X POST https://project23docker-production.up.railway.app/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Once upon a time", "max_tokens": 50}'

# Ответ:
# {
#   "prompt": "Once upon a time",
#   "generated_text": ", he found a good friend and quickly became acquainted...",
#   "model": "gpt2",
#   "tokens_used": 50
# }

# Невалидный запрос (ожидается 422)
curl -X POST https://project23docker-production.up.railway.app/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": ""}'
```

## 9. Известные ограничения

- **Холодный старт**: при первом запросе модель GPT-2 загружается с HuggingFace (~500 МБ), это занимает 1–3 минуты
- **CPU inference**: модель работает на CPU, генерация занимает 5–15 секунд
- **Railway бесплатный план**: сервис может засыпать после простоя, первый запрос после сна занимает до 30 секунд
- **Только английский язык**: GPT-2 обучена на английском тексте, русский промпт даст нечитаемый результат
