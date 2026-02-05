from datetime import date, datetime, time
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import MetaData, Table, select, and_
from sqlalchemy.orm import Session

from database import get_db
from schemas import CoinHistoryRead

router = APIRouter(prefix="/coins", tags=["coins"])


def _reflect_tables(db: Session):
    """
    ORM 클래스(CoinHistory 등)를 몰라도 DB 테이블을 그대로 읽어오는 방식.
    """
    engine = db.get_bind()
    md = MetaData()

    coins = Table("coins", md, autoload_with=engine)
    coin_history = Table("coin_history", md, autoload_with=engine)
    return coins, coin_history


@router.get("/{coin_id}/history", response_model=list[CoinHistoryRead])
def get_coin_history_daily(
    coin_id: int,
    from_: date = Query(..., alias="from", description="YYYY-MM-DD (일 단위)"),
    to: date = Query(..., description="YYYY-MM-DD (일 단위)"),
    limit: int = Query(2000, ge=1, le=10000),
    db: Session = Depends(get_db),
):
    # 날짜 검증
    if from_ > to:
        raise HTTPException(status_code=400, detail="from must be <= to")

    coins, coin_history = _reflect_tables(db)

    # 관심코인 등록(존재) 여부 확인 (coins 테이블 기준)
    coin_exists = db.execute(select(coins.c.id).where(coins.c.id == coin_id)).first()
    if not coin_exists:
        raise HTTPException(status_code=404, detail="등록되지 않은 코인입니다. 먼저 관심코인을 등록하세요.")

    # ✅ 일 단위 범위로만 조회
    start_dt = datetime.combine(from_, time.min)  # 00:00:00
    end_dt = datetime.combine(to, time.max)      # 23:59:59.999999

    stmt = (
        select(coin_history)
        .where(
            and_(
                coin_history.c.coin_id == coin_id,
                coin_history.c.collected_at >= start_dt,
                coin_history.c.collected_at <= end_dt,
            )
        )
        .order_by(coin_history.c.collected_at.asc())
        .limit(limit)
    )

    rows = db.execute(stmt).mappings().all()

    if not rows:
        raise HTTPException(status_code=404, detail="해당 날짜 범위에 저장된 시세 데이터가 없습니다.")

    # mappings()는 dict 형태라 response_model(Pydantic)과 잘 맞음
    return rows