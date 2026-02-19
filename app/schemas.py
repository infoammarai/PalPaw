from pydantic import BaseModel
from typing import Optional

class AppleAuthRequest(BaseModel):
    identityToken: str

class AppleAuthResponse(BaseModel):
    accessToken: str

class DogCreate(BaseModel):
    name: str
    breed: Optional[str] = None
    weightKg: Optional[float] = None

class DogOut(BaseModel):
    id: str
    name: str
    breed: Optional[str] = None
weightKg: Optional[float] = None

class ScanCreate(BaseModel):
    dogId: str
    kind: str = "video"
    durationSec: int = 0
    dogDetected: bool = False
    activityScore: float = 0.0
    summary: str = "Scan saved."

class ScanOut(BaseModel):
    id: str
    createdAt: str
    summary: str
    activityScore: float
    dogName: str
