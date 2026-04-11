BALISE_ID = 'ccs_balise_a'
def transmit():
    return {'balise_id': BALISE_ID, 'track_id': 'CORRIDOR-A'}

if __name__ == '__main__':
    print(f'[BALISE] {transmit()}', flush=True)
