#! /usr/bin/python
#
# Log out from an ICAT session.
#

from __future__ import print_function
import icat
import icat.config
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.CRITICAL)

config = icat.config.Config(needlogin=False)
config.add_variable('sessionid', ("--sessionid",), 
                    dict(help="ICAT session id"))
conf = config.getconfig()

client = icat.Client(conf.url, **conf.client_kwargs)
client.sessionId = conf.sessionid
# The actual logout happens automatically at exit of the script.

print("Log out from session %s" % client.sessionId)

