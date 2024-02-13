# showlimits

The script shows a list of all OCI services, their limits in usage values.
```
Usage:  showlimits.py [-s] [-h] [-o outputfile]
 -h: print usage
 -s: print list of services only
 -o <outfile>: print output to the output file (by default, writes outut to limits.out)
```
The script is looking for a configuration file limits.conf located in the same directory. The configuration file must have the following parameters:

```
[DEFAULT]
services =
regions =
```

For example:
```
[DEFAULT]
services = open-search container-engine compute vcn object-storage filesystem
regions = us-ahsburn-1 us-phoenix-1
```

Setup connectivity using User Authentication
```
1. Login to your OCI Cloud console
2. Create new group : ShowLimitsGroup  
3. Create new Policy: ShowLimitsGroupPolicy with Statements:
   Allow group ShowLimitsGroup to inspect resource-availability in tenancy
4. Add your OCI user to ShowUsageGroup group  
5. Config OCI config file - ~/.oci/config
   Please follow SDK config documentation - https://docs.cloud.oracle.com/en-us/iaas/Content/API/Concepts/sdkconfig.htm 
Steps 1-4 are not required for a user member of OCI Administrators group
```

Setup connectivity using Instance Principals Authentication (to execute the script from an OCI instance)
```
1.Login to your OCI Cloud consoleLogin to your OCI Cloud console
2. Create new Dynamic Group : DynShowLimitsGroup  
   Obtain Compute OCID and add rule - any {ALL {instance.id = 'ocid1.instance.oc1.xxxxxxxxxx'}}
3. Create new Policy: DynShowLimitsGroup with Statements:
   Allow dynamic group DynShowLimitsGroup to inspect resource-availability in tenancy
```


