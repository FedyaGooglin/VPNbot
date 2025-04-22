from datetime import datetime

from sqlalchemy import String, Text, ForeignKey, func, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    created: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100))

    free_keys_taken: Mapped[int] = mapped_column(Integer, default=0)
    last_key_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    vpn_keys: Mapped[list["VpnKey"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan"
    )


class VpnKey(Base):
    __tablename__ = 'vpn_keys'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    config: Mapped[str] = mapped_column(Text, nullable=False)
    created: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    owner: Mapped["User"] = relationship(back_populates="vpn_keys")


class FreeVpnKey(Base):
    __tablename__ = 'free_keys'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    uuid: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=False)
    config: Mapped[str] = mapped_column(Text, nullable=False)

