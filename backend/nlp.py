from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ─────────────────────────────────────────────
# Model — lazy loaded to save RAM on startup
# ─────────────────────────────────────────────

_model = None
_seed_embeddings = None

# ─────────────────────────────────────────────
# Topic seeds for auto-tagging
# ─────────────────────────────────────────────

TOPIC_SEEDS: dict[str, str] = {
    "Biology": "photosynthesis cell respiration DNA genetics evolution",
    "Physics": "force velocity acceleration gravity Newton momentum",
    "Chemistry": "reaction molecules atoms periodic table bonds",
    "Math": "equation algebra calculus geometry probability statistics",
    "History": "war revolution empire civilization ancient modern",
    "Geography": "continent climate country river mountain population",
    "Computer Science": "algorithm data structure programming code software",
    "Economics": "market supply demand inflation GDP trade",
}

_seed_labels: list[str] = list(TOPIC_SEEDS.keys())

def get_model():
    """
    Lazy load the model and seed embeddings the first time they are needed.
    This prevents the app from running out of memory during startup on Render.
    """
    global _model, _seed_embeddings
    if _model is None:
        print("[NLP] Loading MiniLM model into memory for the first time...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("[NLP] Pre-computing topic seed embeddings...")
        _seed_embeddings = _model.encode(list(TOPIC_SEEDS.values()))
    return _model

# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def get_embedding(text: str) -> list[float]:
    """
    Encode a text string into a 384-dimensional embedding vector
    using the all-MiniLM-L6-v2 sentence-transformer model.
    """
    model = get_model()
    vector = model.encode(text)
    return vector.tolist()


def find_similar(new_embedding: list[float], all_questions: list[dict]) -> list[dict]:
    """
    Compare *new_embedding* against every question's stored embedding
    using cosine similarity.

    Returns the top 3 questions whose similarity exceeds 0.3, sorted
    descending by score.

    Each result dict:
        { id, text, tag, similarity_score }
    """
    if not all_questions:
        return []

    # Build matrix of stored embeddings
    stored_embeddings = np.array([q["embedding"] for q in all_questions])
    new_vec = np.array(new_embedding).reshape(1, -1)

    # Cosine similarities → shape (1, N) → flatten
    similarities = cosine_similarity(new_vec, stored_embeddings)[0]

    # Pair each question with its score, filter > 0.3, sort desc, take top 3
    scored = []
    for idx, score in enumerate(similarities):
        if score > 0.3:
            q = all_questions[idx]
            scored.append({
                "id": str(q["_id"]),
                "text": q["text"],
                "tag": q.get("tag"),
                "similarity_score": round(float(score), 2),
            })

    scored.sort(key=lambda x: x["similarity_score"], reverse=True)
    return scored[:3]


def auto_tag(text: str) -> str:
    """
    Automatically assign the most relevant topic tag to a question.

    Embeds the input text and compares it against 8 pre-computed
    topic seed embeddings via cosine similarity. Returns the topic
    label with the highest score.
    """
    model = get_model()
    text_vec = model.encode(text).reshape(1, -1)
    
    # _seed_embeddings is guaranteed to be loaded since get_model() was called
    similarities = cosine_similarity(text_vec, _seed_embeddings)[0]
    best_idx = int(np.argmax(similarities))
    return _seed_labels[best_idx]
