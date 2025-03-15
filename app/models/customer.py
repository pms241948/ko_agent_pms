from pydantic import BaseModel

class CustomerCreditInfo(BaseModel):
    name: str
    credit_score: int
    loan_amount: float
    overdue: int
    income: float

