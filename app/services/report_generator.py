from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from datetime import datetime
import os
import textwrap
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from io import BytesIO
from reportlab.lib.utils import ImageReader
from app.services.ai_analyzer import analyze_customer_data, analyze_credit_trend
from app.utils.data_generator import load_customer_data

# 한글 폰트 설정 (matplotlib)
matplotlib.rcParams['font.family'] = 'NanumGothic'
matplotlib.rcParams['axes.unicode_minus'] = False

# 보고서 저장 디렉토리 설정
REPORTS_DIR = "reports"

# 디렉토리가 없으면 생성
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

# 한글 폰트 등록 (나눔고딕 폰트 사용)
# 폰트 파일 경로는 시스템에 맞게 수정해야 합니다
FONT_PATH = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"  # 시스템에 맞게 경로 수정 필요

# 폰트 파일이 없는 경우 기본 폰트 사용
try:
    pdfmetrics.registerFont(TTFont('NanumGothic', FONT_PATH))
    KOREAN_FONT = 'NanumGothic'
except:
    print("경고: 나눔고딕 폰트를 찾을 수 없습니다. 기본 폰트를 사용합니다.")
    KOREAN_FONT = 'Helvetica'

def draw_wrapped_text(c, text, x, y, width, font_name, font_size, leading=14):
    """
    텍스트를 자동으로 줄바꿈하여 그립니다.
    """
    c.setFont(font_name, font_size)
    
    # 텍스트 줄바꿈
    wrapped_text = textwrap.fill(text, width=width)
    lines = wrapped_text.split('\n')
    
    # 각 줄 그리기
    for i, line in enumerate(lines):
        c.drawString(x, y - i * leading, line)
    
    return len(lines)

def create_credit_score_chart(customer_data, start_date=None, end_date=None):
    """
    신용 점수 추이 차트를 생성합니다.
    
    Args:
        customer_data: 고객 데이터
        start_date: 시작 날짜 (YYYY-MM 형식)
        end_date: 종료 날짜 (YYYY-MM 형식)
    
    Returns:
        BytesIO 객체에 저장된 이미지
    """
    # 월별 데이터 정렬
    sorted_data = sorted(customer_data["monthly_data"], 
                        key=lambda x: datetime.strptime(x["month"], "%Y-%m-%d"))
    
    # 날짜 필터링
    if start_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m")
        sorted_data = [d for d in sorted_data if datetime.strptime(d["month"], "%Y-%m-%d") >= start_date_obj]
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m")
        sorted_data = [d for d in sorted_data if datetime.strptime(d["month"], "%Y-%m-%d") <= end_date_obj]
    
    # 데이터 추출
    months = [datetime.strptime(d["month"], "%Y-%m-%d").strftime("%Y-%m") for d in sorted_data]
    credit_scores = [d["credit_score"] for d in sorted_data]
    
    # 그래프 생성
    plt.figure(figsize=(10, 5))
    plt.plot(months, credit_scores, marker='o', linestyle='-', color='#3366cc', linewidth=2)
    plt.title('신용 점수 추이', fontsize=14)
    plt.xlabel('날짜', fontsize=12)
    plt.ylabel('신용 점수', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # 이미지를 BytesIO 객체에 저장
    img_data = BytesIO()
    plt.savefig(img_data, format='png', dpi=100)
    img_data.seek(0)
    plt.close()
    
    return img_data

def create_financial_chart(customer_data, start_date=None, end_date=None):
    """
    재정 상태 차트를 생성합니다.
    
    Args:
        customer_data: 고객 데이터
        start_date: 시작 날짜 (YYYY-MM 형식)
        end_date: 종료 날짜 (YYYY-MM 형식)
    
    Returns:
        BytesIO 객체에 저장된 이미지
    """
    # 월별 데이터 정렬
    sorted_data = sorted(customer_data["monthly_data"], 
                        key=lambda x: datetime.strptime(x["month"], "%Y-%m-%d"))
    
    # 날짜 필터링
    if start_date:
        start_date_obj = datetime.strptime(start_date, "%Y-%m")
        sorted_data = [d for d in sorted_data if datetime.strptime(d["month"], "%Y-%m-%d") >= start_date_obj]
    
    if end_date:
        end_date_obj = datetime.strptime(end_date, "%Y-%m")
        sorted_data = [d for d in sorted_data if datetime.strptime(d["month"], "%Y-%m-%d") <= end_date_obj]
    
    # 데이터 추출
    months = [datetime.strptime(d["month"], "%Y-%m-%d").strftime("%Y-%m") for d in sorted_data]
    income = [d["income"] for d in sorted_data]
    expenses = [d["expenses"] for d in sorted_data]
    savings = [d["savings"] for d in sorted_data]
    debt = [d["debt"] for d in sorted_data]
    
    # 그래프 생성 (2x2 서브플롯)
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    
    # 수입 및 지출 그래프
    axs[0, 0].plot(months, income, marker='o', linestyle='-', color='#3366cc', label='수입')
    axs[0, 0].plot(months, expenses, marker='s', linestyle='-', color='#dc3912', label='지출')
    axs[0, 0].set_title('월별 수입 및 지출')
    axs[0, 0].set_xlabel('날짜')
    axs[0, 0].set_ylabel('금액 (원)')
    axs[0, 0].grid(True, linestyle='--', alpha=0.7)
    axs[0, 0].legend()
    axs[0, 0].tick_params(axis='x', rotation=45)
    
    # 저축액 그래프
    axs[0, 1].plot(months, savings, marker='o', linestyle='-', color='#109618')
    axs[0, 1].set_title('월별 저축액')
    axs[0, 1].set_xlabel('날짜')
    axs[0, 1].set_ylabel('금액 (원)')
    axs[0, 1].grid(True, linestyle='--', alpha=0.7)
    axs[0, 1].tick_params(axis='x', rotation=45)
    
    # 부채 그래프
    axs[1, 0].plot(months, debt, marker='o', linestyle='-', color='#ff9900')
    axs[1, 0].set_title('월별 부채 총액')
    axs[1, 0].set_xlabel('날짜')
    axs[1, 0].set_ylabel('금액 (원)')
    axs[1, 0].grid(True, linestyle='--', alpha=0.7)
    axs[1, 0].tick_params(axis='x', rotation=45)
    
    # 수입 대비 지출 비율 그래프
    expense_ratio = [e/i*100 if i > 0 else 0 for e, i in zip(expenses, income)]
    axs[1, 1].bar(months, expense_ratio, color='#990099')
    axs[1, 1].set_title('수입 대비 지출 비율')
    axs[1, 1].set_xlabel('날짜')
    axs[1, 1].set_ylabel('비율 (%)')
    axs[1, 1].grid(True, linestyle='--', alpha=0.7)
    axs[1, 1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    # 이미지를 BytesIO 객체에 저장
    img_data = BytesIO()
    plt.savefig(img_data, format='png', dpi=100)
    img_data.seek(0)
    plt.close()
    
    return img_data

def generate_credit_report(customer_id=None, customer_name=None, analysis_question=None):
    """
    고객 신용 정보와 분석 결과를 바탕으로 PDF 보고서를 생성합니다.
    
    Args:
        customer_id: 고객 ID
        customer_name: 고객 이름
        analysis_question: 분석에 사용할 질문
    
    Returns:
        생성된 PDF 파일 이름
    """
    # 고객 데이터 로드
    customer_data = load_customer_data(customer_id, customer_name)
    if not customer_data:
        raise ValueError("해당 고객 정보를 찾을 수 없습니다.")
    
    # AI 분석 수행
    if analysis_question:
        analysis_result = analyze_customer_data(
            customer_id=customer_data["customer_id"], 
            request_text=analysis_question
        )
    else:
        analysis_result = analyze_customer_data(
            customer_id=customer_data["customer_id"], 
            request_text="이 고객의 신용 상태를 평가하고, 대출 승인 가능성과 권장 이자율을 제안해주세요."
        )
    
    # 최신 월별 데이터 가져오기
    sorted_data = sorted(customer_data["monthly_data"], 
                        key=lambda x: datetime.strptime(x["month"], "%Y-%m-%d"))
    latest_data = sorted_data[-1]
    
    # PDF 파일 이름 설정
    filename = os.path.join(REPORTS_DIR, f"credit_report_{customer_data['customer_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    
    # PDF 생성
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # 제목
    c.setFont(KOREAN_FONT, 18)
    c.drawString(2*cm, height - 2*cm, "신용 분석 보고서")
    
    # 날짜
    c.setFont(KOREAN_FONT, 10)
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    c.drawString(width - 5*cm, height - 2*cm, f"생성일: {current_date}")
    
    # 구분선
    c.line(2*cm, height - 2.5*cm, width - 2*cm, height - 2.5*cm)
    
    # 고객 정보 섹션
    y_position = height - 3.5*cm
    c.setFont(KOREAN_FONT, 14)
    c.drawString(2*cm, y_position, "고객 정보")
    
    # 구분선
    y_position -= 0.5*cm
    c.line(2*cm, y_position, width - 2*cm, y_position)
    
    # 고객 정보 표시
    y_position -= 1*cm
    c.setFont(KOREAN_FONT, 12)
    c.drawString(2*cm, y_position, f"이름: {customer_data['name']}")
    y_position -= 0.7*cm
    c.drawString(2*cm, y_position, f"고객 ID: {customer_data['customer_id']}")
    y_position -= 0.7*cm
    c.drawString(2*cm, y_position, f"신용 점수: {latest_data['credit_score']}")
    y_position -= 0.7*cm
    c.drawString(2*cm, y_position, f"월 소득: {latest_data['income']:,.0f}원")
    y_position -= 0.7*cm
    c.drawString(2*cm, y_position, f"월 지출: {latest_data['expenses']:,.0f}원")
    y_position -= 0.7*cm
    c.drawString(2*cm, y_position, f"저축액: {latest_data['savings']:,.0f}원")
    y_position -= 0.7*cm
    c.drawString(2*cm, y_position, f"부채 총액: {latest_data['debt']:,.0f}원")
    y_position -= 0.7*cm
    c.drawString(2*cm, y_position, f"월 대출상환액: {latest_data['loan_payments']:,.0f}원")
    y_position -= 0.7*cm
    c.drawString(2*cm, y_position, f"연체 횟수: {latest_data['overdue_payments']}")
    
    # AI 분석 결과 섹션
    y_position -= 1.5*cm
    c.setFont(KOREAN_FONT, 14)
    c.drawString(2*cm, y_position, "AI 분석 결과")
    
    # 구분선
    y_position -= 0.5*cm
    c.line(2*cm, y_position, width - 2*cm, y_position)
    
    # 분석 결과 표시
    y_position -= 1*cm
    
    # 분석 결과 줄바꿈 처리
    lines = draw_wrapped_text(c, analysis_result, 2*cm, y_position, 70, KOREAN_FONT, 10)
    
    # 페이지 저장
    c.save()
    
    return filename

def generate_timeseries_report(customer_id=None, customer_name=None, start_date=None, end_date=None):
    """
    고객의 시계열 데이터 보고서를 생성합니다.
    
    Args:
        customer_id: 고객 ID
        customer_name: 고객 이름
        start_date: 시작 날짜 (YYYY-MM 형식)
        end_date: 종료 날짜 (YYYY-MM 형식)
    
    Returns:
        생성된 PDF 파일 이름
    """
    # 고객 데이터 로드
    customer_data = load_customer_data(customer_id, customer_name)
    if not customer_data:
        raise ValueError("해당 고객 정보를 찾을 수 없습니다.")
    
    # 신용도 추세 분석
    trend_analysis = analyze_credit_trend(
        customer_id=customer_data["customer_id"],
        start_date=start_date,
        end_date=end_date
    )
    
    # 차트 생성
    credit_score_chart = create_credit_score_chart(customer_data, start_date, end_date)
    financial_chart = create_financial_chart(customer_data, start_date, end_date)
    
    # PDF 파일 이름 설정
    filename = os.path.join(REPORTS_DIR, f"timeseries_report_{customer_data['customer_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    
    # PDF 생성
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4
    
    # 제목
    c.setFont(KOREAN_FONT, 18)
    c.drawString(2*cm, height - 2*cm, "시계열 데이터 분석 보고서")
    
    # 날짜
    c.setFont(KOREAN_FONT, 10)
    current_date = datetime.now().strftime("%Y년 %m월 %d일")
    c.drawString(width - 5*cm, height - 2*cm, f"생성일: {current_date}")
    
    # 구분선
    c.line(2*cm, height - 2.5*cm, width - 2*cm, height - 2.5*cm)
    
    # 고객 정보 섹션
    y_position = height - 3.5*cm
    c.setFont(KOREAN_FONT, 14)
    c.drawString(2*cm, y_position, "고객 정보")
    
    # 구분선
    y_position -= 0.5*cm
    c.line(2*cm, y_position, width - 2*cm, y_position)
    
    # 고객 정보 표시
    y_position -= 1*cm
    c.setFont(KOREAN_FONT, 12)
    c.drawString(2*cm, y_position, f"이름: {customer_data['name']}")
    y_position -= 0.7*cm
    c.drawString(2*cm, y_position, f"고객 ID: {customer_data['customer_id']}")
    
    # 분석 기간 섹션
    y_position -= 1.5*cm
    c.setFont(KOREAN_FONT, 14)
    c.drawString(2*cm, y_position, "분석 기간")
    
    # 구분선
    y_position -= 0.5*cm
    c.line(2*cm, y_position, width - 2*cm, y_position)
    
    # 분석 기간 표시
    y_position -= 1*cm
    c.setFont(KOREAN_FONT, 12)
    start_text = f"{start_date}부터" if start_date else "전체 기간"
    end_text = f"{end_date}까지" if end_date else ""
    c.drawString(2*cm, y_position, f"{start_text} {end_text}")
    
    # 신용 점수 차트 추가
    y_position -= 1.5*cm
    c.setFont(KOREAN_FONT, 14)
    c.drawString(2*cm, y_position, "신용 점수 추이")
    
    # 구분선
    y_position -= 0.5*cm
    c.line(2*cm, y_position, width - 2*cm, y_position)
    
    # 차트 이미지 추가
    y_position -= 10*cm  # 차트 높이에 맞게 조정
    credit_score_img = ImageReader(credit_score_chart)
    c.drawImage(credit_score_img, 2*cm, y_position, width=width-4*cm, height=9*cm)
    
    # 새 페이지 추가
    c.showPage()
    
    # 재정 상태 차트 추가
    y_position = height - 2*cm
    c.setFont(KOREAN_FONT, 14)
    c.drawString(2*cm, y_position, "재정 상태 분석")
    
    # 구분선
    y_position -= 0.5*cm
    c.line(2*cm, y_position, width - 2*cm, y_position)
    
    # 차트 이미지 추가
    y_position -= 15*cm  # 차트 높이에 맞게 조정
    financial_img = ImageReader(financial_chart)
    c.drawImage(financial_img, 1*cm, y_position, width=width-2*cm, height=14*cm)
    
    # 새 페이지 추가
    c.showPage()
    
    # AI 분석 결과 섹션
    y_position = height - 2*cm
    c.setFont(KOREAN_FONT, 14)
    c.drawString(2*cm, y_position, "신용도 추세 분석")
    
    # 구분선
    y_position -= 0.5*cm
    c.line(2*cm, y_position, width - 2*cm, y_position)
    
    # 분석 결과 표시
    y_position -= 1*cm
    
    # 분석 결과 줄바꿈 처리
    lines = draw_wrapped_text(c, trend_analysis, 2*cm, y_position, 70, KOREAN_FONT, 10)
    
    # 페이지 저장
    c.save()
    
    return filename