
from flask import Flask, render_template, Response, jsonify
import cv2
import json

class WebServer:
    def __init__(self, main_app):
        self.app = Flask(__name__)
        self.main_app = main_app

        @self.app.route('/')
        def index():
            return render_template('index.html')

        @self.app.route('/video_feed')
        def video_feed():
            return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

        @self.app.route('/lidar_feed')
        def lidar_feed():
            return Response(self.generate_lidar_data(), mimetype='text/event-stream')

        @self.app.route('/status_feed')
        def status_feed():
            return Response(self.generate_status_data(), mimetype='text/event-stream')

        @self.app.route('/path_feed')
        def path_feed():
            return Response(self.generate_path_data(), mimetype='text/event-stream')

        @self.app.route('/command/<cmd>', methods=['POST'])
        def command(cmd):
            self.main_app.command = cmd
            return jsonify({'status': 'success', 'command': cmd})

    def generate_frames(self):
        while True:
            image = self.main_app.hardware.read_image()
            if image is not None:
                ret, buffer = cv2.imencode('.jpg', image)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def generate_lidar_data(self):
        while True:
            distances, angles = self.main_app.hardware.read_lidar_data()
            if distances is not None and angles is not None:
                data = {'distances': distances.tolist(), 'angles': angles.tolist()}
                yield f"data: {json.dumps(data)}\n\n"

    def generate_status_data(self):
        while True:
            data = {'state': self.main_app.agent.state}
            yield f"data: {json.dumps(data)}\n\n"

    def generate_path_data(self):
        while True:
            if self.main_app.agent.path:
                data = {'grid': self.main_app.grid, 'path': self.main_app.agent.path}
                yield f"data: {json.dumps(data)}\n\n"

    def run(self):
        self.app.run(host='0.0.0.0', port=5000)
