from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from app.utils.data_generator import generate_multiple_customers, save_to_json, load_customer_data
from app.services.ai_analyzer import analyze_customer_data, analyze_credit_trend
from app.services.report_generator import generate_credit_report, generate_timeseries_report
from typing import Optional, List
import os

router = APIRouter()

@router.post("/generate_customers/")
def create_customers(count: int = 5, profile_distribution: dict = None):
    """
    여러 고객의 시계열 데이터를 생성합니다.
    
    Args:
        count: 생성할 고객 수
        profile_distribution: 프로필 유형 분포 (예: {"average": 0.6, "high_risk": 0.2, "premium": 0.2})
    """
    customers = generate_multiple_customers(count, profile_distribution)
    
    # JSON 파일로 저장
    filepath = save_to_json(customers)
    
    # 개별 고객 파일로도 저장
    for customer in customers:
        customer_filepath = save_to_json(
            customer, 
            f"customer_{customer['customer_id']}.json"
        )
    
    return {
        "message": f"{count}명의 고객 데이터가 생성되었습니다.",
        "filepath": filepath,
        "customers": [{"id": c["customer_id"], "name": c["name"]} for c in customers]
    }

@router.get("/customers/")
def get_customers():
    """모든 고객 목록을 반환합니다."""
    customers = load_customer_data()
    return {
        "count": len(customers),
        "customers": [{"id": c["customer_id"], "name": c["name"]} for c in customers]
    }

@router.get("/customer/{customer_id}")
def get_customer(customer_id: str):
    """특정 고객의 정보를 반환합니다."""
    customer = load_customer_data(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="해당 고객 정보를 찾을 수 없습니다.")
    return customer

@router.get("/customer/name/{customer_name}")
def get_customer_by_name(customer_name: str):
    """고객 이름으로 정보를 반환합니다."""
    customer = load_customer_data(customer_name=customer_name)
    if not customer:
        raise HTTPException(status_code=404, detail="해당 고객 정보를 찾을 수 없습니다.")
    return customer

@router.post("/analyze/")
def analyze_customer(customer_id: Optional[str] = None, customer_name: Optional[str] = None, request_text: str = None):
    """
    고객 데이터를 AI로 분석합니다.
    
    Args:
        customer_id: 고객 ID
        customer_name: 고객 이름
        request_text: 분석 요청 텍스트
    """
    if not customer_id and not customer_name:
        raise HTTPException(status_code=400, detail="고객 ID 또는 이름을 제공해야 합니다.")
    
    result = analyze_customer_data(customer_id, customer_name, request_text)
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {"response": result}

@router.post("/analyze_trend/")
def analyze_trend(customer_id: Optional[str] = None, customer_name: Optional[str] = None, 
                 start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    고객의 신용도 추세를 분석합니다.
    
    Args:
        customer_id: 고객 ID
        customer_name: 고객 이름
        start_date: 시작 날짜 (YYYY-MM 형식)
        end_date: 종료 날짜 (YYYY-MM 형식)
    """
    if not customer_id and not customer_name:
        raise HTTPException(status_code=400, detail="고객 ID 또는 이름을 제공해야 합니다.")
    
    result = analyze_credit_trend(customer_id, customer_name, start_date, end_date)
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    
    return {"response": result}

@router.get("/generate_report/")
def create_report(customer_id: Optional[str] = None, customer_name: Optional[str] = None, 
                 analysis_question: Optional[str] = None):
    """
    고객 신용 보고서를 생성합니다.
    
    Args:
        customer_id: 고객 ID
        customer_name: 고객 이름
        analysis_question: 분석에 사용할 질문
    """
    if not customer_id and not customer_name:
        raise HTTPException(status_code=400, detail="고객 ID 또는 이름을 제공해야 합니다.")
    
    try:
        report_filename = generate_credit_report(customer_id, customer_name, analysis_question)
        
        return FileResponse(
            path=report_filename,
            filename=os.path.basename(report_filename),
            media_type="application/pdf"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}")

@router.get("/generate_timeseries_report/")
def create_timeseries_report(customer_id: Optional[str] = None, customer_name: Optional[str] = None,
                            start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    고객의 시계열 데이터 보고서를 생성합니다.
    
    Args:
        customer_id: 고객 ID
        customer_name: 고객 이름
        start_date: 시작 날짜 (YYYY-MM 형식)
        end_date: 종료 날짜 (YYYY-MM 형식)
    """
    if not customer_id and not customer_name:
        raise HTTPException(status_code=400, detail="고객 ID 또는 이름을 제공해야 합니다.")
    
    try:
        report_filename = generate_timeseries_report(customer_id, customer_name, start_date, end_date)
        
        return FileResponse(
            path=report_filename,
            filename=os.path.basename(report_filename),
            media_type="application/pdf"
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"보고서 생성 중 오류가 발생했습니다: {str(e)}")