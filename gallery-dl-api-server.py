from flask import Flask, request
from flask_restful import Api, Resource
import os
import subprocess

app = Flask(__name__)
api = Api(app)


class GalleryDownload(Resource):
    def post(self):
        # Parse the URL from the request data
        data = request.get_json()
        url = data.get('url')
        if not url:
            return {'message': 'URL not provided'}, 400

        # Use gallery-dl to download the gallery/album
        try:
            subprocess.run(['gallery-dl', url], check=True)
            return {'message': 'Download successful'}, 200
        except subprocess.CalledProcessError as e:
            return {'message': 'Download failed', 'error': str(e)}, 500


api.add_resource(GalleryDownload, '/download')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
