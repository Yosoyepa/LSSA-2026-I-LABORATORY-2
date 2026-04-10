import os
import textwrap

# --- T1 Presentation ---

def generate_web_interface(name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'index.html'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            <!DOCTYPE html>
            <html>
            <head><title>{name} Passenger Portal</title></head>
            <body>
            <h1>ERTMS Passenger Portal</h1>
            <p>Component: {name}</p>
            </body>
            </html>
            """))
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""\
            FROM nginx:alpine
            COPY index.html /usr/share/nginx/html/index.html
            """))

def generate_operator_ui(name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'dashboard.html'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            <!DOCTYPE html>
            <html>
            <head><title>{name} Operator Dashboard</title></head>
            <body>
            <h1>ERTMS Operator Dashboard</h1>
            <p>Component: {name}</p>
            <p>Status: Monitoring active routes...</p>
            </body>
            </html>
            """))
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""\
            FROM nginx:alpine
            COPY dashboard.html /usr/share/nginx/html/index.html
            """))

def generate_driver_ui(name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'driver.html'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            <!DOCTYPE html>
            <html>
            <head><title>{name} Driver Interface</title></head>
            <body>
            <h1>ERTMS Driver Interface</h1>
            <p>Component: {name}</p>
            <p>Movement Authority: PENDING</p>
            </body>
            </html>
            """))
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""\
            FROM nginx:alpine
            COPY driver.html /usr/share/nginx/html/index.html
            """))

# --- T2 Communication ---

def generate_api_gateway(name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'app.py'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            from flask import Flask, request, jsonify
            import requests

            app = Flask(__name__)

            ROUTES = {{
                '/passengers': 'http://passengers_ms:80',
                '/routes': 'http://routes_ms:80',
                '/trains': 'http://trains_ms:80',
                '/position': 'http://position_time_ms:80',
                '/tickets': 'http://tickets_ms:80',
                '/authority': 'http://mas:80',
            }}

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
            """))
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""\
            FROM python:3.11-slim
            WORKDIR /app
            COPY . .
            RUN pip install flask requests
            CMD ["python", "app.py"]
            """))

# --- T3 Logic ---

def generate_microservice(name, database=None):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    db_host = database if database else f'{name}_db'
    with open(os.path.join(path, 'app.py'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            from flask import Flask, jsonify, request
            import mysql.connector

            app = Flask(__name__)

            def get_conn():
                return mysql.connector.connect(
                    host='{db_host}',
                    user='root',
                    password='root',
                    database='{db_host}'
                )

            @app.route('/health')
            def health():
                return jsonify(status='ok', service='{name}')

            @app.route('/records')
            def get_records():
                try:
                    conn = get_conn()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM records")
                    rows = cursor.fetchall()
                    cursor.close()
                    conn.close()
                    return jsonify(records=rows)
                except Exception as e:
                    return jsonify(error=str(e)), 500

            @app.route('/records', methods=['POST'])
            def create_record():
                try:
                    data = request.json or {{}}
                    conn = get_conn()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO records (name) VALUES (%s)",
                        (data.get('name', 'unknown'),)
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return jsonify(status='created'), 201
                except Exception as e:
                    return jsonify(error=str(e)), 500

            if __name__ == '__main__':
                app.run(host='0.0.0.0', port=80)
            """))
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""\
            FROM python:3.11-slim
            WORKDIR /app
            COPY . .
            RUN pip install flask mysql-connector-python
            CMD ["python", "app.py"]
            """))

def generate_authority_service(name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'app.py'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            from flask import Flask, jsonify, request

            app = Flask(__name__)

            @app.route('/health')
            def health():
                return jsonify(status='ok', service='{name}')

            @app.route('/authority', methods=['POST'])
            def request_authority():
                data = request.json or {{}}
                train_id = data.get('train_id')
                corridor = data.get('corridor')
                granted = True
                return jsonify(
                    train_id=train_id,
                    corridor=corridor,
                    movement_authority='GRANTED' if granted else 'DENIED'
                )

            if __name__ == '__main__':
                app.run(host='0.0.0.0', port=80)
            """))
    with open(os.path.join(path, 'Dockerfile'), 'w') as f:
        f.write(textwrap.dedent("""\
            FROM python:3.11-slim
            WORKDIR /app
            COPY . .
            RUN pip install flask
            CMD ["python", "app.py"]
            """))

# --- T4 Data ---

def generate_database(name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'init.sql'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            CREATE DATABASE IF NOT EXISTS {name};
            USE {name};
            CREATE TABLE IF NOT EXISTS records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            );
            INSERT INTO records (name) VALUES ('System_Init_Record');
            """))

def generate_data_lake(name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'README.md'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            # {name}
            ERTMS Data Lake
            Aggregated operational and historical data lake.
            """))
    with open(os.path.join(path, 'ingest.py'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            import json, datetime

            def ingest(event: dict):
                record = {{
                    'timestamp': datetime.datetime.utcnow().isoformat(),
                    'payload': event
                }}
                print(json.dumps(record), flush=True)

            if __name__ == '__main__':
                ingest({{'train_id': 'T-001', 'position': '48.8566,2.3522', 'speed_kmh': 220}})
            """))

# --- T5 Physical ---

def generate_onboard_unit(name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'obu.py'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            import time, random

            def read_sensors():
                return {{
                    'speed_kmh': round(random.uniform(0, 300), 1),
                    'position': f'{{random.uniform(40, 55):.4f}}, {{random.uniform(-5, 25):.4f}}'
                }}

            def send_to_ground(data):
                print(f'[OBU {name}] Sending to ground control: {{data}}', flush=True)

            def apply_brake(intensity):
                print(f'[OBU {name}] Applying brake at intensity {{intensity}}', flush=True)

            if __name__ == '__main__':
                while True:
                    data = read_sensors()
                    send_to_ground(data)
                    time.sleep(2)
            """))

def generate_sensor(name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'sensor.py'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            import time, random

            def read():
                return {{
                    'speed_kmh': round(random.uniform(0, 300), 1),
                    'door_closed': random.choice([True, True, False]),
                    'pantograph': 'UP'
                }}

            if __name__ == '__main__':
                while True:
                    print(f'[SENSOR {name}] {{read()}}', flush=True)
                    time.sleep(1)
            """))

def generate_actuator(name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'actuator.py'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            def execute(command):
                action = command.get('action')
                intensity = command.get('intensity', 1.0)
                if action == 'BRAKE':
                    print(f'[ACTUATOR {name}] Emergency brake intensity {{intensity}}', flush=True)

            if __name__ == '__main__':
                execute({{'action': 'BRAKE', 'intensity': 0.8}})
            """))

def generate_balise(name):
    path = f'skeleton/{name}'
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, 'balise.py'), 'w') as f:
        f.write(textwrap.dedent(f"""\
            BALISE_ID = '{name}'
            def transmit():
                return {{'balise_id': BALISE_ID, 'track_id': 'CORRIDOR-A'}}

            if __name__ == '__main__':
                print(f'[BALISE] {{transmit()}}', flush=True)
            """))

# --- docker-compose Orchestrator ---

TIER_ORDER = {'data': 0, 'physical': 1, 'logic': 2, 'communication': 3, 'presentation': 4}

def generate_docker_compose(components):
    path = 'skeleton/'
    os.makedirs(path, exist_ok=True)
    
    sorted_items = sorted(components.items(), key=lambda kv: TIER_ORDER.get(kv[1][0], 5))
    db_names = [n for n, (t, ct) in sorted_items if ct == 'database']
    
    with open(os.path.join(path, 'docker-compose.yml'), 'w') as f:
        f.write("version: '3.8'\nservices:\n")
        
        for i, (name, (tier, ctype)) in enumerate(sorted_items):
            port = 8000 + i
            f.write(f"  {name}:\n")
            
            if ctype == 'database':
                f.write("    image: mysql:8\n")
                f.write("    environment:\n")
                f.write("      - MYSQL_ROOT_PASSWORD=root\n")
                f.write(f"      - MYSQL_DATABASE={name}\n")
                f.write("    volumes:\n")
                f.write(f"      - ./{name}/init.sql:/docker-entrypoint-initdb.d/init.sql\n")
                f.write("    ports:\n")
                # Dinámica estricta para evitar BindError en localhost
                f.write(f"      - '{3306+i}:3306'\n")
                
            elif ctype == 'data_lake':
                f.write("    image: python:3.11-slim\n")
                f.write("    volumes:\n")
                f.write(f"      - ./{name}:/app\n")
                f.write("    working_dir: /app\n")
                f.write("    command: python ingest.py\n")
                
            elif ctype in {'onboard_unit', 'sensor', 'actuator', 'balise'}:
                f.write("    image: python:3.11-slim\n")
                script = {'onboard_unit': 'obu.py', 'sensor': 'sensor.py', 'actuator': 'actuator.py', 'balise': 'balise.py'}[ctype]
                f.write("    volumes:\n")
                f.write(f"      - ./{name}:/app\n")
                f.write("    working_dir: /app\n")
                f.write(f"    command: python {script}\n")
                
            else:
                f.write(f"    build: ./{name}\n")
                f.write("    ports:\n")
                f.write(f"      - '{port}:80'\n")
                
                if ctype == 'microservice' and db_names:
                    matched_db = None
                    for db in db_names:
                        if db.replace('_db', '') in name:
                            matched_db = db
                            break
                    if matched_db:
                        f.write("    depends_on:\n")
                        f.write(f"      - {matched_db}\n")
                            
        f.write("\nnetworks:\n  default:\n    driver: bridge\n")

# --- Dispatcher MDE ---

GENERATORS = {
    'web_interface': generate_web_interface, 'operator_ui': generate_operator_ui,
    'driver_ui': generate_driver_ui, 'api_gateway': generate_api_gateway,
    'microservice': generate_microservice, 'authority_service': generate_authority_service,
    'database': generate_database, 'data_lake': generate_data_lake,
    'onboard_unit': generate_onboard_unit, 'sensor': generate_sensor,
    'actuator': generate_actuator, 'balise': generate_balise,
}

def apply_transformations(model):
    components = {}
    db_map = {}

    for e in model.elements:
        if e.__class__.__name__ == 'Component':
            components[e.name] = (e.tier, e.type)

    db_names = [n for n, (t, ct) in components.items() if ct == 'database']
    for name, (tier, ctype) in components.items():
        if ctype == 'microservice':
            for db in db_names:
                if db.replace('_db', '') in name:
                    db_map[name] = db
                    break

    for name, (tier, ctype) in components.items():
        gen = GENERATORS.get(ctype)
        if gen:
            if ctype == 'microservice':
                gen(name, database=db_map.get(name))
            else:
                gen(name)
                
    generate_docker_compose(components)