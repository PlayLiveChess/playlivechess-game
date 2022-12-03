from django.shortcuts import render
from django.http import JsonResponse
from health.health import Health
from gameserver.settings import LIMIT

# Create your views here.
def index(request):
    return JsonResponse({
        'available_capacity': LIMIT - Health.get_instance().active_connections,
        'ready_to_close': Health.get_instance().active_games == 0 and
            Health.get_instance().max_players_bucket <= 1
    })