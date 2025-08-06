
from flask import Flask, render_template
from flask_socketio import SocketIO

class WebServer:
    def __init__(self):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*") # Allow all origins for development

        self.qcar_connected = False
        self.latest_video_frame = None
        self.latest_lidar_data = None
        self.latest_status_data = None

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.socketio.on('connect')
        def handle_connect():
            print("Client connected!")

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print("Client disconnected!")

        @self.socketio.on('qcar_connect')
        def handle_qcar_connect():
            self.qcar_connected = True
            print("QCar connected!")

        @self.socketio.on('qcar_disconnect')
        def handle_qcar_disconnect():
            self.qcar_connected = False
            print("QCar disconnected!")

        @self.socketio.on('qcar_video_frame')
        def handle_video_frame(data):
            self.latest_video_frame = data # Base64 encoded image
            self.socketio.emit('video_frame', data, broadcast=True)

        @self.socketio.on('qcar_lidar_data')
        def handle_lidar_data(data):
            self.latest_lidar_data = data # JSON object
            self.socketio.emit('lidar_data', data, broadcast=True)

        @self.socketio.on('qcar_status_update')
        def handle_status_update(data):
            self.latest_status_data = data # JSON object
            self.socketio.emit('status_update', data, broadcast=True)

        @self.socketio.on('command')
        def handle_command(cmd):
            print(f"Command received from web: {cmd}")
            if self.qcar_connected:
                self.socketio.emit('web_command', cmd, broadcast=True)
            else:
                print("QCar not connected, command not sent.")

    def run(self):
        self.socketio.run(self.app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
