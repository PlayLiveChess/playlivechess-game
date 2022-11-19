from django.apps import AppConfig
import os
from gamechannels.queue import QueueThread
from gamechannels.health import HealthThread


class GamechannelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gamechannels'

    def ready(self):
        # Starting Queue manager thread
        if os.environ.get('RUN_MAIN') == 'true':
            QueueThread.get_instance().start()
            HealthThread.get_instance().start()
