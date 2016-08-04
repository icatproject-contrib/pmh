$Id: readme.txt 867 2015-04-23 14:13:16Z alistair.mills@stfc.ac.uk $

Pre-requisites:

In order to make it simple to install the OAI_PMH for ICAT, the following configuration is assumed:

operation system:       linux
username:               glassfish
home directory:         /home/glassfish
shell:                  bash
additional software:    wget, svn, python, python-icat, ids-client, mysql, mysql connector jar

In order to make use of this software, you have to do the following:

svn co https://pandata.googlecode.com/svn/trunk/contrib/erasmus2014/poramus/pmh

Overview:

In order to deploy OAI-PMH to publish ICAT data, the following steps are required:

- deploy the data provider joai, then configure joai;
- publish the Metadata namespace definition;  this step is generally not required;
- configure, then execute the collector script.

Detailed instructions on each of these steps are provided in references [1, 2, 3].  

The software has been written so that once configured, the collector runs once per hour, and finds new records in the ISIS catalog and passes them to the provider.  

The metadata namespace definition has been published on http://pandata.org/

Please see the following:

[1] https://code.google.com/p/pandata/source/browse/trunk/contrib/erasmus2014/poramus/pmh/readme.txt Describes how to configure and deploy the OAI-PMH server.

[2] https://code.google.com/p/pandata/source/browse/trunk/contrib/erasmus2014/poramus/pmh/namespace/readme.txt Describes the deployment of the namespace description.

[3] https://code.google.com/p/pandata/source/browse/trunk/contrib/erasmus2014/poramus/pmh/script/properties_description.txt Describes the properties of the collector.

Deploying ICAT OAI-PMH software:

  0. Prepare namespace for oai_qdc - follow instructions from "namespace" directory if not done.

  1. Deploy joai on a local container such as glassfish:

     - It is located in joai folder;
     - Optionally you can get it from here: http://www.dlese.org/dds/services/joai_software.jsp;
     - It is a good idea to install it with default contextroot (it is oai);
     - Use the following commands:
     
     cd joai
     unzip joai.zip
     cd joai_v3.1.1.3
     asadmin deploy --contextroot oai oai.war

  2. Configure joai

     Open browser and go to joai landing page on your container, e.g. https://icat-10.pandata.stfc.ac.uk:8181/oai/ -or- https://icat-10.pandata.stfc.ac.uk/oai

     Browse to Data Provider             : (drop-down)
       -> Setup and Status               : (click)
         -> Repository Information       : (click) 
           -> Edit repository information: (click)
             -> Provide the following repository information:

                          Repository name: ISIS ICAT represented in Qualified Dublin Core
           Administrator's e-mail address: alistair.mills@stfc.ac.uk
        Repository description (optional): Repository for providing selected public metadata from ISIS ICAT in form of Qualified Dublin Core 
          Namespace identifier (optional): pandata.org
                                     Save: (click)
                                       OK: (click)       

     Browse to Data Provider             : (click)
       -> Setup and Status               : (click)
         -> Add Metadata Files           : (click)
           -> Add metadata directory     : (click)
             -> Provide the following information:

                 Nickname for these files: ISIS ICAT files
                          Format of files: oai_qdc
                    Path to the directory: /home/glassfish/data
                                 - the same as PROVIDER_REPOSITORY_DIR from script/setup.properties; 
                                 - defines where the files that were serialized from ICAT by a script are held;
                                 - should be absolute path in server;
                                 - the user that runs joai should have access to files from that repository;
                                 - it is NOT necessary to have access to that files directly from outside (e.g. from a browser);
                                 - this directory must exist already exist.

                       Metadata namespace: http://pandata.org/pmh/oai_qdc/
                          Metadata schema: http://pandata.org/pmh/oai_qdc.xsd
                                     Save: (click)

  3. Pass data to the data provider
     - customize "setup.properties" file (script/setup.properties), if in doubt look into "properties_description.txt";
     - if you do not want to harvest ALL available files, go to script/src/, edit "state" file and provide date above which script will harvest new records;
     - for single harvesting run "get_data_instantly.sh" script;
     - for regular harvesting run "setup.sh" script which sets up cron job; after that you can manage this jobs as usual, by "crontab -e".

  4. [Optional] Apply XSLT transformation to jOAI. Instructions are residing in xslt directory.

  5. Index files manually:
     - Go to jOAI landing page;
     - Browse to Data Provider -> Metadata Files Configuration;
     - Click button called "Reindex all files" and confirm.

  6. Go to https://icat-10.pandata.stfc.ac.uk/oai/provider?verb=ListRecords&metadataPrefix=oai_qdc:
     It should return some xml records.  If you applied XSLT then it will return information in tables.

Technical details of how this software works

The main idea is to get selected data from ICAT, serialize them into XML files, put those files in some repository and share them through OAI-PMH protocol.

The first part (getting and serializing data from ICAT, putting them into repository) is done by "get_data_from_icat.py" script, whereas jOAI software is responsible for managing OAI-PMH protocol.

The most crucial files reside in "script" directory (others are only an addition)
Important files:
--------------------------------------------------------------------------------------------
|                  setup.sh | sets up cron job, which is getting data from ICAT regularly  |
--------------------------------------------------------------------------------------------
|          setup.properties | defines configuration properties for setup.sh                |
--------------------------------------------------------------------------------------------
| src/get_data_from_icat.py | gets data from ICAT and puts them into XML files             |
--------------------------------------------------------------------------------------------
|                 src/state | holds the date of last harvesting                            |
--------------------------------------------------------------------------------------------

How it works in details:

1. jOAI is being installed and prepared by user according to instructions. 
2. User should customize properties in "setup.properties" (see "properties_description.txt")
3. Now user should run "./setup.sh" (and that is all what user should do [1])
   Setup:
   3.1 Reads the properties;
   3.2 Check if ICAT version specified in properties is supported - if not it exits;
   3.3 Creates src/icat_config file which holds ICAT connection parameters (based on setup.properties), this file is used subsequently by other scripts;
   3.4 Creates update script, which is responsible for invoking other scripts in sequence (inter alia get_data_from_icat.py); 
   3.5 MOST IMPORTANT: sets up cron job (adds a new cron entry), that runs update script in time regularly;
   3.6 Updates jOAI indexing frequency specified in properties.

   Now cron job will be invoking update script that:
   3.7 Logs user into ICAT;
   3.8 Calls get_data_from_icat_script.py;
   3.9 Logs user out of ICAT.

   The most important part of work is done by get_data_from_icat script which:
   3.10 Reads the properties file into dictionary;
   3.11 Reads the state file content
   3.12 Searches ICAT for records, that have DOIs (Digital Object Identifiers) and that have a releaseDate later than the date in the state file (date of last checking ICAT), such records represent new records to be published.
   3.13 Serializes selected records into XML files using the script serializer.py; it is easy to guess the meaning of the XML files and to change the content if necessary; some values are constant and are defined in properties; files are saved in directory defined in setup.properties. Only records that weren't downloaded before are saved.
   3.14 Updates state file, so next time qery won't pick up old already downloaded records.

   "serializer.py" holds a simple class that simplifies serializing by encapsulating difficult details (mainly namespaces handling).
   Namespaces are hardcoded in this class since it should not be changed (however if they change, you must change this file).

4. Now, when files are stored in repository, a properly configured jOAI is sharing them. They can be harvested using OAI-PMH harvester.


(1) That's the idea, but user can also call "get_data_instantly.sh" script which mostly will do the same, but only once without cron involvement; please note that it is updating state file as well. The user may also modify state file, but only when he exactly knows what he is doing[2].

(2) One reason manual intervention could be a crash and then trying to recover a file. Another situation could be when populating a clean repository when the user does not want every available record. Also updating XML content (see below) is a good reason.


Other remarks:

1) Each entry in cron.log should end with "Done.". If not, then probably something went wrong.

2) When you want to change the way of creating the XML files:
  You must change "get_data_from_icat.py" script and/or "setup.properties", where the XML constants are defined.

3) If you want to update already downloaded XML (e.g. you know that ISIS changed content of investigations):
  Delete outdated XML file from repository, modify date in state file (it must be earlier than releaseDate of investigation that XML file contained) and run scripts (if you have cron job then you don't have to do anything)

4) In the event of a crash:
  If you do not know what caused the crash, you may want look into file cron.log.
  Then, depending on the situation, it may be a good idea to check the latest files in the repository to determine if they contain invalid content.
  If yes, (they are corrupted) you should delete them, set an appropriate date in state file and run the scripts.
  What you can always do is to delete all the files in the repository, replace the state file with a clean one from the repository and run the scripts getting data from ICAT. Good idea would be then to reindex the jOAI.

- the end -


