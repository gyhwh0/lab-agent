from typing import Any
from pydantic import BaseModel


class Response(BaseModel):
    # 统一封装的返回格式
    code: int
    message: str
    data: Any = None

    #     @classmethod类方法，第一个参数约定名字叫cls（class 的缩写）
    #     普通实例方法第一个参数是 self
    @classmethod
    def success(cls, message: str = "请求成功", data: Any = None):
        return cls(code=200, message=message, data=data)

    @classmethod
    def error(cls, code: int = 500, message: str = "请求失败"):
        return cls(code=code, message=message)


class PageResponse(BaseModel):
    """分页的返回结果"""

    list: Any = []
    total: int = 0
