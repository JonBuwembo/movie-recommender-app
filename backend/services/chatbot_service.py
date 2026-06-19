from flask import Blueprint, request, jsonify
import requests
import time
import random
from rapidfuzz import process, fuzz

from routes.movies import get_movies_by_genre, get_movie_details
from services.movie_service import get_all_movies_service
from routes.search import search_movies, get_similar_movies


# What the LLM can do.
TOOLS = [
    "get_movies_by_genre",
    "get_movie_details",
    "search_movies",
    "get_similar_movies"
]


def send_chatbot_response():
    client = request.get_json()
    user_input = client.get("message")

    intent = detect_intent(user_input)

    reply = ask_qwen(user_input, intent)

    return jsonify({
        "reply" : reply
    })

def detect_intent(user_input):
    

    result = {
        "intent" : None,
        "movie" : None,
        "genre" : None,
        "query" : None
    }


    similar_keywords = [
        "similar",
        "related",
        "like",
        "close to",
        "recommend",
        "recommendation",
        "suggest",
        "suggestions",
        "something like",
        "movies like",
        "anything like",
        "if i liked",
        "fans of",
        "reminds me of"
    ]

    details_keywords = [
        "about",
        "details",
        "information",
        "info",
        "summary",
        "overview",
        "plot",
        "story",
        "tell me about",
        "what is",
        "what's",
        "describe",
        "explain",
    ]

    search_keywords = [
        "search",
        "find",
        "look for",
        "lookup",
        "show",
        "find movie",
        "search for",
        "locate",
        "get",
        "get movie"
    ]

    genre_keywords = [
        "genre",
        "action",
        "comedy",
        "drama",
        "horror",
        "thriller",
        "romance",
        "adventure",
        "fantasy",
        "sci-fi",
        "science fiction",
        "animation",
        "crime",
        "family"
    ]

    user_input = user_input.lower()

    for keyword in similar_keywords: 
        if keyword in user_input:
            result["intent"] = "SIMILAR_MOVIES"
            result["movie"] = extract_movie_title_and_id(user_input)
            return result
    
    for keyword in details_keywords: 
        if keyword in user_input:
            result["intent"] = "MOVIE_DETAILS"
            result["movie"] = extract_movie_title_and_id(user_input)
            return result
    
    for keyword in search_keywords: 
        if keyword in user_input:
            result["intent"] = "SEARCH_MOVIES"
            result["query"] = user_input
            return result

    for keyword in genre_keywords: 
        if keyword in user_input:
            result["intent"] = "GENRE_SEARCH"
            result["genre"] = keyword  
            return result
    
    # fallback
    result['intent'] = "GENERAL_CHAT"
    return result

def extract_movie_title_and_id(user_input):
    
    # user: Recommend movies similar to interstellar
    # we want "interstellar"

    movies = get_all_movies_service()
    user_input = user_input.lower()

    movie_titles = [movie['title'] for movie in movies]

    queried_title = ""
    for movie in movies:
        if movie["title"] in user_input:
            queried_title = movie['title']
            break

    match = process.extractOne(
        queried_title,
        movie_titles,
        scorer=fuzz.partial_ratio
    )


    if match is None:
        return None

    title, score, _ = match

    print("Matched title:", title)
    print(f"score for movie closeness: {score}")

    if score >= 70:
        for movie in movies:
            if movie["title"] == title:
                return {
                    "title": movie["title"],
                    "id": movie["movie_id"]
                }
    
    return None

    
def ask_qwen(user_input, intent):

    start = time.time()

    result = None
    formatted_results = "No information available."

    if intent['intent'] == "SIMILAR_MOVIES":
        movie = intent.get("movie")
        if movie:
            result = get_similar_movies(intent["movie"]["id"])
            print(f"MOVIE RESULTS FROM DB: {result}")
            formatted_results = format_similar_movies(intent, result)

    elif intent['intent'] == "MOVIE_DETAILS":
        movie = intent.get("movie")
        if movie:
            result = get_movie_details(intent["movie"]["id"])
            formatted_results = format_movie_details(intent, result)

    elif intent['intent'] == "SEARCH_MOVIES":
        movie = intent.get("movie")
        if movie:
            result = search_movies(intent)
            formatted_results = format_search_movies(intent, result)

    elif intent['intent'] == "GENRE_SEARCH":
        result = get_movies_by_genre(intent["genre"])
        formatted_results = format_genre_search(intent, result)
    
    print("")
    print(f"INTENT: {intent["intent"]}")
    print(formatted_results)
    print("")


    response = requests.post("http://localhost:11434/api/generate",
        json={
            "model": "phi3:mini",
            "prompt": f"""
            
            You are a movie recommendation assistant.
            Answer the user's question using the database results below.

            User's Question:
            {user_input}

            Database results:
            {formatted_results}

            Rules:
             - The database results are your single source of truth.
             - If the database results contain relevant information, use them.
             - Do not invent movies that are not present in the database results.
             - Do not invent additional information.
             - use and display movie information exactly as provided in the database results.
             - If the database results are empty, say no matching movies were found. 
             - DO NOT explain why the movies are selected.
             - If there a duplicates, display that movie only once.
             - display movie recommendations and information as bullet points.
             - Do not explain your reasoning process.
             - Keep your responses under 100 words.

            """,

            "stream": False
        }
    )

    print("Qwen time:", time.time() - start)

    data = response.json()

    # Return chatbot response.
    return data["response"]


def format_similar_movies(intent, result):

    if not result:
        return "No movies found."

    text = "Similar movies\n\n"

    for movie in result:       
        if movie.get("title"):
            text += f"Title: {movie["title"]}\n"
        if movie.get("genres"):
            text += f"Genre: {movie["genres"]}\n"
        if movie.get("release_year") and movie["release_year"] != 0:
            text += f"Year: {movie["release_year"]}\n"

        text += "\n"
        
    return text

def format_movie_details(intent, result):
    
    if not result:
        return "No information can be found on this movie in our catalog."
    
    text = f"Here is information on {intent["movie"]["title"]}\n\n"

    for movie in result:
        text += (
            f"Title: {movie["title"]}\n"
            f"Overview: {movie["overview"]}\n"
            f"Genre: {movie["genres"]}\n"
            f"Year: {movie["release_year"]}\n\n"
        )
    
    return text


def format_genre_search(intent, result):
    
    if not result:
        return "Cannot find movies within this genre. Please query from our current genre catalog."

    # get random 5 movies
    sample_size = min(5, len(result))
    movies = random.sample(result, sample_size)

    text = f"Here are {sample_size} {intent[genre]} movies:\n\n"


    for movie in movies:
        text += f" - {movie["title"]} ({movie["release_year"]})\n"
    
    return text


# uses rapid fuzz
def format_search_movies(intent, result):

    if not result:
        return "Cannot find any movies within this title."
    
    text = "Here is the closest movie we found:\n\n"
    for movie in result:
        text += (
            f"Title: {movie["title"]}\n"
            f"Overview: {movie["overview"]}\n"
            f"Genre: {movie["genres"]}\n"
            f"Year: {movie["release_year"]}\n\n"
        )
    return text
