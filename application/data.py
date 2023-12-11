from .__init__ import *
from .file_io import load_data, parse_line, download_data, download_from_s3
from .config import datapath, similarity_matrix_path, rating_matrix_path, data_url, s3_bucket_name


def id2title(movie_id: int, movie_dict: dict) -> str:
    """Get movie title from movie id

    Args:
        movie_id (int): Movie id
        movie_dict (dict): Dictionary with movie ids as keys and movie titles as values

    Returns:
        str: Movie title
    """
    if movie_id in movie_dict.keys():
        title = movie_dict[movie_id]
    else:
        title = f"MovieID_{movie_id}"
    return title

# Read data
if not os.path.exists(datapath):
    os.makedirs(datapath)
if not os.path.exists(datapath/"users.dat"):
    download_data(data_url+"users.dat", datapath/"users.dat")
if not os.path.exists(datapath/"ratings.dat"):
    download_data(data_url+"ratings.dat", datapath/"ratings.dat")
if not os.path.exists(datapath/"movies.dat"):
    download_data(data_url+"movies.dat", datapath/"movies.dat")
users = load_data(datapath/"users.dat", header=['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code'])
ratings = load_data(datapath/"ratings.dat", header=['UserID', 'MovieID', 'Rating', 'Timestamp'])
movies = load_data(datapath/"movies.dat", header=['MovieID', 'Title', 'Genres', ])

# Preprocess data
users['UserID'] = users['UserID'].astype(int)
users['Age'] = users['Age'].astype(int)
users['Occupation'] = users['Occupation'].astype(int)
movies['MovieID'] = movies['MovieID'].astype(int)
movies['Genres'] = movies['Genres'].apply(lambda x: np.array(x.split('|'))) # Convert genres to array
ratings['UserID'] = ratings['UserID'].astype(int)
ratings['MovieID'] = ratings['MovieID'].astype(int)
ratings['Rating'] = ratings['Rating'].astype(int)
ratings['Timestamp'] = pd.to_datetime(ratings['Timestamp'], unit='s')

# Global variables


movie_dict = dict(zip(movies['MovieID'], movies['Title'])) # Create dict of movie names and movie ids
movie_dict_inv = dict(zip(movies['Title'], movies['MovieID']))
movie_ids = pd.merge(ratings['MovieID'], movies, on='MovieID', how='inner')['MovieID'].unique()
all_genres = movies['Genres'].explode().unique()


#R = ratings.pivot(index='UserID', columns='MovieID', values='Rating')
# Loading R from Rmat
if not os.path.exists(rating_matrix_path):
    if not download_from_s3(s3_bucket_name, rating_matrix_path.name, datapath):
        print(f"Downloading rating matrix from {s3_bucket_name} failed.")
R = pd.read_csv(rating_matrix_path, index_col=0)
movie_names = R.columns.map(lambda x: id2title(x, movie_dict))
R.columns = movie_names
## Normalize rating matrix R by centering each row around its mean (ignore NaN values)
R_norm = R.sub(R.mean(axis=1), axis=0)
R_np = np.array(R_norm)
n_movies = R_np.shape[1]
R_zeros = R_np.copy()
R_zeros[np.isnan(R_np)] = 0
