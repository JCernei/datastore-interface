from flask import Flask, request, Response
import json

server1 = Flask('server1')
container = {}


@server1.get('/<id>')
def retrieve(id):
    if id not in container:
        return Response(status=404)
    return container[id]


@server1.post('/')
def create():
    content = request.json

    if content['id'] in container:
        return Response(status=409)

    container[content['id']] = content
    return container[content['id']]


@server1.put('/<id>')
def update(id):
    content = request.json
    container[id] = content
    return container[id]


@server1.delete('/<id>')
def delte(id):
    content = container[id]
    del container[id]
    return content
