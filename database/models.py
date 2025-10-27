from datetime import datetime, timezone

from sqlalchemy import BigInteger, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

import secrets

def generate_short_id(): # generate id
    return secrets.token_urlsafe(8)  # example: '4f6LsPVv'

class Base(DeclarativeBase):
    created: Mapped[DateTime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc).replace(microsecond=0))

class User(Base): 
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)  # Telegram user_id
    username: Mapped[str] = mapped_column(String(64), nullable=True)
    
class ThoughtForm(Base): 
    __tablename__ = "thoughtforms"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_short_id)  
    content: Mapped[str] = mapped_column(Text)
    owner_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete='CASCADE'))

    owner = relationship("User", backref="thoughtforms")    
    
class Transfer(Base): 
    __tablename__ = "transfers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    thoughtform_id: Mapped[str] = mapped_column(String(64), ForeignKey("thoughtforms.id", ondelete='CASCADE'))
    sender_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id", ondelete='CASCADE'))
    receiver_username: Mapped[str] = mapped_column(String(64))

    thoughtform = relationship("ThoughtForm")
    sender = relationship("User")    
    
    