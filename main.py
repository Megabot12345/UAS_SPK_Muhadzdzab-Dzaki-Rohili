from http import HTTPStatus
from flask import Flask, request, abort
from flask_restful import Resource, Api
from models import LP as lpModel
from engine import engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from tabulate import tabulate

session = Session(engine)

app = Flask(__name__)
api = Api(app)


class BaseMethod():

    def __init__(self):
        # 1-5
        self.raw_weight = {'ram': 5, 'cpu': 5,'gpu': 5, 'battery': 4, 'harga': 5, 'ukuran_layar': 2}

    @property
    def weight(self):
        total_weight = sum(self.raw_weight.values())
        return {k: round(v/total_weight, 2) for k, v in self.raw_weight.items()}

    @property
    def data(self):
        query = select(lpModel.id, lpModel.brand, lpModel.ram, lpModel.cpu, lpModel.gpu,lpModel.battery, lpModel.harga, lpModel.ukuran_layar)
        result = session.execute(query).fetchall()
        return [{'id': LP.id, 'brand': LP.brand, 'ram': LP.ram, 'cpu': LP.cpu,
                'gpu': LP.gpu, 'battery': LP.battery, 'harga': LP.harga, 'ukuran_layar': LP.ukuran_layar} for LP in result]

    @property
    def normalized_data(self):
        ram_values = []
        cpu_values = []
        gpu_values = []
        battery_values = []
        harga_values = []
        ukuran_layar_values = []

        for data in self.data:
            # ram
            ram_spec = data['ram']
            ram_numeric_values = [
                int(value) for value in ram_spec.split() if value.isdigit()]
            max_ram_value = max(
                ram_numeric_values) if ram_numeric_values else 1
            ram_values.append(max_ram_value)
            
            # cpu
            cpu_spec = data['cpu']
            cpu_numeric_values = [int(
                value.split()[0]) for value in cpu_spec.split() if value.split()[0].isdigit()]
            max_cpu_value = max(
                cpu_numeric_values) if cpu_numeric_values else 1
            cpu_values.append(max_cpu_value)
            
            # gpu
            gpu_spec = data['gpu']
            gpu_numeric_values = [int(
                value.split()[0]) for value in gpu_spec.split() if value.split()[0].isdigit()]
            max_gpu_value = max(
                gpu_numeric_values) if gpu_numeric_values else 1
            gpu_values.append(max_gpu_value)

            # battery
            battery_spec = data['battery']
            battery_numeric_values = [int(
                value.split()[0]) for value in battery_spec.split() if value.split()[0].isdigit()]
            max_battery_value = max(
                battery_numeric_values) if battery_numeric_values else 1
            battery_values.append(max_battery_value)

            # Harga
            harga_cleaned = ''.join(
                char for char in data['harga'] if char.isdigit())
            harga_values.append(float(harga_cleaned)
                                if harga_cleaned else 0)
            
            # ukuran layar
            ukuran_layar_spec = data['ukuran_layar']
            ukuran_layar_numeric_values = [float(value.split()[0]) for value in ukuran_layar_spec.split(
            ) if value.replace('.', '').isdigit()]
            max_ukuran_layar_value = max(
                ukuran_layar_numeric_values) if ukuran_layar_numeric_values else 1
            ukuran_layar_values.append(max_ukuran_layar_value)

        return [
            {'id': data['id'],
             'ram': ram_value / max(ram_values),
             'cpu': cpu_value / max(cpu_values),
             'gpu': gpu_value / max(gpu_values),
             'battery': battery_value / max(battery_values),
             # To avoid division by zero
             'harga': min(harga_values) / max(harga_values) if max(harga_values) != 0 else 0,
             'ukuran_layar': ukuran_layar_value / max(ukuran_layar_values)
             }
            for data, ram_value, cpu_value, gpu_value,battery_value, ukuran_layar_value, harga_value
            in zip(self.data, ram_values, cpu_values, gpu_values, battery_values, ukuran_layar_values, harga_values)
        ]

    def update_weights(self, new_weights):
        self.raw_weight = new_weights

class WeightedProductCalculator(BaseMethod):
    @property
    def calculate(self):
        normalized_data = self.normalized_data
        produk = [
            {
                'id': row['id'],
                'produk': row['ram']**self.weight['ram'] *
                row['cpu']**self.weight['cpu'] *
                row['gpu']**self.weight['gpu'] *
                row['battery']**self.weight['battery'] *
                row['harga']**self.weight['harga'] *
                row['ukuran_layar']**self.weight['ukuran_layar']
            }
            for row in normalized_data
        ]
        sorted_produk = sorted(produk, key=lambda x: x['produk'], reverse=True)
        sorted_data = [
            {
                'id': product['id'],
                'score': product['produk']  # Nilai skor akhir
            }
            for product in sorted_produk
        ]
        return sorted_data

class WeightedProduct(Resource):
    def get(self):
        calculator = WeightedProductCalculator()
        result = calculator.calculate
        return sorted(result, key=lambda x: x['score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        calculator = WeightedProductCalculator()
        calculator.update_weights(new_weights)
        result = calculator.calculate
        return {'LP': sorted(result, key=lambda x: x['score'], reverse=True)}, HTTPStatus.OK.value


class SimpleAdditiveWeightingCalculator(BaseMethod):
    @property
    def calculate(self):
        weight = self.weight
        result = [
            {
                'id': row['id'],
                'Score': round(
                    row['ram'] * weight['ram'] +
                    row['cpu'] * weight['cpu'] +
                    row['gpu'] * weight['gpu'] +
                    row['battery'] * weight['battery'] +
                    row['harga'] * weight['harga'] +
                    row['ukuran_layar'] * weight['ukuran_layar'],
                    2
                )
            }
            for row in self.normalized_data
        ]
        sorted_result = sorted(result, key=lambda x: x.get('Score', 0), reverse=True)
        return sorted_result
    
    def update_weights(self, new_weights):
        self.raw_weight = new_weights


class SimpleAdditiveWeighting(Resource):
    def get(self):
        saw = SimpleAdditiveWeightingCalculator()
        result = saw.calculate
        return sorted(result, key=lambda x: x['Score'], reverse=True), HTTPStatus.OK.value

    def post(self):
        new_weights = request.get_json()
        saw = SimpleAdditiveWeightingCalculator()
        saw.update_weights(new_weights)
        result = saw.calculate
        return {'LP': sorted(result, key=lambda x: x['Score'], reverse=True)}, HTTPStatus.OK.value


class LP(Resource):
    def get_paginated_result(self, url, list, args):
        page_size = int(args.get('page_size', 10))
        page = int(args.get('page', 1))
        page_count = int((len(list) + page_size - 1) / page_size)
        start = (page - 1) * page_size
        end = min(start + page_size, len(list))

        if page < page_count:
            next_page = f'{url}?page={page+1}&page_size={page_size}'
        else:
            next_page = None
        if page > 1:
            prev_page = f'{url}?page={page-1}&page_size={page_size}'
        else:
            prev_page = None

        if page > page_count or page < 1:
            abort(404, description=f'Data Tidak Ditemukan.')
        return {
            'page': page,
            'page_size': page_size,
            'next': next_page,
            'prev': prev_page,
            'Results': list[start:end]
        }

    def get(self):
        query = session.query(lpModel).order_by(lpModel.no)
        result_set = query.all()
        data = [{'id': row.id, 'ram': row.ram, 'cpu': row.cpu, 'gpu': row.gpu,
                'battery': row.battery, 'harga': row.harga, 'ukuran_layar': row.ukuran_layar}
                for row in result_set]
        return self.get_paginated_result('xiaomi/', data, request.args), 200


api.add_resource(LP, '/LP')
api.add_resource(WeightedProduct, '/wp')
api.add_resource(SimpleAdditiveWeighting, '/saw')

if __name__ == '__main__':
    app.run(port='5005', debug=True)