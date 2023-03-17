#!/usr/bin/env python3

from nmap import PortScanner
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
import socket

# https://xael.org/pages/python-nmap-en.html
# https://nmap.org/book/man-port-specification.html

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo:27017/dev"
mongo = PyMongo(app)
db = mongo.db

@app.route("/")
def index():
    hostname = socket.gethostname()
    return jsonify(
        message="Welcome to the NMAP API app service!\
        This service is intended to scan, process, and store nmap results.\
        I am running inside {} pod!".format(hostname)
    )

@app.route('/scan', methods=['POST'])
def nmap_scan():
    ''' Initiate a scan of an IP address or hostname, can be multiple'''
    host = request.form['host']
    nm = PortScanner()
    data = nm.scan(host, arguments='-T4')

    aggregate = {"hosts": []}
    for host in data['scan'].items():
        response = {}
        response["host"] = host[1]['hostnames'][0]['name']
        response["ip"] = host[0]
        response["status"] = host[1]['status']['state'] 
        response["protocol"] = list(host[1].keys())[-1]
        for port in host[1]['tcp'].items():
            if response.get("ports"):
                response["ports"] += [{str(port[0]):port[1]['state']}]
            else:
                response["ports"] = [{str(port[0]):port[1]['state']}]
        aggregate['hosts'].append(response)
        db.nmap_scan_results.insert_one(response)

    aggregate['scanstats'] = data['nmap']['scanstats']

    

    return jsonify(aggregate)

@app.route('/get_scans', methods=['GET'])
def get_scan():
    ''' Makes a call to the MongoDB database to retrieve the latest scans '''
    return True
    

@app.route('/get_changes', methods=['GET'])
def get_scan_changes():
    ''' Makes a call to the MongoDB database to retrieve the last two scans
    and does a difference operation to find deltas'''
    return True
    

if __name__ == '__main__':
    #nmap_scan('scanme.nmap.org 127.0.0.1 8.8.8.8')
    app.run(host='0.0.0.0', port=5000, debug=True)
