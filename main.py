import base64
import os
from subprocess import Popen, STDOUT, DEVNULL
from urllib.parse import urlparse

from bson import ObjectId
from pymongo import MongoClient

from flask import Flask, request, render_template, redirect


class Mongo:
    def __init__(self):
        self.mongo_url = os.environ['MONGODB_URI']  # 'mongodb://localhost:27017/short_url_db' if using locally
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

    def insert_document(self, url):
        obj_id = self.urls_collection.insert_one({'url': base64.urlsafe_b64encode(url.encode())}).inserted_id
        return str(obj_id)

    def find_document(self, object_id):
        doc = self.urls_collection.find({'_id': ObjectId(object_id)})
        url = ''
        for u in doc:
            url = u['url']
        return base64.urlsafe_b64decode(url)


class Helpers:
    def base64_encode(self, string):
        return base64.b64encode(string)

    def base64_decode(self, encoded_string):
        return base64.b64decode(encoded_string)


# mongo = Mongo()
# helpers = Helpers()

app = Flask('sm-url')


@app.route('/', methods=['POST', 'GET'])
def insert_url():
    url = request.form.get('url')
    if urlparse(url).scheme == '':
        url = 'http://{}'.format(url)
    if request.method == 'POST':
        mongo_id = mongo.insert_document(url)
        encoded_mongo_id = helpers.base64_encode(mongo_id.encode())
        return render_template('index.html', short_url=request.url_root + encoded_mongo_id.decode())
    return render_template('index.html')


@app.route('/<short_url>')
def get_url(short_url):
    decoded_mongo_id = helpers.base64_decode(short_url)
    original_url = mongo.find_document(decoded_mongo_id.decode())
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
    # app.run(debug=True)
    print(os.environ)

