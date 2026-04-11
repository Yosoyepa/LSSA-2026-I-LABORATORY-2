from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)
channels = defaultdict(list)

@app.route('/health')
def health():
    return jsonify(status='ok', service='message_broker')

@app.route('/publish', methods=['POST'])
def publish():
    data = request.json or {}
    channel = data.get('channel', 'default')
    payload = data.get('payload', {})
    channels[channel].append(payload)
    return jsonify(status='published', channel=channel), 201

@app.route('/subscribe/<channel>', methods=['GET'])
def subscribe(channel):
    msgs = channels.get(channel, [])
    return jsonify(channel=channel, messages=msgs)

@app.route('/channels', methods=['GET'])
def list_channels():
    return jsonify(channels=list(channels.keys()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
