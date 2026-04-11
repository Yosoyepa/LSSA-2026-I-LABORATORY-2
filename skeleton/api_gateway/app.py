from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

ROUTES = {
    '/passengers': 'http://passengers_ms:80',
    '/routes': 'http://routes_ms:80',
    '/trains': 'http://trains_ms:80',
    '/position': 'http://position_time_ms:80',
    '/tickets': 'http://tickets_ms:80',
    '/authority': 'http://mas:80',
    '/alerts': 'http://alerts_ms:80',
    '/scheduling': 'http://scheduling_ms:80',
}

@app.route('/health')
def health():
    return jsonify(status='ok', service='api_gateway')

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def gateway(path):
    for prefix, target in ROUTES.items():
        if ('/' + path).startswith(prefix):
            sub_path = ('/' + path)[len(prefix):]
            url = target + (sub_path if sub_path else prefix)
            try:
                resp = requests.request(
                    method=request.method,
                    url=url,
                    json=request.get_json(silent=True)
                )
                return jsonify(resp.json()), resp.status_code
            except requests.exceptions.RequestException as e:
                return jsonify(error=str(e)), 502
    return jsonify(error='Route not found'), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
