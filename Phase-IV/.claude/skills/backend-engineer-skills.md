# 🛠️ Backend Engineer Skills & Capabilities

Is file mein `backend-engineer` agent ki core skills aur unhe execute karne ke tareeqe define hain.

### Skill: `configure_neon_db`
- **Description:** Neon Serverless PostgreSQL ka connection establish karna.
- **Action:** `DATABASE_URL` environment variable ko `db.py` mein integrate karna.
- **Tools:** `psycopg2-binary`, `python-dotenv`.

### Skill: `deploy_schema`
- **Description:** SQLModel schemas ko database tables mein convert karna.
- **Action:** `SQLModel.metadata.create_all(engine)` ka istemal karke tables create karna.
- **Files:** `models.py`.

### Skill: `implement_crud_logic`
- **Description:** Tasks ke liye GET, POST, PUT, DELETE, aur PATCH endpoints likhna.
- **Action:** `@specs/api/rest-endpoints.md` ke mutabiq logic likhna aur authenticated `user_id` ka filter lagana.