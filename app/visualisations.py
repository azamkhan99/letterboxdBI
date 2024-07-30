import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import squarify
from pypalettes import load_cmap
from typing import List, Dict, Optional

TEXT_COLOR = '#e0edfd'

def num_entries_kpi(df, year=None):
    
    # st.metric(label='WATCHED', value=df.shape[0])
    st.html(f"<h4 style='text-align: center; color: {TEXT_COLOR};'>{df.shape[0]}<br>ENTRIES</h4>")
    

def num_hours_watched(movie_df, year=None):

    hours_watched = round(movie_df['runtime'].sum()/60, 1)
    
        
    # st.metric(label='HOURS', value=hours_watched)
    st.html(f"<h4 style='text-align: center; color: {TEXT_COLOR};'>{hours_watched}<br>HOURS</h4>")

def num_reviews_kpi(df, year=None):
    
    movies_w_reviews = df[~df['description'].str.contains('Watched on')].shape[0]
    # st.metric(label='REVIEWED', value=movies_w_reviews)
    st.html(f"<h4 style='text-align: center; color: {TEXT_COLOR};'>{movies_w_reviews}<br>REVIEWS</h4>")

def num_new_movies_watched_kpi(movie_data_df, year=None):
    
    
    new_movies = movie_data_df[movie_data_df['release_date'].dt.year == year].shape[0]
    # st.metric(label='NEW FILMS', value=new_movies)
    st.html(f"<h4 style='text-align: center; color: {TEXT_COLOR};'>{new_movies}<br>NEW FILMS</h4>")

def donut_chart(df, year=None):
    genre_counts = df['genres'].explode().value_counts().reset_index()
    dc = alt.Chart(genre_counts).mark_arc(innerRadius=50).encode(
    theta="count",
    color=alt.Color("genres:N", legend=alt.Legend(orient="bottom", columns=5)),
    )
    
    st.altair_chart(dc, use_container_width=True)


def get_treemap_of_genres_movies_watched(movie_data_df):
    genre_counts_df = movie_data_df['genres'].explode().value_counts().reset_index()

    cmap = load_cmap('evergreen')
    category_codes, unique_categories = pd.factorize(genre_counts_df['genres'])
    colors = [cmap(code / (len(unique_categories) - 1)) for code in category_codes]

    # create a treemap
    fig, ax = plt.subplots(figsize=(9,10))
    background_color = '#14181c'
    fig.patch.set_facecolor(background_color)
    
    ax.set_axis_off()
    squarify.plot(
    sizes=genre_counts_df['count'],
    label=genre_counts_df['genres'],
    color=colors,
    text_kwargs={'color':'white', 'fontsize': 18, 'fontfamily': 'sans-serif'},  # Increase font size and change font family
    pad=True,
    ax=ax
    )
    
    ax.set_title('Genres Watched', y=-0.2, fontsize=25, color=f'{TEXT_COLOR}', fontfamily='sans-serif')
    
    st.pyplot(fig)




def bar_chart(df, year=None):
    # value counts of memberRatings

    member_rating_counts = df['memberRating'].value_counts().reset_index()


    bc = alt.Chart(member_rating_counts).mark_bar(size=20, color= '#66dd68').encode(
    alt.X("memberRating:Q", bin=False, title='Ratings Spread',scale=alt.Scale(domain=[0, 5.0]), axis=alt.Axis(ticks=False, labels=False, grid=False, domain=True, domainWidth=4)),
    y=alt.Y("count", axis=None),
    ).properties(title='', height = 170).configure_axisY(title=None)
    
    st.altair_chart(bc, use_container_width=True)
    st.markdown(
            """
        <style>
        button[title="View fullscreen"] {
            display: none;
        }
        </style>
        """,
            unsafe_allow_html=True,
        )

def english_foreign_language_pie_chart(df):
    # pie chart of original_language
    original_language_counts = df['original_language'].value_counts().reset_index()
    
    en_count = original_language_counts[original_language_counts['original_language'] == 'en']['count'].sum()
    non_en_count = original_language_counts[original_language_counts['original_language'] != 'en']['count'].sum()

    # Prepare data for the pie chart
    pie_data = pd.DataFrame({
        'language': ['English', 'Foreign Language'],
        'count': [en_count, non_en_count]
    })

    # Create the pie chart without a legend
    pie_chart = alt.Chart(pie_data, title=alt.TitleParams(text='International Films', orient='top', fontWeight='normal')).mark_arc().encode(
        theta=alt.Theta(field='count', type='quantitative'),
        color=alt.Color(field='language', type='nominal', scale=alt.Scale(range=['#475564','#66dd68']), legend=None),
        tooltip=['language', 'count']
    ).properties(height=170)

    st.altair_chart(pie_chart, theme=None, use_container_width=True)    



def rating_to_stars(rating):
    rating = float(rating)
    stars = '⭐️' * int(rating)
    return stars



def create_movie_thumbnails(movie_df: pd.DataFrame, caption: Optional[str] = None) -> List[Dict[str, str]]:
    records = movie_df[['title', 'memberRating', 'poster_url']].to_dict(orient='records')
    return [
        {
            'image': record['poster_url'],
            'caption': caption if caption in ['First Film', 'Last Film'] else rating_to_stars(record['memberRating'])
        }
        for record in records
    ]

def get_top3_movies(movie_df: pd.DataFrame) -> List[Dict[str, str]]:
    top3 = movie_df.nlargest(3, 'memberRating')
    return create_movie_thumbnails(top3)

def most_recent_log(movie_df: pd.DataFrame) -> List[Dict[str, str]]:
    most_recent = movie_df.nlargest(1, 'logDate')
    return create_movie_thumbnails(most_recent, caption='Last Film')

def first_log(movie_df: pd.DataFrame) -> List[Dict[str, str]]:
    first_log = movie_df.nsmallest(1, 'logDate')
    return create_movie_thumbnails(first_log, caption='First Film')


def vibe_calculator(movie_df):
    
    
    # Calculate the number of films watched in each genre
    # nostalgia merchant = films watched that were released before 2000

    nostalgia_merchant = movie_df[movie_df['release_date'].dt.year < 2000].shape[0]

    # cinema lover = films watched that were released in the current year
    current_year = pd.Timestamp.now().year
    cinema_lover = movie_df[movie_df['release_date'].dt.year == current_year].shape[0]

    # globe trotter = films watched that are not in English
    globe_trotter = movie_df[movie_df['original_language'] != 'en'].shape[0]

    vibes = {
        'Old Soul': nostalgia_merchant,
        'Popcorn Enjoyer': cinema_lover,
        'Globe Trotter': globe_trotter
    }

    max_vibe = max(vibes, key=vibes.get)
    return max_vibe
