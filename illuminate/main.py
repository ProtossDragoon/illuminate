import uvicorn
from fastapi import FastAPI

from illuminate.endpoints import router

# FastAPI 앱 생성
app = FastAPI(
    title='Illuminate API',
    description='YouTube 자막 및 관련 정보 추출 API',
    version='0.1.0',
)

# 라우터 등록
app.include_router(router)


if __name__ == '__main__':
    from illuminate.log_utils import setup_logging

    setup_logging()
    uvicorn.run('illuminate.main:app', host='0.0.0.0', port=8000)
