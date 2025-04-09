import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import user, post
from app.routers import auth, posts, comments
from app.schemas.user import UserOut  # 导入 User 模型
from app.schemas.post import PostOut  # 导入 Post 模型

# 创建数据库表
user.Base.metadata.create_all(bind=engine)
post.Base.metadata.create_all(bind=engine)

# 调用无参数的 model_rebuild()，以确保 forward 引用得到正确解析
UserOut.model_rebuild()

app = FastAPI()

# 允许的源列表
origins = [
    "http://localhost:5173",  # 前端项目的地址
]

# 添加 CORS 中间件，忽略类型检查
app.add_middleware(
    # type: ignore
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)


@app.get("/")
def read_root():
    return {"message": "Forum API"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8800)
