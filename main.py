from typing import List, Dict
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import numpy as np


from application.data import users, ratings, movies, movie_names, all_genres, movie_ids, id2title, movie_dict
from application.recommend import get_top_n_most_popular_movies_by_genre, get_top_n_highly_rated_movies_by_genre, myIBCF_from_dict,get_top_n_highly_rated_movies_all_genres, get_movie_id_by_name
from application.thumbnails import get_thumbnail_url

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the "static" directory at the root URL
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2Templates to use the "static" directory
templates = Jinja2Templates(directory="static")

class UserRating(BaseModel):
    movie_id: int
    ratings: int

class UserRatings(BaseModel):
    user_ratings: List[UserRating]

    
# class UserRatings(BaseModel):
#     movie_id: List[int]
#     ratings: List[int]

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("System1.html", {"request": request})

@app.get("/system1")
async def system1(request: Request):
    return templates.TemplateResponse("System1.html", {"request": request})

@app.get("/system2")
async def blank(request: Request):
    return templates.TemplateResponse("System2.html", {"request": request})

# Input favourite genre, output top 10 most popular movies
@app.get("/recommend/genre/most_popular/{genre}")
async def recommend(genre: str, n: int = 10, top: bool = True):
    if genre not in all_genres:
        raise HTTPException(status_code=404, detail=f"Genre {genre} not found in list of genres")
    recommendations = get_top_n_most_popular_movies_by_genre(movies, ratings, genre, n, top)
    return JSONResponse(content=recommendations)



#Input favourite genre, output top 10 highly rated movies
@app.get("/recommend/genre/highly_rated/{genre}")
async def recommend(genre: str, n: int = 10, top: bool = True):
    if genre not in all_genres:
        raise HTTPException(status_code=404, detail=f"Genre {genre} not found in list of genres")
    recommendations = get_top_n_highly_rated_movies_by_genre(movies, ratings, genre, n, top)
    return JSONResponse(content=recommendations)


    # Get top 100 highly rated movies for all genres
@app.get("/recommend/all_genres/highly_rated/")
async def recommend(n: int = 100):
    top_100 = get_top_n_highly_rated_movies_all_genres()
    # Shuffle the top 100
    np.random.shuffle(top_100)
    response = {int(t):id2title(int(t), movie_dict) for t in top_100}
    return JSONResponse(content=response)



@app.post("/recommendations/ibcf/")
async def recommend(user_ratings: UserRatings):
    user_ratings_dict = {int(item.movie_id): item.ratings for item in user_ratings.user_ratings}
    print(f"////////// {user_ratings_dict}")
    recommendations = myIBCF_from_dict(user_ratings_dict)
    return JSONResponse(content=recommendations)


# @app.post("/recommendations/ibcf/")
# async def recommend(user_ratings: UserRatings):
#     #user_ratings = json.loads(user_ratings)
#     #user_ratings = dict(user_ratings)
#     user_ratings = dict(zip(user_ratings.movie_id, user_ratings.ratings))
#     # user_ratings = dict(zip(user_ratings.user_ratings.movie_id, user_ratings.user_ratings.ratings))
#     print(f"////////// {user_ratings}")
#     recommendations = myIBCF_from_dict(user_ratings)
#     return JSONResponse(content=recommendations)

# @app.post("/recommendations/ibcf")
# async def recommend_movies_ibcf(user_ratings: Dict[int, int]):
#     try:
#         recommendations = myIBCF_from_dict(user_ratings)
#         return recommendations
#     except Exception as e:
#         # Handle exceptions or errors appropriately
#         raise HTTPException(status_code=500, detail=str(e))

@app.get("/get_movie_id")
def get_movie_id(movie_name: str):
    movie_id = get_movie_id_by_name(movie_name)
    if movie_id is not None:
        return {"movie_name": movie_name, "movie_id": movie_id}
    else:
        return {"error": f"Movie with name '{movie_name}' not found."}


@app.get("/movies/{movie_id}")
async def get_movie_art(movie_id: int):
    if movie_id not in movie_ids:
        raise HTTPException(status_code=404, detail=f"Movie {movie_id} not found in list of movies")
    url = get_thumbnail_url(movie_id)
    return url


@app.get("/movies/")
async def get_movie_art(movie_ids: List[int]):
    result = []

    for movie_id in movie_ids:
        if movie_id not in movie_ids:
            # You might want to handle this differently based on your use case
            result.append({"movie_id": movie_id, "error": f"Movie {movie_id} not found in list of movies"})
        else:
            url = get_thumbnail_url(movie_id)
            result.append({"movie_id": movie_id, "url": url})

    return result