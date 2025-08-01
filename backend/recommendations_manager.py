import numpy as np
import requests
from flask import Blueprint
from sqlalchemy.orm import Session
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as genai
import os
from dotenv import load_dotenv
from .extensions import db
from .models import BookGenreMap, BookRating, FriendRequest, FriendSuggestion, User, UserGenreVector
import json

recommendations_manager = Blueprint('recommendations_manager', __name__)

# The list of genres we are tracking for user profiles.
GENRES = [
    "romance", "science_fiction", "fantasy", "mystery", "historical",
    "biography", "non_fiction", "thriller", "young_adult", "self_help"
]

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
except Exception as e:
    print(f"Error configuring Gemini API: {e}")

def normalize_genre(raw_genre: str):

    if not os.getenv("GEMINI_API_KEY"):
        print("GEMINI_API_KEY not configured. Skipping AI genre normalization.")
        return None

    schema = {
        "type": "object",
        "properties": {
            "genre": {
                "type": "string",
                "enum": GENRES
            }
        },
        "required": ["genre"]
    }

    # Configure the model for JSON output
    model = genai.GenerativeModel(
        'gemini-1.5-flash-latest',
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": schema
        }
    )
    
    prompt = f"""
    Analyze the following book category and classify it into exactly one of the following predefined genres: {', '.join(GENRES)}.
    The category is: "{raw_genre}"
    """

    try:
        response = model.generate_content(prompt)
        result = json.loads(response.text)
        return result.get("genre")
    except Exception as e:
        print(f"Error normalizing genre '{raw_genre}' with Gemini: {e}")
        # Fallback to a simple string search if the API fails
        for g in GENRES:
            if g.replace("_", " ") in raw_genre.lower():
                return g
        return None


def update_book_genre_info(book_id, categories):
    """Stores a single normalized genre per book."""
    if not categories:
        return

    # Check if genre already assigned
    existing = BookGenreMap.query.filter_by(book_id=book_id).first()
    if existing:
        return

    for raw_genre in categories:
        normalized = normalize_genre(raw_genre)
        if normalized:
            genre_map = BookGenreMap(book_id=book_id, raw_genre=raw_genre, normalized_genre=normalized)
            db.session.add(genre_map)
            db.session.commit()
            return  


def update_user_genre_vector(user_id):
    """Recalculates a user's genre vector based on their highly-rated books."""
    user_ratings = BookRating.query.filter(BookRating.user_id == user_id, BookRating.rating >= 4).all()
    
    if not user_ratings:
        return

    # Get genres for all books the user has rated highly
    rated_book_ids = [r.book_id for r in user_ratings]
    book_genres = BookGenreMap.query.filter(BookGenreMap.book_id.in_(rated_book_ids)).all()

    # Calculate the new vector
    genre_counts = {genre: 0 for genre in GENRES}
    total_count = 0
    for bg in book_genres:
        if bg.normalized_genre in genre_counts:
            genre_counts[bg.normalized_genre] += 1
            total_count += 1
    
    if total_count == 0:
        return

    # Normalize the vector so that it sums to 1
    vector_values = {genre: count / total_count for genre, count in genre_counts.items()}

    # Update or create the user's vector in the database
    user_vector = UserGenreVector.query.filter_by(user_id=user_id).first()
    if not user_vector:
        user_vector = UserGenreVector(user_id=user_id)
        db.session.add(user_vector)
    
    for genre, value in vector_values.items():
        setattr(user_vector, genre, value)
        
    db.session.commit()


def update_friend_suggestions(user_id: int, top_n: int = 10):
    """This is your pre-calculation logic."""
    session = db.session
    user_vec_row = session.query(UserGenreVector).filter_by(user_id=user_id).first()
    if not user_vec_row:
        return []

    user = session.query(User).get(user_id)
    existing_friend_ids = {f.id for f in user.friends}
    sent_reqs = {r.receiver_id for r in user.sent_friend_requests}
    received_reqs = {r.sender_id for r in user.received_friend_requests}
    exclude_ids = existing_friend_ids | sent_reqs | received_reqs | {user_id}

    user_vector = np.array(user_vec_row.as_vector())
    if np.linalg.norm(user_vector) == 0:
        return []

    all_other_vectors = session.query(UserGenreVector).filter(UserGenreVector.user_id != user_id).all()
    
    similarities = []
    for other in all_other_vectors:
        if other.user_id in exclude_ids:
            continue
        
        other_vector = np.array(other.as_vector())
        if np.linalg.norm(other_vector) > 0:
            similarity = float(cosine_similarity([user_vector], [other_vector])[0][0])
            if similarity > 0.1: # Set a threshold to only suggest relevant users
                similarities.append((other.user_id, similarity))

    top_similar = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_n]

    # Bulk update suggestions
    session.query(FriendSuggestion).filter_by(user_id=user_id).delete()
    for other_id, score in top_similar:
        suggestion = FriendSuggestion(
            user_id=user_id,
            suggested_friend_id=other_id,
            similarity_score=score
        )
        session.add(suggestion)

    session.commit()
