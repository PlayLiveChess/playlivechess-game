from threading import Thread, Lock
from time import sleep
import requests
from gameserver.settings import MASTER_HOST, MASTER_PORT

"""
HealthThread is responsible for maintaining health parameters of the
server. From time to time, it updates the health status to the master
server (also referred to as load balancer in our docs).

This is a singleton class, meaning only one instance of HealthThread
can be created during the scope of the proram.
"""
class HealthThread(Thread):
    # __shared_instance is the one and only object of HealthThread
    __shared_instance = None

    # no of active games currently running on the server
    active_games = 0

    # max no of players currently in any queue bucket
    max_players_bucket = 0

    # lock for manipulating values in HealthThread class
    lock = Lock()

    def __init__(self):
        if self.__shared_instance == None:
            Thread.__init__(self)
            HealthThread.__shared_instance = self
            self.setDaemon(True)
        else:
            raise Exception("HealthThread is Singleton Class!")

    @staticmethod
    def get_instance():
        if HealthThread.__shared_instance == None:
            HealthThread()

        return HealthThread.__shared_instance

    def increment_active_games(self):
        HealthThread.lock.acquire()
        HealthThread.active_games += 1
        HealthThread.lock.release()

    def decrement_active_games(self):
        HealthThread.lock.acquire()
        HealthThread.active_games += 1
        HealthThread.lock.release()

    def set_max_players_bucket(self, max_players_bucket):
        HealthThread.lock.acquire()
        HealthThread.max_players_bucket = max_players_bucket
        HealthThread.lock.release()

    def run(self):
        print('Starting HealthThread...')

        while(True):
            API_ENDPOINT = 'http://' + MASTER_HOST + ':' + str(MASTER_PORT) + '/health'
            data = {
                'active_games': HealthThread.active_games,
                'max_players_bucket': HealthThread.max_players_bucket
            }

            try:
                resp = requests.post(API_ENDPOINT, data)
                if(not resp.ok):
                    raise Exception('Reponse not ok!')
            except:
                # print('Error while sending health check! {', self.active_games, ', ', self.max_players_bucket, '}')
                sleep(9)

            sleep(1)
