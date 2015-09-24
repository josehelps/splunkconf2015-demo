#   Version 6.2.6
#
# This file contains possible attributes and values you can use to configure Splunk's pdf server.
#
# There is a pdf_server.conf in $SPLUNK_HOME/etc/system/default/.  To set custom configurations, 
# place a pdf_server.conf in $SPLUNK_HOME/etc/system/local/.  For examples, see pdf_server.conf.example.
# You must restart the pdf server to enable configurations.
#
# To learn more about configuration files (including precedence) please see the documentation 
# located at http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#     * You can also define global settings outside of any stanza, at the top of the file.
#     * Each conf file should have at most one default stanza. If there are multiple default
#       stanzas, attributes are combined. In the case of multiple definitions of the same
#       attribute, the last definition in the file wins.
#     * If an attribute is defined at both the global level and in a specific stanza, the
#       value in the specific stanza takes precedence.

[settings]
	* Set general Splunk Web configuration options under this stanza name.
	* Follow this stanza name with any number of the following attribute/value pairs.  
	* If you do not specify an entry for each attribute, Splunk will use the default value.

startwebserver = [0|1]
   	* Set whether or not to start the server.
   	* 0 disables Splunk Web, 1 enables it.
   	* Defaults to 1.

httpport = <port_number>
   	* Must be present for the server to start.
   	* If omitted or 0 the server will NOT start an http listener.
        * If using SSL, set to the HTTPS port number.
   	* Defaults to 9000.

enableSplunkWebSSL = [True|False]
	* Toggle between http or https.
	* Set to true to enable https and SSL.
	* Defaults to False.
   
privKeyPath = /certs/privkey.pem
caCertPath = /certs/cert.pem
   * Specify paths and names for Web SSL certs.
   * Path is relative to $SPLUNK_HOME/share/splunk.

supportSSLV3Only = [True|False]
   * Allow only SSLv3 connections if true.
   * NOTE: Enabling this may cause some browsers problems.
   
root_endpoint = <URI_prefix_string>
   * Defines the root URI path on which the appserver will listen.
   * Default setting is '/'.
   * For example: if you want to proxy the splunk UI at http://splunk:8000/splunkui, then set root_endpoint = /splunkui

static_endpoint = <URI_prefix_string>
   * Path to static content.
   * The path here is automatically appended to root_endpoint defined above.
   * Default is /static.

static_dir = <relative_filesystem_path>
   * The directory that actually holds the static content.
   * This can be an absolute URL if you want to put it elsewhere.
   * Default is share/splunk/search_mrsparkle/exposed.

enable_gzip = [True|False]
   * Determines if web server applies gzip compression to responses.
   * Defaults to True.



#
# cherrypy HTTP server config
#

server.thread_pool = <integer>
   * Specifies the numbers of threads the app server is allowed to maintain.
   * Defaults to 10.
   
server.socket_host = <ip_address>
   * Host values may be any IPv4 or IPv6 address, or any valid hostname.
   * The string 'localhost' is a synonym for '127.0.0.1' (or '::1', if your hosts file prefers IPv6).
     The string '0.0.0.0' is a special IPv4 entry meaning "any active interface" (INADDR_ANY), and
     '::' is the similar IN6ADDR_ANY for IPv6. 
   * The empty string or None are not allowed.
   * Defaults to 0.0.0.0

log.access_file = <filename>
   * Specifies the HTTP access log filename.
   * Stored in default Splunk /var/log directory.
   * Defaults to pdf_access.log

log.error_file = <filename>
   * Specifies the HTTP error log filename.
   * Stored in default Splunk /var/log directory.
   * Defaults to pdf_service.log

log.screen = [True|False]
   * Indicates if runtime output is displayed inside an interactive tty.
   * Defaults to True
   
request.show_tracebacks = [True|False]
   * Indicates if an exception traceback is displayed to the user on fatal exceptions.
   * Defaults to True

engine.autoreload_on = [True|False]
   * Indicates if the app server will auto-restart if it detects a python file has changed.
   * Defaults to False

tools.sessions.on = True
    * Indicates if user session support is enabled.
    * Should always be True

tools.sessions.timeout = <integer>
   * Specifies the number of minutes of inactivity before a user session expires.
   * Defaults to 60

response.timeout = <integer>
   * Specifies the number of seconds to wait for the server to complete a response.
   * Some requests such as uploading large files can take a long time.
   * Defaults to 7200

tools.sessions.storage_type = [file]
tools.sessions.storage_path = <filepath>
   * Specifies the session information storage mechanisms.
   * Comment out these two lines to use RAM based sessions instead.
   * Use an absolute path to store sessions outside of the Splunk directory tree.
   * Defaults to storage_type=file, storage_path=var/run/splunk

tools.decode.on = [True|False]
   * Indicates if all strings that come into CherryPy controller methods are decoded as unicode (assumes UTF-8 encoding).
   * WARNING: Disabling this will likely break the application, as all incoming strings are assumed
     to be unicode.
   * Defaults to True

tools.encode.on = [True|False]
   * Encodes all controller method response strings into UTF-8 str objects in Python.
   * WARNING: Disabling this will likely cause high byte character encoding to fail.
   * Defaults to True

tools.encode.encoding = <codec>
   * Force all outgoing characters to be encoded into UTF-8.
   * This only works with tools.encode.on set to True.
   * By setting this to utf-8, CherryPy's default behavior of observing the Accept-Charset header
     is overwritten and forces utf-8 output. Only change this if you know a particular browser
     installation must receive some other character encoding (Latin-1, iso-8859-1, etc.).
   * WARNING: Change this at your own risk.
   * Defaults to utf-8

pid_path = <filepath>
   * Specifies the path to the PID file.
   * Defaults to var/run/splunk/splunkweb.pid.

firefox_cmdline = <cmdline>
   * Specifies additional arguments to pass to Firefox.
   * This should normally not be set.

max_queue = <integer>
   * Specifies the maximum size of the backlog of pending report requests.
   * Once the backlog is reached the server will return an error on receiving additional requests.
   * Defaults to 10.

max_concurrent = <integer>
   * Specifies the maximum number of copies of Firefox that the report server will use concurrently to render reports.
   * Increase only if the host machine has multiple cores and plenty of spare memory.
   * Defaults to 2.

Xvfb = <path>
  * Pathname to the Xvfb program.
  * Defaults to searching the PATH.

xauth = <path>
  * Pathname to the xauth program.
  * Defaults to searching the PATH.

mcookie = <path>
  * Pathname to the mcookie program.
  * Defaults to searching the PATH.

appserver_ipaddr = <ip_networks>
  * If set, the PDF server will only query Splunk app servers on IP addresses within the IP networks
    specified here.
  * Networks can be specified as a prefix (10.1.0.0/16) or using a netmask (10.1.0.0/255.255.0.0).
  * IPv6 addresses are also supported.
  * Individual IP addresses can also be listed (1.2.3.4).
  * Multiple networks should be comma separated.
  * Defaults to accepting any IP address.

client_ipaddr = <ip_networks>
  * If set, the PDF server will only accept requests from hosts whose IP address falls within the IP
    networks specified here.
  * Generally this setting should match the appserver_ipaddr setting.
  * Format matches appserver_ipaddr.
  * Defaults to accepting any IP address.

screenshot_enabled = [True|False]
  * If enabled allows screenshots of the X server to be taken for debugging purposes.
  * Enabling this is a potential security hole as anyone on an IP address matching client_ipaddr will be
    able to see reports in progress.
  * Defaults to False.

