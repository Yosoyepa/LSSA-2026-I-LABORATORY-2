import time, random

def read_sensors():
    return {
        'speed_kmh': round(random.uniform(0, 300), 1),
        'position': f'{random.uniform(40, 55):.4f}, {random.uniform(-5, 25):.4f}'
    }

def send_to_ground(data):
    print(f'[OBU onboard_unit] Sending to ground control: {data}', flush=True)

def apply_brake(intensity):
    print(f'[OBU onboard_unit] Applying brake at intensity {intensity}', flush=True)

if __name__ == '__main__':
    while True:
        data = read_sensors()
        send_to_ground(data)
        time.sleep(2)
