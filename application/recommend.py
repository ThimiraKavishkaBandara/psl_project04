from .__init__ import *
from .data import users, ratings, movies, movie_names, all_genres, movie_ids, R, R_np, R_zeros, n_movies, movie_dict_inv, movie_dict
from .config import datapath
from .similarities import get_similarity_matrix


# Recommender System I - Genres
def get_top_n_most_popular_movies_by_genre(movies: pd.DataFrame, 
                                           ratings: pd.DataFrame, 
                                           genre: str, 
                                           n: int, 
                                           top: bool = True) -> Dict[int, str]:
    """Get top n most popular movies by genre (movies with highest or lowest number of ratings)

    Args:
        movies (pd.DataFrame): Movies dataframe
        ratings (pd.DataFrame): Ratings dataframe
        genre (str): Genre to filter movies by
        n (int): Number of movies to return
        top (bool, optional): Whether to return top or bottom n movies. Defaults to True.

    Returns:
        List[str]: List of movie names
    """
    all_genres = movies['Genres'].explode().unique()
    assert genre in all_genres, f"Genre {genre} not found in list of genres"
    movie_ids = movies[movies['Genres'].apply(lambda x: genre in x)]['MovieID'].unique()
    if top:
        idx = ratings[ratings['MovieID'].isin(movie_ids)].value_counts().head(n).index.get_level_values(1).values
    else:
        idx = ratings[ratings['MovieID'].isin(movie_ids)].value_counts().tail(n).index.get_level_values(1).values
    movie_ids = [int(i) for i in movie_ids] # Convert numpy.int64 to int
    recommendations = {id:name for id, name in zip(list(movie_ids), list(movies.loc[movies['MovieID'].isin(idx), 'Title'].unique()))}
    return recommendations

def get_top_n_highly_rated_movies_by_genre(movies: pd.DataFrame, 
                                           ratings: pd.DataFrame, 
                                           genre: str, 
                                           n: int, 
                                           top: bool = True) -> Dict[int, str]:
    """Get top n most highly rated movies by genre (movies with highest or lowest average rating)

    Args:
        movies (pd.DataFrame): Movies dataframe
        ratings (pd.DataFrame): Ratings dataframe
        genre (str): Genre to filter movies by
        n (int): Number of movies to return
        top (bool, optional): Whether to return top or bottom n movies. Defaults to True.

    Returns:
        List[str]: List of movie names
    """
    all_genres = movies['Genres'].explode().unique()
    assert genre in all_genres, f"Genre {genre} not found in list of genres"
    movie_ids = movies[movies['Genres'].apply(lambda x: genre in x)]['MovieID'].unique()
    if top:
        idx = ratings[ratings['MovieID'].isin(movie_ids)].groupby(by='MovieID').mean().sort_values(by='Rating', ascending=False).head(n).index.values
    else:
        idx = ratings[ratings['MovieID'].isin(movie_ids)].groupby(by='MovieID').mean().sort_values(by='Rating', ascending=True).head(n).index.values
    movie_ids = [int(i) for i in movie_ids] # Convert numpy.int64 to int
    recommendations = {id:name for id, name in zip(list(movie_ids), list(movies.loc[movies['MovieID'].isin(idx), 'Title'].unique()))}
    return recommendations

def get_top_n_highly_rated_movies_all_genres(n: int = 100):
    """Get top n most highly rated movies for all genres

    Returns:
        List[str]: List of movie names
    """
    return list(ratings.groupby(by='MovieID').mean().sort_values(by='Rating', ascending=False).head(n).index.values)

# Recommender System II - Collaborative Filtering

## Load pre-computed similarity matrix 
S_k = get_similarity_matrix(R_zeros, k=30, filename='similarity_matrix_top_k.npy')

# # Do item-based collaborative filtering
# def myIBCF(w: np.array, R: pd.DataFrame, S: np.array, k=30) -> Dict[int, str]:
#     """_summary_

#     Args:
#         w (np.array): new user vector of ratings, n_movies x 1
#         R (pd.DataFrame): rating matrix with movie names for columns, n_users x n_movies
#         S (np.array): similarity matrix, n_movies x n_movies
#         k (int, optional): number of neighbors. Defaults to 30.

#     Returns:
#         List[str]: top 10 movie recommendations as list of names
#     """
#     eps = 10e-10
#     if isinstance(R, np.ndarray):
#         R = pd.DataFrame(R)
#     # prediction p_l ()
#     len_w = len(w)
#     assert len_w == R.shape[1], f"Length of w ({len_w}) does not match number of movies ({R.shape[1]})"
#     p = np.ones(len_w)
#     idx_not_rated = w == 0 # Movies not rated by user
#     idx_rated = w != 0 # Movies rated by user
#     for l in tqdm(range(len_w)):
#         # Determine top k neighbors among rated movies
#         idx_top_k = np.argsort(S[l,:])[-k:]# np.argsort(S[l,idx_rated])[-k:] # idx_rated currently leads to lumping of movies #
#         S_l = S[l,idx_top_k]
#         p[l] = S_l.dot(w[idx_top_k].T) / np.sum(S_l + eps)
#     # Select predictions which have not yet been rated by this user yet
#     #p = p[idx_not_rated]
#     # Select top 10 movies
#     # If there are less than 10 top k movies, fill with top rated movies
#     idx_top_10 = np.argsort(p)[-10:]
#     print(idx_top_10)
#     #Compute top 10 most popular movies
#     idx_top_10_popular = R.sum(axis=0).sort_values(ascending=False).index[:(min(len_w, 10))]
#     idx_top_10_popular = list(map(lambda x: movie_dict_inv.get(x), idx_top_10_popular))
#     print(idx_top_10_popular)
#     # Fill top 10 with most popular movies
#     idx_top_10 = np.concatenate((idx_top_10, idx_top_10_popular[len(idx_top_10):])).astype(int)
#     print(idx_top_10)
#     # Return top 10 movie names
#     idx_top_10 = [int(i+1) for i in idx_top_10] # Convert numpy.int64 to int and shift indices by 1
#     recommendations = {id:movie_dict.get(id, "Unknown Movie") for id in idx_top_10}
#     return recommendations

def myIBCF(w: np.array, R: pd.DataFrame, S: np.array, k=30) -> Dict[int, str]:
    """summary

    Args:
        w (np.array): new user vector of ratings, n_movies x 1
        R (pd.DataFrame): rating matrix with movie names for columns, n_users x n_movies
        S (np.array): similarity matrix, n_movies x n_movies
        k (int, optional): number of neighbors. Defaults to 30.

    Returns:
        List[str]: top 10 movie recommendations as list of names
    """
    # get the index of movies has the user not rated?
    notrated = np.where(np.isnan(w))[0]
    rated = np.where(~np.isnan(w))[0]


    # vectors to store the movies and ratings
    movies_temp = []
    ratings_temp = []

    # loop through the unrated movies
    for l in notrated:
        # l is the index of the movie in rmat and should match the index in S
        if np.nansum((S[l, rated])) > 0:
            left = 1/(np.nansum((S[l, rated])))
            top_indices = np.where(~np.isnan(S[l, :]))[0]
            right = np.nansum(S[l, top_indices] * w[top_indices])
            # get the movie 'name'
            movies_temp.append(R.columns[l])
            # calculate the rating
            ratings_temp.append(left * right)

    # save as a dataframe so we can sort easily
    rec_df = pd.DataFrame({"Movie": movies_temp, "Rating": ratings_temp})
    # sort by rating
    rec_df = rec_df.sort_values(by="Rating", ascending=False)
    # convert to a dictionary
    rec_dict = dict(zip(rec_df["Movie"], rec_df["Rating"]))
    # if there are less than 10 movies, add the top 10 most popular movies
    if len(rec_dict) < 10:
        top_ten = R.sum(axis=0).sort_values(ascending=False).index[:10]
        for i in top_ten:
            if i not in rec_dict.keys():
                rec_dict[i] = 0
    # return the top 10 movies
    rec_dict = dict(list(rec_dict.items())[:10])
    return rec_dict

## Call IBCF function with user ratings as dict of movie ids and ratings
def myIBCF_from_dict(user_ratings: Dict[int, int]) -> Dict[int, str]:
    """_summary_

    Args:
        user_ratings (Dict[int, int]): dict of movie ids and ratings

    Returns:
        List[str]: top 10 movie recommendations as list of names
    """
    w = np.zeros(n_movies)
    print(user_ratings)
    for movie_id, rating in user_ratings.items():
        movie_id = int(movie_id)
        rating = int(rating)
        w[movie_id] = rating
    print(sum(w>0))
    return myIBCF(w, pd.DataFrame(R_zeros), S_k, k=30)



def get_movie_id_by_name(movie_name):
    for movie in movies:
        if movie['Title'] == movie_name:
            return movie['MovieID']
    return None