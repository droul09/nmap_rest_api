#!/usr/bin/env python3

from nmap import PortScanner
from flask import Flask, request
from pymongo import MongoClient

# https://xael.org/pages/python-nmap-en.html

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client['nmap_scans']
collection = db['scans']

@app.route('/scan', methods=['POST'])
def nmap_scan(host):
    ''' Initiate a scan of an IP address or hostname, can be multiple'''
    #hosts = request.json['hosts']
    nm = PortScanner()
    r = nm.scan(host, arguments='-T4')
    #print(r)
    response = {}
    for host in r['scan'].items():
        response["host"] = host[1]['hostnames'][0]['name']
        response["ip"] = host[0]
        response["status"] = host[1]['status']['state'] 
        for port in host[1]['tcp'].items():
            response["port"] = {port[0]:port[1]['state']}
    print(response)



    
    #print(nm.csv())
    # write the scan result to the MongoDB instance
    #collection.insert_one(result)
    return 'Scan results saved to the database'

@app.route('/get_scans', methods=['GET'])
def get_scan():
    ''' Makes a call to the MongoDB database to retrieve the latest scans'''
    results = []
    for scan in collection.find():
        results.append(scan)
    return str(results)

@app.route('/get_changes', methods=['GET'])
def get_scan_changes():
    ''' Makes a call to the MongoDB database to retrieve the last two scans
    and does a difference operation to find deltas'''
    results = []
    scans = list(collection.find().sort("_id", -1).limit(2))
    if len(scans) == 2:
        delta = set(scans[1]['scan']) - set(scans[0]['scan'])
        results.append({'delta': list(delta)})
    return str(results)

if __name__ == '__main__':
    nmap_scan('scanme.nmap.org')
    #app.run(debug=True)
