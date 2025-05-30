from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session as SQLAlchemySession
from datetime import datetime
from typing import Optional

from database import Base, User, License, SessionLocal, engine

app = FastAPI()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LicenseRequest(BaseModel):
    key: str
    volume_serial: Optional[str] = None  # Optional for backward compatibility

class LicenseResponse(BaseModel):
    user: str
    license_name: str
    valid_until: str
    status: str
    volume_match: bool

@app.get("/")
def root():
    return {"status": "API running"}

@app.post("/check_license", response_model=LicenseResponse)
def check_license(data: LicenseRequest, db: SQLAlchemySession = Depends(get_db)):
    license = db.query(License).filter_by(key=data.key).first()
    if not license:
        raise HTTPException(status_code=404, detail="License key not found")

    if license.valid_until < datetime.now():
        raise HTTPException(status_code=400, detail="License has expired")

    volume_match = False
    if data.volume_serial:
        volume_match = (data.volume_serial == license.volume_serial)
        if not volume_match:
            raise HTTPException(
                status_code=403,
                detail="Volume serial number does not match"
            )

    return {
        "user": license.user.username,
        "license_name": license.name,
        "valid_until": license.valid_until.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "valid",
        "volume_match": volume_match
    }

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)
