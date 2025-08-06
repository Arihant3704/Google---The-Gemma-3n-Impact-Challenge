
import socketio
import threading
import time

class SocketClient:
    def __init__(self, server_url):
        self.sio = socketio.Client()
        self.server_url = server_url
        self.connected = False
        self.command_queue = []

        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.on_disconnect)
        self.sio.on('web_command', self.on_web_command)

    def on_connect(self):
        print("Connected to Socket.IO server!")
        self.connected = True
        self.sio.emit('qcar_connect')

    def on_disconnect(self):
        print("Disconnected from Socket.IO server.")
        self.connected = False
        self.sio.emit('qcar_disconnect')

    def on_web_command(self, data):
        print(f"Received command from web: {data}")
        self.command_queue.append(data)

    def connect(self):
        try:
            self.sio.connect(self.server_url)
        except Exception as e:
            print(f"Could not connect to Socket.IO server: {e}")

    def disconnect(self):
        self.sio.disconnect()

    def send_video_frame(self, frame_data):
        if self.connected:
            self.sio.emit('qcar_video_frame', frame_data)

    def send_lidar_data(self, lidar_data):
        if self.connected:
            self.sio.emit('qcar_lidar_data', lidar_data)

    def send_status_update(self, status_data):
        if self.connected:
            self.sio.emit('qcar_status_update', status_data)

    def get_latest_command(self):
        if self.command_queue:
            return self.command_queue.pop(0)
        return None

    def start_background_task(self):
        self.sio.start_background_task(self.sio.wait)
