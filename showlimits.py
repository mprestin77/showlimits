#!/usr/bin/env python3
##########################################################################
# Copyright (c) 2016, 2023, Oracle and/or its affiliates.  All rights reserved.
# This software is dual-licensed to you under the Universal Permissive License (UPL) 1.0 as shown at https://oss.oracle.com/licenses/upl or Apache License 2.0 as shown at http://www.apache.org/licenses/LICENSE-2.0. You may choose either license.
#       
# showlimits.py
#
# The script shows a list of all OCI services, their limits in usage values.
#
# Usage:  showlimits.py [-s] [-h] [-o outputfile]
#  -h: print usage
#  -s: print list of services only
#  -o <outfile>: print output to the output file
#   
# The script is looking for a configuration file limits.conf located in the same directory. The configuration file must have the following parameters:
#
# [DEFAULT]
# tenancy_id = 
# services = 
# regions = 
#
# For example:
#
# [DEFAULT]
# tenancy_id = ocid1.tenancy.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# services = open-search container-engine compute vcn object-storage filesystem
# regions = us-ahsburn-1 us-phoenix-1
#
#
# A user running the script either must be a tenancy Admninstrator or must be a member of a group with the following policy assigned:
#
#   Allow group LimitsAndUsageViewers to inspect resource-availability in tenancy
#   
##########################################################################

import oci                  
import time                 
import datetime                 
import os                   
import platform                 
import sys
import json
import configparser
import getopt


##########################################################################
# get_services
##########################################################################
def get_services(limits_client, tenancy_id):

    services = []

    try:
        services = oci.pagination.list_call_get_all_results(
            limits_client.list_services,
            tenancy_id, sort_by="name",
            retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY
        ).data

    except Exception as e:
            print("\nError in getting a list of services: " + str(e))
            return data

    return services


##########################################################################
# get_limits         
##########################################################################
def get_limits(limits_client, service_list, region, tenancy_id):

    data = []           
    
    try:                    

      services = get_services(limits_client, tenancy_id) 

      if services:    
                        
            # oci.limits.models.ServiceSummary
            for service in services:
                        
             if service_list and service.name in service_list:
                # get the limits per service
                limits = [] 
                try:
                    limits = oci.pagination.list_call_get_all_results(
                        limits_client.list_limit_values,
                        tenancy_id,
                        service_name=service.name,
                        sort_by="name",
                        retry_strategy=oci.retry.DEFAULT_RETRY_STRATEGY
                    ).data
                except oci.exceptions.Exception as e:
                    print("\nError in getting limits for service " + service.name + ": " + str(e)) 
                    continue
    
                # oci.limits.models.LimitValueSummary
                for limit in limits:
                    val = {
                        'name': str(service.name),
                        'description': str(service.description),
                        'limit_name': str(limit.name),
                        'availability_domain': ("" if limit.availability_domain is None else str(limit.availability_domain)),
                        'scope_type': str(limit.scope_type),
                        'value': str(limit.value),
                        'used': "",
                        'available': "",
                        'region_name': region
                    }

                    # if not limit, continue, don't calculate limit = 0
                    if limit.value == 0:
                        continue

                    # get usage per limit if available
                    try:
                        limit_compartment = tenancy_id

                        usage = []
                        if limit.scope_type == "AD":
                            usage = limits_client.get_resource_availability(service.name, limit.name, limit_compartment, availability_domain=limit.availability_domain).data
                        else:
                            usage = limits_client.get_resource_availability(service.name, limit.name, limit_compartment).data

                        # oci.limits.models.ResourceAvailability
                        if usage.used is not None:
                            val['used'] = str(usage.used)
                        if usage.available is not None:
                            val['available'] = str(usage.available)
                    except oci.exceptions.ServiceError as e:
                        if e.code == 'NotAuthorizedOrNotFound':
                            val['used'] = 'NotAuth'
                            val['available'] = 'NotAuth'
                    except Exception:
                        pass

                    # add to array
                    data.append(val)

      return data

    except Exception as e:
        print("\nError: " + str(e)) 
        return data


##########################################################################
# print_usage
##########################################################################
def print_usage():
  print ('showlimits.py [-s] [-h] [-o outputfile]')
  print('-h: print usage')
  print('-s: print list of services')
  print('-o <outfile>: print output to the output file')

##########################################################################
#  Main 
##########################################################################
def main(argv):
  outputfile = ''
  print_services=False
  try:
     opts, args = getopt.getopt(argv,"hso:",["ofile="])
  except getopt.GetoptError:
     print_usage()
     sys.exit()

  outfile = sys.stdout

  for opt, arg in opts:
     if opt == '-h':
       print_usage()
       sys.exit()
     elif opt == '-s':
       print_services=True
     elif opt in ("-o", "--ofile"):
       outfile=open(arg, 'w')
     else:
       print_usage()
       sys.exit()
     

  config = configparser.ConfigParser()
  config.read(r'limits.conf')
  tenancy_id = config.get('DEFAULT','tenancy_id')
  services = config.get('DEFAULT','services')
  regions = config.get('DEFAULT','regions')

  oci_config = oci.config.from_file()
  limits_client = oci.limits.LimitsClient(oci_config)

  if print_services:
    services = get_services(limits_client, tenancy_id)
    for service in services:
      print(service.name)
    sys.exit()
  else:
    limits={}
    for region in regions.split():
      print("############# region " + region + " #############",file=outfile)
      limits[region]=get_limits(limits_client, services, region, tenancy_id)
      for limit in limits[region]:
        print(json.dumps(limit,indent=2),file=outfile)


if __name__ == "__main__":
   main(sys.argv[1:])
