from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from .core.config import settings
from .api.chat import router as chat_router
from pathlib import Path

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(
    chat_router,
    prefix=settings.API_V1_STR,
    tags=["chat"]
)

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 配置静态文件和模板
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# 修改根路由
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(
        "welcome.html",
        {
            "request": request,
            "project_name": settings.PROJECT_NAME,
            "version": "1.0.0",
            "api_docs_url": f"{settings.API_V1_STR}/docs"
        }
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
