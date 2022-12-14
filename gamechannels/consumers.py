from asyncio import sleep
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from gamechannels.queue import QueueThread
from health.health import Health
from gameserver.settings import LIMIT

class AsyncPlayerConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rating = None
        self.name = None
        self.reset_game()

    def reset_game(self):
        self.opponent_channel_name = None
        self.game = None
        self.color = None
        self.queued = False

    def get_rating(self):
        if(self.rating):
            return self.rating
        return 1000
    
    def get_name(self):
        if(self.name):
            return self.name
        return 'Player'

    def get_opponent_channel_name(self):
        if(not self.opponent_channel_name):
            raise Exception('Opponent channel is not ready yet!')
        return self.opponent_channel_name

    def get_game(self):
        if(not self.game):
            raise Exception('Game has not started yet!')
        return self.game

    async def start_game(self, game, color, opponent_channel_name, playerDetails):
        self.game = game
        self.color = color
        self.opponent_channel_name = opponent_channel_name

        # TODO: Add opponent details here
        await self.send_json({
            'type': 'start',
            'color': color,
            'opponentDetails': playerDetails
        })


    async def connect(self):
        Health.get_instance().increment_active_connections()
        if(Health.get_instance().active_connections < LIMIT):
            print('Connected!')
            await self.accept()
        else:
            print('Limit Reached! Connection Rejected')

    async def receive_json(self, content):
        resp = {
            'type': 'reply',
            'success': 'true',
        }

        if content['type'] == 'queue':
            # Enqueue the player
            if(self.queued):
                resp['success'] = 'false'
                resp['value'] = 'Already Queued!'
            else:
                try:
                    self.name = content['playerDetails']['name']
                    self.rating = int(content['playerDetails']['rating'])
                except:
                    pass

                QueueThread.get_instance().enqueue(self)
                self.queued = True

        elif content['type'] == 'move':
            # The player is trying to play a move

            valid_move = True
            outcome = None

            try:
                turn = 'black'
                if(self.get_game().turn):
                    turn = 'white'

                if(self.color != turn):
                    raise Exception('Not your turn!')

                try:
                    self.get_game().push_san(content['value'])
                except:
                    raise Exception('Invalid move!')

                # check game endings
                outcome = self.get_game().outcome(claim_draw = True)

                opponent_move = {
                    'type': 'opponent.move',
                    'text': {
                        'type': 'opponent',
                        'value': content['value']
                    }
                }

                if(outcome):
                    resp['outcome'] = {
                        'termination': str(outcome.termination.value),
                        'result': outcome.result()
                    }
                    if outcome.winner:
                        resp['outcome']['winnner'] = 'white'
                    elif outcome.winner == False:
                        resp['outcome']['winnner'] = 'black'

                    opponent_move['text']['outcome'] = resp['outcome']

                await self.channel_layer.send(self.get_opponent_channel_name(), opponent_move)

            except Exception as e:
                resp['success'] = 'false'
                resp['value'] = str(e)


            if(outcome):
                self.reset_game()
                Health.get_instance().decrement_active_games()

        else:
            resp['success'] = 'false'
            resp['value'] = 'Unrecognized command!'

        await self.send_json(resp)

    async def opponent_move(self, content):
        await self.send_json(content['text'])

        if('outcome' in content['text'].keys()):
            self.reset_game()
    
    async def opponent_disconnect(self, content):
        await self.send_json(content['text'])
        self.reset_game()

    async def disconnect(self, close_code):
        disconnect_message = {
            'type': 'opponent.disconnect',
            'text': {
                'type': 'disconnect'
            }
        }
        if(self.opponent_channel_name):
            await self.channel_layer.send(self.get_opponent_channel_name(), disconnect_message)
            Health.get_instance().decrement_active_games()

        if(self.queued):
            QueueThread.get_instance().dequeue(self)

        Health.get_instance().decrement_active_connections()
        print('Disconnected!')