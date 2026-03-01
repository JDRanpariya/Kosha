from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    preferences_json = Column(JSON, default={})


class Source(Base):
    __tablename__ = "sources"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String, index=True) # e.g., 'rss', 'youtube'
    url = Column(String)
    config_json = Column(JSON, default={})
    last_fetched_at = Column(DateTime(timezone=True), nullable=True)
    enabled = Column(Boolean, default=True)


class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    external_id = Column(String, index=True)
    title = Column(String)
    author = Column(String, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    url = Column(String)
    content_hash = Column(String, unique=True)
    

class ItemContent(Base):
    __tablename__ = "item_content"
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)
    raw_content = Column(Text)
    parsed_content = Column(Text)
    metadata_json = Column(JSON, default={})
    # pgvector embedding column (size 384 is typical for sentence-transformers)
    embedding = Column(Vector(384))


class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    type = Column(String) # 'viewed', 'saved', 'dismissed'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    metadata_json = Column(JSON, default={})
