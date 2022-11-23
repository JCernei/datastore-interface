from flask import Flask, request, Response
import requests
import sys
import random
import os

PORT = None
servers = ['http://server1:8080', 'http://server2:8081', 'http://server3:8082']
LEADER = False
container = {}
ID = 0
servers_alive = {'http://server1:8080': True,
                 'http://server2:8081': True,
                 'http://server3:8082': True}

cluster_server = Flask('cluster_server')


@cluster_server.post('/leader')
def post_leader():
    global LEADER
    LEADER = True
    return Response(status=200)


@cluster_server.get('/status')
def get_status():
    return Response(status=200)


def check_status():
    for server in servers:
        if server.endswith(PORT):
            continue
        else:
            try:
                r = requests.get(f'{server}/status')
            except:
                servers_alive[server] = False


def get_on_server(id):
    for server in servers:
        if server.endswith(PORT):
            data = get_local(id)
        else:
            try:
                r = requests.get(f'{server}/{id}')
                if r.status_code == 200:
                    return r.json()
            except:
                pass
    return data


def get_local(id):
    if id not in container:
        return Response(status=404)
    return container[id]


@cluster_server.get('/<id>')
def get(id):
    if LEADER:
        cluster_server.logger.info(
            f'EXTERNAL request from client to lider port:{PORT}')
        return get_on_server(id)
    else:
        cluster_server.logger.info(
            f'INTERNAL request from leader to folower port:{PORT}')
        return get_local(id)


def post_on_server(content):
    check_status()
    sum([i for _, i in servers_alive.items()])

    for server in random.sample(servers, len(servers)//2+1):
        if server.endswith(PORT):
            data = post_local(content)
        else:
            try:
                r = requests.post(server, json=content)
                data = r.json()
            except:
                pass
    return data


def post_local(content):
    container[content['id']] = content
    return container[content['id']]


def generate_id():
    global ID
    ID += 1
    return ID


@cluster_server.post('/')
def post():
    content = request.json
    if LEADER:
        cluster_server.logger.info(
            f'EXTERNAL request from client to lider port:{PORT}')

        contetn_id = {"id": f"{generate_id()}"}
        content.update(contetn_id)
        return post_on_server(content)
    else:
        cluster_server.logger.info(
            f'INTERNAL request from leader to folower port:{PORT}')
        return post_local(content)


def put_on_server(id, content):
    for server in servers:
        if server.endswith(PORT):
            data = put_local(id, content)
        else:
            try:
                r = requests.put(f'{server}/{id}', json=content)
                if r.status_code == 200:
                    data = r.json()
            except:
                pass
    return data


def put_local(id, content):
    if id not in container:
        return Response(status=404)

    container[id] = content
    return container[id]


@cluster_server.put('/<id>')
def put(id):
    content = request.json
    contetn_id = {"id": f"{id}"}
    content.update(contetn_id)
    if LEADER:
        cluster_server.logger.info(
            f'EXTERNAL request from client to lider port:{PORT}')
        return put_on_server(id, content)
    else:
        cluster_server.logger.info(
            f'INTERNAL request from leader to folower port:{PORT}')
        return put_local(id, content)


def delete_on_server(id):
    for server in servers:
        if server.endswith(PORT):
            data = delete_local(id)
        else:
            try:
                r = requests.delete(f'{server}/{id}')
                if r.status_code == 200:
                    data = r.json()
            except:
                pass
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
        cluster_server.logger.info(
            f'EXTERNAL request from client to lider port:{PORT}')
        return delete_on_server(id)
    else:
        cluster_server.logger.info(
            f'INTERNAL request from leader to folower port:{PORT}')
        return delete_local(id)


if __name__ == '__main__':
    PORT = os.environ.get('PORT')
    if PORT == '8080':
        LEADER = True

    cluster_server.run(host='0.0.0.0', port=PORT, debug=True)
