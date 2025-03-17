import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("ERROR: OPENAI_API_KEY가 설정되지 않았습니다! `.env` 파일을 확인하세요.")