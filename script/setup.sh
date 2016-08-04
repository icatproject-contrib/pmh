#get the directory from which script was invoked, so it could be launched from whichever directory
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


properties=$CURRENT_DIR/setup.properties
if [ -f $properties ]; then

    #source properties file
    . $properties


    if [ $ICAT_VERSION != 4.7 ]; then
        echo "Only version 4.7 of ICAT is being supported"
        exit 1
    fi

    cd $CURRENT_DIR/src;

    #create icat_cfg
    echo $connection_id > icat_cfg
    cat $CURRENT_DIR/setup.properties | grep -E "^\b(url|auth|username|password|idsurl)\b" >> icat_cfg


    #if state file does not exists then create it with default content
    if [ ! -f $STATE_FILE ]; then
        #printf doesn't produce newline at the end
        printf "1900-01-01 00:00:00.000000" > $STATE_FILE
    fi
    
    #create UPDATE_SCRIPT
    UPDATE_SCRIPT_NAME=update.sh
    CONN_ID=`echo $connection_id | cut -c2- | rev | cut -c2- | rev`

    echo -e "PYTHON=python

    \$PYTHON login.py -c icat_cfg -s $CONN_ID
    \$PYTHON get_data_from_icat.py -c icat_cfg -s $CONN_ID --sessionid \`cat .sessionid\`
    \$PYTHON logout.py -c icat_cfg -s $CONN_ID --sessionid \`cat .sessionid\`

    rm -f .sessionid\n" > $UPDATE_SCRIPT_NAME
    chmod +x $UPDATE_SCRIPT_NAME


    #add update script to crone
    crontab -l | { cat; echo "$CHECKING_ICAT_FREQUENCY bash -l -c 'cd $CURRENT_DIR/src; ./$UPDATE_SCRIPT_NAME >> $CRON_LOGFILE 2>&1'"; } | crontab -

    #apply jaoi indexing frequency from properties
    WEB_XML_FILE_LOCATION=$JOAI_DIRECTORY/WEB-INF/web.xml
    TEXT_TO_INSERT="\t\t<param-name>updateFrequency<\/param-name>\n\t\t<param-value>$JOAI_INDEXING_FREQUENCY<\/param-value>"
    sed -ie "/updateFrequency/{N; s/.*/$TEXT_TO_INSERT/}" $WEB_XML_FILE_LOCATION

else
    echo "setup.properties not found"
fi
