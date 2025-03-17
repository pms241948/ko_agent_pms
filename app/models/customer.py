from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CustomerCreditInfo(BaseModel):
    name: str
    credit_score: int
    loan_amount: int
    overdue: int
    income: int

class MonthlyCustomerData(BaseModel):
    month: datetime  # 데이터 기준 월
    credit_score: int
    income: float
    expenses: float
    savings: float
    debt: float
    loan_payments: float
    overdue_payments: Optional[int] = 0
    
class CustomerTimeSeriesData(BaseModel):
    customer_id: str
    name: str
    monthly_data: List[MonthlyCustomerData]
    
    def get_latest_data(self) -> MonthlyCustomerData:
        """가장 최근 월 데이터 반환"""
        return sorted(self.monthly_data, key=lambda x: x.month, reverse=True)[0]
    
    def get_data_for_period(self, start_month: datetime, end_month: datetime) -> List[MonthlyCustomerData]:
        """특정 기간의 데이터 반환"""
        return [data for data in self.monthly_data 
                if start_month <= data.month <= end_month]

