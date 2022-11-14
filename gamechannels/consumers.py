from asyncio import sleep
from channels.consumer import SyncConsumer, AsyncConsumer, StopConsumer

class MySyncConsumer(SyncConsumer):
    def websocket_connect(self, event):
        print('Connected! ', event)
        self.send({
            'type': 'websocket.accept'
        })

    def websocket_receive(self, event):
        print('Received! ', event)

    def websocket_disconnect(self, event):
        print('Disconnected! ', event)
        raise StopConsumer()

class MyAsyncConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        print('Connected! ', event)
        await self.send({
            'type': 'websocket.accept'
        })

    async def websocket_receive(self, event):
        print('Received! ', event)
        for i in range(10):
            await self.send({
                'type': 'websocket.send',
                'text': event['text'] + str(count)
            })

    async def websocket_disconnect(self, event):
        print('Disconnected! ', event)
        raise StopConsumer()