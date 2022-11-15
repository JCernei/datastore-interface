from flask import Flask, request, Response
import requests
import sys

PORT = None
servers = ['8080', '8081', '8082']
LEADER = False
container = {}

cluster_server = Flask('cluster_server')


@cluster_server.get('/<id>')
def retrieve(id):
    if id not in container:
        return Response(status=404)
    if LEADER:
        for server in servers:
            if server == PORT:
                continue
            r = requests.get(f'http://127.0.0.1:{server}/{id}')
    return container[id]


@cluster_server.post('/')
def create():
    content = request.json
    if content['id'] in container:
        return Response(status=409)

    container[content['id']] = content
    if LEADER:
        for server in servers:
            if server == PORT:
                continue
            r = requests.post(f'http://127.0.0.1:{server}/', json=content)
    return container[content['id']]


@cluster_server.put('/<id>')
def update(id):
    if id not in container:
        return Response(status=404)

    content = request.json
    container[id] = content
    if LEADER:
        for server in servers:
            if server == PORT:
                continue
            r = requests.put(
                f'http://127.0.0.1:{server}/{id}', json=content)
    return container[id]


@cluster_server.delete('/<id>')
def delte(id):
    if id not in container:
        return Response(status=404)

    content = container[id]
    del container[id]
    if LEADER:
        for server in servers:
            if server == PORT:
                continue
            r = requests.delete(
                f'http://127.0.0.1:{server}/{id}')

    return content


if __name__ == '__main__':
    PORT = sys.argv[1]
    if PORT == '8080':
        LEADER = True

    cluster_server.run(host='127.0.0.1', port=PORT, debug=True)
