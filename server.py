import Pyro4
import csv
from collections import defaultdict

with open('ratings.csv', newline='') as f:
    reader = csv.reader(f, delimiter=',')
    next(reader)
    totals = defaultdict(int)
    nums = defaultdict(int)
    for row in reader:
        movie_id = row[0]
        totals[movie_id] += float(row[1])
        nums[movie_id] += 1

@Pyro4.expose
class MovieRating:
    def get_movie(self, movie_id):
       return {
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
ns.register('MovieRating', uri)

print('Ready')
daemon.requestLoop()
