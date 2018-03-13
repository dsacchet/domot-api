# domot-api
Little REST API to work with my home

Example :

```bash
# curl -H "Content-Type: application/json" -X PUT http://localhost/maison/chaudiere/consigne/jour -d '{ "temperature":"21"}'
{ "route" : "putMaisonChaudiereConsigneJour", "returnCode": "0", "result" : "Requested setting : 21.0" }
# curl http://localhost/maison/chaudiere/consigne/jour
{ "route" : "getMaisonChaudiereConsigneJour", "returnCode": "0", "result" : "21.0" }
# curl -H "Content-Type: application/json" -X PUT http://kwazii/maison/vmc/mode -d '{ "mode":"low"}'
{ "route" : "putMaisonVmcMode", "returnCode": "0", "result" : "Current setting : low" }
```
