# CountingActionParser
The class enables to parse lines based on regular expressions and at the same time count pattern occurrences.

## Example
Sample usage of the CountingParser is provided in the 'amavisParser' file. 
Custom action was defined by the MySqlAction class.

Basically we use this script to parse a mail server log file. Amavis records any spam abuse from a client by
lines containing `... Blocked SPAM [X.X.X.X] ...` or `... Passed SPAMMY [X.X.X.X] ...`. We need to identify such lines,
extract the IPs and count the occurrences of IPs in such lines. 

Based on the number of occurrences we take further countermeasures. In this concrete example we execute an "INSERT" SQL 
command, which inserts malicious client IP into a Postfix access database (only if the IP is not already in the 
database). This happens only if a client has sent more than 5 SPAM messages.

This script is to be executed each hour and it expects log entries for the past one hour on STDIN.
