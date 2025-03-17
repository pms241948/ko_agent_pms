from fastapi import FastAPI
from app.routes.customer_api import router as customer_router

app = FastAPI(
    title="금융 데이터 분석 API",
    description="고객 데이터 생성, 분석 및 보고서 생성을 위한 API",
    version="1.0.0"
)

# 라우터 등록
app.include_router(customer_router, prefix="/api", tags=["고객 데이터"])

@app.get("/")
def read_root():
    return {
        "message": "금융 데이터 분석 API에 오신 것을 환영합니다.",
        "documentation": "/docs"
    }