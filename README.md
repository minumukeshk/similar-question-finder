# SimilarQ — Similar Question Finder

> An EdTech tool that finds semantically similar study questions using sentence embeddings, auto-tags questions by subject, and serves a clean React interface backed by a FastAPI + MongoDB API.

---

## Option Chosen: Option B — Similar Question Finder with Auto-Tagging

Rather than keyword search, this project uses **dense vector embeddings** to match questions by *meaning*, not by shared words. A question about "photosynthesis and light" will correctly surface results about "sunlight and plant energy" even when no keywords overlap. An auto-tagger classifies every question into one of eight academic subjects without any manual labelling.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI (Python 3.11) + Uvicorn |
| **Database** | MongoDB Atlas (Motor async driver) |
| **NLP / Embeddings** | `sentence-transformers` — `all-MiniLM-L6-v2` |
| **Similarity** | `scikit-learn` cosine similarity |
| **Auth** | JWT (python-jose) + bcrypt password hashing |
| **Frontend** | React 18 + Vite + Tailwind CSS v3 |
| **HTTP Client** | Axios with Bearer token interceptor |
| **Routing** | React Router v6 |
| **Backend Deploy** | Render (render.yaml / Dockerfile included) |
| **Frontend Deploy** | Vercel / Netlify (static Vite build) |

---

## Local Setup — Backend

### Prerequisites
- Python 3.11+
- MongoDB running locally (`mongodb://localhost:27017`) **or** a MongoDB Atlas connection string

```bash
# 1. Move into the backend folder
cd backend

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
copy .env.example .env      # Windows
# cp .env.example .env      # macOS / Linux
# → Edit .env and fill in MONGO_URI and JWT_SECRET

# 5. Start the development server
uvicorn main:app --reload
```

The API will be available at **http://localhost:8000**.  
Interactive docs (Swagger UI) are at **http://localhost:8000/docs**.

---

## Local Setup — Frontend

### Prerequisites
- Node.js 18+

```bash
# 1. Move into the frontend folder
cd frontend

# 2. Install dependencies
npm install

# 3. Configure environment variables
copy .env.example .env      # Windows
# cp .env.example .env      # macOS / Linux
# → VITE_API_URL=http://localhost:8000 (default, no change needed for local)

# 4. Start the development server
npm run dev
```

The app will be available at **http://localhost:5173**.

---

## How the AI/ML Works

### 1. Turning Questions into Vectors

When a user submits a question, the backend passes the text to `all-MiniLM-L6-v2`, a compact but powerful **sentence transformer** model. The model returns a **384-dimensional vector** — a list of 384 floating-point numbers that encodes the *semantic meaning* of the sentence. These vectors are stored in MongoDB alongside the question text.

### 2. Measuring Similarity with Cosine Distance

To find similar questions, the backend computes the **cosine similarity** between the new question's vector and every existing vector in the database.

Cosine similarity measures the **angle** between two vectors in 384-dimensional space. A score of **1.0** means identical meaning; **0.0** means completely unrelated. Only questions scoring above **0.30** are returned, and the top 3 are surfaced to the user.

**Why this beats keyword search:**

> *"Why does photosynthesis need light?"*  
> *"What is the role of sunlight in photosynthesis?"*

These two sentences share no exact keywords, yet their embedding vectors are very close together because the model has learned that *light*, *sunlight*, *photosynthesis*, and *role/need* cluster in the same region of meaning-space. A traditional keyword or TF-IDF search would return zero overlap; the embedding approach correctly identifies them as near-duplicates.

### 3. Auto-Tagging by Subject

When a question is saved, `auto_tag()` classifies it into one of eight subjects:

| Subject | Seed sentence used for classification |
|---|---|
| Biology | *"photosynthesis cell respiration DNA genetics evolution"* |
| Physics | *"force velocity acceleration gravity Newton momentum"* |
| Chemistry | *"reaction molecules atoms periodic table bonds"* |
| Math | *"equation algebra calculus geometry probability statistics"* |
| History | *"war revolution empire civilization ancient modern"* |
| Geography | *"continent climate country river mountain population"* |
| Computer Science | *"algorithm data structure programming code software"* |
| Economics | *"market supply demand inflation GDP trade"* |

The question's embedding is compared against each seed sentence's embedding using cosine similarity. Whichever seed scores highest wins the tag — **no labelled training data required**.

### 4. Why Embeddings Matter for EdTech

Students paraphrase constantly. A student searching for help with *"why do plants need the sun"* should find existing questions about *"the role of light in photosynthesis"* — even if no words are shared. Embeddings make this possible. Keyword systems would silently return nothing, leaving the student to re-ask a question that's already been answered.

---

## Deployment

### Backend → Render

1. Push the `backend/` folder to a GitHub repository.
2. Create a new **Web Service** on [render.com](https://render.com) and connect the repo.
3. Render auto-detects `render.yaml` and configures the service.
4. Set the following environment variables in the Render dashboard:
   - `MONGO_URI` — your MongoDB Atlas connection string
   - `JWT_SECRET` — a long random secret (`python -c "import secrets; print(secrets.token_hex(32))"`)
   - `FRONTEND_URL` — the deployed frontend URL (for CORS)

### Frontend → Vercel

```bash
# From the frontend/ directory
npm run build
# Deploy the dist/ folder to Vercel, Netlify, or any static host.
# Set VITE_API_URL to your Render backend URL in the host's env settings.
```

---

## Project Structure

```
.
├── README.md
├── backend/
│   ├── main.py            # FastAPI app, CORS, router registration
│   ├── database.py        # Motor async MongoDB client
│   ├── models.py          # Pydantic v2 models
│   ├── auth.py            # /auth/register, /auth/login, JWT utilities
│   ├── nlp.py             # get_embedding, find_similar, auto_tag
│   ├── questions.py       # /questions CRUD routes
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── render.yaml
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api.js          # Axios instance + JWT interceptor
    │   ├── App.jsx         # Router + route guards
    │   ├── components/
    │   │   └── Navbar.jsx
    │   └── pages/
    │       ├── Login.jsx
    │       ├── Register.jsx
    │       ├── Home.jsx
    │       └── History.jsx
    ├── vite.config.js
    ├── tailwind.config.js
    └── .env.example
```
