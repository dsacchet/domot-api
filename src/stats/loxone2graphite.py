#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
loxone2graphite.py : listen on an UDP socket for message from a loxone
                     miniserver convert data and send them back to a
                     carbon relay every n seconds
"""

import socket
import sys
import struct
from threading import Thread
from datetime import datetime
import pprint
import time
from carbon.util import pickle
from optparse import OptionParser
import json
import jsonschema
import logging
import logging.config
import logging.handlers

# Variable Globale partagée entre le Receiver et le Publisher
buckets={}

def avg(list_metrics):
    return sum(list_metrics)/len(list_metrics)

def last(list_metrics):
    return list_metrics[len(list_metrics)-1]

def first(list_metrics):
    return list_metrics[0]

def mapping_extract_source_destination(mapping):
    result={}
    for i,v in enumerate(mapping):
        result[v["source"]]=v["destination"]
    return result

def mapping_extract_destination_aggregation(mapping):
    result={}
    for i,v in enumerate(mapping):
        result[v["destination"]]=v["aggregation"]
    return result

# Thread de reception des metriques

class Receiver(Thread):

    def __init__(self, ip, port, metrics_mapping, flush_interval):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.metrics_mapping = metrics_mapping
        self.flush_interval = flush_interval
        self.logger = logging.getLogger('loxone2graphite')

    def run(self):
        global buckets

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.ip,self.port))

        while True:
            data,addr = sock.recvfrom(1024)
            datestr,metric,value = data.split(';')
            date=datetime.strptime(datestr,"%Y-%m-%d %H:%M:%S")
            if metric not in self.metrics_mapping:
                self.logger.error('[RECEIVER] %s dont have a mapping'%(metric))
            else:
                timestamp=int(date.strftime('%s'))
                bucket_start=timestamp-timestamp%self.flush_interval
                metric=self.metrics_mapping[metric]
                value=float(value.strip())
                self.logger.debug('[RECEIVER] %d:%s:%0.1f'%(timestamp,metric,value))
                if bucket_start not in buckets:
                    buckets[bucket_start]={}
                    buckets[bucket_start][metric]=[value]
                else:
                    if metric not in buckets[bucket_start]:
                        buckets[bucket_start][metric]=[value]
                    else:
                        buckets[bucket_start][metric].append(value)

# Thread de publication des metriques

class Publisher(Thread):

    def __init__(self,method,ip,port,aggregation_methods,prefix=""):
        Thread.__init__(self)
        self.method = method
        self.ip = ip
        self.port = port
        self.aggregation_methods = aggregation_methods
        self.prefix = prefix
        self.logger = logging.getLogger('loxone2graphite')

    def run(self):
        global buckets
        last_values={}
        sock = socket.socket()
        sock.connect((self.ip, self.port))

        pp=pprint.PrettyPrinter(indent=4)

        while True:
            time.sleep(5)

            pp.pprint(buckets)

            # On recupere la liste de bucket et on supprime le dernier
            list_buckets=buckets.keys()
            try:
                if len(list_buckets) == 0:
                    next
                list_buckets.pop()
            except Exception as e:
                self.logger.debug('[PUBLISHER] Exception, le tableau buckets est vide')
                next
            # Pour chaque bucket restant
            for bucket in list_buckets:
                self.logger.debug('[PUBLISHER] Current bucket : %d'%(bucket))
                current_bucket = buckets[bucket]
                # On calcule les aggregations definies pour cette metrique et on met a jour last_values
                for metric in current_bucket:
                    self.logger.debug('[PUBLISHER] Current metric : %s'%(metric))
                    list_metrics=current_bucket[metric]
                    for aggregation_method in self.aggregation_methods[metric]:
                        self.logger.debug('[PUBLISHER] Current aggregation method : %s'%(aggregation_method))
                        last_values[metric][aggregation_method]=globals()[aggregation_method](list_metrics)
                        self.logger.debug('[PUBLISHER] Current result : %0.2f'%(last_values[metric][aggregation_method]))
                # On publie last_values sur graphite via le protocole pickle
                graphite_data=[]
                for metric in last_values:
                    for x in ['min','avg','max']:
                        path='%s%s.%s'%(prefix,metric,x)
                        timestamp=bucket
                        value=last_values[metric][x]
                        graphite_data.append([path,[timestamp,value]])
                        self.logger.debug('[PUBLISHER] %s %0.1f %d'%(path,value,timestamp))

                payload = pickle.dumps(graphite_data, protocol=2)
                header = struct.pack("!L",len(payload))
                message = header + payload
                sock.sendall(message)
                # On supprime le bucket pour qu'il ne soit pas retraite
                del buckets[bucket]

def main():

    parser = OptionParser()
    parser.add_option("-D", "--daemon", action="store_true", dest="daemon", default="False", help="Daemonize the process")
    parser.add_option("-c", "--conf", action="store", dest="conffile", default="/etc/domot-api/loxone2graphite.json", help="Specify a configuration file")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default="False", help="Display message on console")
    (options,args) = parser.parse_args()

    try:
        fp=open(options.conffile,"r")
        configuration=json.load(fp,encoding="utf-8")
        fp.close()
    except IOError as e:
        print('Impossible de lire le fichier de configuration ',options.conffile,' : ',e.strerror)
        exit(1)
    
    try:
        fp=open("loxone2graphite.schema","r")
        schema=json.load(fp,encoding="utf-8")
        fp.close()
    except IOError as e:
        print('Impossible de lire le fichier de schema : ',e.strerror)
        exit(1)
    
    try:
        jsonschema.validate(configuration,schema)
    except jsonschema.exceptions.ValidationError as e:
        print('La configuration est invalide : ',e)
        exit(1)

    try:
        logging.config.dictConfig(configuration['global']['logging'])
    except Exception as e:
        pp=pprint.PrettyPrinter(indent=4)
        pp.pprint(e)
        exit(1)

    logger=logging.getLogger("loxone2graphite")
    logger.info("message info")
    logger.debug("message debug")

    receiver = Receiver(
            configuration['global']['receiver']['endpoint']['ip'],
            configuration['global']['receiver']['endpoint']['port'],
            mapping_extract_source_destination(configuration['metrics']['mapping']),
            configuration['global']['receiver']['flush_interval'])
    publisher = Publisher(
            configuration['global']['publisher']['method'],
            configuration['global']['publisher']['endpoint']['ip'],
            configuration['global']['publisher']['endpoint']['port'],
            mapping_extract_destination_aggregation(configuration['metrics']['mapping']))
    receiver.start()
    publisher.start()
    receiver.join()
    publisher.join()

if __name__ == "__main__":
    main()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
