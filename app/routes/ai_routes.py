from fastapi import APIRouter, HTTPException, Query
from app.services.ai_agent import analyze_credit_info, analyze_credit_trend, predict_future_credit, recommend_financial_products
from app.routes.customer_routes import customers_db  # 실제 고객 정보 저장소 불러오기
import openai
from config.settings import OPENAI_API_KEY

router = APIRouter()
client = openai.OpenAI(api_key=OPENAI_API_KEY)

@router.post("/analyze_credit/")
def analyze_credit(name: str, request_text: str):
    """
    고객 신용 정보를 바탕으로 GPT 분석을 수행하는 API
    """
    # 실제 고객 정보 조회 (딕셔너리에서 찾기)
    if name not in customers_db:
        raise HTTPException(status_code=404, detail="해당 고객 정보를 찾을 수 없습니다.")

    customer_data = customers_db[name]  # 등록된 고객 정보 가져오기

    response = analyze_credit_info(customer_data, request_text)
    return {"response": response}

@router.post("/summarize_response/")
def summarize_response(text: str = Query(..., description="요약할 텍스트")):
    """
    GPT-4o-mini를 사용하여 긴 응답을 요약하는 API
    """
    summary_prompt = f"다음 분석 결과를 3줄 요약해 주세요:\n\n{text}"

    summary_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 금융 전문가입니다."},
            {"role": "user", "content": summary_prompt}
        ],
        max_tokens=150
    )

    return {"summary": summary_response.choices[0].message.content}

@router.get("/analyze_credit_trend/{customer_id}")
def analyze_credit_trend_route(
    customer_id: str,
    start_date: str = None,  # YYYY-MM 형식
    end_date: str = None     # YYYY-MM 형식
):
    """
    고객의 신용도 추세를 분석하는 API
    """
    response = analyze_credit_trend(customer_id, start_date, end_date)
    return {"response": response}

@router.get("/predict_future_credit/{customer_id}")
def predict_future_credit_route(customer_id: str, months_ahead: int = 6):
    """
    고객의 미래 신용 점수를 예측하는 API
    """
    response = predict_future_credit(customer_id, months_ahead)
    return {"response": response}

@router.get("/recommend_financial_products/{customer_id}")
def recommend_financial_products_route(customer_id: str):
    """
    고객에게 적합한 금융 상품을 추천하는 API
    """
    response = recommend_financial_products(customer_id)
    return {"response": response}
