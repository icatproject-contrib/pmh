#! /usr/bin/python
#
# Serialize ICAT to XML file using ICAT API
#
#

from __future__ import print_function
from serializer import XMLSerializer
from sys import exit
from icat import config, Client
from datetime import datetime, timedelta
from re import sub, match
from os import listdir
import logging


logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.CRITICAL)

config = config.Config(needlogin=False)
config.add_variable('sessionid', ("--sessionid",), 
                    dict(help="ICAT session id"))

conf = config.getconfig()

client = Client(conf.url, **conf.client_kwargs)
client.sessionId = conf.sessionid
client.autoLogout = False


# make dictionary from setup.properties
properties = {}
with open('../setup.properties', "r") as properties_file:
    for line in properties_file:
        if '=' in line:
            k, v = line.split('=')
            v = v.strip()
            properties[k] = sub(r'^"|"$', '', v) #remove first and last double quotes if exists


# read time of last checking data
try:
    with open(properties['STATE_FILE'], "r") as sf:
        state_file_ts = sf.readline().split('.')[0] #2014-07-18 16:11:07.198051 -> 2014-07-18 16:11:07 - query requires this format 
except IOError, OSError:
    exit("Oooops, state file not found!")


# get list of ids of investigations which have been already got (based on filenames)
# 1) filter files which are already serialized xml files
match_expression = r'^'+properties['FILES_PREFIX']+'_.*.xml$'
list_of_already_harvested_id = [filename for filename in listdir(properties['PROVIDER_REPOSITORY_DIR'])\
                                if match(match_expression, filename)]
# 2) extract list of ids from filenames
sub_expression = r'^'+properties['FILES_PREFIX']+'_([0-9]*).xml$'
list_of_already_harvested_id = [sub(sub_expression, r'\g<1>', filename) for filename in list_of_already_harvested_id]


#prepare filename path
file_name_ts = properties['FILES_PREFIX']
if not properties['PROVIDER_REPOSITORY_DIR'].endswith("/"):
    properties['PROVIDER_REPOSITORY_DIR'] += "/"
xml_file = properties['PROVIDER_REPOSITORY_DIR'] + file_name_ts + "_"


print("\nCreating xml files...")

#get date for state file
current_ts = datetime.now()

for investigation in client.search("SELECT inv FROM Investigation inv WHERE inv.releaseDate > {ts "+state_file_ts+"} AND inv.doi != NULL"):
        
    if str(investigation.id) in list_of_already_harvested_id:
        continue

    xml_filename = xml_file + str(investigation.id) + ".xml"

    tree = XMLSerializer()

    tree.addEntry("identifier", unicode(investigation.doi))
    tree.addEntry("title", unicode(investigation.title))
    tree.addEntry("description", unicode(investigation.summary))


    instrumentFullName = client.search("SELECT i.fullName FROM Instrument i JOIN i.investigationInstruments ii JOIN ii.investigation inv WHERE inv.id = "+ str(investigation.id))        
    rbNumber = "RB" + unicode(investigation.name)
    parameters = client.search("SELECT ip.type.name FROM InvestigationParameter ip WHERE ip.investigation.id = " + str(investigation.id))
    param = ""
    for parameter in parameters:
        param += ";" + unicode(parameter)
    tree.addEntry("relation", unicode(instrumentFullName) + ";" + rbNumber + param)


    tree.addEntry("references", unicode("http://dx.doi.org/" + investigation.doi), use_second_namespace=True)

    for user in client.search("SELECT iu.user FROM InvestigationUser iu WHERE iu.investigation.id = "+ str(investigation.id)):
        tree.addEntry("creator", unicode(user.fullName))

    tree.addEntry("contributor", unicode(properties['CONTRIBUTOR']))
    tree.addEntry("subject", unicode(properties['SUBJECT']))
    tree.addEntry("issued", unicode(investigation.releaseDate), use_second_namespace=True)
    tree.addEntry("language", unicode(properties['LANGUAGE']))

    facility = client.search("SELECT i.facility FROM Investigation i WHERE i.id = "+ str(investigation.id))
    tree.addEntry("publisher", unicode(facility[0].name + ";" + facility[0].fullName + ";" + facility[0].url) + ";" + unicode(instrumentFullName))

    
    format = client.search("SELECT dff FROM DatafileFormat dff JOIN dff.datafiles df JOIN df.dataset ds JOIN ds.investigation i WHERE i.id = "+ str(investigation.id))
    ## tree.addEntry("format", unicode(format[0].name)+";"+unicode(format[0].type)+";"+unicode(format[0].version)+";"+unicode(format[0].description))


    tree.addEntry("relation", unicode(properties['RELATION_GEO_DESC']))
    tree.addEntry("rights", unicode(properties['RIGHTS']))
    tree.addEntry("relation", unicode(properties['RELATION_PROJECT']))
    tree.addEntry("relation", unicode(properties['RELATION_COUNTRY']), xsi_type="dcterms:ISO3166")
    tree.addEntry("temporal", unicode(investigation.startDate)+";"+unicode(investigation.endDate), use_second_namespace=True)

    tree.write(xml_filename)

    print(xml_filename + " created")

with open(properties['STATE_FILE'], "w") as sf:
    sf.write(str(current_ts))

print("Done")
print()
