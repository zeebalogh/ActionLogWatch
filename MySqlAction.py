#!/usr/bin/python

import pymysql
from datetime import datetime
from CountingActionParser import Action


class MySqlAction(Action):

  def prepare(self, section):
    """
    In this particular action we connect to the database and execute a query based on the passed 'key'.

    :param section: Configuration section to use

    :return: Nothing
    """
    # Connect to the database
    self.conn = pymysql.connect(
      db=self.config.get(section, "DB"),
      user=self.config.get(section, "USER"),
      passwd=self.config.get(section, "PW"),
      host=self.config.get(section, "HOST"),
    )

    self.cur = self.conn.cursor()

  def execute(self, key):
    """
    We need to execute the following SQL:
    INSERT INTO postfix_access (source, access, type)
      SELECT * FROM (SELECT '134.255.239.53', 'REJECT', 'client') AS tmp
        WHERE NOT EXISTS (
          SELECT source FROM postfix_access WHERE source = '134.255.239.53'
        ) LIMIT 1

    :return:
    """
    self.cur.execute("INSERT INTO postfix_access (source, access, type, comment) \
      SELECT * FROM (SELECT '" + key + "', 'REJECT', 'client', 'reason: SPAM_DETECTED_BY_AMAVIS, datetime: " + str(
      datetime.now()) + "') AS tmp \
        WHERE NOT EXISTS ( \
          SELECT source FROM postfix_access WHERE source = '" + key + "' \
        ) LIMIT 1"
                     )