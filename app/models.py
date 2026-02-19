from sqlalchemy import String, DateTime, ForeignKey, Float, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .db import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # we’ll use appleSub as id for simplicity
    apple_sub: Mapped[str] = mapped_column(String, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    dogs: Mapped[list["Dog"]] = relationship(back_populates="user")
    scans: Mapped[list["Scan"]] = relationship(back_populates="user")

class Dog(Base):
    __tablename__ = "dogs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)

    name: Mapped[str] = mapped_column(String, index=True)
    breed: Mapped[str | None] = mapped_column(String, nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="dogs")
    scans: Mapped[list["Scan"]] = relationship(back_populates="dog")

class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), index=True)
    dog_id: Mapped[str] = mapped_column(String, ForeignKey("dogs.id"), index=True)

    kind: Mapped[str] = mapped_column(String, default="video")
    duration_sec: Mapped[int] = mapped_column(Integer, default=0)

    dog_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    activity_score: Mapped[float] = mapped_column(Float, default=0.0)
    summary: Mapped[str] = mapped_column(String, default="Scan saved.")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="scans")
    dog: Mapped["Dog"] = relationship(back_populates="scans")
