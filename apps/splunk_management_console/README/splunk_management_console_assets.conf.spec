# This file describes the splunk_management_console_assets.conf file that is included
# with the Splunk Distributed Management Console.
#
# THIS FILE IS FOR INTERNAL USE ONLY. 
# DO NOT EDIT default/splunk_management_console_assets.conf.
# DO NOT EDIT local/splunk_management_console_assets.conf.
#
# Modifying either of these files will result in unexpected behavior within the Distributed Management Console dashboards.
#

# ---- General settings ----
[settings]

disabled = [1|0]
	* Whether or not this settings stanza should be used
	* 1 = true, 0 = false

configuredPeers = <search-peer-identifier>, <search-peer-identifier>, ...
	* This comma-separated list identifies search peers configured with this Distributed Management Console
	* Each <search-peer-identifier> is identified by its IP address (or FQDN) plus port, per its title entry in /services/search/distributed/peers
		* Example: myindexer.foo.com:8089
	* This list identifies search peers whose data should appear in Distributed Management Console dashboards

blackList = <search-peer-identifier>, <search-peer-identifier>, ...
	* A comma-separated list of search peers that have been explicitly disabled to be used by the Distributed Management Console
	* Each <search-peer-identifier> is identified by its IP address (or FQDN) plus port, per its title entry in /services/search/distributed/peers
		* Example: myindexer.foo.com:8089
	* This list identifies search peers whose data should explicity not appear in Distributed Management Console dashboards


# ---- Overrides for search peers ----
# In some cases, you might wish to override which host and host_fqdn values the
# Distributed Management Console uses to drive its dashboards. These overrides, which
# you set through the DMC setup in Splunk Web, are stored in the following stanzas,
# titled by peer identifier.


[<search-peer-identifier>]
* Each <search-peer-identifier> is its IP address (or FQDN) plus port, per its title entry in /services/search/distributed/peers.
	* For example: myindexer.foo.com:8089

disabled = [1|0]
	* Whether or not to use this stanza
	* 1 = true, 0 = false

host = <host-override-string>
	* Which host value should be used to identify this instance.
	* By default, every instance uses the "host" value from /services/search/distributed/peers/<search-peer-identifier>.
		* This value is read from <search-peer-identifier>'s inputs.conf "host" value.

host_fqdn = <host_fqdn-override-string>
	* Which host_fqdn value should be used to identify this instance.
	* By default, every instance uses the "host_fqdn" value from /services/search/distributed/peers/<search-peer-identifier>.
		* This value is whatever the instance believes its FQDN is.


