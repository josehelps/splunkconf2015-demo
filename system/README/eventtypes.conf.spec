#   Version 6.2.6 
#
# This file contains all possible attributes and value pairs for an eventtypes.conf file.  
# Use this file to configure event types and their properties. You can also pipe any search
# to the "typelearner" command to create event types.  Event types created this way will be written
# to $SPLUNK_HOME/etc/systems/local/eventtypes.conf.
#
# There is an eventtypes.conf in $SPLUNK_HOME/etc/system/default/.  To set custom configurations, 
# place an eventtypes.conf in $SPLUNK_HOME/etc/system/local/. For examples, see 
# eventtypes.conf.example. You must restart Splunk to enable configurations.
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

[<$EVENTTYPE>]
* Header for the event type
* $EVENTTYPE is the name of your event type.
* You can have any number of event types, each represented by a stanza and any number of the following 
attribute/value pairs.  
* NOTE: If the name of the event type includes field names surrounded by the percent 
character (for example "%$FIELD%") then the value of $FIELD is substituted into the event type
name for that event.  For example, an event type with the header [cisco-%code%] that has
"code=432" becomes labeled "cisco-432".

disabled = [1|0]
* Toggle event type on or off.
* Set to 0 to disable.
	
search = <string>
* Search terms for this event type. 
* For example: error OR warn.

priority = <integer, 1 through 10>
* Value used to determine the order in which the matching eventtypes of an event are displayed.  
* 1 is the highest and 10 is the lowest priority. 

description = <string>
* Optional human-readable description of this saved search.

tags = <string>
* DEPRECATED - see tags.conf.spec
