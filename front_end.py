import Pyro4
import json
from flask import Flask, request
app = Flask(__name__)

movie_rating = Pyro4.Proxy('PYRONAME:MovieRating')

@app.route('/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    return json.dumps(movie_rating.get_movie(movie_id))

@app.route('/<movie_id>/rating', methods=['POST'])
def post_rating(movie_id):
    rating = int(request.form['rating'])
    movie_rating.add_rating(movie_id, rating)
    return json.dumps(movie_rating.get_movie(movie_id))

print('Ready')
