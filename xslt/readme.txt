$Id: readme.txt 868 2015-04-23 16:01:05Z alistair.mills@stfc.ac.uk $

You can apply XSLT to jOAI response in order to see formated response in browser.

1. Make the file oai2.xsl file accessible for your application server. If using Glassfish, copy it to:

$GLASSFISH_HOME/glassfish/domains/domain1/applications/oai

2. Modify jOAI response

Go to the jOAI installation directory, then to oai_requests catalogue.  For example, if using Glassfish:

cd $GLASSFISH_HOME/glassfish/domains/domain1/applications/oai/oai_requests

You will find the following files:

errors.jsp
GetRecord.jsp
Identify.jsp
ListIdentifiers.jsp
ListMetadataFormats.jsp
ListRecords.jsp
ListSets.jsp

These files came from the joai.zip file, and require customization.  You can replace them with the contents of oai_requests.tar.

If you want to do it for yourself, here is the procedure to follow:

Assuming that you copied oai2.xsl as described above, add following line to each of the above files:

<?xml-stylesheet type="text/xsl" href="/oai/oai2.xsl" ?>

Add it just after:

<?xml version="1.0" encoding="UTF-8" ?>

This always occurs at the beginning of the file.

E.g. Identify.jsp file should look like:

<?xml version="1.0" encoding="UTF-8" ?>
<?xml-stylesheet type="text/xsl" href="/oai/oai2.xsl" ?>
<%@ page contentType="text/xml; charset=UTF-8" %> 
...

If everything was done correctly, when requesting your provider, e.g.

https://icat-10.pandata.stfc.ac.uk/oai/provider?verb=Identify

where http://icat-10.pandata.stfc.ac.uk is your host, you should see some nice formatted tables instead of raw xml file.
    
- the end -

