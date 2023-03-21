# nmap_rest_api
NMAP Rest API service

## Description:
This NMAP Rest API is a stateless service intended to provide basic functionailty around the NMAP (Network Map) utility commonly used for network discovery and security auditing. This service has 3 main functions or calls:
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

#### > Why Python3 + Flask for the langauge and web framework?
I really enjoy Python! But besides that, Flask is a lightweight web framework that is easy to use and configure, making it a popular choice for building REST APIs. Flask provides a simple and intuitive interface for defining routes and handling HTTP requests, which makes it easy to build a scalable and maintainable API service.

Python3 is a powerful and versatile programming language that is widely used in development. Python3 has a large and active community of developers who create libraries and frameworks that make it easy to build complex web applications. Python3 also has a rich set of standard libraries that make it easy to perform tasks like data processing, networking, and system administration.

Together, Python3 and Flask provide a powerful and flexible platform for building REST APIs. Flask's simplicity and ease of use make it easy to get started, while Python3's rich set of libraries and powerful language features make it easy to build complex and scalable applications. Additionally, Python3 and Flask have excellent documentation and community support, which can make it easier to find help and resources when building the NMAP API service.

#### > Why MonogDB for the datastore?
MongoDB is an excellent choice for storing unstructured data like NMAP scan results. MongoDB's document-based data model is ideal for storing unstructured data because it allows for flexible and dynamic schema designs. The document model allows you to store data in a hierarchy of nested documents, arrays, and values, which makes it easy to store complex and unstructured data types.

In the case of NMAP scan results, the data is generally not structured, and it can vary depending on the type of scan being performed. MongoDB allows you to store these results as documents, which can include all of the relevant information about the scan, such as the IP address, open ports, and other details. You can store this data in a single collection and retrieve it using powerful query capabilities provided by MongoDB, such as range queries, full-text search, and geospatial queries.

Additionally, MongoDB's indexing capabilities make it easy to search and retrieve data quickly, even as the amount of data stored in the database grows. MongoDB supports various types of indexes, including single field indexes, compound indexes, text indexes, and geospatial indexes. These indexes can be used to optimize query performance and improve the speed of data retrieval.

MongoDB also has built-in support for sharding and provides a powerful, flexible, and scalable way to distribute data across multiple nodes. MongoDB uses a sharding key to divide the data into ranges and then distributes the ranges across shards based on the key's value. MongoDB's sharding architecture is highly scalable and can support petabytes of data and thousands of nodes. Additionally, MongoDB provides automatic rebalancing of data across shards, making it easier to manage large, distributed databases. MongoDB makes sharding easier to manage, such as automatic balancing of data across shards and automatic failover of replica sets. MongoDB's sharding architecture is designed to support high levels of read and write throughput, making it an excellent choice for applications with high-volume workloads.

#### > Why Kubernetes for Container Orchestration?
Kubernetes is a good choice for running the NMAP service. Kubernetes is a powerful and flexible container orchestration platform that makes it easy to deploy, scale, and manage containerized applications. By running the NMAP service on Kubernetes, you can take advantage of features like load balancing, auto-scaling, and rolling updates, which can help ensure that your service is always available and responsive.

Kubernetes also provides a rich set of tools and features for managing containerized applications, including resource management, service discovery, and logging and monitoring. This can help make it easier to troubleshoot issues and ensure that your service is running smoothly.

In addition, running the NMAP service on Kubernetes allows you to easily scale the service up or down as needed to handle changes in demand. For example, if you need to handle a sudden spike in traffic, you can quickly and easily scale up the number of replicas running the NMAP service to handle the increased load.

The Kubernetes cluster components consists of:
- nmap-api-svc - external load balancer to the nmap-api pods, handles and distributes incoming requests to nmap-api pods
- nmap-api (deployment) - handles the deployment of the nmap-api service, to include replicas and container images
- mongo-svc - internal load balancer to distribute traffic from nmap-api pods to the backend MongoDB database
- monogo (deployment) - handles the deployment of the MongoDB database
- monogo-volume - the persistant volume that stores the MongoDB data

<img src="https://user-images.githubusercontent.com/126095600/226509984-e1dee4a3-ec9f-41cd-85af-1475b48b4178.png" width="700">

### Data Flow Diagram
<img src="https://user-images.githubusercontent.com/126095600/226513269-51dbcc05-04a3-4807-91e0-25c95189000b.png" width ="700">

### Scaling to handle 1M request per second
There are many factors at play when operating at large scale and building a service that can handle that scale, most often it revolves around aspects of horizontal scaling, fault tolerance / auto-healing, distributed architecture, database scaling (sharding or clustering), caching, etc.

Some aspects to make this nmap api service more capable of serving 1M requests per second:
- Load balancing: To handle such a massive load of requests, the service would need to employ a load balancer that distributes the incoming requests across multiple instances of the NMAP Rest API service running in parallel. While the current architecture does this, it can be enhanced using Kubernetes Horizontal Pod Autoscaling (HPA), which automatically scales the number of pods based on CPU utilization or other metrics.
- Caching: To reduce the response time of the API service, caching can be implemented at various levels such as client-side, CDN, and server-side caching. This reduces the time taken to generate a response and reduces the load on the backend MongoDB database. Using a distributed caching solution, such as Redis or Memcached, would enable you to cache responses across multiple servers and scale horizontally as needed.
- Database optimization: As the MongoDB database is used as the backend datastore, it needs to be optimized to handle a massive load of requests. One way to optimize it is by employing sharding, which partitions the data across multiple servers. This enables the database to handle more requests in parallel. Another aspect to think about is creating indexes on frequently accessed fields, ensuring that the database is appropriately tuned for the workload it will be handling.
- Asynchronous processing: To improve the performance of the API service, it's better to perform scans asynchronously using tools like Celery, Kafka, or RabbitMQ. This would allow multiple scans to run concurrently without blocking other requests.
- Autoscaling groups: Autoscaling groups in Kubernetes can automatically scale the number of replicas of a pod based on CPU utilization or other metrics. Using autoscaling groups would enable you to scale the service horizontally to handle a massive load of requests.

## System Pre-reqs
- python3
- Docker w/cli, preferable via Docker Desktop
- kubectl (kuberenetes cli)
- kubernetes cluster (via Docker Desktop, MiniKube, etc.)
- linux/amd64 OS platform

For Docker Desktop you can enable a local, single-node cluster by going into Settings > Kubernetes and checking enable

<img src="https://user-images.githubusercontent.com/126095600/226502450-202fb113-89c6-4cbe-9485-9ca75568bdc0.png" width="700">

### Setup
Recommended: Kubernetes deployment
1. Clone the repository locally (git clone)
2. Run `kubectl create -f k8s/compiled.yaml`
3. Wait a minute or two and then run `kubectl get pods`, you should see 4 pods ( 3 for nmap-api, 1 for mongodb)
4. Validate some other resources, `kubectl get deployments` - you should see two deployments,  `kubectl get svc` - you should see mongo and nmap-api-svc, `kubectl get pv` - you should see the mongo-pv persistant volume list as bound
5. The output of `kubectl get svc`, should have localhost under the External-IP column

Optional: If you would like to build the image locally for local testing
1. Navigate to the nmap_api directory
2. Run `docker build -t nmap_api-python:1.0.0 .`
3. Once the docker build completes, you should be able to see the nmap_api-python:1.0.0 image via `docker images`
4. `docker network create nmap_api-net` - creates a bridge network, allowing communication between nmap-api container and mongo container
5. `docker run --name=mongo --rm -d --network=nmap_api-net mongo` - run the mongo container
6. `docker run --name=nmap_api-python --rm -p 5000:5000 -d --network=nmap_api-net nmap_api-python:1.0.0` - run the nmap_api-python container, exposing port 5000

**ARM-based MAC users**:
If you are on an ARM-based MAC you will likely experience some different behavior in the nmap api service because the service was built for the linux/amd64 platform not the linux/arm64/v8 platform. However, do not fret! There is a workaround with Docker Desktop to ensure you don't miss out on the fun! You will need to change two settings:
- General > Enable `Use Virtualization framework`
- Features in development > Enable `Use Rosetta for x86/amd64 emulation on Apple Silicon`
- Restart Docker Desktop
- Reference: https://collabnix.com/warning-the-requested-images-platform-linux-amd64-does-not-match-the-detected-host-platform-linux-arm64-v8/

### Testing the Service
- See if the service is up and running correctly on localhost port 5000 (Do it a couple times to see the LoadBalancer in action)
   - `curl localhost:5000`
<img src="https://user-images.githubusercontent.com/126095600/226518880-a8d479b5-ad44-4609-9163-b9d033955e2b.png">

**/scan**
- Make some calls to scan some hosts. The more you do, the more data the MongoDB has. Format:
   - single host: `curl --data "host=localhost" http://localhost:5000/scan`
   - multi-host: `curl --data "host=localhost 8.8.8.8 scanme.nmap.org" http://localhost:5000/scan`
<img src="https://user-images.githubusercontent.com/126095600/226519892-6270c433-5b54-4a07-9872-8a2b71ad10be.png">

**/get_scans**
- Make some calls to retreive scans for a host(ip or hostname). Accepts an optional `scans` argument. Format:
   - no scan limit (default 5): `curl "http://localhost:5000/get_scans?host=scanme.nmap.org"`
   - with scan limit: `curl "http://localhost:5000/get_scans?host=scanme.nmap.org&scans=1"`
<img src="https://user-images.githubusercontent.com/126095600/226521464-4a7f7509-a139-436c-be58-39d35fa53265.png">

**/get_changes**
- Make a call to see if there are any port changes for a host(ip or hostname). Format:
   - e.g.: `curl "http://localhost:5000/get_changes?host=localhost"`
<img src="https://user-images.githubusercontent.com/126095600/226522470-73265cf3-59da-4e35-bfd4-b93579131533.png">

  Note: If you want to simulate a port change, you can do so via:
  - `docker ps` - locate and copy the container id for the nmap_api-python container
  - `docker exec -it <container id> bash` - this will put you in an interactive shell on the container
  - `ncat -l 8000` - this will tell the container to listen on port 8000
  - While port 8000 is listening, do a `curl --data "host=localhost" http://localhost:5000/scan` followed by `curl "http://localhost:5000/get_changes?host=localhost"`
  - You can then ctrl+c in the container to stop the `ncat -l 8000` command
  - Type `exit` to exit the container

### Snooping around the datastore
If you get curious and want to look into the MongoDB datastore, you can do that via:
- `docker ps` - locate and copy the container id for the mongo container
- `docker exec -it <container id> bash` - this will put you in an interactive shell on the container
- Once inside the mongo container, type `mongosh`
- `show databases` - to see the availabel databases (ours is nmap)
- `use nmap`
- `show collections` - to view the collections inside the nmap db, there should only be `nmap_scan_results`
- `db.nmap_scan_results.find()` - to view all items in the collections
- `db.nmap_scan_results.find({"host":"dns.google"})` - to view scans for a specific host, found by hostname
- `db.nmap_scan_results.find({"ip":"127.0.0.1"})` - to view scans for a specific host, found by IP

<img src="https://user-images.githubusercontent.com/126095600/226524457-ed0d0a4b-3c3b-4269-a3da-82d2dbcb34d9.png">











