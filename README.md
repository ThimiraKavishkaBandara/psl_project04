# PSL Project 04

## Team Members
- Michael Conlin
- Constantin Kappel
- Thimira Bandara

## Project Description
The task is to build a recommender engine for movies. We get a dataset created by thousands of users who rated movies. The recommender engine should match new users to movies they might like. If available the new user's ratings should be taken into account. Other information available per movie are: userID, rating, predicted, MovieID, Title, Genres.  

## Some thoughts on technical realization
- The problem could be solved by creating vector embeddings of the movies and users. One possible way of doing this could be by contrastive learning and self-supervision. 
- For contrastive learning to work we need to find vectors which are similar based on context and dissimilar by finding random samples. For example, users could be similar if they rate the same movies similarly. Users could be dissimilar if they rate different movies differently.
- Based on a new user's ratings we could find similar users and recommend movies they liked.

## Start web application
- Backend is written in FastAPI and can be started with `uvicorn main:app --reload`
- Find the self-documenting API at http://127.0.0.1:8000/docs