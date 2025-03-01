import asyncio
import enum
from datetime import datetime
from enum import unique

from sqlalchemy import String, DECIMAL, select, ForeignKey, LargeBinary, DateTime, func, Integer
from sqlalchemy.dialects.postgresql import BYTEA
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column

from db import Base, db
from db.utils import CreatedModel

# ctrl + space*2
class AccountData(CreatedModel):
    username: Mapped[str] = mapped_column(String(55), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    last_used: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    worked: Mapped["Worked"] = relationship("Worked", back_populates="account")

class Worked(CreatedModel):
    accounts_id: Mapped[int] = mapped_column(Integer, ForeignKey("accountdatas.id", ondelete="cascade"), nullable=False)
    operation_type: Mapped[str] = mapped_column(String(20), nullable=False)
    target: Mapped[str] = mapped_column(String(255), nullable=False)
    count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(20), default="success")
    account: Mapped["AccountData"] = relationship("AccountData", back_populates="worked")


metadata = Base.metadata

