import openai
from config.settings import OPENAI_API_KEY
import json
from datetime import datetime
from app.utils.data_generator import load_customer_data

client = openai.OpenAI(api_key=OPENAI_API_KEY)

class CustomerAnalyzer:
    def __init__(self, customer_id=None, customer_name=None):
        """
        고객 데이터 분석기 초기화
        
        Args:
            customer_id: 고객 ID
            customer_name: 고객 이름
        """
        if not customer_id and not customer_name:
            raise ValueError("고객 ID 또는 이름을 제공해야 합니다.")
            
        self.customer_data = load_customer_data(customer_id, customer_name)
        if not self.customer_data:
            raise ValueError("해당 고객 정보를 찾을 수 없습니다.")
        
        self.customer_id = self.customer_data["customer_id"]
        self.name = self.customer_data["name"]
    
    def get_latest_data(self):
        """최신 월별 데이터 반환"""
        if not self.customer_data["monthly_data"]:
            return None
        
        sorted_data = sorted(self.customer_data["monthly_data"], 
                            key=lambda x: datetime.strptime(x["month"], "%Y-%m-%d"))
        return sorted_data[-1]
    
    def get_data_for_period(self, start_date=None, end_date=None):
        """특정 기간의 데이터 반환"""
        if not start_date:
            start_date = datetime(1900, 1, 1)
        if not end_date:
            end_date = datetime(2100, 12, 31)
            
        period_data = []
        for data in self.customer_data["monthly_data"]:
            data_date = datetime.strptime(data["month"], "%Y-%m-%d")
            if start_date <= data_date <= end_date:
                period_data.append(data)
                
        return sorted(period_data, key=lambda x: datetime.strptime(x["month"], "%Y-%m-%d"))
    
    def analyze_credit_info(self, request_text):
        """
        고객 신용 정보 분석
        
        Args:
            request_text: 분석 요청 텍스트
        """
        latest_data = self.get_latest_data()
        
        prompt = f"""
        고객의 신용 정보를 바탕으로 질문에 답해주세요.
        고객 정보:
        - 이름: {self.name}
        - 신용 점수: {latest_data["credit_score"]}
        - 월 소득: {latest_data["income"]:,}원
        - 월 지출: {latest_data["expenses"]:,}원
        - 저축액: {latest_data["savings"]:,}원
        - 부채 총액: {latest_data["debt"]:,}원
        - 월 대출상환액: {latest_data["loan_payments"]:,}원
        - 연체 횟수: {latest_data["overdue_payments"]}

        질문:
        {request_text}
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 금융 전문가입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return {"error": "AI 분석 중 오류가 발생했습니다.", "details": str(e)}
    
    def analyze_credit_trend(self, start_date=None, end_date=None):
        """
        고객의 신용도 추세 분석
        
        Args:
            start_date: 시작 날짜 (YYYY-MM 형식)
            end_date: 종료 날짜 (YYYY-MM 형식)
        """
        try:
            # 날짜 파싱
            start_month = datetime.strptime(start_date, "%Y-%m") if start_date else None
            end_month = datetime.strptime(end_date, "%Y-%m") if end_date else None
            
            # 기간 데이터 필터링
            period_data = self.get_data_for_period(start_month, end_month)
            
            if not period_data:
                return {"error": "해당 기간에 데이터가 없습니다."}
            
            # 첫 달과 마지막 달 데이터
            first_month = period_data[0]
            last_month = period_data[-1]
            
            # 신용점수 변화
            credit_change = last_month["credit_score"] - first_month["credit_score"]
            
            # 수입 변화
            income_change_pct = ((last_month["income"] - first_month["income"]) / first_month["income"] * 100) if first_month["income"] > 0 else 0
            
            # 부채 변화
            debt_change_pct = ((last_month["debt"] - first_month["debt"]) / first_month["debt"] * 100) if first_month["debt"] > 0 else 0
            
            # 데이터 포맷팅
            formatted_data = []
            for data in period_data:
                data_date = datetime.strptime(data["month"], "%Y-%m-%d")
                formatted_data.append({
                    "월": data_date.strftime("%Y년 %m월"),
                    "신용점수": data["credit_score"],
                    "수입": f"{data['income']:,.0f}원",
                    "지출": f"{data['expenses']:,.0f}원",
                    "저축": f"{data['savings']:,.0f}원",
                    "부채": f"{data['debt']:,.0f}원",
                    "대출상환액": f"{data['loan_payments']:,.0f}원",
                    "연체횟수": data["overdue_payments"]
                })
            
            prompt = f"""
            다음은 {self.name} 고객의 {start_month.strftime('%Y년 %m월') if start_month else '시작'}부터 {end_month.strftime('%Y년 %m월') if end_month else '현재'}까지의 재정 데이터입니다.
            
            ## 고객 정보
            - 이름: {self.name}
            - 고객 ID: {self.customer_id}
            
            ## 월별 데이터
            {json.dumps(formatted_data, ensure_ascii=False, indent=2)}
            
            ## 주요 변화
            - 분석 기간: {len(period_data)}개월
            - 신용점수 변화: {credit_change}점 ({first_month["credit_score"]}점 → {last_month["credit_score"]}점)
            - 월 수입 변화: {income_change_pct:.1f}% ({first_month["income"]:,.0f}원 → {last_month["income"]:,.0f}원)
            - 부채 변화: {debt_change_pct:.1f}% ({first_month["debt"]:,.0f}원 → {last_month["debt"]:,.0f}원)
            
            ## 분석 요청
            1. 고객의 신용도 추세를 분석해주세요.
            2. 재정 상태의 강점과 약점을 파악해주세요.
            3. 신용 점수 개선을 위한 구체적인 조언을 제공해주세요.
            4. 현재 재정 상황에 적합한 대출 상품을 추천해주세요.
            5. 향후 6개월간의 신용 점수 및 재정 상태 예측을 해주세요.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 시계열 금융 데이터 분석 전문가입니다. 고객의 재정 데이터를 분석하여 신용도 추세, 재정 상태 평가, 맞춤형 조언을 제공합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return {"error": "AI 분석 중 오류가 발생했습니다.", "details": str(e)}
    
    def predict_future_credit(self, months_ahead=6):
        """
        고객의 미래 신용 점수 예측
        
        Args:
            months_ahead: 예측할 개월 수
        """
        try:
            # 모든 데이터 가져오기
            all_data = self.get_data_for_period()
            
            # 데이터가 부족한 경우
            if len(all_data) < 3:
                return {"error": "예측을 위한 충분한 데이터가 없습니다. 최소 3개월 이상의 데이터가 필요합니다."}
            
            # 최근 3개월 데이터
            recent_data = all_data[-3:]
            
            # 데이터 포맷팅
            formatted_data = []
            for data in all_data:
                data_date = datetime.strptime(data["month"], "%Y-%m-%d")
                formatted_data.append({
                    "월": data_date.strftime("%Y년 %m월"),
                    "신용점수": data["credit_score"],
                    "수입": data["income"],
                    "지출": data["expenses"],
                    "저축": data["savings"],
                    "부채": data["debt"],
                    "대출상환액": data["loan_payments"],
                    "연체횟수": data["overdue_payments"]
                })
            
            prompt = f"""
            다음은 {self.name} 고객의 재정 데이터입니다.
            
            ## 고객 정보
            - 이름: {self.name}
            - 고객 ID: {self.customer_id}
            
            ## 전체 월별 데이터
            {json.dumps(formatted_data, ensure_ascii=False, indent=2)}
            
            ## 최근 3개월 요약
            - 최근 3개월 평균 신용점수: {sum(d["credit_score"] for d in recent_data) / 3:.1f}점
            - 최근 3개월 평균 수입: {sum(d["income"] for d in recent_data) / 3:,.0f}원
            - 최근 3개월 평균 지출: {sum(d["expenses"] for d in recent_data) / 3:,.0f}원
            - 최근 3개월 평균 저축: {sum(d["savings"] for d in recent_data) / 3:,.0f}원
            - 최근 3개월 평균 부채: {sum(d["debt"] for d in recent_data) / 3:,.0f}원
            
            ## 분석 요청
            1. 향후 {months_ahead}개월 동안의 신용 점수 예측을 월별로 제공해주세요.
            2. 예측의 근거와 주요 영향 요인을 설명해주세요.
            3. 신용 점수 향상을 위한 구체적인 행동 계획을 제안해주세요.
            4. 현재 추세가 지속될 경우와 개선 조치를 취할 경우의 시나리오를 비교해주세요.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 금융 예측 전문가입니다. 고객의 과거 재정 데이터를 분석하여 미래 신용 점수와 재정 상태를 예측합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return {"error": "AI 분석 중 오류가 발생했습니다.", "details": str(e)}
    
    def recommend_financial_products(self):
        """고객에게 적합한 금융 상품 추천"""
        try:
            # 최신 데이터 가져오기
            latest_data = self.get_latest_data()
            
            # 최근 6개월 데이터
            recent_data = self.get_data_for_period()[-6:] if len(self.get_data_for_period()) >= 6 else self.get_data_for_period()
            
            # 데이터 포맷팅
            formatted_data = []
            for data in recent_data:
                data_date = datetime.strptime(data["month"], "%Y-%m-%d")
                formatted_data.append({
                    "월": data_date.strftime("%Y년 %m월"),
                    "신용점수": data["credit_score"],
                    "수입": f"{data['income']:,.0f}원",
                    "지출": f"{data['expenses']:,.0f}원",
                    "저축": f"{data['savings']:,.0f}원",
                    "부채": f"{data['debt']:,.0f}원",
                    "대출상환액": f"{data['loan_payments']:,.0f}원",
                    "연체횟수": data["overdue_payments"]
                })
            
            # 부채 대 소득 비율
            debt_to_income = latest_data["debt"] / latest_data["income"] if latest_data["income"] > 0 else 0
            
            # 저축 대 소득 비율
            savings_to_income = latest_data["savings"] / latest_data["income"] if latest_data["income"] > 0 else 0
            
            prompt = f"""
            다음은 {self.name} 고객의 최근 재정 데이터입니다.
            
            ## 고객 정보
            - 이름: {self.name}
            - 고객 ID: {self.customer_id}
            
            ## 최신 재정 상태 (기준: {datetime.strptime(latest_data["month"], "%Y-%m-%d").strftime('%Y년 %m월')})
            - 신용점수: {latest_data["credit_score"]}점
            - 월 수입: {latest_data["income"]:,.0f}원
            - 월 지출: {latest_data["expenses"]:,.0f}원
            - 저축액: {latest_data["savings"]:,.0f}원
            - 부채 총액: {latest_data["debt"]:,.0f}원
            - 월 대출상환액: {latest_data["loan_payments"]:,.0f}원
            - 연체횟수: {latest_data["overdue_payments"]}회
            
            ## 주요 재정 지표
            - 부채 대 소득 비율: {debt_to_income:.2f}
            - 저축 대 소득 비율: {savings_to_income:.2f}
            - 월 가처분 소득: {latest_data["income"] - latest_data["expenses"]:,.0f}원
            
            ## 최근 데이터 추이
            {json.dumps(formatted_data, ensure_ascii=False, indent=2)}
            
            ## 분석 요청
            1. 이 고객에게 가장 적합한 대출 상품 3가지를 추천하고 이유를 설명해주세요.
            2. 각 상품의 예상 이자율과 대출 한도를 제시해주세요.
            3. 고객의 재정 상황 개선을 위한 저축 및 투자 상품도 추천해주세요.
            4. 현재 재정 상황에서 피해야 할 금융 상품이나 행동을 조언해주세요.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "당신은 금융 상품 추천 전문가입니다. 고객의 재정 상황을 분석하여 최적의 대출, 저축, 투자 상품을 추천합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return {"error": "AI 분석 중 오류가 발생했습니다.", "details": str(e)}

def analyze_customer_data(customer_id=None, customer_name=None, request_text=None):
    """
    고객 데이터를 분석하는 통합 함수
    
    Args:
        customer_id: 고객 ID
        customer_name: 고객 이름
        request_text: 분석 요청 텍스트
    
    Returns:
        AI 분석 결과
    """
    # 고객 데이터 로드
    customer_data = load_customer_data(customer_id, customer_name)
    if not customer_data:
        return {"error": "해당 고객 정보를 찾을 수 없습니다."}
    
    # 기본 분석 질문 설정
    if not request_text:
        request_text = "이 고객의 신용 상태를 평가하고, 대출 승인 가능성과 권장 이자율을 제안해주세요."
    
    # 최신 월별 데이터 가져오기
    if not customer_data.get("monthly_data"):
        return {"error": "고객의 월별 데이터가 없습니다."}
    
    sorted_data = sorted(customer_data["monthly_data"], 
                        key=lambda x: datetime.strptime(x["month"], "%Y-%m-%d"))
    latest_data = sorted_data[-1]
    
    # 프롬프트 구성
    prompt = f"""
    고객의 신용 정보를 바탕으로 질문에 답해주세요.
    고객 정보:
    - 이름: {customer_data["name"]}
    - 고객 ID: {customer_data["customer_id"]}
    - 신용 점수: {latest_data["credit_score"]}
    - 월 소득: {latest_data["income"]:,}원
    - 월 지출: {latest_data["expenses"]:,}원
    - 저축액: {latest_data["savings"]:,}원
    - 부채 총액: {latest_data["debt"]:,}원
    - 월 대출상환액: {latest_data["loan_payments"]:,}원
    - 연체 횟수: {latest_data["overdue_payments"]}

    질문:
    {request_text}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 금융 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return {"error": "AI 분석 중 오류가 발생했습니다.", "details": str(e)}

def analyze_credit_trend(customer_id=None, customer_name=None, start_date=None, end_date=None):
    """
    고객의 신용도 추세를 분석하는 함수
    
    Args:
        customer_id: 고객 ID
        customer_name: 고객 이름
        start_date: 시작 날짜 (YYYY-MM 형식)
        end_date: 종료 날짜 (YYYY-MM 형식)
    """
    # 고객 데이터 로드
    customer_data = load_customer_data(customer_id, customer_name)
    if not customer_data:
        return {"error": "해당 고객 정보를 찾을 수 없습니다."}
    
    # 날짜 파싱
    try:
        start_month = datetime.strptime(start_date, "%Y-%m") if start_date else datetime(1900, 1, 1)
        end_month = datetime.strptime(end_date, "%Y-%m") if end_date else datetime(2100, 12, 31)
    except ValueError:
        return {"error": "날짜 형식은 YYYY-MM이어야 합니다."}
    
    # 기간 데이터 필터링
    period_data = []
    for data in customer_data["monthly_data"]:
        data_date = datetime.strptime(data["month"], "%Y-%m-%d")
        if start_month <= data_date <= end_month:
            period_data.append(data)
    
    # 데이터가 없는 경우
    if not period_data:
        return {"error": "해당 기간에 데이터가 없습니다."}
    
    # 데이터 정렬
    period_data.sort(key=lambda x: datetime.strptime(x["month"], "%Y-%m-%d"))
    
    # 데이터 포맷팅
    formatted_data = []
    for data in period_data:
        data_date = datetime.strptime(data["month"], "%Y-%m-%d")
        formatted_data.append({
            "월": data_date.strftime("%Y년 %m월"),
            "신용점수": data["credit_score"],
            "수입": f"{data['income']:,.0f}원",
            "지출": f"{data['expenses']:,.0f}원",
            "저축": f"{data['savings']:,.0f}원",
            "부채": f"{data['debt']:,.0f}원",
            "대출상환액": f"{data['loan_payments']:,.0f}원",
            "연체횟수": data["overdue_payments"]
        })
    
    # 첫 달과 마지막 달 데이터
    first_month = period_data[0]
    last_month = period_data[-1]
    
    # 신용점수 변화
    credit_change = last_month["credit_score"] - first_month["credit_score"]
    
    # 수입 변화
    income_change_pct = ((last_month["income"] - first_month["income"]) / first_month["income"] * 100) if first_month["income"] > 0 else 0
    
    # 부채 변화
    debt_change_pct = ((last_month["debt"] - first_month["debt"]) / first_month["debt"] * 100) if first_month["debt"] > 0 else 0
    
    prompt = f"""
    다음은 {customer_data["name"]} 고객의 {start_month.strftime('%Y년 %m월')}부터 {end_month.strftime('%Y년 %m월')}까지의 재정 데이터입니다.
    
    ## 고객 정보
    - 이름: {customer_data["name"]}
    - 고객 ID: {customer_data["customer_id"]}
    
    ## 월별 데이터
    {json.dumps(formatted_data, ensure_ascii=False, indent=2)}
    
    ## 주요 변화
    - 분석 기간: {len(period_data)}개월
    - 신용점수 변화: {credit_change}점 ({first_month["credit_score"]}점 → {last_month["credit_score"]}점)
    - 월 수입 변화: {income_change_pct:.1f}% ({first_month["income"]:,.0f}원 → {last_month["income"]:,.0f}원)
    - 부채 변화: {debt_change_pct:.1f}% ({first_month["debt"]:,.0f}원 → {last_month["debt"]:,.0f}원)
    
    ## 분석 요청
    1. 고객의 신용도 추세를 분석해주세요.
    2. 재정 상태의 강점과 약점을 파악해주세요.
    3. 신용 점수 개선을 위한 구체적인 조언을 제공해주세요.
    4. 현재 재정 상황에 적합한 대출 상품을 추천해주세요.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 시계열 금융 데이터 분석 전문가입니다. 고객의 재정 데이터를 분석하여 신용도 추세, 재정 상태 평가, 맞춤형 조언을 제공합니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        return {"error": "AI 분석 중 오류가 발생했습니다.", "details": str(e)}