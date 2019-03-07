import Pyro4
import random

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
refresh_servers()

class NoServersOnlineError(Exception):
    pass

@Pyro4.expose
class FrontEnd():
    def get_movie(self, movie_id):
        print('get_movie')
        refresh_servers()
        return self.execute('get_movie', servers[:], movie_id)

    def add_rating(self, movie_id, rating):
        print('get_rating')
        refresh_servers()
        global update_id
        update_id += 1
        return self.execute('add_rating', servers[:], movie_id, rating, update_id)

    def execute(self, func, avail, *args):
        print('servers', servers)
        print('avail', avail)
        if len(servers) == 0:
            return {"error": "No replica managers online"}
        if len(avail) == 0:
            choose_from = servers[:]
        else:
            choose_from = avail
        server = random.choice(choose_from)
        proxy = proxies[server]
        try:
            status = proxy.get_status()
            if status == 'overloaded' and len(avail) > 0:
                print(server + ' is overloaded, trying another')
                choose_from.remove(server)
                return self.execute(func, choose_from, *args)
            result = {}
            result['result'] = getattr(proxy, func)(*args)
            result['server'] = server
            return result
        except Pyro4.errors.CommunicationError:
            ns.remove(server)
            servers.remove(server)
            choose_from.remove(server)
            return self.execute(func, choose_from, *args)

daemon = Pyro4.Daemon()
ns = Pyro4.locateNS()
uri = daemon.register(FrontEnd)
ns.register('FrontEnd', uri)
print('Ready')
daemon.requestLoop()
