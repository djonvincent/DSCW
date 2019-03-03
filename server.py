import Pyro4

@Pyro4.expose
class MovieRating:
    def __init__(self):
        self.movies = {
            'A': {
                'avg': 4,
                'num': 2
            }
        }
    def get_movie(self, name):
       return self.movies[name]

    def add_rating(self, name, rating):
        if name not in self.movies:
            self.movies[name] = {
                'avg': rating,
                'num': 1
            }
            return
        movie = self.movies[name]
        avg = movie['avg']
        num = movie['num']
        self.movies[name]['avg'] = (avg*num + rating)/(num+1)
        movie['num'] += 1

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(MovieRating)
ns.register('MovieRating', uri)

print('Ready')
daemon.requestLoop()
