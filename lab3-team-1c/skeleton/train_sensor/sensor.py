import time, random

def read():
    return {
        'speed_kmh': round(random.uniform(0, 300), 1),
        'door_closed': random.choice([True, True, False]),
        'pantograph': 'UP'
    }

if __name__ == '__main__':
    while True:
        print(f'[SENSOR train_sensor] {read()}', flush=True)
        time.sleep(1)
