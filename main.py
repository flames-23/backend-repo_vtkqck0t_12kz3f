import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime

from database import db, create_document, get_documents
from schemas import Project as ProjectSchema, Post as PostSchema, ContactMessage as ContactMessageSchema

app = FastAPI(title="Arnav Parashar Portfolio API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProjectResponse(BaseModel):
    title: str
    slug: str
    description: str
    tags: List[str] = []
    stack: List[str] = []
    impact: Optional[str] = None
    cover_url: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None
    featured: bool = False


class PostResponse(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    content: str
    tags: List[str] = []
    published_at: Optional[datetime] = None


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str


@app.get("/")
def read_root():
    return {"message": "Arnav Portfolio API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


# ------------------------ Seed Helpers ------------------------

def ensure_seed_data():
    if db is None:
        return

    # Seed projects if empty
    if db.project.count_documents({}) == 0:
        examples = [
            ProjectSchema(
                title="Real-time Vector Search Service",
                slug="vector-search",
                description="Low-latency vector DB layer with HNSW + PQ, tuned for p95 < 20ms.",
                tags=["AI", "Infra"],
                stack=["Rust", "gRPC", "ANN", "Redis", "Docker"],
                impact="p95 latency ↓ 38% at 10k QPS",
                cover_url="/covers/vector.jpg",
                github_url="https://github.com/example/vector-search",
                demo_url=None,
                featured=True,
            ),
            ProjectSchema(
                title="LLM-Assisted Code Review Bot",
                slug="code-review-bot",
                description="Context-aware PR reviewer with inline suggestions and risk flags.",
                tags=["AI", "Open Source", "Web"],
                stack=["Python", "FastAPI", "OpenAI", "Postgres"],
                impact="review time ↓ 45% across 120+ PRs",
                cover_url="/covers/bot.jpg",
                github_url="https://github.com/example/code-review-bot",
                demo_url=None,
                featured=False,
            ),
            ProjectSchema(
                title="Telemetry Pipeline for Edge Devices",
                slug="edge-telemetry",
                description="Exactly-once ingestion with Kafka + Flink; real-time dashboards.",
                tags=["Infra", "Data"],
                stack=["Kafka", "Flink", "Debezium", "ClickHouse"],
                impact="throughput ↑ 3.2x, data loss ~0%",
                cover_url="/covers/telemetry.jpg",
                github_url=None,
                demo_url=None,
                featured=False,
            ),
        ]
        for p in examples:
            create_document("project", p)

    # Seed posts if empty
    if db.post.count_documents({}) == 0:
        posts = [
            PostSchema(
                title="Notes on low-latency systems",
                slug="low-latency-notes",
                excerpt="What actually moves p95 and p99 in real systems.",
                content="# Low-latency notes\nA practical list of levers that matter.",
                tags=["systems", "perf"],
                published_at=datetime.utcnow(),
            )
        ]
        for post in posts:
            create_document("post", post)


# ------------------------ Project Endpoints ------------------------

@app.get("/api/projects", response_model=List[ProjectResponse])
def list_projects(tag: Optional[str] = None):
    ensure_seed_data()
    filt = {"tags": tag} if tag else {}
    projects = get_documents("project", filt)
    # Normalize Mongo docs
    return [
        ProjectResponse(
            title=p.get("title"),
            slug=p.get("slug"),
            description=p.get("description"),
            tags=p.get("tags", []),
            stack=p.get("stack", []),
            impact=p.get("impact"),
            cover_url=p.get("cover_url"),
            github_url=p.get("github_url"),
            demo_url=p.get("demo_url"),
            featured=p.get("featured", False),
        ) for p in projects
    ]


@app.get("/api/projects/{slug}", response_model=ProjectResponse)
def get_project(slug: str):
    ensure_seed_data()
    projects = get_documents("project", {"slug": slug}, limit=1)
    if not projects:
        raise HTTPException(status_code=404, detail="Project not found")
    p = projects[0]
    return ProjectResponse(
        title=p.get("title"),
        slug=p.get("slug"),
        description=p.get("description"),
        tags=p.get("tags", []),
        stack=p.get("stack", []),
        impact=p.get("impact"),
        cover_url=p.get("cover_url"),
        github_url=p.get("github_url"),
        demo_url=p.get("demo_url"),
        featured=p.get("featured", False),
    )


# ------------------------ Blog Endpoints ------------------------

@app.get("/api/posts", response_model=List[PostResponse])
def list_posts(tag: Optional[str] = None):
    ensure_seed_data()
    filt = {"tags": tag} if tag else {}
    posts = get_documents("post", filt)
    return [PostResponse(**{
        "title": po.get("title"),
        "slug": po.get("slug"),
        "excerpt": po.get("excerpt"),
        "content": po.get("content"),
        "tags": po.get("tags", []),
        "published_at": po.get("published_at")
    }) for po in posts]


@app.get("/api/posts/{slug}", response_model=PostResponse)
def get_post(slug: str):
    ensure_seed_data()
    posts = get_documents("post", {"slug": slug}, limit=1)
    if not posts:
        raise HTTPException(status_code=404, detail="Post not found")
    po = posts[0]
    return PostResponse(**{
        "title": po.get("title"),
        "slug": po.get("slug"),
        "excerpt": po.get("excerpt"),
        "content": po.get("content"),
        "tags": po.get("tags", []),
        "published_at": po.get("published_at")
    })


# ------------------------ Contact Endpoint ------------------------

@app.post("/api/contact")
def submit_contact(payload: ContactRequest):
    doc = ContactMessageSchema(**payload.dict())
    msg_id = create_document("contactmessage", doc)
    return {"status": "ok", "id": msg_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
