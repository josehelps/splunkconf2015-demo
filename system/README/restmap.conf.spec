#   Version 6.2.6
#
# This file contains possible attribute and value pairs for creating new Representational State Transfer
# (REST) endpoints.
#
# There is a restmap.conf in $SPLUNK_HOME/etc/system/default/.  To set custom configurations, 
# place a restmap.conf in $SPLUNK_HOME/etc/system/local/. For help, see
# restmap.conf.example. You must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) please see the documentation 
# located at http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

# NOTE: You must register every REST endpoint via this file to make it available.

###########################
# Global stanza

[global]
* This stanza sets global configurations for all REST endpoints. 
* Follow this stanza name with any number of the following attribute/value pairs.

allowGetAuth=[true|false]
* Allow user/password to be passed as a GET parameter to endpoint services/auth/login.  
* Setting this to true, while convenient, may result in user/password getting logged as cleartext
  in Splunk's logs *and* any proxy servers in between. 
* Defaults to false.  

pythonHandlerPath=<path>
* Path to 'main' python script handler.
* Used by the script handler to determine where the actual 'main' script is located.  
* Typically, you should not need to change this.
* Defaults to $SPLUNK_HOME/bin/rest_handler.py.


###########################
# Applicable to all REST stanzas
# Stanza definitions below may supply additional information for these.
#

[<rest endpoint name>:<endpoint description string>]
match=<path>
* Specify the URI that calls the handler. 
* For example if match=/foo, then https://$SERVER:$PORT/services/foo calls this handler.  
* NOTE: You must start your path with a /.

requireAuthentication=[true|false]
* This optional attribute determines if this endpoint requires authentication.  
* Defaults to 'true'.

authKeyStanza=<stanza>
* This optional attribute determines the location of the pass4SymmKey in the server.conf to be used for endpoint authentication.  
* Defaults to 'general' stanza.
* Only applicable if the requireAuthentication is set true.

capability=<capabilityName>
capability.<post|delete|get|put>=<capabilityName>
* Depending on the HTTP method, check capabilities on the authenticated session user.
* If you use 'capability.post|delete|get|put,' then the associated method is checked 
against the authenticated user's role. 
* If you just use 'capability,' then all calls get checked against this capability (regardless 
of the HTTP method).

acceptFrom=<network_acl> ...
* Lists a set of networks or addresses to allow this endpoint to be accessed from.
* This shouldn't be confused with the setting of the same name in the
  [httpServer] stanza of server.conf which controls whether a host can
  make HTTP requests at all
* Each rule can be in the following forms:
*   1. A single IPv4 or IPv6 address (examples: "10.1.2.3", "fe80::4a3")
*   2. A CIDR block of addresses (examples: "10/8", "fe80:1234/32")
*   3. A DNS name, possibly with a '*' used as a wildcard (examples: "myhost.example.com", "*.splunk.com")
*   4. A single '*' which matches anything
* Entries can also be prefixed with '!' to cause the rule to reject the
  connection.  Rules are applied in order, and the first one to match is
  used.  For example, "!10.1/16, *" will allow connections from everywhere
  except the 10.1.*.* network.
* Defaults to "*" (accept from anywhere)

includeInAccessLog=[true|false]
* If this is set to false, requests to this endpoint will not appear in splunkd_access.log
* Defaults to 'true'.

###########################
# Per-endpoint stanza 
# Specify a handler and other handler-specific settings.  
# The handler is responsible for implementing arbitrary namespace underneath each REST endpoint.

[script:<uniqueName>]
* NOTE: The uniqueName must be different for each handler.
* Call the specified handler when executing this endpoint.
* The following attribute/value pairs support the script handler.

scripttype=python
* Tell the system what type of script to execute when using this endpoint.
* Defaults to python.
* Python is currently the only option for scripttype.
	
handler=<SCRIPT>.<CLASSNAME>
* The name and class name of the file to execute.  
* The file *must* live in an application's bin subdirectory.
* For example, $SPLUNK_HOME/etc/apps/<APPNAME>/bin/TestHandler.py has a class called
  MyHandler (which, in the case of python must be derived from a base class called 
  'splunk.rest.BaseRestHandler'). The tag/value pair for this is: "handler=TestHandler.MyHandler".

xsl=<path to XSL transform file>
* Optional.
* Perform an optional XSL transform on data returned from the handler.
* Only use this if the data is XML.

script=<path to a script executable>
* Optional.
* Execute a script which is *not* derived from 'splunk.rest.BaseRestHandler'.
* Put the path to that script here.  
* This is rarely used.
* Do not use this unless you know what you are doing.

output_modes=<csv list>
* Specifies which output formats can be requested from this endpoint.
* Valid values are: json, xml.
* Defaults to xml.


#############################
# 'admin'
# The built-in handler for the Extensible Administration Interface. 
# Exposes the listed EAI handlers at the given URL.
#

[admin:<uniqueName>]

match=<partial URL>
* URL which, when accessed, will display the handlers listed below.

members=<csv list>
* List of handlers to expose at this URL.
* See https://localhost:8089/services/admin for a list of all possible handlers.

#############################
# 'admin_external'
# Register Python handlers for the Extensible Administration Interface.
# Handler will be exposed via its "uniqueName".
#

[admin_external:<uniqueName>]

handlertype=<script type>
* Currently only the value 'python' is valid.

handlerfile=<unique filename>
* Script to execute.
* For bin/myAwesomeAppHandler.py, specify only myAwesomeAppHandler.py.

handleractions=<comma separated list>
* List of EAI actions supported by this handler.
* Valid values are: create, edit, list, delete, _reload.

#########################
# Validation stanzas
# Add stanzas using the following definition to add arg validation to
# the appropriate EAI handlers.

[validation:<handler-name>]

<field> =  <validation-rule> 

* <field> is the name of the field whose value would be validated when an object is being saved. 
* <validation-rule> is an eval expression using the validate() function to evaluate arg correctness 
  and return an error message. If you use a boolean returning function, a generic message is displayed. 
* <handler-name> is the name of the REST endpoint which this stanza applies to handler-name is what is
  used to access the handler via /servicesNS/<user>/<app/admin/<handler-name>.
* For example:
* action.email.sendresult = validate( isbool('action.email.sendresults'), "'action.email.sendresults' must
  be a boolean value").
* NOTE: use ' or $ to enclose field names that contain non alphanumeric characters.

#############################
# 'eai'
# Settings to alter the behavior of EAI handlers in various ways.
# These should not need to be edited by users.
#

[eai:<EAI handler name>]

showInDirSvc = [true|false]
* Whether configurations managed by this handler should be enumerated via the
  directory service, used by SplunkWeb's "All Configurations" management page.
  Defaults to false.

desc = <human readable string>
* Allows for renaming the configuration type of these objects when enumerated
  via the directory service.


#############################
# Miscellaneous
# The un-described parameters in these stanzas all operate according to the
# descriptions listed under "script:", above.
# These should not need to be edited by users - they are here only to quiet
# down the configuration checker.
#

[input:...]
dynamic = [true|false]
* If set to true, listen on the socket for data.
* If false, data is contained within the request body.
* Defaults to false.

[peerupload:...]
path = <directory path>
* Path to search through to find configuration bundles from search peers.
untar = [true|false]
* Whether or not a file should be untarred once the transfer is complete.
