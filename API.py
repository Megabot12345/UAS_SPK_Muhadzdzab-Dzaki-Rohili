from http import HTTPStatus

from flask import Flask, request, abort
from flask_restful import Resource, Api 

from models import Movie as MovieModel

app = Flask(__name__)
api = Api(app)        

from flask_restful import Resource, abort, request
from http import HTTPStatus

class Laptop(Resource):
    def get_paginated_result(self, url, data, args):
        page_size = int(args.get('page_size', 10))
        page = int(args.get('page', 1))
        page_count = int((len(data) + page_size - 1) / page_size)
        start = (page - 1) * page_size
        end = min(start + page_size, len(data))

        if page < page_count:
            next_page = f'{url}?page={page + 1}&page_size={page_size}'
        else:
            next_page = None
        if page > 1:
            prev_page = f'{url}?page={page - 1}&page_size={page_size}'
        else:
            prev_page = None

        if page > page_count or page < 1:
            abort(404, description=f'Halaman {page} tidak ditemukan.')

        return {
            'page': page,
            'page_size': page_size,
            'next': next_page,
            'prev': prev_page,
            'Results': data[start:end]
        }

    def calculate_wp(self, row, weights):
        score = 1
        for key in weights.keys():
            score *= float(row[key]) ** weights[key]
        return score

    def calculate_saw(self, row, weights):
        score = 0
        for key in weights.keys():
            score += float(row[key]) * weights[key]
        return score

    def get(self):
        # Assuming you have a method to retrieve laptop data, replace it accordingly
        laptop_model = LaptopModel()
        laptops = laptop_model.get_laptops()

        weights = {
            'ram': 0.1,
            'cpu': 0.15,
            'gpu': 0.2,
            'battery': 0.15,
            'harga': 0.2,
            'ukuran_layar': 0.2
        }

        # Calculate scores using WP or SAW
        for laptop in laptops:
            laptop['wp_score'] = self.calculate_wp(laptop, weights)
            laptop['saw_score'] = self.calculate_saw(laptop, weights)

        # Sort the laptops based on the calculated scores
        sorted_laptops_wp = sorted(laptops, key=lambda x: x['wp_score'], reverse=True)
        sorted_laptops_saw = sorted(laptops, key=lambda x: x['saw_score'], reverse=True)

        return {
            'wp_results': self.get_paginated_result('laptops/', sorted_laptops_wp, request.args),
            'saw_results': self.get_paginated_result('laptops/', sorted_laptops_saw, request.args)
        }, HTTPStatus.OK.value

class Movie(Resource):

    def get_paginated_result(self, url, list, args):
        page_size = int(args.get('page_size', 10))
        page = int(args.get('page', 1))
        page_count = int((len(list) + page_size - 1) / page_size)
        start = (page - 1) * page_size
        end = min(start + page_size, len(list))

        if page<page_count:
            next = f'{url}?page={page+1}&page_size={page_size}'
        else:
            next=None
        if page>1:
            prev = f'{url}?page={page-1}&page_size={page_size}'
        else:
            prev = None
        
        if page > page_count or page < 1:
            abort(404, description = f'Halaman {page} tidak ditemukan.') 
        return  {
            'page': page, 
            'page_size': page_size,
            'next': next, 
            'prev': prev,
            'Results': list[start:end]
        }

    def get(self):
        movie = MovieModel()
        return self.get_paginated_result('movies/', movie.film_data, request.args), HTTPStatus.OK.value



class Recommendation(Resource):

    def post(self):
        data = request.get_json()
        movie_id = data.get('movie_id')
        length = data.get('length', 10)
        movie = MovieModel()
        
        if not movie_id:
            return 'movie_id is empty', HTTPStatus.BAD_REQUEST.value
        
        if not movie.film_data_dict.get(movie_id):
            return 'movie_id is not found', HTTPStatus.NOT_FOUND.value

        
        recommendations = movie.get_recs(movie_id, int(length))
        results = [{'movie_id': int(rec[0]),'movie_title': movie.film_data_dict[int(rec[0])], 'score': round(rec[1] * 100, 2)} for rec in recommendations]

        return {
            'movie_id': int(movie_id),
            'movie_title': movie.film_data_dict[movie_id],
            'recommendations': results
        }, HTTPStatus.OK.value


api.add_resource(Movie, '/movies')
api.add_resource(Recommendation, '/recommendation')
api.add_resource(Laptop, '/laptops')

if __name__ == '__main__':
    app.run(port='5005', debug=True)