from asyncio import sleep
from channels.generic.websocket import AsyncJsonWebsocketConsumer, StopConsumer

class AsyncPlayerConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def connect(self):
        print('Connected!')
        await self.accept()

    async def receive_json(self, content):
        print('Received! ', content)
        for i in range(10):
            await self.send_json({
                'type': 'websocket.send',
                'text': content
            })
            await sleep(1)

    async def disconnect(self, close_code):
        print('Disconnected!')