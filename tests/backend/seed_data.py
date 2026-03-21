from backend.db.database import SessionLocal
from backend.db.models import Source

db = SessionLocal()

# Add Paul Graham RSS
pg_rss = Source(
    name="Paul Graham Essays",
    type="rss",
    enabled=True,
    config_json={"feed_url": "https://paulgraham.com/rss.html"}
)

# Add ArXiv AI
arxiv_ai = Source(
    name="ArXiv CS.AI",
    type="arxiv",
    enabled=True,
    config_json={"categories": ["cs.AI"]}
)

db.add(pg_rss)
db.add(arxiv_ai)
db.commit()
db.close()
print("Seed data added!")
