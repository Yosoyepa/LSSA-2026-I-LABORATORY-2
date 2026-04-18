from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify(status='ok', service='gsm_r_gateway', protocol='GSM-R/Euroradio')

@app.route('/uplink', methods=['POST'])
def uplink():
    data = request.json or {}
    train_id = data.get('train_id', 'UNKNOWN')
    payload = data.get('payload', {})
    print(f'[GSM-R GW] Uplink from train {train_id}: {payload}', flush=True)
    return jsonify(status='received', train_id=train_id), 200

@app.route('/downlink', methods=['POST'])
def downlink():
    data = request.json or {}
    train_id = data.get('train_id', 'UNKNOWN')
    command = data.get('command', {})
    print(f'[GSM-R GW] Downlink to train {train_id}: {command}', flush=True)
    return jsonify(status='transmitted', train_id=train_id), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
