from fastapi import APIRouter
from app.models.customer import CustomerCreditInfo
from app.db import customers_db  # 전역 DB 사용

router = APIRouter()

@router.post("/add_customer/")
def add_customer(data: CustomerCreditInfo):
    customers_db[data.name] = data.dict()  #  dict()로 변환하여 저장
    return {"message": f"{data.name}님의 신용정보가 저장되었습니다."}

@router.get("/list_customers/")
def list_customers():
    return {"customers": customers_db}
