#!/usr/bin/python

import os
import re
import ConfigParser


class CountingParser:
  """
  The class enables to parse lines based on regular expressions and at the same time count pattern occurrences.
  """

  def __init__(self, pattern, count_matches = False, next_parser = None):
    """
    Setup the Parser.

    The regexp patter should have exactly two matches (groups). The first match will be used as the key - we will count
    the occurrences of the key. The second match will be the "rest of line" which will be used to call chained parsers.

    We can specify if we want to count the key occurrences or not (default behaviour).

    We can chain the Parsers by specifying the 'next_parser' parameter.

    :param pattern:       Regexp with exactly 2 matches (groups) which should be matched
    :param count_matches: Indicate if we want to count matches or not
    :param next_parser:   By specifying the 'next' parser we can chain several parsers together
    :type  next_parser:   CountingParser[]
    """

    self.pattern = re.compile(pattern)  # Compile the regexp
    self.count_matches = count_matches
    if count_matches:
      self.counter = Counter()
    self.next = next_parser


  def getNextParser(self):
    return self.next


  def parse(self, line):
    """
      Function parses a single line from parameter and checks if it matches the 'self.pattern'.

      The 'self.pattern' regexp should match exactly 2 groups. The first one will be the key
      which will be used to count occurrences. The second group will be the rest of the line
      used to call any chained parsers. If 'self.next' is set, then the 'rest' will be passed to the parse
      function of this Parser.

      :param line:   Line to match with the pattern

      :return:       True if matched, False if not matched
    """

    if line != "":

      # Exec regexp pattern with the current line
      match = self.pattern.match(line)

      if match:
        key, rest = match.group(1), match.group(2)

        #print "Matched: " + line + "\n" + "K: " + key + ", L: " + rest + "\n",

        # Should we count 'key' occurrences?
        if self.count_matches:
          self.counter.inc(key)

        # If we have chained another parser, use the output of this Parser
        if isinstance(self.next, CountingParser):
          return self.next.parse(rest)

        if isinstance(self.next, list):
          for parser in self.next:
            if isinstance(parser, CountingParser):
              parser.parse(rest)

        # Return True if match found
        return True

    # If the regexp did not match return False
    return False


class Counter:
  """
  A simple counter which sets up a dictionary of counters.
  Each counter counts 'key' occurrences based on the inc() function call.

  :type count: dict
  """

  count = {}   # Dictionary

  def __init__(self):
    pass


  def inc(self, key):
    """
    Increment count[] for 'key' by one.

    :param key: The key
    """
    if key in self.count > 0:
      self.count[key] += 1
    else:
      self.count[key] = 1


  def printAll(self):
    """
    DEBUGGING ONLY
    Print out the Counter for every key:

      key: counter[key]
      ...

    """
    for key in self.count:
      print key + ": ",
      print self.count[key]


class Action:
  """
  Action enables us to make any action based on key and value
  This class must be extended to define concrete Action.

  Sample usage:
    action = Action("/etc/my_dir/my_action.conf)
    action.prepare("Config_Section")
    action.execute(key)
  """

  def __init__(self, config_file):
    """
    Init the 'Action' object. Try to open a 'config_file'.

    :param config_file:
    """

    # Read from config file
    self.config = ConfigParser.RawConfigParser()

    # Read in the Config File
    if os.path.isfile(config_file):
      self.config.read(config_file)
    else:
      print "Error opening config file '" + config_file + "'"
      exit(-1)


  def prepare(self, section):
    """
    A dummy function for preparing the Action.
    Should be implemented by each child class.

    :param section: Which config section from the config_file to use.

    :return:
    """
    pass


  def execute(self, key):
    """
    Execute the action with the given key.

    :param key:
    :return:
    """
    print key
    pass


class ActionRules:
  """
  ActionRules enables to define rules which are used to check against a defined key value.
  """
  rules = []

  def __init__(self, action):
    """
    Initialize the ActionRules object

    :param action: Which Action to fire, upon rule
    :type action:  Action
    """
    self.action = action

  def addRule(self, op, value):
    """
    Add a rule to be matched.

    :param op:    Operator from the 'operator' lib (i.e. lt, gt, ...)
    :type  op: Operator

    :param value: Value to which we will be comparing the key

    :return:
    """
    self.rules.append([op, value])


  def fire(self, key):
    """
    Go through every rule. If any of the rules match, return true.

    :param key: The key value to which we compare the rules

    :return: Does any of the rules match? If yes return True, otherwise False
    """
    for rule in self.rules:
      op    = rule[0]  # Operator from the 'operator' lib (i.e. lt, gt, ..) https://docs.python.org/3/library/operator.html
      value = rule[1]  # Value to which we are comparing

      print "DEBUG op: " + str(op) + ", key: " + str(key) + ", value: " + str(value) + ", fire: " + str(op(key, value))

      if op(key, value):
        return True

    return False


  def fireAgainstCounter(self, counter):
    """
    Try to fire rules against each counter.

    :param counter: We will test each counter against the rules
    :type  counter: Counter

    :return: True if at least one fired, otherwise False
    """
    at_least_one_fired = False

    for key in counter.count:
      if self.fire(counter.count[key]):  # If any of the rules fire against the 'key'
        self.action.execute(key)
        at_least_one_fired = True

    return at_least_one_fired
