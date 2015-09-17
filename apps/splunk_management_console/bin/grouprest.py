#!/usr/bin/env python

import re
import sys
from splunklib.searchcommands import \
  dispatch, GeneratingCommand, Configuration, Option, Validator
from splunklib.client import Collection
import splunklib.results
import time


class ValueList(Validator):
  """ Validates a CSV list of field values.

  """
  def __init__(self, pattern=r'''[_.a-zA-Z-][_.a-zA-Z0-9-]*$'''):
    self.pattern = re.compile(pattern)

  def __call__(self, value):
    value = str(value)
    values = filter(None, value.split(','))
    for v in values:
      if self.pattern.match(v) is None:
        raise ValueError('Illegal list value: %s' % v)

    return values

  def __format__(self, value):
    return str(value)



@Configuration()
class GroupRestCommand(GeneratingCommand):
  """
  General Usage:
    | grouprest splunk_server_groups="<list of groups>" <endpoint>

  Example
    | grouprest splunk_server_groups="nonindexers" /services/server/roles

  The command looks up the groups specified in splunk_server_groups in distsearch.conf.
  For the servers in those groups, it returns the values those servers return
  for that endpoint.
  This command is a generalization of the | rest command.

  """

  splunk_server_groups = Option(require=True, validate=ValueList())

  def generate(self):
    # Custom search commands don't allow slashes??
    endpoint = self.fieldnames[0]
    splunk_server_groups = self.splunk_server_groups
    service = self.service
    groups = [group for group in service.confs['distsearch'] if group.name.startswith('distributedSearch:')]
    peers = Collection(service, '/services/search/distributed/peers').list()
    groupToServers = dict()

    # Determine the splunk server names for every server that we found in any group
    for group in groups:
      serversCsv = group['servers']
      serversCsv = serversCsv if serversCsv != '0' else ''
      servers = serversCsv.split(',')
      groupName = group.name[len('distributedSearch:'):]
      groupToServers[groupName] = list()

      for server in servers:
        splunkServer = [peer['peerName'] for peer in peers if peer.name == server][0]
        groupToServers[groupName].append(splunkServer)

    # Tally up the servers we need to query
    servers_to_query = set()
    for server_group in splunk_server_groups:
      servers_to_query.update(groupToServers.get(server_group, []))

    if len(servers_to_query) == 0:
      return

    # Build the query
    prefix_servers = ['splunk_server="%s"' % server for server in servers_to_query]
    query = "| rest %s | search (%s)" % (endpoint, " OR ".join(prefix_servers))

    search_results = service.jobs.oneshot(query)
    reader = splunklib.results.ResultsReader(search_results)
    known_keys = set()
    to_return = list()

    for item in reader:
      property_bag = {'_time': time.time()}
      rawValues = []
      for column, row in item.iteritems():
        property_bag[column] = row or "1"
        rawValues.append("%s=%s" % (column, row or "1" ))
        known_keys.update([column])
      property_bag['_raw'] = ','.join(rawValues)
      to_return.append(property_bag)

    # We can't return heterogeneous objects here, need to normalize them all
    for bag in to_return:
      for column in known_keys:
        if not column in bag:
          bag[column] = None
      yield bag

dispatch(GroupRestCommand, sys.argv, sys.stdin, sys.stdout, __name__)
