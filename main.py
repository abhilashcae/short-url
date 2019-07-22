import base64
import os
from subprocess import Popen, STDOUT, DEVNULL
from urllib.parse import urlparse

from flask import Flask, request, render_template, redirect
from nanoid import generate
from pymongo import MongoClient


class Mongo:
    def __init__(self):
        self.mongo_url = 'mongodb+srv://difficultname:kr699icbTFnM8X6N@cluster0-3dtvi.mongodb.net/test?retryWrites=true&w=majority'#os.environ['MONGODB_URI']  # 'mongodb://localhost:27017/short_url_db' if using locally
        self.client = MongoClient(self.mongo_url)
        self.db = self.client.short_url_db
        self.urls_collection = self.db.urls

    def run_mongo_daemon(self):
        """
        Needed only if you're running Mongo locally!
        :return:
        """
        command = ['mongod']
        mongod = Popen(command, stderr=STDOUT, stdout=DEVNULL)
        return mongod

    def insert_url(self, url):
        body = {
            'url': base64.urlsafe_b64encode(url.encode()),
            'nano_id': generate(size=5)
        }
        obj_id = self.urls_collection.insert_one(body).inserted_id
        nano_id = self.urls_collection.find_one({'_id': obj_id})
        return nano_id['nano_id']

    def find_url(self, nano_id):
        doc = self.urls_collection.find_one({'nano_id': nano_id})
        url = doc['url']
        return base64.urlsafe_b64decode(url)


class Helpers:
    def base64_encode(self, string):
        return base64.b64encode(string)

    def base64_decode(self, encoded_string):
        return base64.b64decode(encoded_string)


mongo = Mongo()
helpers = Helpers()

app = Flask('sm-url')


@app.route('/', methods=['POST', 'GET'])
def insert_url():
    url = request.form.get('url')
    if urlparse(url).scheme == '':
        url = 'http://{}'.format(url)
    if request.method == 'POST':
        nano_id = mongo.insert_url(url)
        return render_template('index.html', short_url=request.url_root + nano_id)
    return render_template('index.html')


@app.route('/<short_url>')
def get_url(short_url):
    original_url = mongo.find_url(short_url)
    return redirect(original_url)


if __name__ == '__main__':
    """
    If you're running Mongo locally:
    mongod = mongo.run_mongo_daemon()
    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        mongod.terminate()
    else:
        mongod.terminate()
    """
    app.run(debug=True)
