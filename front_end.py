import Pyro4
import json
from flask import Flask, request, abort
app = Flask(__name__)

movie_rating = Pyro4.Proxy('PYRONAME:MovieRating')

@app.errorhandler(404)
def not_found(error):
        return json.dumps({
            'error': 'Movie not found'
        }), 404

@app.route('/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    try:
        movie = movie_rating.get_movie(movie_id)
        return json.dumps(movie)
    except KeyError:
        abort(404)

@app.route('/<movie_id>/rating', methods=['POST'])
def post_rating(movie_id):
    try:
        rating = int(request.form['rating'])
        movie_rating.add_rating(movie_id, rating)
        return json.dumps(movie_rating.get_movie(movie_id))
    except KeyError:
        abort(404)

print('Ready')
