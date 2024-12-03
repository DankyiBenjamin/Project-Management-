import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.group_name = f"project_{self.project_id}"

        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        # Broadcast the data to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'send_comment',
                'comment': data['comment']
            }
        )

    # Receive message from group
    async def send_comment(self, event):
        comment = event['comment']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'comment': comment
        }))
