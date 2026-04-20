from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
 
 
# Мокаем загрузку модели до импорта app
mock_inference = MagicMock()
mock_inference.model_path = "gpt2"
mock_inference.generate.return_value = {"text": "test response", "tokens_used": 10}
 
with patch("app.inference.inference_service", mock_inference):
    with patch("app.inference.ModelInference.load_model"):
        from app.main import app
 
client = TestClient(app)
 
 
def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
 
 
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "version" in data
    assert "description" in data
 
 
def test_generate_valid():
    with patch("app.main.inference_service", mock_inference):
        response = client.post("/generate", json={"prompt": "Привет мир"})
    assert response.status_code == 200
    data = response.json()
    assert "prompt" in data
    assert "generated_text" in data
    assert "model" in data
    assert "tokens_used" in data
 
 
def test_generate_empty_prompt():
    response = client.post("/generate", json={"prompt": ""})
    assert response.status_code == 422
 
 
def test_generate_whitespace_prompt():
    response = client.post("/generate", json={"prompt": "   "})
    assert response.status_code == 422
 
 
def test_generate_max_tokens_invalid():
    response = client.post("/generate", json={"prompt": "hello", "max_tokens": 9999})
    assert response.status_code == 422
