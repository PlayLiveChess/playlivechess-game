from threading import Thread, Lock
from time import sleep
from collections import deque


"""
Bucket represents rating buckets.
Players are enqueue in different buckets according to their rating.
"""
class Bucket():
    def __init__(self, min_rating, max_rating):
        self.min_rating = min_rating
        self.max_rating = max_rating
        self.player_channels = deque()
        self.lock = Lock()

    def push(self, player_channel):
        if(player_channel.get_rating() < self.min_rating or
            player_channel.get_rating() > self.max_rating):
                raise Exception('Player\'s rating is out of bucket range!')

        # Append while adding, removeleft while removing
        self.player_channels.append(player_channel)

    def pop(self):
        return self.player_channels.popleft()

    def length(self):
        return self.player_channels.__len__()

    def remove(self, player_channel):
        self.player_channels.remove(player_channel)

    def acquire(self):
        self.lock.acquire()

    def release(self):
        self.lock.release()


"""
QueueThread is responsible for managing pairing of various
players connecting to the gameserver.

This is a singleton class, meaning only one instance of QueueThread
can be created during the scope of the proram.
"""
class QueueThread(Thread):
    # __shared_instance is the one and only object of QueueThread
    __shared_instance = None

    # Buckets for different ratings
    waiting_buckets = []

    # max supported rating
    max_supported_rating = 5000

    def __init__(self):
        if self.__shared_instance == None:
            Thread.__init__(self)
            QueueThread.__shared_instance = self
            self.setDaemon(True)

            # Initialize waiting buckets
            # Max rating supported: 5000
            for i in range(self.max_supported_rating // 100):
                self.waiting_buckets.append(Bucket(i * 100, (i + 1) * 100))

        else:
            raise Exception("QueueThread is Singleton Class!")

    def enqueue(self, player_channel):
        if(player_channel.get_rating() > self.max_supported_rating or
            player_channel.get_rating() < 0):
            raise Exception('Invalid rating!')

        bucket_index = player_channel.get_rating() // 100

        # critical section
        self.waiting_buckets[bucket_index].acquire()

        self.waiting_buckets[bucket_index].push(player_channel)

        self.waiting_buckets[bucket_index].release()

    @staticmethod
    def get_instance():
        if QueueThread.__shared_instance == None:
            QueueThread()

        return QueueThread.__shared_instance

    def run(self):
        print('Starting QueueThread...')

        while(True):
            sleep(1)
