from flask import Flask, request, jsonify
import requests
import itertools

app = Flask(__name__)

BACKENDS = [
    'http://passengers_ms:80',
    'http://routes_ms:80',
    'http://trains_ms:80',
]

_pool = itertools.cycle(BACKENDS)

@app.route('/health')
def health():
    return jsonify(status='ok', service='load_balancer')

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def balance(path):
    target = next(_pool)
    url = target + '/' + path
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            json=request.get_json(silent=True)
        )
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify(error=str(e)), 502

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
