PYTHON=python

    $PYTHON login.py -c icat_cfg -s icat_connection
    $PYTHON get_data_from_icat.py -c icat_cfg -s icat_connection --sessionid `cat .sessionid`
    $PYTHON logout.py -c icat_cfg -s icat_connection --sessionid `cat .sessionid`

    rm -f .sessionid

