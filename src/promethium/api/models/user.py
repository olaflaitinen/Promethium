"""
User model for authentication and authorization.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from promethium.api.models.base import Base


class User(Base):
    """
    User account for authentication and authorization.
    
    Attributes:
        id: Primary key.
        email: Unique email address for login.
        hashed_password: Bcrypt-hashed password.
        full_name: Display name.
        role: User role (admin, user).
        is_active: Whether the account is active.
        created_at: Account creation timestamp.
        updated_at: Last modification timestamp.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), default="user", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow, nullable=True)

    # Relationships
    datasets: Mapped[List["Dataset"]] = relationship("Dataset", back_populates="owner")
    pipelines: Mapped[List["Pipeline"]] = relationship("Pipeline", back_populates="owner")
    experiments: Mapped[List["Experiment"]] = relationship("Experiment", back_populates="owner")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
