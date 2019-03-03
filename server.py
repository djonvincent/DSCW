import Pyro4
import csv
from collections import defaultdict

PYRONAME = 'MovieRating'

with open('ratings.csv', newline='') as f:
    reader = csv.reader(f, delimiter=',')
    next(reader)
    totals = defaultdict(int)
    nums = defaultdict(int)
    for row in reader:
        movie_id = row[0]
        totals[movie_id] += float(row[1])
        nums[movie_id] += 1

with open('movies.csv', newline='') as f:
    reader = csv.reader(f, delimiter=',')
    next(reader)
    titles = dict(row[:2] for row in reader)

@Pyro4.expose
class MovieRating:
    def get_movie(self, movie_id):
       return {
            'title': titles[movie_id],
            'avg': totals[movie_id] / nums[movie_id],
            'num': nums[movie_id]
        }

    def add_rating(self, movie_id, rating):
        if rating < 0 or rating > 5:
            raise ValueError('Rating must be between 0 and 5')
        totals[movie_id] += rating
        nums[movie_id] += 1
        return

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(MovieRating)
next_id = -1
for key in ns.list(prefix=PYRONAME):
    i = int(key[len(PYRONAME):])
    if i > next_id:
        next_id = i
name = f'{PYRONAME}{next_id+1}'
ns.register(name, uri)

print('Ready')
daemon.requestLoop()
