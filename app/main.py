from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from app.models import PredictionRequest, PredictionResponse
from app.inference import inference_service
 
 
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        inference_service.load_model()
        yield
    finally:
        pass
 
 
app = FastAPI(
    title="AI Production API",
    version="1.0.0",
    description="API для генерации текста с помощью дообученной модели",
    lifespan=lifespan
)
 
 
# Обязательный корневой эндпоинт (Проект 23)
@app.get("/")
async def root():
    return {
        "service": "AI Production API",
        "version": "1.0.0",
        "description": "Fine-tuned LLM inference API"
    }
 
 
# Health check — должен возвращать именно {"status": "ok"}
@app.get("/health")
async def health_check():
    return {"status": "ok"}
 
 
@app.post("/generate", response_model=PredictionResponse)
async def generate_text(request: PredictionRequest):
    try:
        result = inference_service.generate(request.prompt, request.max_tokens)
        return PredictionResponse(
            prompt=request.prompt,
            generated_text=result["text"],
            model=inference_service.model_path,
            tokens_used=result["tokens_used"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))