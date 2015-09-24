#   Version 6.2.6
#
# This file contains possible attributes and values for configuring global 
# saved search actions in alert_actions.conf.  Saved searches are configured 
# in savedsearches.conf.
#
# There is an alert_actions.conf in $SPLUNK_HOME/etc/system/default/.  To set custom configurations, 
# place an alert_actions.conf in $SPLUNK_HOME/etc/system/local/.  For examples, see 
# alert_actions.conf.example. You must restart Splunk to enable configurations.
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

maxresults = <integer>
	* Set the global maximum number of search results sent via alerts.
	* Defaults to 100.

hostname = [protocol]<host>[:<port>]
	* Sets the hostname used in the web link (url) sent in alerts.
	* This value accepts two forms.
	   * hostname
		examples: splunkserver, splunkserver.example.com
	   * protocol://hostname:port
		examples: http://splunkserver:8000, https://splunkserver.example.com:443
	* When this value is a simple hostname, the protocol and port which
	  are configured within splunk are used to construct the base of
	  the url.
	* When this value begins with 'http://', it is used verbatim.  
	  NOTE: This means the correct port must be specified if it is not
	  the default port for http or https.
	* This is useful in cases when the Splunk server is not aware of
	  how to construct an externally referenceable url, such as SSO
	  environments, other proxies, or when the Splunk server hostname
	  is not generally resolvable.
	* Defaults to current hostname provided by the operating system, 
	  or if that fails, "localhost".
	* When set to empty, default behavior is used.

ttl     = <integer>[p]
	* optional argument specifying the minimum time to live (in seconds) 
	  of the search artifacts, if this action is triggered.
 	* if p follows integer, then integer is the number of 
	  scheduled periods.
	* If no actions are triggered, the artifacts will have their ttl
	  determined by the "dispatch.ttl" attribute in savedsearches.conf.
	* Defaults to 10p 
	* Defaults to 86400 (24 hours)   for: email, rss
	* Defaults to   600 (10 minutes) for: script 
	* Defaults to   120 (2 minutes)  for: summary_index, populate_lookup 
 
maxtime = <integer>[m|s|h|d]
	* The maximum amount of time that the execution of an action
	  is allowed to take before the action is aborted.
	* Use the d, h, m and s suffixes to define the period of time:
	  d = day, h = hour, m = minute and s = second.
	  For example: 5d means 5 days.
	* Defaults to 5m for everything except rss.
	* Defaults to 1m for rss.
 
track_alert = [1|0]
 	* indicates whether the execution of this action signifies a trackable
	  alert.
 	* Defaults to 0 (false).

command = <string>
	* The search command (or pipeline) which is responsible for executing
	  the action.
	* Generally the command is a template search pipeline which is realized
	  with values from the saved search - to reference saved search
	  field values wrap them in dollar signs ($).
	* For example, to reference the savedsearch name use $name$. To
	  reference the search, use $search$

################################################################################
# EMAIL: these settings are prefaced by the [email] stanza name
################################################################################

[email]
	* Set email notification options under this stanza name.
	* Follow this stanza name with any number of the following
	  attribute/value pairs.  
	* If you do not specify an entry for each attribute, Splunk will
	  use the default value.
	
from = <string>
	* Email address from which the alert originates. 
	* Defaults to splunk@$LOCALHOST.

to      = <string>
	* to email address receiving alert.
 
cc      = <string>
	* cc email address receiving alert.

bcc     = <string>
	* bcc email address receiving alert.

message.report = <string>
    * Specify a custom email message for scheduled reports.  
    * Includes the ability to reference attributes from 
    * result, saved search, job

message.alert = <string>
    * Specify a custom email message for alerts.  
    * Includes the ability to reference attributes from 
    * result, saved search, job

subject = <string>
	* Specify an alternate email subject if useNSSubject is false.
	* Defaults to SplunkAlert-<savedsearchname>.  

subject.alert = <string>
	* Specify an alternate email subject for an alert.
	* Defaults to SplunkAlert-<savedsearchname>.  

subject.report = <string>
    * Specify an alternate email subject for a scheduled report.
    * Defaults to SplunkReport-<savedsearchname>. 

useNSSubject = [1|0]
	* Specify whether to use the namespaced subject (i.e subject.report)
	* or subject.

footer.text = <string>
	* Specify an alternate email footer.
	* Defaults to If you believe you've received this email in error, please see your 
	* Splunk administrator.\r\n\r\nsplunk > the engine for machine data.

format = [table|raw|csv]
	* Specify the format of inline results in the email.
	* Acceptable values:  table, raw, and csv.
	* Previously accepted values plain and html are no longer respected
	* and equate to table.
	* All emails are sent as HTML messages with an alternative plain text version.

include.results_link = [1|0]
    * Specify whether to include a link to the results.

include.search = [1|0]
    * Specify whether to include the search that cause 
    * an email to be sent.

include.trigger = [1|0]
    * Specify whether to show the trigger condition that 
    * caused the alert to fire. 

include.trigger_time = [1|0]
    * Specify whether to show the time that the alert
    * was fired. 

include.view_link = [1|0]
    * Specify whether to show the title and a link to 
    * enable the user to edit the saved search. 

sendresults = [1|0]
	* Specify whether the search results are included in the email. The 
	  results can be attached or inline, see inline (action.email.inline)
	* Defaults to 0 (false).
     
inline = [1|0]
	* Specify whether the search results are contained in the body of
	  the alert email.
	* Defaults to 0 (false).
priority = [1|2|3|4|5]
	* Set the priority of the email as it appears in the email client.
	* Value mapping: 1 to highest, 2 to high, 3 to normal, 4 to low, 5 to lowest.
	* Defaults to 3.

mailserver = <host>[:<port>]
	* You must have a Simple Mail Transfer Protocol (SMTP) server available
	  to send email. This is not included with Splunk. 
	* The SMTP mail server to use when sending emails.
	* <host> can be either the hostname or the IP address.
	* Optionally, specify the SMTP <port> that Splunk should connect to.
	* When the "use_ssl" attribute (see below) is set to 1 (true), you
	  must specify both <host> and <port>.
	  (Example: "example.com:465")
	* Defaults to $LOCALHOST:25.
	
use_ssl    = [1|0]
	* Whether to use SSL when communicating with the SMTP server.
	* When set to 1 (true), you must also specify both the server name or
	  IP address and the TCP port in the "mailserver" attribute.
	* Defaults to 0 (false).
	
use_tls    = [1|0]
	* Specify whether to use TLS (transport layer security) when 
	  communicating with the SMTP server (starttls)
	* Defaults to 0 (false).

auth_username   = <string>
	* The username to use when authenticating with the SMTP server. If this
	  is not defined or is set to an empty string, no authentication is
	  attempted.
	  NOTE: your SMTP server might reject unauthenticated emails.
	* Defaults to empty string.

auth_password   = <string>
	* The password to use when authenticating with the SMTP server. 
	  Normally this value will be set when editing the email settings,
	  however you can set a clear text password here and it will be
	  encrypted on the next Splunk restart.
	* Defaults to empty string.

sendpdf = [1|0]
 	* Specify whether to create and send the results as a PDF.
	* Defaults to 0 (false).

sendcsv = [1|0]
 	* Specify whether to create and send the results as a csv file.
	* Defaults to 0 (false).

pdfview = <string>
    * Name of view to send as a PDF

reportServerEnabled = [1|0]
    * Setting was REMOVED in 6.2 GA. Please do not configure

reportServerURL = <url>
    *  Setting was REMOVED in 6.2 GA. Please do not configure

reportPaperSize = [letter|legal|ledger|a2|a3|a4|a5]
	* Default paper size for PDFs
	* Acceptable values: letter, legal, ledger, a2, a3, a4, a5
	* Defaults to "letter".

reportPaperOrientation = [portrait|landscape]
	* Paper orientation: portrait or landscape
	* Defaults to "portrait".

reportIncludeSplunkLogo = [1|0]
    * Specify whether to include a Splunk logo in Integrated PDF Rendering
    * Defaults to 1 (true)

reportCIDFontList = <string>
    * Specify the set (and load order) of CID fonts for handling
      Simplified Chinese(gb), Traditional Chinese(cns), 
      Japanese(jp), and Korean(kor) in Integrated PDF Rendering.
    * Specify in space separated list
    * If multiple fonts provide a glyph for a given character code, the glyph
      from the first font specified in the list will be used
    * To skip loading any CID fonts, specify the empty string
    * Defaults to "gb cns jp kor"

width_sort_columns = <bool>
    * Whether columns should be sorted from least wide to most wide left to right.
    * Valid only if format=text
    * Defaults to true

preprocess_results = <search-string>
	* Supply a search string to Splunk to preprocess results before
	  emailing them. Usually the preprocessing consists of filtering
	  out unwanted internal fields.
	* Defaults to empty string (no preprocessing)
	
################################################################################
# RSS: these settings are prefaced by the [rss] stanza
################################################################################

[rss]
	* Set RSS notification options under this stanza name.
	* Follow this stanza name with any number of the following
	  attribute/value pairs.  
	* If you do not specify an entry for each attribute, Splunk will
	  use the default value.

items_count = <number>
	* Number of saved RSS feeds.
	* Cannot be more than maxresults (in the global settings).
	* Defaults to 30.

################################################################################
# script: Used to configure any scripts that the alert triggers.
################################################################################
[script]
filename = <string>
	* The filename, with no path, of the script to trigger.
	* The script should be located in: $SPLUNK_HOME/bin/scripts/
	* For system shell scripts on Unix, or .bat or .cmd on windows, there
	  are no further requirements.
	* For other types of scripts, the first line should begin with a #!
	  marker, followed by a path to the interpreter that will run the
	  script.
	  * Example: #!C:\Python27\python.exe
	* Defaults to empty string.

################################################################################
# summary_index: these settings are prefaced by the [summary_index] stanza
################################################################################
[summary_index]
inline = [1|0]
       	* Specifies whether the summary index search command will run as part 
	 of the scheduled search or as a follow-on action. This is useful 
	 when the results of the scheduled search are expected to be large.
	* Defaults to 1 (true).

_name = <string>
        * The name of the summary index where Splunk will write the events.
	* Defaults to "summary".
	
################################################################################
# populate_lookup: these settings are prefaced by the [populate_lookup] stanza
################################################################################
[populate_lookup]
dest = <string>
	* the name of the lookup table to populate (stanza name in 
	  transforms.conf) or the lookup file path to where you want the 
	  data written. If a path is specified it MUST be relative to
	  $SPLUNK_HOME and a valid lookups directory.
	  For example: "etc/system/lookups/<file-name>" or 
	  "etc/apps/<app>/lookups/<file-name>"
	* The user executing this action MUST have write permissions 
	  to the app for this action to work properly.
