from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Portfolio
from app.utils.security import get_current_user
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/portfolios", tags=["Portfolios"])


class PortfolioCreate(BaseModel):
    json_data: Dict[str, Any]
    theme: Optional[str] = "default"


class PortfolioUpdate(BaseModel):
    json_data: Optional[Dict[str, Any]] = None
    theme: Optional[str] = None


@router.post("/")
def create_portfolio(
    data: PortfolioCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    portfolio = Portfolio(
        user_id=current_user.id,
        json_data=data.json_data,
        theme=data.theme
    )
    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)

    return {"message": "Portfolio created", "portfolio_id": portfolio.id}


@router.get("/")
def list_portfolios(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    portfolios = db.query(Portfolio).filter(Portfolio.user_id == current_user.id).all()
    return portfolios


@router.get("/{portfolio_id}")
def get_portfolio(
    portfolio_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio


@router.put("/{portfolio_id}")
def update_portfolio(
    portfolio_id: str,
    data: PortfolioUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    if data.json_data is not None:
        portfolio.json_data = data.json_data
    if data.theme is not None:
        portfolio.theme = data.theme

    db.commit()
    db.refresh(portfolio)
    return {"message": "Portfolio updated", "portfolio": portfolio}
