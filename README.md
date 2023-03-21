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

