import httpx
import asyncio
from typing import Optional
from ..utils.config import DEEPSEEK_API_KEY
from ..utils.prompts import CONSULTATION_PROMPT, DOCUMENT_ANALYSIS_PROMPT

class AIService:
    def __init__(self, api_key: str = DEEPSEEK_API_KEY):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        
    async def get_consultation(self, question: str) -> str:
        """Получить юридическую консультацию"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {
                                "role": "system",
                                "content": CONSULTATION_PROMPT
                            },
                            {
                                "role": "user",
                                "content": question
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return "❌ Ошибка получения ответа от AI. Попробуйте позже."
                    
        except Exception as e:
            print(f"AI Service error: {e}")
            return "❌ Произошла ошибка при обработке запроса. Попробуйте позже."

    async def analyze_document(self, document_text: str) -> str:
        """Анализ документа"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {
                                "role": "system",
                                "content": DOCUMENT_ANALYSIS_PROMPT
                            },
                            {
                                "role": "user",
                                "content": f"Проанализируй этот документ:\n\n{document_text}"
                            }
                        ],
                        "temperature": 0.5,
                        "max_tokens": 3000
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"]
                else:
                    return "❌ Ошибка анализа документа. Попробуйте позже."
                    
        except Exception as e:
            print(f"AI Service error: {e}")
            return "❌ Произошла ошибка при анализе документа. Попробуйте позже."

    async def is_legal_question(self, question: str) -> bool:
        """Проверить, является ли вопрос юридическим"""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    self.base_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Определи, является ли вопрос юридическим. Отвечай только 'ДА' или 'НЕТ'."
                            },
                            {
                                "role": "user",
                                "content": question
                            }
                        ],
                        "temperature": 0.1,
                        "max_tokens": 10
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data["choices"][0]["message"]["content"].strip().upper()
                    return answer == "ДА"
                else:
                    return True  # По умолчанию считаем вопрос юридическим
                    
        except Exception:
            return True  # По умолчанию считаем вопрос юридическим
