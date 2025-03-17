import random
import json
from datetime import datetime, timedelta
import os

def generate_customer_timeseries(customer_id: str, name: str, months: int = 12, 
                                profile_type: str = "average"):
    """
    고객의 시계열 데이터를 임의로 생성합니다.
    
    Args:
        customer_id: 고객 ID
        name: 고객 이름
        months: 생성할 월 데이터 수 (기본값: 12개월)
        profile_type: 고객 프로필 유형 (average, high_risk, premium)
    
    Returns:
        생성된 고객 시계열 데이터
    """
    # 프로필 유형에 따른 초기값 설정
    profiles = {
        "average": {
            "credit_score_range": (650, 750),
            "income_range": (3000000, 6000000),
            "expense_ratio": (0.4, 0.7),
            "savings_ratio": (0.1, 0.3),
            "debt_ratio": (1, 2.5),
            "overdue_prob": 0.15
        },
        "high_risk": {
            "credit_score_range": (500, 650),
            "income_range": (2000000, 4000000),
            "expense_ratio": (0.6, 0.9),
            "savings_ratio": (0.05, 0.15),
            "debt_ratio": (2, 4),
            "overdue_prob": 0.3
        },
        "premium": {
            "credit_score_range": (750, 850),
            "income_range": (7000000, 15000000),
            "expense_ratio": (0.3, 0.6),
            "savings_ratio": (0.2, 0.4),
            "debt_ratio": (0.5, 1.5),
            "overdue_prob": 0.05
        }
    }
    
    profile = profiles.get(profile_type, profiles["average"])
    
    # 초기 값 설정
    initial_credit_score = random.randint(*profile["credit_score_range"])
    initial_income = random.randint(*profile["income_range"])
    initial_expenses = initial_income * random.uniform(*profile["expense_ratio"])
    initial_savings = initial_income * random.uniform(*profile["savings_ratio"])
    initial_debt = initial_income * random.uniform(*profile["debt_ratio"])
    initial_loan_payments = initial_debt * random.uniform(0.02, 0.05)
    
    # 월별 데이터 생성
    monthly_data = []
    start_date = datetime.now() - timedelta(days=30 * months)
    
    credit_score = initial_credit_score
    income = initial_income
    expenses = initial_expenses
    savings = initial_savings
    debt = initial_debt
    loan_payments = initial_loan_payments
    
    for i in range(months):
        # 날짜 계산
        current_month = start_date + timedelta(days=30 * i)
        
        # 변동성 추가
        credit_score_change = random.randint(-10, 15)
        income_change = random.uniform(-0.03, 0.05)
        expenses_change = random.uniform(-0.05, 0.08)
        savings_change = random.uniform(-0.1, 0.15)
        debt_change = random.uniform(-0.03, 0.04)
        
        # 값 업데이트
        credit_score = max(300, min(850, credit_score + credit_score_change))
        income = max(2000000, income * (1 + income_change))
        expenses = max(1000000, expenses * (1 + expenses_change))
        savings = max(0, savings * (1 + savings_change))
        debt = max(0, debt * (1 + debt_change))
        loan_payments = debt * random.uniform(0.02, 0.05)
        
        # 연체 횟수
        overdue = 0
        if random.random() < profile["overdue_prob"]:
            overdue = random.randint(1, 2)
            # 연체 시 신용점수 추가 감소
            credit_score = max(300, credit_score - random.randint(5, 15))
        
        # 월별 데이터 추가
        monthly_data.append({
            "month": current_month.strftime("%Y-%m-%d"),
            "credit_score": int(credit_score),
            "income": round(income),
            "expenses": round(expenses),
            "savings": round(savings),
            "debt": round(debt),
            "loan_payments": round(loan_payments),
            "overdue_payments": overdue
        })
    
    # 고객 데이터 구성
    customer_data = {
        "customer_id": customer_id,
        "name": name,
        "profile_type": profile_type,
        "monthly_data": monthly_data
    }
    
    return customer_data

def generate_multiple_customers(count: int = 5, profile_distribution: dict = None):
    """
    여러 고객의 시계열 데이터를 생성합니다.
    
    Args:
        count: 생성할 고객 수
        profile_distribution: 프로필 유형 분포 (예: {"average": 0.6, "high_risk": 0.2, "premium": 0.2})
    
    Returns:
        생성된 고객 데이터 목록
    """
    customers = []
    
    # 기본 프로필 분포
    if profile_distribution is None:
        profile_distribution = {"average": 0.6, "high_risk": 0.2, "premium": 0.2}
    
    # 프로필 유형 리스트 생성
    profile_types = []
    for profile, ratio in profile_distribution.items():
        profile_count = int(count * ratio)
        profile_types.extend([profile] * profile_count)
    
    # 부족한 수 채우기
    while len(profile_types) < count:
        profile_types.append("average")
    
    # 랜덤 섞기
    random.shuffle(profile_types)
    
    first_names = ["김", "이", "박", "최", "정", "강", "조", "윤", "장", "임"]
    last_names = ["민준", "서준", "예준", "도윤", "시우", "주원", "지호", "지훈", "준서", "준우",
                 "서연", "서윤", "지우", "서현", "민서", "하은", "하윤", "윤서", "지민", "채원"]
    
    for i in range(count):
        customer_id = f"CUST{100 + i}"
        name = f"{random.choice(first_names)}{random.choice(last_names)}"
        profile_type = profile_types[i]
        
        customer_data = generate_customer_timeseries(customer_id, name, profile_type=profile_type)
        customers.append(customer_data)
    
    return customers

def load_customer_data(customer_id=None, customer_name=None):
    """
    저장된 고객 데이터를 로드합니다.
    
    Args:
        customer_id: 고객 ID (선택적)
        customer_name: 고객 이름 (선택적)
    
    Returns:
        고객 데이터 또는 모든 고객 데이터 리스트
    """
    data_dir = "data"
    
    # 특정 고객 ID로 검색
    if customer_id:
        filepath = os.path.join(data_dir, f"customer_{customer_id}.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    # 모든 고객 데이터 로드
    all_customers_path = os.path.join(data_dir, "customer_data.json")
    if not os.path.exists(all_customers_path):
        return []
    
    with open(all_customers_path, 'r', encoding='utf-8') as f:
        customers = json.load(f)
    
    # 이름으로 검색
    if customer_name:
        for customer in customers:
            if customer["name"] == customer_name:
                return customer
        return None
    
    return customers

def save_to_json(data, filename="customer_data.json"):
    """
    데이터를 JSON 파일로 저장합니다.
    """
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    filepath = os.path.join(data_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filepath

if __name__ == "__main__":
    # 5명의 고객 데이터 생성
    customers = generate_multiple_customers(5)
    
    # JSON 파일로 저장
    filepath = save_to_json(customers)
    print(f"고객 데이터가 {filepath}에 저장되었습니다.")
    
    # 개별 고객 파일로도 저장
    for customer in customers:
        customer_filepath = save_to_json(
            customer, 
            f"customer_{customer['customer_id']}.json"
        )
        print(f"고객 {customer['name']}의 데이터가 {customer_filepath}에 저장되었습니다.")