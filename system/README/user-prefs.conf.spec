# This file describes some of the settings that are used, and
# can be configured on a per-user basis for use by the Splunk Web UI.

# Settings in this file are requested with user and application scope
# of the relevant user, and the user-prefs app.  

# Additionally, settings by the same name which are available in the
# roles the user belongs to will be used at lower precedence.

# This means interactive setting of these values will cause the values
# to be updated in
# $SPLUNK_HOME/etc/users/user-prefs/<username>/local/user-prefs.conf
# where <username> is the username for the user altering their
# preferences.

# It also means that values in another app will never be used unless
# they are exported globally (to system scope) or to the user-prefs
# app.

# In practice, providing values in other apps isn't very interesting,
# since values from the authorize.conf roles settings are more
# typically sensible ways to defaults for values in user-prefs.

[general]

default_namespace = <app name>
* Specifies the app that the user will see initially upon login to the
  Splunk Web User Interface.
* This uses the "short name" of the app, such as launcher, or search,
  which is synonymous with the app directory name.
* Splunk defaults this to 'launcher' via the default authorize.conf

tz = <timezone>
* Specifies the per-user timezone to use
* If unset, the timezone of the Splunk Server or Search Head is used.
* Only canonical timezone names such as America/Los_Angeles should be
  used (for best results use the Splunk UI).
* Defaults to unset.


[default]
# Additional settings exist, but are entirely UI managed.
<setting> = <value>

