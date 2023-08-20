# -*- coding: utf-8 -*-
"""
Created on Sat Nov 26 00:23:12 2022

@author: FNU Amanraj
"""
from zipfile import ZipFile

import datetime			# Why do you need this?  How is it used?
import pandas as pd		# What is this used for? 
                                # Why use this?
import matplotlib.pyplot as plt

import numpy as np
import math
from sklearn.cluster import AgglomerativeClustering

from scipy.cluster.hierarchy import linkage, dendrogram


def get_gps_data():    
    gps_file	= open(gps_filename, 'r')   
    # linesc = len(gps_file.readlines())
    # print(gps_filename)
    # totalhours=int((linesc-5)/(241*60))
    # print('Total Number of hours:'+str(totalhours))
    # print('Total Number of minutes:'+str(int((linesc-5)/(241))))
    # gps_file.close()
    # gps_file	= open(gps_filename, 'r')
    
    cnt=0
    # For every line in the gps data file.
    for line in gps_file:
        
        # If this line is an RMC line.
        if line.split(',')[0] == "$GPRMC":
            cnt=cnt+1
            # Split the line on commas and set each value to a variable (based on its location per the protocol).
            try:
                label, timestamp, validity, latitude, lat_dir, longitude, long_dir, knots, course, \
                datestamp, variation, var_dir, checksum	= line.split(',')
            # If this line is missing a value or has too many, assume it's an error and skip the line.
            except ValueError:
                continue
            
            
            # If the validity is 'V' (per the protocol, a gps error), skip the line.
            if validity == 'V':
                continue
            # if timestamp in gps_info.keys():
            #     print("already there")
            # Get the timestamp into a datetime object.
            # Start by getting the HHMMSS part, the part before the '.'.
            
            
            cnt=cnt+1
            # Convert the latitude into degrees.
            # This math might be wrong.
            degrees	= int(float(latitude) / 100)
            mins	= float(latitude) - (degrees * 100)
            # N is positive, S is negative.
            if lat_dir == 'N':
                fixed_latitude	= degrees + (mins / 60)
            else:
                fixed_latitude	= -degrees + (-mins / 60)

            # Convert the longitude into degrees.
            degrees	= int(float(longitude) / 100)
            mins	= float(longitude) - (degrees * 100)
            # E is positive, W is negative.
            if long_dir == 'E':
                fixed_longitude	= degrees + (mins / 60)
            else:
                fixed_longitude	= -degrees + (-mins / 60)

            # Add this line's information to the dictionary, with the timestamp as the key.
            # Using the timestamp means that multiple lines from the same time (e.g. if there's also GGA from this time)
            # will be combined.
            # If it's already in the dictionary, we want to update the entry instead of setting to keep from overriding
            #    any GGA information from that time (such as altitude).
            timestampkey=timestamp
            
            if cnt>241*60*24:
                timestampkey='1'+timestamp
                
            date_time_obj	= converttime(timestampkey)
           
            if timestampkey in gps_info:
                gps_info[timestampkey].update({'datetime': date_time_obj, 'latitude': round(fixed_latitude, 6),
                                            'longitude': round(fixed_longitude, 6), 'knots': float(knots),
                                            'course': course, 'variation': variation})
            else:
                gps_info[timestampkey]	= {'datetime': date_time_obj, 'latitude': round(fixed_latitude, 6),
                                       'longitude': round(fixed_longitude, 6),
                                       'knots': knots, 'course': course, 'variation': variation}

        # If this line is a GGA line.
        elif line.split(',')[0] == "$GPGGA":
            # If the GPS quality indicator is not zero, this line should be valid.
            cnt=cnt+1
            lisp=line.split(',')
            # print(lisp)
            if lisp[len(lisp)-1] != '0':
                # Split the line on commas and set each value to a variable (based on its location per the protocol).
                try:
                    label, timestamp, latitude, lat_dir, longitude, long_dir, gps_quality, num_satellites, horiz_dilution, \
                    antenna_alt, antenna_alt_units, geoidal, geo_units, age_since_update, checksum	= line.split(',')
                # If this failed, that means something is wrong with this line.
                except ValueError:
                    continue
                if latitude=='' or longitude=='':
                    continue
                
                # Convert the latitude into degrees.
                degrees	= int(float(latitude) / 100)
                mins	= float(latitude) - (degrees * 100)
                # N is positive, S is negative.
                if lat_dir == 'N':
                    fixed_latitude	= degrees + (mins / 60)
                else:
                    fixed_latitude	= -degrees + (-mins / 60)

                # Convert the longitude into degrees.
                degrees	= int(float(longitude) / 100)
                mins	= float(longitude) - (degrees * 100)
                # E is positive, W is negative.
                if long_dir == 'E':
                    fixed_longitude	= degrees + (mins / 60)
                else:
                    fixed_longitude	= -degrees + (-mins / 60)

                
                timestampkey=timestamp
                
                if cnt>241*60*24:
                    timestampkey='1'+timestamp
                
                
                if timestampkey in gps_info:
                    gps_info[timestampkey].update({'latitude': round(fixed_latitude, 6),
                                                'longitude': round(fixed_longitude, 6),
                                                'altitude': float(antenna_alt)})
                else:
                    gps_info[timestampkey]	= {'latitude': round(fixed_latitude, 6), 'longitude': round(fixed_longitude, 6),
                                           'altitude': float(antenna_alt)}
        # We don't care about any other protocols.
        else:
            continue

def converttime(timestamp):
    f=0
    
    if len(timestamp)>10:
        f=int(timestamp[0])
        timestamp=timestamp[1:]
    timestamp_split	= timestamp.split('.')[0]
    # Join every two characters with ':' (that is, get it into HH:MM:SS form), and then append the MS part.
    time_str	= ':'.join([timestamp_split[index:index + 2] for index in range(0, len(timestamp_split), 2)]) + \
               ':' + timestamp.split('.')[1]
    # print(timestamp)
    
    date_time_obj	= datetime.datetime.strptime(time_str, '%H:%M:%S:%f')
    date_time_obj= date_time_obj+datetime.timedelta(days=f)
    return date_time_obj





def findStops():
    red=[]
    yellow=[]
    green=[]
        
    
    key_list	= list(gps_info.keys())
    st=0
    stop=0
    for key_index in range(0, len(key_list) - 1):
        # if gps_filename=='2022_06/2022_06_05__212220_gps_file.txt':
        #     print("Integer"+str(key_list[key_index]))
        # Get the coordinates of the current and next entries in the dictionary.
        this_latitude	= gps_info[key_list[key_index]]['latitude']
        next_latitude	= gps_info[key_list[key_index + 1]]['latitude']
        this_longitude	= gps_info[key_list[key_index]]['longitude']
        next_longitude	= gps_info[key_list[key_index + 1]]['longitude']
        lat=this_latitude-next_latitude
        long=this_longitude-next_longitude
        # print(lat,long)
        
        if lat<0.00002 and long<0.00002:
            if stop==0:
                st=key_list[key_index]
                stop=1   
            else:
                pass
        else:
            if stop==1:
                t1=converttime(st)
                t2=converttime(key_list[key_index])
                dt=t2-t1
                time=dt.total_seconds()
                # print(time)            
                if abs(time)>86400:
                    red.append([gps_info[st]['latitude'],gps_info[st]['longitude']])
                    gRed[st]=gps_info[st]
                elif abs(time)>2700:
                    yellow.append([gps_info[st]['latitude'],gps_info[st]['longitude']])
                    gYellow[st]=gps_info[st]
                elif abs(time)>900:
                    green.append([gps_info[st]['latitude'],gps_info[st]['longitude']])
                    gGreen[st]=gps_info[st]
                else:
                    continue
                stop=0
            else:
                pass
                    
    return [red,yellow,green]
        

        
    
def my_round(x1,y1) : 
    x=round(x1,5)
    y=round(y1,5)
    # print(x-y)
    if abs(x-y)>=0.0 and abs(x-y)<=0.00002:
        return True
    else:
        # print(x-y)
        return False

    
    
    


def remove_redundant_GPS_points():
    # Get a list of all of the keys for the dictionary of GPS info.
    key_list	= list(gps_info.keys())
    
    # Iterate through the list of keys.
    for key_index in range(0, len(key_list) - 1):
        # Get the coordinates of the current and next entries in the dictionary.
        
        this_latitude	= gps_info[key_list[key_index]]['latitude']
        next_latitude	= gps_info[key_list[key_index + 1]]['latitude']
        this_longitude	= gps_info[key_list[key_index]]['longitude']
        next_longitude	= gps_info[key_list[key_index + 1]]['longitude']

        # If the coordinates are the same (rounded down a bit, to account for GPS skew)
        # meaning we haven't moved, remove one of the values.
        if my_round(this_latitude,next_latitude) and my_round(this_longitude,next_longitude):            
            gps_info.pop(key_list[key_index])
            continue
        
            
        # If we didn't remove the data for the key right before this one, and this isn't the first key.
        if key_index != 0 and key_list[key_index - 1] in gps_info:

            # Get coordinates of the preceding entry.
            last_latitude 	= gps_info[key_list[key_index - 1]]['latitude']
            last_longitude 	= gps_info[key_list[key_index - 1]]['longitude']

            # Get the latitude and longitude differences in both directions.
            lat_diff_from_last	= abs(this_latitude - last_latitude)
            long_diff_from_last	= abs(this_longitude - last_longitude)
            lat_diff_from_next	= abs(this_latitude - next_latitude)
            long_diff_from_next	= abs(this_longitude - next_longitude)

            # If our speed is constant and we're moving in a straight line, remove the unnecessary point in between.
            tolerance	= 0.00004   # This is WAY TOO BIG!! 
            if abs(lat_diff_from_last - lat_diff_from_next) <= tolerance and \
                    abs(long_diff_from_last - long_diff_from_next) <= tolerance :
                gps_info.pop(key_list[key_index])
                
                continue

            # If the last entry has speed data (some lines may not if they were only GGA).
            if 'knots' in gps_info[key_list[key_index - 1]]:

                # Get the speed of the last entry.
                last_speed	= float(gps_info[key_list[key_index - 1]]['knots'])

                # Remove the entry if the difference in latitude or longitude is too high compared to the speed.
                # This manages errors where a GPS reading is way off (e.g. in the middle of the ocean.)
                if long_diff_from_last/10 > last_speed or lat_diff_from_next/10 > last_speed:
                    gps_info.pop(key_list[key_index])
                    continue


#
# Write the kml file.
#
# REWRITE THIS TO TAKE IN A FILENAME.
#
# Write now it outputs a path.
# Instead we want to output a flag for where the car spent a lot of time.
#
def write_out_KML_file(stops,pin,color):
    # Open it to write (such that it will be created if it does not already exist).
    
    last_alt 	= 0
    for stop in stops.values():
        if 'altitude' in stop:
            last_alt 	= stop['altitude']

        kml_file.write('<Placemark>\n')
        kml_file.write('\t<description>'+pin+' PIN for A Stop</description>\n')
        kml_file.write('\t<Style>\n')
        kml_file.write('\t\t<IconStyle>\n')
        kml_file.write('\t\t\t<color>'+color+'</color>\n')
        kml_file.write('\t\t\t<Icon>\n')
        kml_file.write('\t\t\t\t<href>http://maps.google.com/mapfiles/kml/paddle/1.png</href>\n')
        kml_file.write('\t\t\t</Icon>\n')
        kml_file.write('\t\t</IconStyle>\n')
        kml_file.write('\t</Style>\n')
        kml_file.write('\t<Point>\n')
        kml_file.write(
            '\t\t<coordinates>' + str(stop['longitude']) + ',' + str(stop['latitude']) + ',' + str(last_alt) +
            '</coordinates>\n')
        kml_file.write('\t</Point>\n')
        kml_file.write('</Placemark>\n')
    







        





    

    
   
    
        
       
        
        
        

     


        

