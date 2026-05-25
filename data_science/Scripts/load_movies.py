
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path)
sys.path.append(str(backend_path))

df = pd.read_csv('C:/Users/jonab/.vscode/PROJECTS/Web Development Projects/Movie Recommendation Application/data_science/datasets/processed/movies_clean_again.csv')

# renaming clean_title to title to match database.
df.drop(columns=['title'], inplace=True, errors='ignore')
df.rename(columns={'clean_title': 'title'}, inplace=True)


engine = create_engine('postgresql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{TABLE}')

with engine.begin() as connection:
    # FIRST: Insert movies without genres since genres will be another table

    df['title'] = df['title'].str.strip()

    movies_df = df[['title', 'overview', 'release_year', 'rating_avg', 'poster_url']]
    movies_df.to_sql('movies', connection, if_exists='append', index=False)

    # THEN SECOND: Insert unique genres into its own table 
    all_genres = set()
    for g_list in df['genres']:
        if pd.notna(g_list):
            for g in g_list.split('|'):
                all_genres.add(g.strip())

    for genre in all_genres:
        connection.execute(
            text("INSERT INTO genres (name) VALUES (:name) ON CONFLICT DO NOTHING"),
            {"name": genre}
        )
    

    # NEXT STEPS: Inserting into joinned table MovieGenres
    # First, retrieve mapping from genre name --> genre id
    genre_map = pd.read_sql("SELECT * FROM Genres", connection).set_index('name')['genre_id'].to_dict()
    # Second, retrieving mapping from movie title ---> movie id
   

    movie_map = pd.read_sql("SELECT * FROM Movies", connection).set_index('title')['movie_id'].to_dict()

    # Insert rows into join table
    joined_rows = []

    # loop through each row in the CSV
    for _, row in df.iterrows():
        # find the id of a movie in that row using the movie_map dictionary
        movie_id = movie_map[row['title']]
        # if there were  assigned genres in that row
        if pd.notna(row['genres']):
            # capture every genre in that row, delimitated by |
            for g in row['genres'].split('|'):
                # get the associated id for each genre from the dictionary
                genre_id = genre_map[g.strip()]
                # add to the data list of the MoviesGenres table.
                joined_rows.append({"movie_id": movie_id, "genre_id": genre_id})

    join_df = pd.DataFrame(joined_rows)
    join_df.to_sql('MovieGenres', connection, if_exists='append', index=False)

print("CSV data loaded into Movies, Genres, and MovieGenres successfully!!")

