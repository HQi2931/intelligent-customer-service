from pydantic import BaseModel, Field


class ReportRequest(BaseModel):
    user_id: str | None = Field(None, description="用户ID，不传则自动获取")
    month: str | None = Field(None, description="月份，格式 YYYY-MM，不传则取当前月")


class ReportResponse(BaseModel):
    report: str = Field(..., description="报告内容 (Markdown)")
    user_id: str = Field(..., description="用户ID")
    month: str = Field(..., description="报告月份")
