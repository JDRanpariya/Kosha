# 🪷 Kosha
**Fully Open Source Personalized Content Streamer**

## First-time Setup

Create the following secret files before running `docker compose up`:

```bash
echo "kosha_dev_password" > infra/secrets/db_password.txt
echo "minioadmin"         > infra/secrets/minio_root_user.txt
echo "minioadmin"         > infra/secrets/minio_root_password.txt
echo ""                   > infra/secrets/spotify_client_id.txt
echo ""                   > infra/secrets/spotify_client_secret.txt
echo ""                   > infra/secrets/youtube_api_key.txt
```

Spotify and YouTube secrets can be left empty — those connectors are skipped if credentials are missing.

---

## 🚀 Minimal MVP Roadmap (4–6 weeks)

### Week 0: Repo + Infra
- Scaffold monorepo (backend, frontend, connectors)  
- Docker Compose environment  
- Postgres + Redis + MinIO  

### Week 1–2: Ingestion + Storage
- Implement 3 connectors (RSS, YouTube, newsletters via Mailgun webhook or IMAP parsing)  
- Parse → clean → store core schema + raw content  
- Add transcript extraction for YouTube/podcasts  

### Week 2–3: Embeddings + Basic UI
- Hook in embedding model, store vectors in pgvector  
- Build simple React UI showing daily digest from last 24h  
- Add Obsidian export endpoint  

### Week 3–4: Feedback & Ranking
- Add explicit feedback API (save, highlight + reason)  
- Basic ranking: recency + source weight + embedding similarity  

### Week 4+: Iterate
- Add Celery tasks  
- Scheduled digest generation  
- Analytics dashboard  
- Begin gathering feedback for Phase 1 ML  

---

## ⚠️ Danger Zones & Mitigations

- **RLHF too early** → wait for high-signal feedback (≥ 500 explicit examples)  
- **Over-indexing content** → prune old vectors, compress, or store reduced embeddings  
- **Connector maintenance** → build adapters + monitoring/tests per connector  

---

## ✅ Quick Checklist to Start Coding (Actionable)

- [x] Initialize repo + Docker Compose (Postgres, Redis, MinIO)  
- [x] Define DB schema (users, sources, items, interactions, feedback)  
- [x] Implement RSS & YouTube fetchers + HTML → Markdown parser  
- [ ] Add sentence-transformers embedding job and pgvector integration  
- [x] Build FastAPI endpoints for digest and feedback  
- [ ] Minimal React UI to view digest, mark likes/highlights, export to Obsidian  

---

[Full Architecture Details](./docs/architecture.md)


# Workflow
![](./docs/workflow_old.jpeg)
