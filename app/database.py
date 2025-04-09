import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

# 安全获取环境变量（带默认值）
DB_CONFIG = "mysql+pymysql://{user}:{pwd}@{host}/{db}".format(
    user=os.getenv("DB_USER", "root"),
    pwd=os.getenv("DB_PASSWORD", "123456789"),
    host=os.getenv("DB_HOST", "localhost"),
    db=os.getenv("DB_NAME", "forum_db")
) + "?charset=utf8mb4"

# 配置连接池
engine = create_engine(
    DB_CONFIG,
    pool_size=20,
    max_overflow=10,
    pool_recycle=1800,
    pool_pre_ping=True
)

# 使用 scoped_session 确保线程安全
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)
Base = declarative_base()  # 正确声明基类


def get_db():
    """自动处理提交和回滚的上下文管理器"""
    db = Session()
    try:
        yield db
        db.commit()  # 无异常时提交
    except Exception as e:
        db.rollback()  # 异常时回滚
        raise e
    finally:
        db.close()  # 关闭会话（返回连接至连接池）
        Session.remove()  # 清除线程局部会话
