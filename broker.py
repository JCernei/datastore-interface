from flask import Flask, request, Response, redirect
from requests.exceptions import ConnectionError
import requests
import sys
import random
import os

leader = 'http://server1:8080'

leader_status = {'http://server1:8080': True,
                 'http://server2:8081': False,
                 'http://server3:8082': False}


def change_leader():
    global leader, leader_status
    for server in leader_status:
        if server == leader:
            continue
        try:
            response = requests.get(f'{server}/status')
            if response.status_code == 200:
                leader_status[leader] = False
                leader_status[server] = True
                leader = server
                requests.post(f'{leader}/leader')
                break
        except ConnectionError:
            pass


broker = Flask('broker')


@broker.get('/<id>')
def get(id):
    try:
        response = requests.get(f'{leader}/{id}')
        return response.json()
    except ConnectionError:
        change_leader()
        response = requests.get(f'{leader}/{id}')
        return response.json()


@broker.post('/')
def post():
    content = request.json
    try:
        response = requests.post(leader, json=content)
        return response.json()
    except ConnectionError:
        change_leader()
        response = requests.post(leader, json=content)
        return response.json()


@broker.put('/<id>')
def put(id):
    content = request.json
    try:
        response = requests.put(f'{leader}/{id}', json=content)
        return response.json()
    except ConnectionError:
        change_leader()
        response = requests.put(f'{leader}/{id}', json=content)
        return response.json()


@broker.delete('/<id>')
def delete(id):
    try:
        response = requests.delete(f'{leader}/{id}')
        return response.json()
    except ConnectionError:
        change_leader()
        response = requests.delete(f'{leader}/{id}')
        return response.json()


if __name__ == '__main__':
    PORT = os.environ.get('PORT')
    broker.run(host='0.0.0.0', port=PORT)
