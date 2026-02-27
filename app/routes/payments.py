from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Payment, User, Portfolio
from app.utils.security import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/payments", tags=["Payments"])

class PaymentCreate(BaseModel):
    amount: float
    transaction_id: str

@router.post("/upgrade")
def upgrade_to_premium(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.is_premium:
        raise HTTPException(status_code=400, detail="User is already premium.")

    # In reality, verify transaction_id with payment gateway (Stripe/Razorpay, etc.)
    # Mocking successful payment
    payment = Payment(
        user_id=current_user.id,
        amount=data.amount,
        status="success",
        transaction_id=data.transaction_id
    )
    db.add(payment)

    current_user.is_premium = True
    db.commit()

    return {"message": "Successfully upgraded to Premium."}


@router.post("/build-apk/{portfolio_id}")
async def build_apk(
    portfolio_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not current_user.is_premium:
        raise HTTPException(status_code=403, detail="Premium feature only. Upgrade to build APK.")

    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.user_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    # Here we would trigger the APK Builder Microservice via celery/redis or httpx
    # For now, simulate success.
    # e.g., send json_data to an external service or enqueue task
    apk_download_url = f"https://s3.aws.com/appify-apks/{current_user.id}/{portfolio_id}/app.apk"
    portfolio.apk_url = apk_download_url
    db.commit()

    return {
        "message": "APK build triggered successfully",
        "status": "building",
        "download_url": apk_download_url
    }
