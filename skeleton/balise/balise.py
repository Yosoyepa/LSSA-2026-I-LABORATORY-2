BALISE_ID = 'balise'
def transmit():
    return {'balise_id': BALISE_ID, 'track_id': 'CORRIDOR-A'}

if __name__ == '__main__':
    print(f'[BALISE] {transmit()}', flush=True)
