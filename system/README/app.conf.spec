#   Version 6.2.6 
#
# This file maintains the state of a given app in Splunk Enterprise. It may also be used
# to customize certain aspects of an app.
#
# There is no global, default app.conf. Instead, an app.conf may exist in each
# app in Splunk Enterprise.
#
# You must restart Splunk Enterprise to reload manual changes to app.conf.
#
# To learn more about configuration files (including precedence) please see the documentation
# located at http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles

#
# Settings for how this app appears in Launcher (and online on Splunkbase)
#

[launcher]

# global setting

remote_tab = <bool>
* Set whether the Launcher interface will connect to splunkbase.splunk.com.
* This setting only applies to the Launcher app and should be not set in any other app
* Defaults to true.

# per-application settings

version = <version string>
* Version numbers are a number followed by a sequence of dots and numbers.
* Version numbers for releases should use three digits.
* Pre-release versions can append a single-word suffix like "beta" or "preview."
* Pre-release designations should use lower case and no spaces.
* Examples:
*    1.2.0
*    3.2.1
*    11.0.34
*    2.0beta
*    1.3beta2
*    1.0preview

description = <string>
* Short explanatory string displayed underneath the app's title in Launcher.
* Descriptions should be 200 characters or less because most users won't read long descriptions!

author = <name>
* For apps you intend to post to Splunkbase, enter the username of your splunk.com account.
* For internal-use-only apps, include your full name and/or contact info (e.g. email).

# Your app can include an icon which will show up next to your app
# in Launcher and on Splunkbase. You can also include a screenshot,
# which will show up on Splunkbase when the user views info about your
# app before downloading it. Icons are recommended, although not required.
# Screenshots are optional.
#
# There is no setting in app.conf for these images. Instead, icon and
# screenshot images should be placed in the appserver/static dir of
# your app. They will automatically be detected by Launcher and Splunkbase.
#
# For example:
#
#     <app_directory>/appserver/static/appIcon.png    (the capital "I" is required!)
#     <app_directory>/appserver/static/screenshot.png
#
# An icon image must be a 36px by 36px PNG file.
# An app screenshot must be 623px by 350px PNG file.


#
# [package] defines upgrade-related metadata, and will be
# used in future versions of Splunk Enterprise to streamline app upgrades.
#

[package]

id = <appid>
* id should be omitted for internal-use-only apps which are not intended
    to be uploaded to Splunkbase
* id is required for all new apps uploaded to Splunkbase. Future versions
    of Splunk Enterprise will use appid to correlate locally-installed apps and
    the same app on Splunkbase (e.g. to notify users about app updates)
* id must be the same as the folder name in which your app lives in $SPLUNK_HOME/etc/apps
* id must adhere to cross-platform folder-name restrictions:
  - must contain only letters, numbers, "." (dot), and "_" (underscore) characters
  - must not end with a dot character
  - must not be any of the following names: CON, PRN, AUX, NUL,
      COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9,
      LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9

check_for_updates = <bool>
* Set whether Splunk Enterprise should check Splunkbase for updates to this app.
* Defaults to true.


#
# Set install settings for this app
#

[install]

state = disabled | enabled
* Set whether app is disabled or enabled.
* If an app is disabled, its configs are ignored.
* Defaults to enabled.

state_change_requires_restart = true | false
* Set whether changing an app's state ALWAYS requires a restart of Splunk Enterprise.
* State changes include enabling or disabling an app.
* When set to true, changing an app's state always requires a restart.
* When set to false, modifying an app's state may or may not require a restart
  depending on what the app contains. This setting cannot be used to avoid all
  restart requirements!
* Defaults to false.

is_configured = true | false
* Stores indication of whether the application's custom setup has been performed
* Defaults to false

build = <integer>
* Required.
* Must be a positive integer.
* Increment this whenever you change files in appserver/static.
* Every release must change both "version" and "build" settings.
* Ensures browsers don't use cached copies of old static files
  in new versions of your app.
* Build is a single integer, unlike version which can be a complex string
  like 1.5.18.

allows_disable = true | false
* Set whether an app allows itself to be disabled.
* Defaults to true.

install_source_checksum = <string>
* Optional.
* Records a checksum of the tarball from which a given app was installed.
* Splunk will automatically populate this value upon install; there is no need
  to set it explicitly within your app.

#
# Handle reloading of custom .conf files (4.2+ versions only)
#

[triggers]

reload.<conf_file_name> = [ simple | rest_endpoints | access_endpoints <handler_url> ]
* Splunk Enterprise will reload app configuration after every 
  app-state change: install, update, enable, and disable.
* If your app does not use a custom config file (e.g. myconffile.conf) 
  then it won't need a [triggers] stanza, because 
  $SPLUNK_HOME/etc/system/default/app.conf already includes a [triggers]
  stanza which automatically reloads config files normally used by Splunk Enterprise.
* If your app uses a custom config file (e.g. myconffile.conf) and you want to 
  avoid unnecessary Splunk Enterprise restarts, you'll need to add a reload value in
  the [triggers] stanza.
* If you don't include [triggers] settings and your app uses a custom 
  config file, a Splunk Enterprise restart will be required after every state change.
* Specifying "simple" implies that Splunk Enterprise will take no special action to reload 
  your custom conf file.
* Specify "access_endpoints" and a URL to a REST endpoint, and Splunk Enterprise will call
  its _reload() method at every app state change.
* "rest_endpoints" is reserved for Splunk Enterprise internal use for reloading 
  restmap.conf.

* Examples: 

        [triggers]
        # Do not force a restart of Splunk Enterprise for state changes of MyApp
        # Do not run special code to tell MyApp to reload myconffile.conf
        # Apps with custom config files will usually pick this option
        reload.myconffile = simple

        # Do not force a restart of Splunk Enterprise for state changes of MyApp.
        # Splunk Enterprise calls the /admin/myendpoint/_reload method
        # in my custom EAI handler.
        # Use this advanced option only if MyApp requires custom code to reload 
        # its configuration when its state changes
        reload.myotherconffile = access_endpoints /admin/myendpoint  

#
# Set UI-specific settings for this app
#

[ui]

is_visible = true | false
* Indicates if this app should be visible/navigable as a UI app
* Apps require at least 1 view to be available from the UI

is_manageable = true | false
* This setting is deprecated. It no longer has any effect.
    
label = <string>
* Defines the name of the app shown in the Splunk GUI and Launcher
* Recommended length between 5 and 80 characters.
* Must not include "Splunk For" prefix.
* Label is required.
* Examples of good labels:
    IMAP Monitor
    SQL Server Integration Services
    FISMA Compliance
  
docs_section_override = <string>
* Defines override for auto-generated app-specific documentation links
* If not specified, app-specific documentation link will include [<app-name>:<app-version>]
* If specified, app-specific documentation link will include [<docs_section_override>]
* This only applies to apps with documentation on the Splunk documentation site

#
# Credential-verification scripting (4.2+ versions only)
#

[credentials_settings]
verify_script = <string>
 * Optional setting.
 * Command line to invoke to verify credentials used for this app.
 * For scripts, the command line should include both the interpreter and the script for it to run.
    * Example: "$SPLUNK_HOME/bin/python" "$SPLUNK_HOME/etc/apps/<myapp>/bin/$MY_SCRIPT"
 * The invoked program is communicated with over standard in / standard out via the same protocol as splunk scripted auth.
 * Paths incorporating variable expansion or explicit spaces must be quoted.
    * For example, a path including $SPLUNK_HOME should be quoted, as likely will expand to C:\Program Files\Splunk

[credential:<realm>:<username>]
password = <string>
* Password that corresponds to the given username for the given realm. Note that realm is optional
* The password can be in clear text, however when saved from splunkd the password will always be encrypted
    
    
    
