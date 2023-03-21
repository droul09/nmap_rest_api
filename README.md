# nmap_rest_api
NMAP Rest API service

## Description:
This NMAP Rest API is a stateless service intended to provide basic functionailty around the NMAP (Network Map) utility commonly used for network discovery and security audtiting. This service has 3 main functions or calls:
- /scan, HTTP Method = POST
- /get_scans, HTTP Method = GET
- /get_changes, HTTP Method = GET

These 3 functions were created based off the following requirements:
- Initiating a scan of an IP address or hostname
- Retrieving results of recent scans against an IP address or hostname
- Retrieving changes between scans - for example, if port 80 is open on the most recent
scan and was not previously, that should be called out in the response
- Returning an error when a request is made for an invalid IP address or hostname
- Project will use the NMAP command line tool
- Ability to input multiple IP addresses or hosts and the scans of those IP addresses/hosts
are done in parallel
- All responses should be returned as JSON
- Port scan history must be stored and displayed via a backend datastore of your choice

## Architecture
This API service was created using Python3 + Flask to create the core funcationality and is supported by a MongoDB database backend (NoSQL).
The API service has been containerized via Docker and the MongoDB database is also being run as an open-source Docker container.
These containers are orchestrated via a local single-node Kubernetes (v1.25.4) cluster run via Docker Desktop.

The Kubernetes cluster components consists of:
- nmap-api-svc - external load balancer to the nmap-api pods, handles and distributes incoming requests to nmap-api pods
- nmap-api (deployment) - handles the deployment of the nmap-api service, to include replicas and container images
- mongo-svc - internal load balancer to distribute traffic from nmap-api pods to the backend MongoDB database
- monogo (deployment) - handles the deployment of the MongoDB database
- monogo-volume - the persistant volume that stores the MongoDB data

<img src="https://user-images.githubusercontent.com/126095600/226509984-e1dee4a3-ec9f-41cd-85af-1475b48b4178.png" width="700">


### System Pre-reqs
- python3
- Docker w/cli, preferable via Docker Desktop
- kubectl (kuberenetes cli)
- kubernetes cluster (via Docker Desktop, MiniKube, etc.)

For Docker Desktop you can enable a local, single-node cluster by going into Settings > Kubernetes and checking enable
<img src="https://user-images.githubusercontent.com/126095600/226502450-202fb113-89c6-4cbe-9485-9ca75568bdc0.png" width="700">

### Setup 
1. Clone the repository locally (git clone)
2. Navigate to the nmap_api directory
3. Run `docker build -t nmap_api-python:1.0.0 .`
4. 







