import Pyro4
import csv
import time
import threading
import random
from collections import defaultdict

PYRONAME = 'MovieRating'

proxies = {}
servers = []

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
    update_log = []
    gossip_batch = []
    last_gossip_time = time.time()
    def get_movie(self, movie_id):
       return {
            'title': titles[movie_id],
            'avg': totals[movie_id] / nums[movie_id],
            'num': nums[movie_id]
        }

    def add_rating(self, movie_id, rating, update_id):
        if update_id in MovieRating.update_log:
            return
        if rating < 0 or rating > 5:
            raise ValueError('Rating must be between 0 and 5')
        totals[movie_id] += rating
        nums[movie_id] += 1
        MovieRating.update_log.append(update_id)
        MovieRating.gossip_batch.append((movie_id, rating, update_id))
        return

    def gossip(self, gossip_stop):
        if not gossip_stop.is_set():
            threading.Timer(30, self.gossip, [gossip_stop]).start()
        refresh_servers()
        if len(servers) == 0:
            return
        server = random.choice(servers)
        proxy = proxies[server]
        batch = Pyro4.batch(proxy)
        for update in MovieRating.gossip_batch:
            batch.add_rating(*update)
        batch()

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

def refresh_servers():
    global proxies
    global servers
    proxies = {}
    servers = []
    for k, v in ns.list(prefix='MovieRating').items():
        if k == name:
            continue
        proxies[k] = Pyro4.Proxy(v)
        servers.append(k)

print('Ready')
movie_rating = MovieRating()
gossip_stop = threading.Event()
movie_rating.gossip(gossip_stop)
daemon.requestLoop()
