from fastapi import APIRouter
from app.services.ai_agent import analyze_credit_info
from app.db import customers_db  # ✅ 같은 전역 DB 사용

router = APIRouter()

@router.post("/analyze_credit/")
def analyze_credit(name: str, request_text: str):
    if name not in customers_db:
        return {"error": "해당 고객 정보가 존재하지 않습니다."}

    customer_data = customers_db[name]

    # ✅ customer_data가 dict인지 확인 후 변환
    if not isinstance(customer_data, dict):
        customer_data = dict(customer_data)

    response = analyze_credit_info(customer_data, request_text)
    return {"response": response}
