Requirements:
    - Python 3.6 or later
    - Pyro4 (included in requirements.txt)

Instructions:
    1. Start the Pyro4 naming server by running the command 'pyro4-ns' or
       'python -m Pyro4.naming'
    2. Start any number of replica managers by running 'python server.py' for
       each (in separate terminals)
    3. Start the front end server with 'python front_end.py'
    4. Start any number of clients by running 'python client.py' for each (in
       separate terminals)
    5. Follow the instructions in the client (type numbers to choose options)

Description:

When a new RM is brought online it will register itself on the name server so
that the front end can automatically detect it. When the front end receives a
request from the client it will avoid sending this to RMs that are overloaded,
and if the RM is offline it will remove it from the name server to avoid
sending further requests to it. This means the front end should always work as
long as at least one RM is online. The front end also supports any number of
clients connecting to it.

Each RM maintains a log of update IDs it has processed (either from the front
end directly or from other RMs in gossip messages) so that it will never apply
the same update more than once. After this happens, the full update will also
be recorded in a list called the 'gossip batch'. I have implemented the gossip
message as a Pyro batch object, which provides a fast way of calling all of
the methods in the gossip batch in one go. These gossip messages are sent from
each RM to all others every 15 seconds (configurable in server.py), ensuring
all RMs are up-to-date. 
