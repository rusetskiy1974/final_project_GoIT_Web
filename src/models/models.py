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
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    username = Column(String(50))
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    password = Column(String(length=1024), nullable=False)
    role = Column(Enum(Role), default=Role.user, nullable=False)
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    registered_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    confirmed = Column(Boolean, default=False, nullable=False)
    images = relationship("Image", back_populates="owner")
    comments = relationship("Comment", back_populates="user")


class ImageTagAssociation(Base):
    __tablename__ = "image_tag_association"
    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey("images.id", ondelete="CASCADE", onupdate="CASCADE"))
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE", onupdate="CASCADE"))



class Image(Base):
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    size = Column(Integer, nullable=False, index=True)
    title = Column(String, index=True)
    image_path = Column(String, index=True)
    mime_type = Column(String, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    count_tags = Column(Integer, default=0, nullable=False)
    owner = relationship("User", back_populates="images", lazy="joined")
    tags = relationship("Tag", secondary="image_tag_association", back_populates="images", lazy="joined")
    comments = relationship("Comment", back_populates="image")


class Tag(Base):
    __tablename__ = 'tags'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    images = relationship("Image", secondary="image_tag_association", back_populates="tags", lazy="joined")


class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'))
    image_id = Column(Integer, ForeignKey('images.id'))

    user = relationship("User", back_populates="comments")
    image = relationship("Image", back_populates="comments")
