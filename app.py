from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from functools import wraps
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv  # Import dotenv to manage environment variables
from datetime import datetime, timezone
import requests

from extensions import db, migrate, jwt

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app and load configuration
app = Flask(__name__)
app.config.from_object('config.Config')

# Ensure the upload folder exists when the app starts
def ensure_upload_folder():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

ensure_upload_folder()

# Initialize extensions with the Flask app
db.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)
CORS(app)

# Import models after initializing db to avoid circular imports
from models import User, Movie, Rating, UploadedFile


# ==========================
# USER AUTHENTICATION ROUTES
# ==========================

# User Registration Endpoint
@app.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    is_admin = data.get('is_admin', False)

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'User already exists'}), 409

    # Create new user and store in the database
    new_user = User(username=username, is_admin=is_admin)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201


# User Login Endpoint
@app.route('/login', methods=['POST'])
def login():
    """User login and token creation."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Authenticate the user
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        # Create JWT token
        access_token = create_access_token(identity={'id': user.id, 'is_admin': user.is_admin})
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin
            }
        }), 200
    else:
        return jsonify({'message': 'Invalid username or password'}), 401


# Decorator to restrict admin access
def admin_required(f):
    """Decorator to check if the user is an admin."""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        identity = get_jwt_identity()
        if not identity['is_admin']:
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function


# ====================
# MOVIE MANAGEMENT API
# ====================

# Admin Adds a New Movie Endpoint
@app.route('/movies', methods=['POST'])
@admin_required
def add_movie():
    """Admin adds a new movie to the database."""
    data = request.get_json()
    title = data.get('title')

    # Check if movie already exists
    if Movie.query.filter_by(title=title).first():
        return jsonify({'message': 'Movie already exists'}), 409

    # Add new movie
    new_movie = Movie(title=title)
    db.session.add(new_movie)
    db.session.commit()

    return jsonify({'message': 'Movie added successfully', 'movie_id': new_movie.id}), 201


# User Submits a Rating Endpoint
@app.route('/movies/<int:movie_id>/rate', methods=['POST'])
@jwt_required()
def rate_movie(movie_id):
    """User submits a rating for a movie."""
    data = request.get_json()
    rating_value = data.get('rating')

    # Validate rating value
    if not isinstance(rating_value, int) or not (1 <= rating_value <= 5):
        return jsonify({'message': 'Rating must be an integer between 1 and 5'}), 400

    # Fetch movie by ID
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({'message': 'Movie not found'}), 404

    # Check if user already rated the movie
    identity = get_jwt_identity()
    user_id = identity['id']
    existing_rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if existing_rating:
        return jsonify({'message': 'You have already rated this movie'}), 409

    # Add the new rating
    new_rating = Rating(rating=rating_value, user_id=user_id, movie_id=movie_id)
    db.session.add(new_rating)
    db.session.commit()

    return jsonify({'message': 'Rating submitted successfully'}), 201


# Retrieve All User Ratings for All Movies Endpoint
@app.route('/ratings', methods=['GET'])
@jwt_required()
def get_all_ratings():
    """Retrieve all user ratings for all movies."""
    ratings = Rating.query.all()
    output = []
    for rating in ratings:
        rating_data = {
            'id': rating.id,
            'rating': rating.rating,
            'user_id': rating.user_id,
            'movie_id': rating.movie_id,
            'timestamp': rating.timestamp.isoformat()
        }
        output.append(rating_data)
    return jsonify({'ratings': output}), 200


# Fetch Details for a Specific Movie Endpoint
@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    """Fetch details for a specific movie by ID, including its ratings."""
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({'message': 'Movie not found'}), 404

    # Fetch all ratings related to the movie
    ratings = Rating.query.filter_by(movie_id=movie_id).all()
    ratings_list = [{'user_id': r.user_id, 'rating': r.rating} for r in ratings]

    # Create movie_data dictionary with all necessary fields
    movie_data = {
        'id': movie.id,
        'title': movie.title,
        'overview': movie.overview,
        'release_date': movie.release_date,
        'poster_path': movie.poster_path,
        'vote_average': movie.vote_average,
        'ratings': ratings_list
    }

    return jsonify({'movie': movie_data}), 200


# Update User's Own Movie Rating Endpoint
@app.route('/movies/<int:movie_id>/rate', methods=['PUT'])
@jwt_required()
def update_rating(movie_id):
    """User updates their own movie rating."""
    data = request.get_json()
    new_rating_value = data.get('rating')

    # Validate rating value
    if not isinstance(new_rating_value, int) or not (1 <= new_rating_value <= 5):
        return jsonify({'message': 'Rating must be an integer between 1 and 5'}), 400

    # Fetch user's rating
    identity = get_jwt_identity()
    user_id = identity['id']
    rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if not rating:
        return jsonify({'message': 'Rating not found'}), 404

    # Update rating
    rating.rating = new_rating_value
    db.session.commit()

    return jsonify({'message': 'Rating updated successfully'}), 200


# Admin Deletes Any Movie's User Rating Endpoint
@app.route('/ratings/<int:rating_id>', methods=['DELETE'])
@admin_required
def delete_rating_admin(rating_id):
    """Admin deletes any user's rating for a movie."""
    rating = Rating.query.get(rating_id)
    if not rating:
        return jsonify({'message': 'Rating not found'}), 404

    db.session.delete(rating)
    db.session.commit()

    return jsonify({'message': 'Rating deleted successfully'}), 200


# User Deletes Their Own Rating Endpoint
@app.route('/movies/<int:movie_id>/rate', methods=['DELETE'])
@jwt_required()
def delete_rating_user(movie_id):
    """User deletes their own rating for a movie."""
    identity = get_jwt_identity()
    user_id = identity['id']
    rating = Rating.query.filter_by(user_id=user_id, movie_id=movie_id).first()
    if not rating:
        return jsonify({'message': 'Rating not found'}), 404

    db.session.delete(rating)
    db.session.commit()

    return jsonify({'message': 'Rating deleted successfully'}), 200


# =======================
# FILE MANAGEMENT ROUTES
# =======================

# Helper Function to Check Allowed Extensions
def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# File Upload Endpoint
@app.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload a file."""
    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'message': 'No file selected for uploading'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        identity = get_jwt_identity()
        user_id = identity['id']

        # Add the file to the database
        uploaded_file = UploadedFile(
            filename=filename,
            filepath=filepath,
            user_id=user_id
        )
        db.session.add(uploaded_file)
        db.session.commit()

        return jsonify({'message': f'File {filename} uploaded successfully'}), 201
    else:
        allowed = ", ".join(app.config['ALLOWED_EXTENSIONS'])
        return jsonify({'message': f'Allowed file types are: {allowed}'}), 400


# List All Uploaded Files (Admin Only) Endpoint
@app.route('/files', methods=['GET'])
@admin_required
def get_all_uploaded_files():
    """Admin retrieves a list of all uploaded files."""
    files = UploadedFile.query.all()
    output = []
    for file in files:
        file_data = {
            'id': file.id,
            'filename': file.filename,
            'upload_date': file.upload_date,
            'user_id': file.user_id
        }
        output.append(file_data)
    return jsonify({'files': output}), 200


# List User's Uploaded Files Endpoint
@app.route('/users/me/files', methods=['GET'])
@jwt_required()
def get_user_uploaded_files():
    """User retrieves a list of their own uploaded files."""
    identity = get_jwt_identity()
    user_id = identity['id']
    files = UploadedFile.query.filter_by(user_id=user_id).all()
    output = []
    for file in files:
        file_data = {
            'id': file.id,
            'filename': file.filename,
            'upload_date': file.upload_date
        }
        output.append(file_data)
    return jsonify({'files': output}), 200


# Download a Specific File Endpoint
@app.route('/files/<int:file_id>', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """User or admin downloads a specific file."""
    file = UploadedFile.query.get(file_id)
    if not file:
        return jsonify({'message': 'File not found'}), 404

    identity = get_jwt_identity()
    user_id = identity['id']
    is_admin = identity['is_admin']

    # Allow admins or the user who uploaded the file to download
    if file.user_id != user_id and not is_admin:
        return jsonify({'message': 'Access denied'}), 403

    return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename, as_attachment=True)


# Delete a File Endpoint
@app.route('/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """User or admin deletes a file."""
    file = UploadedFile.query.get(file_id)
    if not file:
        return jsonify({'message': 'File not found'}), 404

    identity = get_jwt_identity()
    user_id = identity['id']
    is_admin = identity['is_admin']

    # Allow admins or the user who uploaded the file to delete
    if file.user_id != user_id and not is_admin:
        return jsonify({'message': 'Access denied'}), 403

    # Delete the file from the filesystem
    try:
        os.remove(file.filepath)
    except Exception as e:
        pass  # Handle the exception as needed

    # Delete the file record from the database
    db.session.delete(file)
    db.session.commit()

    return jsonify({'message': 'File deleted successfully'}), 200


# ==========================
# FETCHING MOVIES AND STATIC
# ==========================

# Fetch All Movies Endpoint
@app.route('/movies', methods=['GET'])
def get_movies():
    """Fetch all movies with pagination."""
    page = request.args.get('page', 1, type=int)  # Default to page 1 if not provided
    per_page = 20  # Number of movies per page
    movies = Movie.query.paginate(page=page, per_page=per_page, error_out=False)
    
    output = [{
        'id': movie.id,
        'title': movie.title,
        'overview': movie.overview,
        'release_date': movie.release_date,
        'poster_path': movie.poster_path,
        'vote_average': movie.vote_average
    } for movie in movies.items]

    return jsonify({
        'movies': output,
        'total_pages': movies.pages,
        'current_page': movies.page
    }), 200


# Serve Static Files
@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
