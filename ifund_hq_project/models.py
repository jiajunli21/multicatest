from typing import Optional
from pydantic import BaseModel, Field


class EtfRankItem(BaseModel):
    code: str = Field("", description="ETF代码")
    name: str = Field("", description="ETF名称")
    chgpct: Optional[float] = Field(None, description="涨跌幅(%)")
    speedRatio: Optional[float] = Field(None, description="涨速")
    volumeRatio: Optional[float] = Field(None, description="量比")
    etfLimitUpStockCnt: Optional[int] = Field(None, description="涨停个股数")
    topLeadStockCode: Optional[str] = Field(None, description="领涨成分股代码")
    topLeadStockName: Optional[str] = Field(None, description="领涨成分股名称")
    topLeadStockChangeRatio: Optional[float] = Field(None, description="领涨成分股涨跌幅(%)")
    bottomLeadStockCode: Optional[str] = Field(None, description="领跌成分股代码")
    bottomLeadStockName: Optional[str] = Field(None, description="领跌成分股名称")
    bottomLeadStockChangeRatio: Optional[float] = Field(None, description="领跌成分股涨跌幅(%)")


class RankData(BaseModel):
    updateTime: Optional[int] = Field(None, description="数据更新时间(Unix timestamp)")
    changeRatioTop9: list[EtfRankItem] = Field(default_factory=list)
    changeRatioBottom9: list[EtfRankItem] = Field(default_factory=list)
    speedRatioTop9: list[EtfRankItem] = Field(default_factory=list)
    speedRatioBottom9: list[EtfRankItem] = Field(default_factory=list)
    volumeRatioTop9: list[EtfRankItem] = Field(default_factory=list)
    volumeRatioBottom9: list[EtfRankItem] = Field(default_factory=list)
    limitUpCountTop9: list[EtfRankItem] = Field(default_factory=list)
    limitUpCountBottom9: list[EtfRankItem] = Field(default_factory=list)


class ApiResponse(BaseModel):
    code: int = Field(0, description="状态码: 0=成功, -1=错误")
    message: str = Field("success", description="状态消息")
    data: RankData = Field(default_factory=RankData)
    timestamp: int = Field(0, description="响应时间戳")
