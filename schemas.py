from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CoinHistoryRead(BaseModel):
    id: int
    coin_id: int

    trade_price: Optional[float] = None
    trade_volume: Optional[float] = None
    trade_timestamp: Optional[int] = None

    opening_price: Optional[float] = None
    high_price: Optional[float] = None
    low_price: Optional[float] = None
    prev_closing_price: Optional[float] = None

    change_price: Optional[float] = None
    change_rate: Optional[float] = None

    collected_at: datetime

    class Config:
        # Pydantic v2면 from_attributes=True가 더 정확하지만,
        # dict 반환(mappings())이면 어차피 잘 동작함.
        from_attributes = True