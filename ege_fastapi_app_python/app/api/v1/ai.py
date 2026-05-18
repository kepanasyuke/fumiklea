from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.infrastructure.services.ai_grader import AIGraderService
from app.core.security import verify_token

router = APIRouter(prefix="/ai", tags=["ai"])

class CheckRequest(BaseModel):
    task_text: str
    solution_text: str

@router.post("/check")
async def check_solution(
    request: CheckRequest,
    token: str = Depends(verify_token)
):
    ai = AIGraderService()
    return await ai.check_solution(request.task_text, request.solution_text)