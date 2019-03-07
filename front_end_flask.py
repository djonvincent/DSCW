import Pyro4
import json
import random
from flask import Flask, request, abort
app = Flask(__name__)

update_id = 0
ns = Pyro4.locateNS()
proxies = {}
servers = []
def refresh_servers():
    global proxies
    global servers
    proxies = {}
    servers = []
    for k, v in ns.list(prefix='MovieRating').items():
        proxies[k] = Pyro4.Proxy(v)
        servers.append(k)
    print(servers)
refresh_servers()

class NoServersOnlineError(Exception):
    pass

def execute(func, *args, avoid=[]):
    if len(servers) == 0:
        raise NoServersOnlineError()
    servers_copy = servers[:]
    for s in avoid:
        servers_copy.remove(s)
    if len(servers_copy) == 0:
        servers_copy = servers[:]
    server = random.choice(servers_copy)
    proxy = proxies[server]
    try:
        status = proxy.get_status()
        if status == 'overloaded':
            print(server + ' is overloaded, trying another')
            avoid.append(server)
            return execute(func, *args, avoid=avoid)
        result = {}
        result['result'] = getattr(proxy, func)(*args)
        result['server'] = server
        return result
    except Pyro4.errors.CommunicationError:
        ns.remove(server)
        servers.remove(server)
        return execute(func, *args)

@app.errorhandler(404)
def not_found(error):
    return json.dumps({
        'error': 'Movie not found'
    }), 404

@app.route('/<movie_id>', methods=['GET'])
def get_movie(movie_id):
    refresh_servers()
    try:
        result = execute('get_movie', movie_id, avoid=[])
        return json.dumps(result)
    except NoServersOnlineError:
        abort(503)
    except KeyError:
        abort(404)

@app.route('/<movie_id>/rating', methods=['POST'])
def post_rating(movie_id):
    refresh_servers()
    global update_id
    try:
        rating = int(request.form['rating'])
        execute('add_rating', movie_id, rating, update_id, avoid=[])
        update_id += 1
        return json.dumps({'status': 'updated'})
    except NoServersOnlineError:
        abort(503)
    except KeyError:
        abort(404)

print('Ready')
