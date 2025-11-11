"""
Database Schemas for Arnav Parashar Portfolio

Each Pydantic model corresponds to a MongoDB collection with the lowercased
class name as the collection name.

Collections:
- project
- post
- contactmessage
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class Stat(BaseModel):
    label: str
    value: str

class Project(BaseModel):
    title: str = Field(..., description="Project title")
    slug: str = Field(..., description="URL friendly id")
    description: str = Field(..., description="Short description")
    tags: List[str] = Field(default_factory=list, description="Filterable tags like AI, Infra, Web")
    stack: List[str] = Field(default_factory=list, description="Technology stack chips")
    impact: Optional[str] = Field(None, description="Outcome metric e.g., latency ↓ 35%")
    cover_url: Optional[str] = Field(None, description="Image/video cover URL")
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    case_study: Optional[str] = Field(None, description="Markdown/MDX content for case study")
    stats: List[Stat] = Field(default_factory=list)
    featured: bool = Field(default=False)

class Post(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    tags: List[str] = Field(default_factory=list)
    published_at: Optional[datetime] = None

class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str
