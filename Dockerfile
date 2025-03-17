# Python 3.9 이미지를 기본으로 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 패키지 설치를 위한 requirements.txt 복사
COPY requirements.txt .

# 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사 (.env 파일은 .dockerignore에 의해 제외됨)
COPY . .

# 컨테이너가 시작될 때 실행할 명령어 설정
# main.py는 FastAPI 애플리케이션의 진입점 파일명으로 변경하세요
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# 포트 노출
EXPOSE 8000
