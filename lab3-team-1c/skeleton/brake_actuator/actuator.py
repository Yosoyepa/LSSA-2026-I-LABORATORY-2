def execute(command):
    action = command.get('action')
    intensity = command.get('intensity', 1.0)
    if action == 'BRAKE':
        print(f'[ACTUATOR brake_actuator] Emergency brake intensity {intensity}', flush=True)

if __name__ == '__main__':
    execute({'action': 'BRAKE', 'intensity': 0.8})
