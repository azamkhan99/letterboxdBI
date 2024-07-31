import streamlit as st
from app.movie_data import get_movie_data_from_rss_feed
from datetime import datetime
from streamlit_extras.stylable_container import stylable_container
from app.visualisations import (
    num_entries_kpi, num_hours_watched, bar_chart, get_top3_movies,
    num_reviews_kpi, most_recent_log, first_log, num_new_movies_watched_kpi,
    get_treemap_of_genres_movies_watched, english_foreign_language_pie_chart,
)
from st_social_media_links import SocialMediaIcons
from app.poster_generator import create_poster


@st.cache_data
def load_data(year, username):
    return get_movie_data_from_rss_feed(f'https://letterboxd.com/{username}/rss/', year)

def render_disclaimer():
    st.markdown("""
    ---
    **Disclaimer:** This dashboard uses data from Letterboxd and The Movie Database (TMDB). 
    All movie-related data and images are the property of their respective owners. 
    This project is for personal use only and is not affiliated with, endorsed, or sponsored by Letterboxd or TMDB.
    """)

def generate_story(username, movie_df, current_year, top3):
    with st.spinner("Generating Story..."):
        poster_bytes = create_poster(username, movie_df, current_year, top3)
        st.download_button(
            label="Download Story",
            data=poster_bytes,
            file_name=f"{username}s_{current_year}_in_film.png",
            mime="image/png",
            use_container_width=True
        )
        

def set_page_style():
    st.set_page_config(page_title="my year in film", page_icon="🎬", layout="wide")
    st.markdown("""
    <style>
        .block-container {
            padding-top: 3rem;
            padding-bottom: 0rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
    </style>
    """, unsafe_allow_html=True)

def create_username_form(empty):
    username_form = empty.form(key="my_form", border=False, clear_on_submit=True)
    with username_form:
        st.html("<h1 style='text-align: center; color: #e0edfd;'>Letterboxd-BI</h1>")
        
        st.html("<p style='text-align: center; color: #ef8833;'>Enter your Letterboxd username below to generate your Year in Film story :)</p>")
        username = st.text_input(label="username", placeholder="Enter your Letterboxd username", label_visibility="collapsed", )
        submit_button1 = st.form_submit_button(label="Generate Story", use_container_width=True)
        submit_button2 = st.form_submit_button(label="View Dashboard (ONLY ON DESKTOP PLEASE 🥹)", use_container_width=True, on_click=lambda: setattr(st.session_state, 'clicked', True))
    return username, submit_button1, submit_button2



def display_top3_movies(top3):
    with stylable_container(
        key="container_with_border",
        css_styles="""
            {
            border: 7px solid #1f212b;
            border-radius: 1.0rem;
            padding: calc(1em - 1px);
            background-color: #1f212b;
            color: white;
            box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.8);
            }
            """,
    ):
        st.markdown("<h6 style='text-align: left; color: white;'>TOP 3 MOVIES</h6>", unsafe_allow_html=True)
        cols = st.columns(3)
        for col, movie in zip(cols, top3):
            with col:
                st.image(movie["image"], caption=movie["caption"], use_column_width=True)

def display_social_media_links():
    social_media_links = [
        "https://www.github.com/azamkhan99",
        "https://www.linkedin.com/in/khanazam1/"
    ]
    colours = ["#66dd68", "#66dd68"]
    social_media_icons = SocialMediaIcons(social_media_links, colours)
    social_media_icons.render()


def display_dashboard(username, movie_df, current_year, top3):
    col1, col2, col3 = st.columns([1, 7, 1])
    with col1:
        first_movie = first_log(movie_df)
        st.image(first_movie[0]['image'], first_movie[0]['caption'], width=110)
    with col2:
        st.html(f"<h1 style='text-align: center; color: #e0edfd;'>{current_year}<br>{username}'s Year in Film</h1>")
        if st.button("Generate Story", use_container_width=True, key="generate_story_button_through_dashboard"):
            generate_story(username, movie_df, current_year, top3)
    with col3:
        recent_movie = most_recent_log(movie_df)
        print(recent_movie)
        st.image(recent_movie[0]['image'], recent_movie[0]['caption'], width=110)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        num_entries_kpi(movie_df)
    with col2:
        num_new_movies_watched_kpi(movie_df, current_year)
    with col3:
        num_hours_watched(movie_df)
    with col4:
        num_reviews_kpi(movie_df)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        get_treemap_of_genres_movies_watched(movie_df)
    with col2:
        container = st.container(border=False, height=352)
        with container:
            english_foreign_language_pie_chart(movie_df)
            bar_chart(movie_df)
    with col3:
        display_top3_movies(top3)

    

    
    # display_social_media_links()

    

def main():
    # set_page_style()
    if 'clicked' not in st.session_state:
        st.session_state.clicked = False

    # set_page_style()
    text_input_container = st.empty()
    
    username, submit_button1, submit_button2 = create_username_form(text_input_container)
    # disclaimer_container = st.empty()
    # with disclaimer_container:
    #     render_disclaimer()

    if submit_button1:
        current_year = datetime.now().year
        movie_df = load_data(current_year, username)
        top3 = get_top3_movies(movie_df)
        generate_story(username, movie_df, current_year, top3)

    if st.session_state.clicked:
        text_input_container.empty()
        # disclaimer_container.empty()
        current_year = datetime.now().year
        movie_df = load_data(current_year, username)
        
        top3 = get_top3_movies(movie_df)
        display_dashboard(username, movie_df, current_year, top3)

    display_social_media_links()

# if __name__ == "__main__":
#     main()