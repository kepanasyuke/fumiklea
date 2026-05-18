import httpx
from app.core.config import settings

class AIGraderService:
    async def check_solution(self, task_text: str, solution_text: str) -> dict:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "meta-llama/llama-3.3-70b-instruct",
                        "messages": [
                            {"role": "system", "content": "Ты эксперт ЕГЭ по профильной математике. Оцени решение ученика по критериям ЕГЭ (0-4 балла) и дай краткий комментарий."},
                            {"role": "user", "content": f"Задача: {task_text}\nРешение ученика:\n{solution_text}"}
                        ],
                        "temperature": 0.1
                    },
                    timeout=30.0
                )
                result = response.json()
                return {"evaluation": result["choices"][0]["message"]["content"]}
            except Exception as e:
                return {"error": str(e)}