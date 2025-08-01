from flask import Blueprint,render_template,request,jsonify,redirect,url_for,flash
from flask_login import login_required,current_user
from .models import User,Message,FriendRequest,BookRating
import requests
from bs4 import BeautifulSoup
from .extensions import db
from sqlalchemy import func
import datetime

books_manager=Blueprint('books_manager',__name__)


@books_manager.route('/books')
@login_required
def books():
    # --- LEADERBOARD LOGIC ---
    # Query to get the top 5 book_ids based on average rating and count
    top_books_query = db.session.query(
        BookRating.book_id,
        func.avg(BookRating.rating).label('average_rating'),
        func.count(BookRating.id).label('rating_count')
    ).group_by(BookRating.book_id).order_by(func.avg(BookRating.rating).desc()).limit(5).all()

    leaderboard_books = []
    for book_data in top_books_query:
        try:
            # Fetch book details from Google Books API
            url = f"https://www.googleapis.com/books/v1/volumes/{book_data.book_id}"
            res = requests.get(url)
            res.raise_for_status()  # Raise an exception for bad status codes
            data = res.json()
            
            info = data.get('volumeInfo', {})
            leaderboard_books.append({
                'id': book_data.book_id,
                'title': info.get('title', 'Title not available'),
                'thumbnail': info.get('imageLinks', {}).get('thumbnail'),
                'avg_rating': round(book_data.average_rating, 2),
                'rating_count': book_data.rating_count
            })
        except requests.exceptions.RequestException as e:
            print(f"Error fetching book data for {book_data.book_id}: {e}")
            continue # Skip this book if API call fails

    return render_template('books.html', user=current_user, leaderboard_books=leaderboard_books)

@books_manager.route('/book/<book_id>')
@login_required
def book(book_id):
    url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    res = requests.get(url)
    data = res.json()

    info = data.get('volumeInfo', {})
    Title= info.get("title")
    Authors=info.get("authors")
    Publisher=info.get("publisher")
    Category=info.get("categories")
    pageCount=info.get("pageCount")
    Description=info.get("description")
    if Description:
        Description=BeautifulSoup(Description, "html.parser").get_text()
    Thumbnail=info.get("imageLinks", {}).get("thumbnail")

    # --- RATING DATA ---
    # Get average rating and count
    avg_rating_query = db.session.query(func.avg(BookRating.rating)).filter_by(book_id=book_id).scalar()
    avg_rating = round(avg_rating_query, 2) if avg_rating_query else "Not yet rated"
    rating_count = BookRating.query.filter_by(book_id=book_id).count()

    # Get the current user's rating for this book, if it exists
    user_rating_obj = BookRating.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    user_rating = user_rating_obj.rating if user_rating_obj else 0

    return render_template("book_detail.html",user=current_user,
                           book_id=book_id,
                           Title=Title,
                           Authors=Authors,
                           Publisher=Publisher,
                           Category=Category,
                           pageCount=pageCount,
                           Description=Description,
                           Thumbnail=Thumbnail,
                           avg_rating=avg_rating,
                           rating_count=rating_count,
                           user_rating=user_rating)

@books_manager.route('/book/search/<query>')
@login_required
def book_search(query):
    """Searches for a book and redirects to its detail page."""
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    res = requests.get(url)
    data = res.json()

    if data.get('items'):
        # Get the ID of the first book found and redirect
        first_book_id = data['items'][0]['id']
        return redirect(url_for('books_manager.book', book_id=first_book_id))
    else:
        # Handle case where no books are found
        flash('No books found for that query.', 'error')
        return redirect(url_for('books_manager.books'))
    
@books_manager.route('/rate_book/<book_id>', methods=['POST'])
@login_required
def rate_book(book_id):
    """API endpoint for submitting or updating a book rating."""
    data = request.get_json()
    rating_value = data.get('rating')

    if not rating_value or not 1 <= rating_value <= 5:
        return jsonify({'status': 'error', 'message': 'Invalid rating value.'}), 400

    # Check if the user has already rated this book to decide whether to update or create.
    existing_rating = BookRating.query.filter_by(book_id=book_id, user_id=current_user.id).first()

    if existing_rating:
        # Update the existing rating
        existing_rating.rating = rating_value
        existing_rating.timestamp = datetime.datetime.utcnow()
    else:
        # Or, create a new rating
        new_rating = BookRating(
            book_id=book_id,
            user_id=current_user.id,
            rating=rating_value
        )
        db.session.add(new_rating)
    
    db.session.commit()

    # Calculate the new average rating for the book
    avg_rating_query = db.session.query(func.avg(BookRating.rating)).filter_by(book_id=book_id).scalar()
    avg_rating = round(avg_rating_query, 2) if avg_rating_query else 0

    return jsonify({'status': 'success', 'message': 'Rating submitted!', 'new_average': avg_rating}), 200
