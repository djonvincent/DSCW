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
    for k, v in ns.list(prefix='ReplicaManager').items():
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
        if len(servers) == 0:
            print('No servers online')
            return {"error": "No replica managers online"}
        if len(avail) == 0:
            choose_from = servers[:]
        else:
            choose_from = avail
        server = random.choice(choose_from)
        proxy = proxies[server]
        try:
            status = proxy.get_status()
            if status == 'overloaded' and len(avail) > 0 or status == 'offline':
                print(f'{server} is {status}, trying another')
                choose_from.remove(server)
                if status == 'offline':
                    servers.remove(server)
                return self.execute(func, choose_from, *args)
            result = {}
            result['result'] = getattr(proxy, func)(*args)
            result['server'] = server
            print(f'Using {server}')
            return result
        except Pyro4.errors.CommunicationError:
            print(f'{server} is offline, trying another')
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
