from fastapi import FastAPI
from app.routes import customer_routes, ai_routes

app = FastAPI()

app.include_router(customer_routes.router)
app.include_router(ai_routes.router)

@app.get("/")
def read_root():
    return {"message": "빅데이터 신용정보 AI 에이전트 API"}