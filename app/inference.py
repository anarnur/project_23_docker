import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os
from dotenv import load_dotenv
 
load_dotenv()
 
 
class ModelInference:
    def __init__(self):
        self.model_path = os.getenv("MODEL_PATH", "gpt2")
        self.tokenizer = None
        self.model = None
 
    def load_model(self):
        print(f"Загрузка модели из: {self.model_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_path,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        print("Модель успешно загружена!")
 
    def generate(self, prompt: str, max_tokens: int = 256) -> dict:
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        input_len = inputs["input_ids"].shape[1]
 
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                do_sample=True,
                temperature=0.7,
                pad_token_id=self.tokenizer.eos_token_id,
            )
 
        generated_ids = outputs[0][input_len:]
        text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
        return {"text": text, "tokens_used": len(generated_ids)}
 
 
inference_service = ModelInference()