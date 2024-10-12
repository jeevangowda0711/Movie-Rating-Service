async function fetchMovies() {
  try {
      const response = await fetch('/movies');
      const data = await response.json();
      const movieList = document.getElementById('movie-list');
      movieList.innerHTML = '';

      data.movies.forEach(movie => {
          const movieItem = document.createElement('li');

          // Build the image URL
          const img = document.createElement('img');
          const posterPath = movie.poster_path 
              ? `https://image.tmdb.org/t/p/w185${movie.poster_path}`
              : 'https://fakeimg.pl/300x450?text=No+poster'; // Placeholder image if poster_path is missing
          img.src = posterPath;
          img.alt = movie.title;
          img.style.width = '150px';  // Adjust image size as needed

          // Add movie details
          const title = document.createElement('h3');
          title.textContent = movie.title;

          const overview = document.createElement('p');
          overview.textContent = movie.overview;

          // Append everything to the list item
          movieItem.appendChild(img);
          movieItem.appendChild(title);
          movieItem.appendChild(overview);

          // Append the movie item to the movie list
          movieList.appendChild(movieItem);
      });
  } catch (error) {
      console.error('Error fetching movies:', error);
  }
}

document.addEventListener('DOMContentLoaded', fetchMovies);
