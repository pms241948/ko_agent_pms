import openai
from config.settings import OPENAI_API_KEY

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def analyze_credit_info(customer_data: dict, request_text: str):
    try:
        if not isinstance(customer_data, dict):
            customer_data = dict(customer_data)

        prompt = f"""
        고객의 신용 정보를 바탕으로 질문에 답해주세요.
        고객 정보:
        - 이름: {customer_data["name"]}
        - 신용 점수: {customer_data["credit_score"]}
        - 대출 신청 금액: {customer_data["loan_amount"]}원
        - 연체 횟수: {customer_data["overdue"]}
        - 연간 소득: {customer_data["income"]}원

        질문:
        {request_text}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 금융 전문가입니다."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("OpenAI API 오류 발생:", str(e))
        return {"error": "AI 분석 중 오류가 발생했습니다.", "details": str(e)}








