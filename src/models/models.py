import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, func, Column, Boolean, Table, Enum, CheckConstraint, UUID
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    role = Column(Enum(Role), default=Role.user, nullable=False)
    avatar: Mapped[str] = mapped_column(String(255), nullable=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    images = relationship("Image", back_populates="owner")
    comments = relationship("Comment", back_populates="user")


class ImageTagsAssociation(Base):
    __tablename__ = "image_tag_association"

    tag_id = mapped_column(Integer, ForeignKey("tags.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    image_id = mapped_column(Integer, ForeignKey("images.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)


class Image(Base):
    __tablename__ = 'images'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False, index=True)
    size: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    image_path: Mapped[str] = mapped_column(String, index=True)
    mime_type: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    owner_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    count_tags: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    owner = relationship("User", back_populates="images", lazy="joined")
    tags = relationship("Tag", secondary="image_tag_association", back_populates="images")
    comments = relationship("Comment", back_populates="image")


class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    images = relationship('Image', secondary="image_tag_association", back_populates='tags')


class Comment(Base):
    __tablename__ = 'comments'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'))
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey('images.id'))

    user = relationship("User", back_populates="comments")
    image = relationship("Image", back_populates="comments")
