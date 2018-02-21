#!/usr/bin/python
# -*- coding: UTF-8 -*-

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

# Variable Globale partagée entre le Receiver et le Publisher
buckets={}

# Thread de reception des metriques

class Receiver(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global buckets

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((RECEIVER_UDP_IP, RECEIVER_UDP_PORT))

        while True:
            data,addr = sock.recvfrom(1024)
            datestr,metric,value = data.split(';')
            date=datetime.strptime(datestr,"%Y-%m-%d %H:%M:%S")
            if metric not in metrics_mapping:
                print('[RECEIVER] ',metric," dont have a mapping")
            else:
                timestamp=int(date.strftime('%s'))
                bucket_start=timestamp-timestamp%interval
                metric=metrics_mapping[metric]
                value=float(value.strip())
                print('[RECEIVER] %d:%s:%0.1f'%(timestamp,metric,value))
                if bucket_start not in buckets:
                    buckets[bucket_start]={}
                else:
                    if metric not in buckets[bucket_start]:
                        buckets[bucket_start][metric]=[value]
                    else:
                        buckets[bucket_start][metric].append(value)

# Thread de publication des metriques

class Publisher(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global buckets
        last_values={}
        sock = socket.socket()
        sock.connect((CARBON_SERVER_PICKLE_ADDRESS,CARBON_SERVER_PICKLE_PORT))

        while True:
            time.sleep(5)

            # On recupere la liste de bucket et on supprime le dernier
            list_buckets=buckets.keys()
            if len(list_buckets) == 0:
                next
            list_buckets.pop()
            # Pour chaque bucket restant
            for bucket in list_buckets:
                current_bucket = buckets[bucket]
                # On calcule min/avg/max de chaque metrique qu'il contient et on met a jour last_values
                for metric in current_bucket:
                    list_metrics=current_bucket[metric]
                    min_value=min(list_metrics)
                    avg_value=sum(list_metrics)/len(list_metrics)
                    max_value=max(list_metrics)
                    last_values[metric]={ 'min':min_value, 'avg':avg_value,'max':max_value }
                # On publie last_values sur graphite via le protocole pickel
                graphite_data=[]
                for metric in last_values:
                    for x in ['min','avg','max']:
                        path='%s.%s'%(metric,x)
                        timestamp=bucket
                        value=last_values[metric][x]
                        graphite_data.append([path,[timestamp,value]])
                        print('[PUBLISHER] %s %0.1f %d'%(path,value,timestamp))

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
  (options,args) = parser.parse_args()

  try:
    fp=open(options.conffile,"r")
    configuration=json.load(fp)
    fp.close()
  except IOError as e:
    print('Impossible de lire le fichier de configuration ',options.conffile,' : ',e.strerror)
    exit(1)
  
  try:
    fp=open("loxone2graphite.schema","r")
    schema=json.load(fp)
    fp.close()
  except IOError as e:
    print('Impossible de lire le fichier de schema : ',e.strerror)
    exit(1)
  
  try:
    jsonschema.validate(configuration,schema)
  except jsonschema.exceptions.ValidationError as e:
    print('La configuration est invalide : ',e)
    exit(1)

  receiver = Receiver()
  publisher = Publisher()
  receiver.start()
  publisher.start()
  receiver.join()
  publisher.join()

if __name__ == "__main__":
  main()
