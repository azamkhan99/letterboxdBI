# Letterboxd - BI

This Streamlit app creates a dashboard of a user's Letterboxd entry data for the current year.
Users can also download a summary of their Letterboxd data to share on social media.

## Setup

1. Clone the repository:

   ```
   git clone https://github.com/azamkhan99/letterboxdBI.git
   cd letterboxdBI
   ```

2. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project root and add your TMDB API key:

   ```
   TMDB_API_KEY=your_tmdb_api_key_here
   ```

4. Run the Streamlit app:

   ```
   streamlit run app.py
   ```

5. Open your web browser and go to `http://localhost:8501` to view the dashboard.

## Customization

To use this dashboard for your own Letterboxd data, update the RSS feed URL in `main.py`:

```python
movie_df = get_movie_data_from_rss_feed(f'https://letterboxd.com/{username}/rss/', current_year)
```

Replace `username` with your Letterboxd username.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Data Sources

This project uses data from the following sources:

- [Letterboxd](https://letterboxd.com/): User movie ratings and reviews
- [The Movie Database (TMDB)](https://www.themoviedb.org/): Additional movie information and images

Please note that this project is for personal use only and is not affiliated with, endorsed, or sponsored by Letterboxd or TMDB. All movie-related data and images are the property of their respective owners.
