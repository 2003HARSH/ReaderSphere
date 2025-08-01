from flask import Blueprint,render_template,request,jsonify,redirect,url_for,flash
from flask_login import login_required,current_user
from .models import User,Message,FriendRequest,BookRating
import requests
from bs4 import BeautifulSoup
from .extensions import db
from sqlalchemy import func
import datetime
from .recommendations_manager import update_book_genre_info, update_user_genre_vector, update_friend_suggestions

books_manager=Blueprint('books_manager',__name__)


@books_manager.route('/books')
@login_required
def books():
    MIN_RATINGS_THRESHOLD = 2 
    global_avg_rating_decimal = db.session.query(func.avg(BookRating.rating)).scalar()
    if global_avg_rating_decimal is None:
        return render_template('books.html', user=current_user, leaderboard_books=[])
    global_avg_rating = float(global_avg_rating_decimal)
    books_stats_query = db.session.query(
        BookRating.book_id,
        func.avg(BookRating.rating).label('average_rating'),
        func.count(BookRating.id).label('rating_count')
    ).group_by(BookRating.book_id).having(func.count(BookRating.id) >= MIN_RATINGS_THRESHOLD).all()
    ranked_books = []
    for book_stat in books_stats_query:
        v = book_stat.rating_count
        R = float(book_stat.average_rating)
        weighted_rating = (v / (v + MIN_RATINGS_THRESHOLD)) * R + (MIN_RATINGS_THRESHOLD / (v + MIN_RATINGS_THRESHOLD)) * global_avg_rating
        ranked_books.append({
            'book_id': book_stat.book_id,
            'average_rating': R,
            'rating_count': v,
            'weighted_score': weighted_rating
        })
    top_books = sorted(ranked_books, key=lambda x: x['weighted_score'], reverse=True)[:5]
    leaderboard_books = []
    for book_data in top_books:
        try:
            url = f"https://www.googleapis.com/books/v1/volumes/{book_data['book_id']}"
            res = requests.get(url)
            res.raise_for_status()
            data = res.json()
            info = data.get('volumeInfo', {})
            leaderboard_books.append({
                'id': book_data['book_id'],
                'title': info.get('title', 'Title not available'),
                'thumbnail': info.get('imageLinks', {}).get('thumbnail'),
                'avg_rating': round(book_data['average_rating'], 2),
                'rating_count': book_data['rating_count']
            })
        except requests.exceptions.RequestException as e:
            print(f"Error fetching book data for {book_data['book_id']}: {e}")
            continue
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
    avg_rating_query = db.session.query(func.avg(BookRating.rating)).filter_by(book_id=book_id).scalar()
    avg_rating = round(avg_rating_query, 2) if avg_rating_query else "Not yet rated"
    rating_count = BookRating.query.filter_by(book_id=book_id).count()
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
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    res = requests.get(url)
    data = res.json()
    if data.get('items'):
        first_book_id = data['items'][0]['id']
        return redirect(url_for('books_manager.book', book_id=first_book_id))
    else:
        flash('No books found for that query.', 'error')
        return redirect(url_for('books_manager.books'))
    
@books_manager.route('/rate_book/<book_id>', methods=['POST'])
@login_required
def rate_book(book_id):
    data = request.get_json()
    rating_value = data.get('rating')

    if not rating_value or not 1 <= rating_value <= 5:
        return jsonify({'status': 'error', 'message': 'Invalid rating value.'}), 400

    existing_rating = BookRating.query.filter_by(book_id=book_id, user_id=current_user.id).first()
    if existing_rating:
        existing_rating.rating = rating_value
        existing_rating.timestamp = datetime.datetime.utcnow()
    else:
        new_rating = BookRating(book_id=book_id, user_id=current_user.id, rating=rating_value)
        db.session.add(new_rating)
    
    db.session.commit()

    #TRIGGER RECOMMENDATION UPDATE 
    try:
        url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
        res = requests.get(url)
        data = res.json()
        categories = data.get('volumeInfo', {}).get('categories')
        if categories:
            update_book_genre_info(book_id, categories)
        
        # Update the user's genre vector based on their new rating
        update_user_genre_vector(current_user.id)
        
        # Recalculate and store new friend suggestions for the user
        update_friend_suggestions(current_user.id)

    except Exception as e:
        # Log the error but don't crash the request. The rating was still saved.
        print(f"Error during recommendation update for user {current_user.id}: {e}")

    avg_rating_query = db.session.query(func.avg(BookRating.rating)).filter_by(book_id=book_id).scalar()
    avg_rating = round(avg_rating_query, 2) if avg_rating_query else 0
    return jsonify({'status': 'success', 'message': 'Rating submitted!', 'new_average': avg_rating}), 200
