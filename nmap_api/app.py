#!/usr/bin/env python3

from nmap import PortScanner
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from socket import getaddrinfo, gethostname, gaierror
import logging
import re

'''
Author: David Rouleau
Last Updated: March 20th, 2023

Description: The purpose of this API is to enable the ability to scan, process, and store
the output of an NMAP scan against a host(s) (hostname or IP address.)
'''

logging.basicConfig(filename='app.log', level=logging.DEBUG)

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo:27017/nmap"
mongo = PyMongo(app)
db = mongo.db

def check_host(host):
    ''' Input validation on the hostname or ip address using socket '''
    try:
        getaddrinfo(host, None)
        return True
    except gaierror:
        return False
    
def is_ip(host):
    ''' Checks to see if the provided host is an IP address or not using regex'''
    if re.match("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", host):
        item = "ip"
    else:
        item = "host"
    return item

@app.route("/")
def index():
    ''' Basic landing page for the nmap service'''
    hostname = gethostname()
    return jsonify(
        message="Welcome to the NMAP API app service! This service is intended to scan, process, and store nmap results. I am running inside {} pod!".format(hostname)
    )

@app.route('/scan', methods=['POST'])
def nmap_scan():
    ''' Initiate a scan of an IP address or hostname, can be multiple'''
    
    host = request.form['host']

    for item in host.split():
        if not check_host(item):
            logging.error("Invalid host or IP addess: {}".format(item))
            return jsonify({'error': 'Invalid host or IP address'}), 400

    nm = PortScanner()
    data = nm.scan(host, arguments='-T4')

    aggr_response = {"hosts": []}
    for host in data['scan'].items():
        host_response = {}
        host_response["host"] = host[1]['hostnames'][0]['name']
        host_response["ip"] = host[0]
        host_response["status"] = host[1]['status']['state'] 
        host_response["protocol"] = list(host[1].keys())[-1]
        for port in host[1]['tcp'].items():
            if host_response.get("ports"):
                host_response["ports"] += [{str(port[0]):port[1]['state']}]
            else:
                host_response["ports"] = [{str(port[0]):port[1]['state']}]
        host_response["timestamp"] = data['nmap']['scanstats']['timestr']
        aggr_response['hosts'].append(host_response)
        
        try:
            dbcall = db.nmap_scan_results.insert_one(host_response)
            logging.info("Scan results inserted into MongoDB dev db with object ID: {}".format(dbcall.inserted_id))
        except Exception as e:
            logging.error("Error inserting scan results into MongoDB dev: {}".format(e))
        
        # It is necessary to del the ['_id'] key in the response as this key/value pair gets
        # appended as a result of the MongoDB call
        # {'host': 'scanme.nmap.org', 'ip': '45.33.32.156', 'status': 'up', 'protocol': 'tcp', 'ports': 
        # [{'22': 'open'}, {'25': 'filtered'}, {'80': 'open'}, {'135': 'filtered'}, {'139': 'filtered'}, 
        # {'445': 'filtered'}, {'9929': 'open'}, {'31337': 'open'}], '_id': ObjectId('641858b025e0632bfbdd5618')}
        del host_response['_id']
        
    aggr_response['scanstats'] = data['nmap']['scanstats']
    logging.debug("Scan results: {}".format(aggr_response))

    #return jsonify(aggr_response)
    return aggr_response

@app.route('/get_scans', methods=['GET'])
def get_scans():
    ''' Makes a call to the MongoDB database to retrieve scans for a single host '''
    # curl http://localhost:5000/get_scans?host=<host_or_ip_address>
    host = request.args.get('host')
    if not check_host(host):
        logging.error("Invalid host or IP addess: {}".format(host))
        return jsonify({"error": "Invalid host or IP address."}), 400
    
    try:
        scans = request.args.get('scans')
        if not scans:
            scans = 5
        scans = int(scans)
    except ValueError as e:
        logging.error("Scans argument must be an integer")
        return jsonify({"error": "Scans argument must be an integer."}), 400
    
    #scan_results = db.nmap_scan_results.find_one({"{}".format(item): host}, sort=[('timestamp', -1)], projection={'_id': False})
    scan_results = list(db.nmap_scan_results.find({"{}".format(is_ip(host)): host}, {"_id": 0}).sort("timestamp", -1).limit(scans))
    if not scan_results:
        logging.error("No scans found for host: {}".format(host))
        return jsonify({"error": "No scans found for host: {}".format(host)}), 404

    # Add logging output
    logging.info('Retrieved scan results for host: {}'.format(host))

    return jsonify(scan_results)

@app.route('/get_changes', methods=['GET'])
def get_scan_changes():
    ''' Makes a call to the MongoDB database to retrieve the last two scans for a single host
    and does a difference operation to find deltas'''
    host = request.args.get('host')
    if not check_host(host):
        logging.error("Invalid host or IP addess: {}".format(host))
        return jsonify(error="Invalid hostname or IP address"), 400
    
    if re.match("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", host):
        item = "ip"
    else:
        item = "host"

    scans = list(db.nmap_scan_results.find({"{}".format(is_ip(host)): host}, {"_id": 0}).sort("timestamp", -1).limit(2))
    if len(scans) < 2:
        return jsonify(error="Not enough scans for host"), 404

    current_scan = scans[0]
    previous_scan = scans[1]

    current_ports = {pn:state for port in current_scan["ports"] for pn, state in port.items()}
    previous_ports = {pn:state for port in previous_scan["ports"] for pn, state in port.items()}

    new_ports = {port: current_ports[port] for port in current_ports if port not in previous_ports}
    removed_ports = {port: previous_ports[port] for port in previous_ports if port not in current_ports}
    changed_ports = {port: current_ports[port] for port in current_ports if port in previous_ports and current_ports[port] != previous_ports[port]}

    result = {
        "host": host,
        "new_ports": new_ports,
        "removed_ports": removed_ports,
        "changed_ports": changed_ports,
    }

    return jsonify(result)
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
