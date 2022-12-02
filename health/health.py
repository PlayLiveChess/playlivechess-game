from threading import Lock

"""
Health is responsible for maintaining health parameters of the
server. From time to time, master server (also referred to as
load balancer in our docs) takes updates of hese parameters.

This is a singleton class, meaning only one instance of Health
can be created during the scope of the proram.
"""
class Health():
    # __shared_instance is the one and only object of Health
    __shared_instance = None

    # no of active games currently running on the server
    active_games = 0

    # no of active socket connections
    active_connections = 0

    # max no of players currently in any queue bucket
    max_players_bucket = 0

    # lock for manipulating values in Health class
    lock = Lock()

    def __init__(self):
        if self.__shared_instance == None:
            Health.__shared_instance = self
        else:
            raise Exception("Health is Singleton Class!")

    @staticmethod
    def get_instance():
        if Health.__shared_instance == None:
            Health()

        return Health.__shared_instance

    def increment_active_games(self):
        Health.lock.acquire()
        Health.active_games += 1
        Health.lock.release()

    def decrement_active_games(self):
        Health.lock.acquire()
        Health.active_games -= 1
        Health.lock.release()

    def increment_active_connections(self):
        Health.lock.acquire()
        Health.active_connections += 1
        Health.lock.release()

    def decrement_active_connections(self):
        Health.lock.acquire()
        Health.active_connections -= 1
        Health.lock.release()

    def set_max_players_bucket(self, max_players_bucket):
        Health.lock.acquire()
        Health.max_players_bucket = max_players_bucket
        Health.lock.release()
