from flask import Flask, request, Response
import requests
import sys
import random

PORT = None
servers = ['http://server1:8080', 'http://server2:8081', 'http://server3:8082']
LEADER = False
container = {}

cluster_server = Flask('cluster_server')


def get_on_server(id):
    for server in servers:
        if server.endswith('8080'):
            data = get_local(id)
        else:
            r = requests.get(f'{server}/{id}')
            if r.status_code == '200':
                return r.json()
    return data


def get_local(id):
    if id not in container:
        return Response(status=404)
    return container[id]


@cluster_server.get('/<id>')
def get(id):
    if LEADER:
        return get_on_server(id)
    else:
        return get_local(id)


def post_on_server(content):
    for server in random.sample(servers, len(servers)//2+1):
        if server.endswith('8080'):
            data = post_local(content)
        else:
            r = requests.post(server, json=content)
            data = r.json()
    return data


def post_local(content):
    container[content['id']] = content
    return container[content['id']]


def check_if_eists(content):
    id = content['id']

    if content['id'] in container:
        return True
    for server in servers:
        if server.endswith('8080'):
            continue
        r = requests.get(f'{server}/{id}')
        if r.status_code == '200':
            return True
    return False


@cluster_server.post('/')
def post():
    content = request.json

    if LEADER:
        if check_if_eists(content):
            return Response(status=409)

        return post_on_server(content)
    else:
        return post_local(content)


def put_on_server(id, content):
    for server in servers:
        if server.endswith('8080'):
            data = put_local(id, content)
        else:
            r = requests.put(f'{server}/{id}', json=content)
            if r.status_code == '200':
                data = r.json()
    return data


def put_local(id, content):
    if id not in container:
        return Response(status=404)

    container[id] = content
    return container[id]


@cluster_server.put('/<id>')
def put(id):
    content = request.json
    if LEADER:
        return put_on_server(id, content)
    else:
        return put_local(id, content)


def delete_on_server(id):
    for server in servers:
        if server.endswith('8080'):
            data = delete_local(id)
        else:
            r = requests.delete(f'{server}/{id}')
            if r.status_code == '200':
                data = r.json()
    return data


def delete_local(id):
    if id not in container:
        return Response(status=404)
    content = container[id]
    del container[id]
    return content


@cluster_server.delete('/<id>')
def delte(id):
    if LEADER:
        return delete_on_server(id)
    else:
        return delete_local(id)


if __name__ == '__main__':
    PORT = sys.argv[1]
    if PORT == '8080':
        LEADER = True

    cluster_server.run(host='0.0.0.0', port=PORT, debug=True)
