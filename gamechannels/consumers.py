from asyncio import sleep
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from gamechannels.queue import QueueThread

class AsyncPlayerConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.rating = None
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

    def get_opponent_channel_name(self):
        if(not self.opponent_channel_name):
            raise Exception('Opponent channel is not ready yet!')
        return self.opponent_channel_name

    def get_game(self):
        if(not self.game):
            raise Exception('Game has not started yet!')
        return self.game

    async def start_game(self, game, color, opponent_channel_name):
        self.game = game
        self.color = color
        self.opponent_channel_name = opponent_channel_name

        # TODO: Add opponent details here
        await self.send_json({
            'type': 'start',
            'color': color
        })


    async def connect(self):
        print('Connected!')
        await self.accept()

    async def receive_json(self, content):
        if content['type'] == 'queue':
            # Enqueue the player
            resp = {
                'type': 'reply',
                'success': 'true',
            }
            if(self.queued):
                resp['success'] = 'false'
                resp['value'] = 'Already Queued!'
            else:
                QueueThread.get_instance().enqueue(self)
                self.queued = True

            await self.send_json(resp)

        elif content['type'] == 'move':
            # The player is trying to play a move
            resp = {
                'type': 'reply',
                'success': 'true',
            }

            valid_move = True
            outcome = None

            turn = 'black'
            if(self.game.turn):
                turn = 'white'

            if(self.color != turn):
                valid_move = False
                resp['success'] = 'false'
                resp['value'] = 'Not your turn!'

            try:
                if(valid_move):
                    self.get_game().push_san(content['value'])
                    # check game endings
                    outcome = self.get_game().outcome(claim_draw = True)
            except:
                valid_move = False
                resp['success'] = 'false'
                resp['value'] = 'Invalid move!'

            if(outcome):
                resp['outcome'] = {
                    'termination': str(outcome.termination.value),
                    'result': outcome.result()
                }
                if outcome.winner:
                    resp['outcome']['winnner'] = 'white'
                elif outcome.winner == False:
                    resp['outcome']['winnner'] = 'black'

            try:
                if(valid_move):
                    opponent_move = {
                        'type': 'opponent.move',
                        'text': {
                            'type': 'opponent',
                            'value': content['value']
                        }
                    }
                    if(outcome):
                        opponent_move['text']['outcome'] = resp['outcome']

                    await self.channel_layer.send(self.get_opponent_channel_name(), opponent_move)
            except:
                resp['success'] = 'false'
                resp['value'] = 'Error while sending to opponnent!'

            await self.send_json(resp)

            if(outcome):
                self.reset_game()

    async def opponent_move(self, content):
        await self.send_json(content['text'])

        if('outcome' in content['text'].keys()):
            self.reset_game()

    async def disconnect(self, close_code):
        print('Disconnected!')