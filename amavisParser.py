#!/usr/bin/python

import sys
import operator
from CountingActionParser import CountingParser, ActionRules
from MySqlAction import MySqlAction


def main():
  """
  Sample usage of the CountingActionParser. Custom action was defined by the MySqlAction class.

  Basically we use this script to parse a mail server log file. Amavis records any spam abuse from a client by
  lines containing "... Blocked SPAM [IP] ..." or "... Passed SPAMMY [IP] ...". We need to identify such lines,
  extract the IPs and count the occurrences of IPs in such lines. Based on the number of occurrences we take further
  countermeasures. In this concrete example we execute an "INSERT" SQL command, which inserts malicious client IP into
  a Postfix access database (only if the IP is not already in the database). This happens only if a client has sent
  more than 5 SPAM messages.

  This script is to be executed each hour and it expects log entries for the past one hour on STDIN.
  """

  # Generic regexp patterns
  IP_RE = '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+'  # Any IPv4 Address RegExp

  # Setup Parsers
  amavisParser = \
    CountingParser('^(.+ [0-9]+ [0-9]{2}:[0-9]{2}:[0-9]{2}) (.+)', False, [  # "Sep 13 10:52:53 ..."
      CountingParser('^(.+ amavis\[[0-9]+\]\: \(.*\)) (.*)', False, [        # "host_name amavis[15415]: (15415-07) ..."
        CountingParser('^Blocked SPAM, \[(' + IP_RE + ')\] (\[' + IP_RE + '\] .*)', True),  # "Blocked SPAM [IP] ..."
        CountingParser('^Passed SPAMMY, \[(' + IP_RE + ')\] (\[' + IP_RE + '\] .*)', True), # "Passed SPAMMY [IP] ..."
      ])
    ])


  # Process every line from STDIN by the defined parsers and count matches
  for line in sys.stdin:
    amavisLine = amavisParser.parse(line)

  # Print out the found matches
  spamIpCounter   = amavisParser.next[0].next[0].counter
  print "SPAM: "
  spamIpCounter.printAll()

  spammyIpCounter = amavisParser.next[0].next[1].counter
  print "SPAMMY: "
  spammyIpCounter.printAll()

  # Define an Action
  insertRejectClient = MySqlAction("/etc/host2u/parser_mysql_action.conf")
  insertRejectClient.prepare("MySQL")

  # Create Action Rules
  ar = ActionRules(insertRejectClient)
  ar.addRule(operator.gt, 5)   # (key > 5)
  ar.fireRulesAgainstCounter(spamIpCounter)
  ar.fireRulesAgainstCounter(spammyIpCounter)


if __name__ == "__main__":
    main()

# end.
