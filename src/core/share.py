"""Define Share class and corresponding SQL table schema."""

from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column


class Base(MappedAsDataclass, DeclarativeBase):
    # Base class for all table-defining classes, for use with sqlalchemy.orm
    # See https://docs.sqlalchemy.org/en/20/orm/dataclasses.html
    pass


class Share(Base):
    """
    The Share is the most basic concept in LinkSharer.
    It represents a downloadable set of files, with some additional metadata and features:

    - UUID for access
    - Creation date
    - Expiration date
    - Password protection (PLANNED)
    - Writability (PLANNED)

    This class is implemented as a SQLAlchemy ORM class for easy interfacing between Python and the db.
    """

    __tablename__ = "shares"

    # Standard metadata
    id: Mapped[UUID] = mapped_column(
        init=False, primary_key=True, default_factory=uuid4
    )
    created: Mapped[datetime] = mapped_column(init=False, default_factory=datetime.now)
    _path_str: Mapped[str]  # Cannot map a Path object sadly

    # Optionals
    name: Mapped[Optional[str]]  # Can be used as access shorthand
    expiry: Mapped[Optional[datetime]]

    # Dynamic properties
    @property
    def is_expired(self) -> bool:
        if not self.expiry:
            return False

        return datetime.now() >= self.expiry

    @cached_property
    def path(self):
        return Path(self._path_str)
