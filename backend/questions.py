from datetime import datetime, timezone
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Query, status

from auth import get_current_user
from database import questions_collection
from nlp import get_embedding, find_similar, auto_tag

router = APIRouter()


# ─────────────────────────────────────────────
# POST /questions — create a question
# ─────────────────────────────────────────────

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new question and find similar ones",
)
async def create_question(
    body: dict,
    current_user: dict = Depends(get_current_user),
):
    """
    End-to-end question processing pipeline:

    1. Generate a 384-dim embedding of the question text.
    2. Fetch all existing questions from MongoDB.
    3. Find the top 3 semantically similar questions (cosine > 0.3).
    4. Auto-tag the question against 8 topic categories.
    5. Persist the question document with embedding, tag, and similar IDs.
    6. Return the saved question with its similar matches.
    """
    text = body.get("text", "").strip()
    if not text or len(text) < 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Question text is required and must be at least 5 characters.",
        )

    user_id = current_user["sub"]

    # Step 1 — Embedding
    embedding = get_embedding(text)

    # Step 2 — Fetch all existing questions (only those with embeddings)
    cursor = questions_collection.find({"embedding": {"$exists": True, "$ne": []}})
    all_questions = await cursor.to_list(length=None)

    # Step 3 — Find similar
    similar = find_similar(embedding, all_questions)
    similar_ids = [s["id"] for s in similar]

    # Step 4 — Auto-tag
    tag = auto_tag(text)

    # Step 5 — Save to MongoDB
    now = datetime.now(timezone.utc)
    question_doc = {
        "user_id": user_id,
        "text": text,
        "embedding": embedding,
        "tag": tag,
        "similar_question_ids": similar_ids,
        "created_at": now,
    }

    result = await questions_collection.insert_one(question_doc)
    question_id = str(result.inserted_id)

    # Step 6 — Response
    return {
        "id": question_id,
        "text": text,
        "tag": tag,
        "similar_questions": [
            {
                "text": s["text"],
                "tag": s["tag"],
                "similarity_score": s["similarity_score"],
            }
            for s in similar
        ],
    }


# ─────────────────────────────────────────────
# GET /questions — list current user's questions
# ─────────────────────────────────────────────

@router.get(
    "",
    summary="List your questions (newest first, optional tag filter)",
)
async def list_questions(
    tag: Optional[str] = Query(None, description="Filter by topic tag, e.g. Biology"),
    current_user: dict = Depends(get_current_user),
):
    """
    Return all questions belonging to the authenticated user,
    sorted newest-first. Optionally filter by tag.
    """
    user_id = current_user["sub"]

    query = {"user_id": user_id}
    if tag:
        query["tag"] = tag

    cursor = questions_collection.find(query).sort("created_at", -1)
    docs = await cursor.to_list(length=None)

    questions = []
    for doc in docs:
        questions.append({
            "id": str(doc["_id"]),
            "user_id": doc["user_id"],
            "text": doc["text"],
            "tag": doc.get("tag"),
            "similar_question_ids": doc.get("similar_question_ids", []),
            "created_at": doc["created_at"].isoformat(),
        })

    return questions
