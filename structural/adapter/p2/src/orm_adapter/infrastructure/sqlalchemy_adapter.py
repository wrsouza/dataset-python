"""Adapter 1 — SQLAlchemy 2.0 ORM wrapped to implement UserRepository (Target).

Adaptee: SQLAlchemy Session + declarative model.
Adapter: SQLAlchemyUserAdapter translates UserRepository calls into ORM queries.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from orm_adapter.domain.entities import User, UserNotFoundError


class _Base(DeclarativeBase):
    pass


class UserModel(_Base):
    """SQLAlchemy ORM model — infrastructure detail, not a domain entity."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


def create_tables(engine: object) -> None:
    """Create all tables. Call once at startup."""
    _Base.metadata.create_all(engine)  # type: ignore[arg-type]


class SQLAlchemyUserAdapter:
    """Adapter: bridges SQLAlchemy Session (Adaptee) to UserRepository (Target).

    LSP: every method satisfies the UserRepository contract precisely.
    DIP: callers depend on UserRepository, not on this class.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, user_id: int) -> User | None:
        model = self._session.get(UserModel, user_id)
        return self._to_entity(model) if model else None

    def find_all(self) -> list[User]:
        models = self._session.execute(select(UserModel)).scalars().all()
        return [self._to_entity(m) for m in models]

    def save(self, user: User) -> User:
        if user.id:
            model = self._session.get(UserModel, user.id)
            if model is None:
                raise UserNotFoundError(user.id)
            model.name = user.name
            model.email = user.email
            model.is_active = user.is_active
        else:
            model = UserModel(
                name=user.name,
                email=user.email,
                is_active=user.is_active,
            )
            self._session.add(model)

        self._session.commit()
        self._session.refresh(model)
        return self._to_entity(model)

    def delete(self, user_id: int) -> None:
        model = self._session.get(UserModel, user_id)
        if model is None:
            raise UserNotFoundError(user_id)
        self._session.delete(model)
        self._session.commit()

    @staticmethod
    def _to_entity(model: UserModel) -> User:
        return User(
            id=model.id,
            name=model.name,
            email=model.email,
            is_active=model.is_active,
        )
