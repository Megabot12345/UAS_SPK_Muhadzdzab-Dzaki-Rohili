USER = 'postgres'
PASSWORD = 'admin'
HOST = 'localhost'
PORT = '5432'
DATABASE_NAME = 'laptop'

DEV_SCALE = {
    'ram': {
        '16GB': 5,
        '12GB': 3,
        '8GB': 1,
    },
    'cpu': {
        'Intel Core i9 Gen12': 5,
        'Intel Core i7 Gen12': 4,
        'Intel Core i5 Gen12': 3,
        'AMD Ryzen 7': 2,
        'AMD Ryzen 5': 1,
        
    },
    'gpu': {
        'NVIDIA GeForce RTX 3080': 5,
        'NVIDIA GeForce RTX 3070': 4,
        'NVIDIA GeForce RTX 3060': 3,
        'NVIDIA GeForce RTX 3050': 2,
    },
    'battery': {
        '>= 75Whr': 5,
        '50Whr-74Whr': 3,
        '<= 49Whr': 1,
    },
    'harga': {
        '<= 10.999.999': 5,
        '11.000.000 - 14.999.999': 3,
        '>= 15.000.000': 1,
    },
    'ukuran_layar': {
        '>= 17 inci': 5,
        '14 inci - 16 inci': 3,
        '<= 13 inci': 1,
    },
}