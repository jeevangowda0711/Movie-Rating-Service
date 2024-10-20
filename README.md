# Movie Rating Service

# cpsc449proj.1

Kevin Byon     CWID: 887345262      

email: kbyon@csu.fullerton.edu 


Johnny Quach   CWID: 888862059

email: JqJohnny@csu.fullerton.edu


Jeevan Gowda   CWID: 885168989

email: jeevangowda@csu.fullerton.edu


Samantha Rehome   CWID: 887904126  

email: 4srehome@csu.fullerton.edu

## Overview

The **Movie Rating Service** is a full-stack web application that allows users to register, log in, rate movies, and upload files. Admin users have additional privileges to manage movies and delete any user's ratings. The application is built with a Flask backend, and the movie data is fetched from the **TMDB (The Movie Database)** API. The project implements user authentication, role-based access control, and file handling for movie-related uploads.

## Features

- **User Authentication:**
  - Register, log in, and secure routes using JWT-based authentication.
  - Role-based access control (regular users and admin users).

- **Movie Management:**
  - Fetch popular movie data from the TMDB API.
  - Admins can add new movies and delete user ratings.
  - Regular users can rate movies on a scale of 1-5.
  - Movies include details such as title, overview, release date, poster path, and vote average.

- **Rating System:**
  - Users can submit, update, and delete their own ratings.
  - Admins can delete any user's rating.

- **File Uploads:**
  - Users can upload files (such as images) related to movies.
  - Admin users can view all uploaded files.
  
- **Pagination:**
  - Movies are paginated with a default of 20 movies per page.

## Technology Stack

### Backend
- **Flask**: The web framework used to build the backend API.
- **SQLAlchemy**: ORM for interacting with the PostgreSQL database.
- **Flask-JWT-Extended**: For implementing secure JWT-based authentication.
- **Flask-Migrate**: Handles database migrations.
- **Flask-CORS**: Enables Cross-Origin Resource Sharing (CORS) to allow communication between frontend and backend.
- **psycopg2**: PostgreSQL adapter for Python.

### Frontend
- **HTML, CSS, JavaScript**: Basic static files (for rendering templates and static assets).

### Database
- **PostgreSQL**: Used to store user information, movie data, ratings, and uploaded file metadata.

## Setup Instructions

### Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.7+**
- **PostgreSQL**
- **Git**

### Steps to Setup the Project

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/jeevangowda0711/Movie-Rating-Service.git
   cd Movie-Rating-Service
   ```

2. **Create and Activate a Virtual Environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the Required Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**

   Create a `.env` file in the root of the project with the following variables:

   ```bash
   SECRET_KEY=<your_secret_key>
   JWT_SECRET_KEY=<your_jwt_secret_key>
   DATABASE_URI=<your_postgresql_uri>
   TMDB_API_KEY=<your_tmdb_api_key>
   ```

   Example for `DATABASE_URI`:

   ```
   DATABASE_URI=postgresql://username:password@localhost:5432/moviedb
   ```

5. **Initialize the Database:**

   Run the following commands to create the database tables and perform migrations:

   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. **Run the Application:**

   Start the Flask server:

   ```bash
   flask run
   ```

   The app will run at `http://127.0.0.1:5000/`.

7. **Access the TMDB Fetch Utility:**

   To fetch and insert movies into the database from the TMDB API, run the following command:

   ```bash
   python tmdb_fetch.py
   ```

## API Endpoints

### Authentication

- **Register**: `POST /register`
- **Login**: `POST /login`

### Movies

- **Add a Movie (Admin Only)**: `POST /movies`
- **Fetch All Movies**: `GET /movies?page=<page_number>`
- **Fetch Specific Movie**: `GET /movies/<movie_id>`
  
### Ratings

- **Rate a Movie**: `POST /movies/<movie_id>/rate`
- **Update Rating**: `PUT /movies/<movie_id>/rate`
- **Delete Rating (User)**: `DELETE /movies/<movie_id>/rate`
- **Delete Rating (Admin)**: `DELETE /ratings/<rating_id>`

### File Uploads

- **Upload a File**: `POST /upload`
- **List All Files (Admin Only)**: `GET /files`
- **List User's Files**: `GET /users/me/files`
- **Download a File**: `GET /files/<file_id>`
- **Delete a File**: `DELETE /files/<file_id>`

## Directory Structure

```
Movie-Rating-Service/
│
├── migrations/            # Database migration files
├── static/                # Static files (CSS, JavaScript)
│   ├── css/
│   └── js/
├── templates/             # HTML templates
├── uploads/               # Uploaded files
├── app.py                 # Flask application
├── config.py              # Configuration settings
├── extensions.py          # Flask extensions
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── tmdb_fetch.py          # Script to fetch movies from TMDB
└── README.md              # Project documentation
```

## Future Enhancements

- Implement user profile pages displaying ratings and uploaded files.
- Add search functionality for movies.
- Improve UI/UX by integrating a modern JavaScript frontend framework like **Svelte** or **React**.
- Add real-time notifications for rating updates.

## License

This project is licensed under the MIT License.

## Acknowledgments

- **TMDB API** for providing movie data.
- **Flask** community for their comprehensive documentation.
