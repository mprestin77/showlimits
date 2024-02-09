# showlimits
show limits of OCI services and usage values

The script shows a list of all OCI services, their limits in usage values.

Usage:  showlimits.py [-s] [-h] [-o outputfile]

 -h: print usage

 -s: print list of services only

 -o <outfile>: print output to the output file

The script is looking for a configuration file limits.conf located in the same directory. The configuration file must have the following parameters:

[DEFAULT]

tenancy_id =

services =

regions =

For example:

[DEFAULT]

tenancy_id = ocid1.tenancy.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

services = open-search container-engine compute vcn object-storage filesystem

regions = us-ahsburn-1 us-phoenix-1

A user running the script either must be a tenancy Admninstrator or must be a member of a group with the following policy:

 Allow group LimitsAndUsageViewers to inspect resource-availability in tenancy
