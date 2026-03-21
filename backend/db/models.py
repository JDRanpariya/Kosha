from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from backend.db.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    preferences_json = Column(JSON, default=dict)


class Source(Base):
    __tablename__ = "sources"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    type = Column(String, index=True)
    url = Column(String)
    config_json = Column(JSON, default=dict)
    last_fetched_at = Column(DateTime(timezone=True), nullable=True)
    enabled = Column(Boolean, default=True)
    items = relationship("Item", back_populates="source", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    external_id = Column(String, index=True)
    title = Column(String)
    author = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    url = Column(String)
    content_hash = Column(String, unique=True)
    source = relationship("Source", back_populates="items")
    content = relationship(
        "ItemContent",
        uselist=False,
        back_populates="item",
        cascade="all, delete-orphan",
    )
    interactions = relationship(
        "Interaction",
        back_populates="item",
        cascade="all, delete-orphan",
    )


class ItemContent(Base):
    __tablename__ = "item_content"
    __table_args__ = {'extend_existing': True}
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    raw_content = Column(Text)
    parsed_content = Column(Text)
    metadata_json = Column(JSON, default=dict)
    embedding = Column(Vector(384))
    item = relationship("Item", back_populates="content")


class Interaction(Base):
    __tablename__ = "interactions"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    # ondelete CASCADE so the DB enforces cleanup even if SQLAlchemy
    # ORM cascade is bypassed (e.g. bulk deletes via raw SQL)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"))
    type = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata_json = Column(JSON, default=dict)
    item = relationship("Item", back_populates="interactions")
