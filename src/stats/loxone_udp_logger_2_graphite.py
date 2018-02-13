#!/usr/bin/python
# -*- coding: UTF-8 -*-

import socket
import sys
from threading import Thread
from datetime import datetime
import pprint
import time

metrics_mapping = {
        'Puissance Baie Info':'compteurs.electricite.puissance.ec1',
        'Puissance VMC':'compteurs.electricite.puissance.ec2',
        'Puissance Chaudière':'compteurs.electricite.puissance.ec3',
        'Puissance TI':'compteurs.electricite.puissance.ti',
        'Tension Baie Info':'compteurs.electricite.tension.ec1',
        'Tension VMC':'compteurs.electricite.tension.ec2',
        'Tension Chaudière':'compteurs.electricite.tension.ec3',
        'Tension TI':'compteurs.electricite.tension.ti',
        'Intensite Baie Info':'compteurs.electricite.intensite.ec1',
        'Intensité VMC':'compteurs.electricite.intensite.ec2',
        'Intensité chaudière':'compteurs.electricite.intensite.ec3',
        'Intensité TI':'compteurs.electricite.intensite.ti',
        'Energie Baie Info':'compteurs.electricite.energie.ec1',
        'Energie VMC':'compteurs.electricite.energie.ec2',
        'Energie Chaudière':'compteurs.electricite.energie.ec3',
        'Energie TI':'compteurs.electricite.energie.ti',
        'SM.5.0.1.Vent':'compteurs.station_meteo.vent',
        'SM.5.0.2.Température':'compteurs.station_meteo.temperature',
        'SM.5.0.4.Luminosité':'compteurs.station_meteo.luminosite',
        'SM.5.0.5.Azimut soleil':'compteurs.station_meteo.azimut_soleil',
        'SM.5.0.6.Elevation soleil':'compteurs.station_meteo.elevation_soleil',
        'SM.5.0.7.Direction vent':'compteurs.station_meteo.direction_vent',
        'SM.5.2.0.Luminosite C1':'compteurs.station_meteo.luminosite_c1',
        'SM.5.2.1.Luminosite C2':'compteurs.station_meteo.luminosite_c2',
        'SM.5.2.2.Luminosite C3':'compteurs.station_meteo.luminosite_c3',
        'SM.5.2.3.Luminosite C4':'compteurs.station_meteo.luminosite_c4',
        'SM.5.2.10.Rayonnement global':'compteurs.station_meteo.rayonnement_global'
}

UDP_IP="192.168.3.254"
UDP_PORT=1234
interval=60

buckets={}

pp = pprint.PrettyPrinter(indent=4)

class Receiver(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global buckets

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))

        while True:
            data,addr = sock.recvfrom(1024)
            datestr,metric,value = data.split(';')
            date=datetime.strptime(datestr,"%Y-%m-%d %H:%M:%S")
            if metric not in metrics_mapping:
                print '[RECEIVER] ',metric," dont have a mapping"
            else:
                timestamp=int(date.strftime('%s'))
                bucket_start=timestamp-timestamp%interval
                metric=metrics_mapping[metric]
                value=float(value.strip())
                print '[RECEIVER] %d:%s:%0.1f'%(timestamp,metric,value)
                if bucket_start not in buckets:
                    buckets[bucket_start]={}
                else:
                    if metric not in buckets[bucket_start]:
                        buckets[bucket_start][metric]=[value]
                    else:
                        buckets[bucket_start][metric].append(value)

class Publisher(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        global buckets
        last_values={}
        while True:
            time.sleep(30)
            list_buckets=buckets.keys()
            list_buckets.pop()
            for bucket in list_buckets:
                current_bucket = buckets[bucket]
                for metric in current_bucket:
                    list_metrics=current_bucket[metric]
                    min_value=min(list_metrics)
                    avg_value=sum(list_metrics)/len(list_metrics)
                    max_value=max(list_metrics)
                    last_values[metric]={ 'min':min_value, 'avg':avg_value,'max':max_value }
                for metric in last_values:
                    for x in ['min','avg','max']:
                        print '[PUBLISHER] %s.%s %0.1f %d'%(metric,x,last_values[metric][x],bucket)
                del buckets[bucket]

receiver = Receiver()
publisher = Publisher()
receiver.start()
publisher.start()

receiver.join()
publisher.join()
