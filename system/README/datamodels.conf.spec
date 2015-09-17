#   Version 6.2.6 
#
# This file contains possible attribute/value pairs for configuring datamodels.
# To configure a datamodel for an app, put your custom datamodels.conf in
# $SPLUNK_HOME/etc/apps/MY_APP/local/

# For examples, see datamodels.conf.example.  You must restart Splunk to enable configurations.

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


[<datamodel_name>]
        * Each stanza represents a datamodel; the datamodel name is the stanza name.

acceleration = <bool>
        * Set this to true to enable automatic acceleration of this datamodel
        * Automatic acceleration will create auxiliary column stores for the fields and
          values in the events for this datamodel on a per-bucket basis.
        * These column stores take additional space on disk so be sure you have the
          proper amount of disk space. Additional space required depends on the number
          of events, fields, and distinct field values in the data.
        * These column stores are created and maintained on a schedule you can specify with
          'acceleration.cron_schedule', and can be later queried with the 'tstats' command

acceleration.earliest_time = <relative-time-str>
        * Specifies how far back in time Splunk should keep these column stores (and create if
          acceleration.backfill_time is not set)
        * Specified by a relative time string, e.g. '-7d' accelerate data within the last 7 days
        * Defaults to the empty string, meaning keep these stores for all time

acceleration.backfill_time = <relative-time-str>
       * ADVANCED: Specifies how far back in time Splunk should create these column stores
       * ONLY set this parameter if you want to backfill less data than your retention period
         set by 'acceleration.earliest_time'. You may want to use this to limit your time window for
         creation in a large environment where initially creating all of the stores is an expensive
         operation.
       * WARNING: If one of your indexers is down for a period longer than this backfill time, you
         may miss accelerating a window of your incoming data. It is for this reason we do not recommend
         setting this to a small window.
       * MUST be set to a more recent time than acceleration.earliest_time. For example, if earliest
         time is set to '-1y' to keep the stores for a 1 year window, you could set backfill to
         '-20d' to only create stores for data from the last 20 days. However, you could not set
         backfill to '-2y', as that's farther back in time than '-1y'
       * If empty or unset (default), Splunk will always backfill fully to acceleration.earliest_time

acceleration.max_time = <unsigned int>
       * The maximum amount of time that the column store creation search is allowed to run (in seconds)
       * Note that this is an approximate time, as the 'summarize' search will only finish on clean bucket
         boundaries to avoid wasted work
       * Defaults to: 3600
       * 0 implies no limit

acceleration.cron_schedule = <cron-string>
        * Cron schedule to be used to probe/generate the column stores for this datamodel

acceleration.manual_rebuilds = <bool>
       * This is an ADVANCED command.  
       * Normally, the 'summarize' command will automatically rebuild summaries during the creation
         phase that are considered to be out of-date, such as when the configuration backing the
         data model changes.
           * A summary being out of date implies that the datamodel search stored in the metadata
             for this summary no longer matches the current datamodel search, OR the search in the
             metadata can no longer be parsed.

       * If set to true, out-of-date summaries are not rebuilt by the 'summarize' command.
       * NOTE: If we find a partial summary be out of date, we will always rebuild that summary so
         that a bucket summary only has results corresponding to one datamodel search.
       * Defaults to false
