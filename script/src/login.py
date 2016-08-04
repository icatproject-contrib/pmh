#! /usr/bin/python

from __future__ import print_function
import icat
import icat.config
import logging
import datetime



print("\n\n\n------------------------------------------------------------------------------")
print("Entry time: " + str(datetime.datetime.now()))
print("Login attempt...")

logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)

conf = icat.config.Config(ids="optional").getconfig()

client = icat.Client(conf.url, **conf.client_kwargs)
client.autoLogout = False
sessionId = client.login(conf.auth, conf.credentials)

print("Login to", conf.url, "was successful.")
print("Session:", sessionId)
username = client.getUserName()
print("User:", username)

with open(".sessionid", "w") as f:
    f.write(sessionId + "\n")
