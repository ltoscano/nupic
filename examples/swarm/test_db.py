#! /usr/bin/env python
# ----------------------------------------------------------------------
# Numenta Platform for Intelligent Computing (NuPIC)
# Copyright (C) 2013, Numenta, Inc.  Unless you have an agreement
# with Numenta, Inc., for a separate license for this software code, the
# following terms and conditions apply:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero Public License for more details.
#
# You should have received a copy of the GNU Affero Public License
# along with this program.  If not, see http://www.gnu.org/licenses.
#
# http://numenta.org/licenses/
# ----------------------------------------------------------------------

"""This script lets the user know which NuPIC config file is being used
   and whether or not they are able to connect to the mysql database and create
   databases/tables given the configuration information provided."""

import pymysql
from nupic.support.configuration import Configuration

DEFAULT_CONFIG = "nupic-default.xml"
USER_CONFIG = "nupic-site.xml"


def get_file_used():
    """
      Determine which NuPIC configuration file is being used and returns the
      name of the configuration file it is using. Either DEFAULT_CONFIG or
      USER_CONFIG.
    """

    # output will be {} if the file passed into Configuration._readConfigFile
    # can not be found in the standard paths returned by
    # Configuration._getConfigPaths.
    output = Configuration._readConfigFile(USER_CONFIG) #pylint: disable=protected-access
    if output != {}:
        return USER_CONFIG
    return DEFAULT_CONFIG

def test_db_connection(host, port, user, passwd):
    """
      Determine if the specified host, port, user, passwd is able to connect
      to a running mysql database, create test database, create a test table,
      insert something into the table, delete the table, and delete the database.
      returns true if this is successful, false if there is an error in this
      process.
    """
    try:
        conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd)
        cursor = conn.cursor()
        cursor.execute('CREATE DATABASE IF NOT EXISTS testing')
        conn.select_db('testing')
        cursor.execute("CREATE TABLE test \
                                (teststring VARCHAR(255),\
                                 someint INT)")
        cursor.execute("INSERT INTO test VALUES ('testing123', 123)")
        cursor.execute('DROP TABLE IF EXISTS test')
        cursor.execute('DROP DATABASE IF EXISTS testing')
        return True

    except pymysql.err.OperationalError:
        return False


def db_validator():
    """
       let the user know what NuPIC config file is being used
       and whether or not they have mysql set up correctly for
       swarming.
    """
    fileused = get_file_used()

    # Get the values we need from NuPIC's configuration
    host = Configuration.get('nupic.cluster.database.host')
    port = int(Configuration.get('nupic.cluster.database.port'))
    user = Configuration.get('nupic.cluster.database.user')
    passwd = Configuration.get('nupic.cluster.database.passwd')


    print "This script will validate that your MySQL is setup correctly for NuPIC."
    print "MySQL is required for NuPIC swarming. The settings are defined in a "
    print "configuration file found in $NUPIC/src/nupic/support/nupic-default.xml "
    print "Out of the box those settings contain MySQL's default access "
    print "credentials."
    print
    print "The nupic-default.xml can be duplicated to define user specific changes,"
    print " calling the copied file $NUPIC/src/nupic/support/nupic-site.xml"
    print "Refer to the nupic-default.xml for additional instructions."
    print
    print "Defaults: localhost, 3306, root, no password"
    print
    print "Retrieved the following NuPIC configuration using: ", fileused
    print "    host   :    ", host
    print "    port   :    ", port
    print "    user   :    ", user
    print "    passwd :    ", passwd


    if test_db_connection(host, port, user, passwd):
        print "Connection successful!!"
    else:
        print ("Couldn't connect to the database or you don't have the"
               " permissions required to create databases and tables."
               " Please ensure you have MySQL\n installed, running,"
               " accessible using the NuPIC configuration settings,"
               " and the user specified has permission to create both"
               " databases and tables.")

if __name__ == '__main__':
    db_validator()
