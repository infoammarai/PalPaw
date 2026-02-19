from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from .db import Base, engine
from .models import User, Dog, Scan
from .deps import get_db, require_user_id
from .schemas import (
    AppleAuthRequest, AppleAuthResponse,
    DogCreate, DogOut,
    ScanCreate, ScanOut
)
from .auth_apple import verify_apple_identity_token
from .auth_jwt import sign_access_token

app = FastAPI(title="Pet Intel API")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/auth/apple", response_model=AppleAuthResponse)
async def auth_apple(body: AppleAuthRequest, db: Session = Depends(get_db)):
    try:
      apple_sub = await verify_apple_identity_token(body.identityToken)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"apple_token_invalid: {str(e)}")

    # Use apple_sub as both id and apple_sub for simplicity (fine for MVP)
    user = db.get(User, apple_sub)
    if not user:
        user = User(id=apple_sub, apple_sub=apple_sub)
        db.add(user)
        db.commit()

    access = sign_access_token(user.id)
    return AppleAuthResponse(accessToken=access)

@app.get("/dogs", response_model=list[DogOut])
def list_dogs(user_id: str = Depends(require_user_id), db: Session = Depends(get_db)):
    dogs = db.query(Dog).filter(Dog.user_id == user_id).order_by(Dog.created_at.desc()).all()
    return [
        DogOut(id=d.id, name=d.name, breed=d.breed, weightKg=d.weight_kg)
        for d in dogs
    ]

@app.post("/dogs", response_model=DogOut)
def create_dog(body: DogCreate, user_id: str = Depends(require_user_id), db: Session = Depends(get_db)):
    dog = Dog(
        id=str(uuid.uuid4()),
        user_id=user_id,
        name=body.name,
        breed=body.breed,
        weight_kg=body.weightKg
    )
    db.add(dog)
    db.commit()
    db.refresh(dog)
    return DogOut(id=dog.id, name=dog.name, breed=dog.breed, weightKg=dog.weight_kg)

@app.get("/scans", response_model=list[ScanOut])
def list_scans(user_id: str = Depends(require_user_id), db: Session = Depends(get_db)):
    scans = (
        db.query(Scan)
        .join(Dog, Dog.id == Scan.dog_id)
        .filter(Scan.user_id == user_id)
        .order_by(Scan.created_at.desc())
        .limit(100)
        .all()
    )

    out: list[ScanOut] = []
    for s in scans:
        dog = db.get(Dog, s.dog_id)
        out.append(ScanOut(
            id=s.id,
            createdAt=s.created_at.isoformat(),
            summary=s.summary,
            activityScore=s.activity_score,
            dogName=dog.name if dog else "Unknown"
        ))
    return out

@app.post("/scans")
def create_scan(body: ScanCreate, user_id: str = Depends(require_user_id), db: Session = Depends(get_db)):
    dog = db.query(Dog).filter(Dog.id == body.dogId, Dog.user_id == user_id).first()
    if not dog:
        raise HTTPException(status_code=404, detail="dog_not_found")

    scan = Scan(
        id=str(uuid.uuid4()),
        user_id=user_id,
        dog_id=body.dogId,
        kind=body.kind,
        duration_sec=body.durationSec,
        dog_detected=body.dogDetected,
        activity_score=body.activityScore,
        summary=body.summary,
        created_at=datetime.utcnow(),
    )
    db.add(scan)
    db.commit()
    return {"id": scan.id}
