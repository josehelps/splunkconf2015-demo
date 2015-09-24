#   Version 6.2.6 
#
# This file contains all possible options for an indexes.conf file.  Use this file to configure 
# Splunk's indexes and their properties.
#
# There is an indexes.conf in $SPLUNK_HOME/etc/system/default/.  To set custom configurations, 
# place an indexes.conf in $SPLUNK_HOME/etc/system/local/. For examples, see 
# indexes.conf.example. You must restart Splunk to enable configurations.
#
# To learn more about configuration files (including precedence) please see the documentation 
# located at http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles
#
# CAUTION:  You can drastically affect your Splunk installation by changing these settings.  
# Consult technical support (http://www.splunk.com/page/submit_issue) if you are not sure how 
# to configure this file.
#
# DO NOT change the attribute QueryLanguageDefinition without consulting technical support.

# GLOBAL SETTINGS
# Use the [default] stanza to define any global settings.
#     * You can also define global settings outside of any stanza, at the top of the file.
#     * Each conf file should have at most one default stanza. If there are multiple default
#       stanzas, attributes are combined. In the case of multiple definitions of the same
#       attribute, the last definition in the file wins.
#     * If an attribute is defined at both the global level and in a specific stanza, the
#       value in the specific stanza takes precedence.

sync = <nonnegative integer>
	* The index processor syncs events every <integer> number of events.
	* Set to 0 to disable.
	* Defaults to 0.
	* Highest legal value is 32767

defaultDatabase = <index name>
	* If no index is specified during search, Splunk searches the default index.
	* The specified index displays as the default in Splunk Manager settings.
	* Defaults to "main".
  	
queryLanguageDefinition = <path to file>
	* DO NOT EDIT THIS SETTING. SERIOUSLY. 
	* The path to the search language definition file.
	* Defaults to $SPLUNK_HOME/etc/searchLanguage.xml.

blockSignatureDatabase = <index name>
    * Setting was REMOVED in 6.2 GA. Please do not configure

memPoolMB = <positive integer>|auto
	* Determines how much memory is given to the indexer memory pool. This restricts the number of outstanding events in the indexer at any given time.
	* Must be greater than 0; maximum value is 1048576 (which corresponds to 1 TB)
	* Setting this too high can lead to splunkd memory usage going up substantially.
	* Setting this too low can degrade splunkd indexing performance.
	* Setting this to "auto" or an invalid value will cause Splunk to autotune this parameter.
	* Defaults to "auto".
 	  * The values derived when "auto" is seen are as follows:
 	    * System Memory Available less than ... | memPoolMB
                           1 GB                     |    64  MB
                           2 GB                     |    128 MB
                           8 GB                     |    128 MB
                           8 GB or higher           |    512 MB
	* Only set this value if you are an expert user or have been advised to by Splunk Support.
	* CARELESSNESS IN SETTING THIS MAY LEAD TO PERMANENT BRAIN DAMAGE OR LOSS OF JOB.

indexThreads = <nonnegative integer>|auto
	* Determines the number of threads to use for indexing.
	* Must be at least 1 and no more than 16.
	* This value should not be set higher than the number of processor cores in the box.
	* If splunkd is also doing parsing and aggregation, the number should be set lower than the total number of 
	  processors minus two.
	* Setting this to "auto" or an invalid value will cause Splunk to autotune this parameter.
	* Defaults to "auto".
	* Only set this value if you are an expert user or have been advised to by Splunk Support.
	* CARELESSNESS IN SETTING THIS MAY LEAD TO PERMANENT BRAIN DAMAGE OR LOSS OF JOB.

assureUTF8 = true|false
	* Verifies that all data retrieved from the index is proper UTF8.
	* Will degrade indexing performance when enabled (set to true).
	* Can only be set globally, by specifying in the [default] stanza.
	* Defaults to false.

enableRealtimeSearch = true|false
	* Enables real-time searches.
	* Defaults to true.

suppressBannerList = <comma-separated list of strings>
	* suppresses index missing warning banner messages for specified indexes
	* Defaults to empty

maxRunningProcessGroups = <positive integer>
	* splunkd fires off helper child processes like splunk-optimize, recover-metadata, etc.  This param limits how many child processes can be running at any given time.
	* This maximum applies to entire splunkd, not per index.  If you have N indexes, there will be at most maxRunningProcessGroups child processes, not N*maxRunningProcessGroups
	* Must maintain maxRunningProcessGroupsLowPriority < maxRunningProcessGroups
	* This is an advanced parameter; do NOT set unless instructed by Splunk Support
	* Defaults to 8 (note: up until 5.0 it defaulted to 20)
	* Highest legal value is 4294967295

maxRunningProcessGroupsLowPriority = <positive integer>
	* Of the maxRunningProcessGroups (q.v.) helper child processes, at most maxRunningProcessGroupsLowPriority may be low-priority (e.g. fsck) ones.
	* This maximum applies to entire splunkd, not per index.  If you have N indexes, there will be at most maxRunningProcessGroupsLowPriority low-priority child processes, not N*maxRunningProcessGroupsLowPriority
	* Must maintain maxRunningProcessGroupsLowPriority < maxRunningProcessGroups
	* This is an advanced parameter; do NOT set unless instructed by Splunk Support
	* Defaults to 1
	* Highest legal value is 4294967295

bucketRebuildMemoryHint = <positive integer>[KB|MB|GB]|auto
        * Suggestion for the bucket rebuild process for the size (bytes) of tsidx file it will try to build.
        * Larger files use more memory in rebuild, but rebuild will fail if there is not enough.
        * Smaller files make the rebuild take longer during the final optimize step.
        * Note: this value is not a hard limit on either rebuild memory usage or tsidx size.
        * This is an advanced parameter, do NOT set this unless instructed by Splunk Support.
        * Defaults to "auto", which varies by the amount of physical RAM on the host
        *    less than 2GB RAM = 67108864 (64MB) tsidx
        *    2GB to 8GB RAM = 134217728 (128MB) tsidx
        *    more than 8GB RAM = 268435456 (256MB) tsidx
        * If not "auto", then must be 16MB-1GB.
        * Value may be specified using a size suffix: "16777216" or "16MB" are equivalent.
        * Inappropriate use of this parameter will cause splunkd to not start if rebuild is required.
        * Highest legal value (in bytes) is 4294967295

inPlaceUpdates = true|false
        * If true, metadata updates are written to the .data files directly
        * If false, metadata updates are written to a temporary file and then moved into place
        * Intended for advanced debugging of metadata issues
        * Setting this parameter to false (to use a temporary file) will impact indexing 
          performance, particularly with large numbers of hosts, sources, or sourcetypes 
          (~1 million, across all indexes.)
        * This is an advanced parameter; do NOT set unless instructed by Splunk Support
        * Defaults to true

serviceOnlyAsNeeded = true|false
	* Causes index service (housekeeping tasks) overhead to be incurred only after index activity.
	* Indexer module problems may be easier to diagnose when this optimization is disabled (set to false).
	* Defaults to true.

serviceSubtaskTimingPeriod = <positive integer>
	* Subtasks of indexer service task will be timed on every Nth execution, where N = value of this parameter.
	* Smaller values will give greater accuracy; larger values will lessen timer overhead.
	* Timer measurements will be found in metrics.log, marked "group=subtask_seconds, task=indexer_service"
	* In seconds.
	* Defaults to 30
	* Highest legal value is 4294967295
	* We strongly suggest value of this parameter divide evenly into value of 'rotatePeriodInSecs' parameter.

processTrackerServiceInterval = <nonnegative integer>
	* Controls how often indexer checks status of the child OS processes it had launched to see if it can launch new processes for queued requests.
	* In seconds.
	* If set to 0, indexer will check child process status every second.
	* Defaults to 15
	* Highest legal value is 4294967295

maxBucketSizeCacheEntries = <nonnegative integer>
	* This value is not longer needed and its value is ignored.

tsidxStatsHomePath = <path on server>
        * An absolute path that specifies where Splunk creates namespace data with 'tscollect' command
        * If the directory does not exist, we attempt to create it
        * Optional. If this is unspecified, we default to the 'tsidxstats' directory under $SPLUNK_DB

hotBucketTimeRefreshInterval = <positive integer>
        * Controls how often each index refreshes the available hot bucket
          times used by the indexes REST endpoint.
        * Refresh will occur every N times service is performed for each index.
          * For busy indexes, this is a mutiple of seconds.
          * For idle indexes, this is a multiple of the second-long-periods in
            which data is received.
        * This tunable is only intended to relax the frequency of these
          refreshes in the unexpected case that it adversely affects
          performance in unusual production scenarios.
        * This time is tracked on a per-index basis, and thus can be adjusted
          on a per-index basis if needed.
        * If, for some reason, you want have the index information refreshed
          with every service (and accept minor performance overhead), you can
          use the value 1.
        * Defaults to 10 (services).

#******************************************************************************
# PER INDEX OPTIONS
# These options may be set under an [<index>] entry.
#
# Index names must consist of only numbers, letters, periods, underscores, and hyphens. 
#******************************************************************************

disabled = true|false
	* Toggles your index entry off and on.
	* Set to true to disable an index.
	* Defaults to false.

deleted = true
	* If present, means that this index has been marked for deletion: if splunkd is running,
	  deletion is in progress; if splunkd is stopped, deletion will re-commence on startup.
	* Normally absent, hence no default.
	* Do NOT manually set, clear, or modify value of this parameter.
	* Seriously: LEAVE THIS PARAMETER ALONE.

homePath = <path on index server>
	* An absolute path that contains the hotdb and warmdb for the index. 
	* Splunkd keeps a file handle open for warmdbs at all times.
	* May contain a volume reference (see volume section below).
	* CAUTION: Path MUST be writable.
	* Required. Splunk will not start if an index lacks a valid homePath.
	* Must restart splunkd after changing this parameter; index reload will not suffice.

coldPath = <path on index server>
	* An absolute path that contains the colddbs for the index. 
	* Cold databases are opened as needed when searching.
	* May contain a volume reference (see volume section below).
	* CAUTION: Path MUST be writable.
	* Required. Splunk will not start if an index lacks a valid coldPath.
	* Must restart splunkd after changing this parameter; index reload will not suffice.

thawedPath = <path on index server>
	* An absolute path that contains the thawed (resurrected) databases for the index.
	* May NOT contain a volume reference.
	* Required. Splunk will not start if an index lacks a valid thawedPath.
	* Must restart splunkd after changing this parameter; index reload will not suffice.

bloomHomePath = <path on index server>
    * Location where the bloomfilter files for the index are stored.
	* If specified, MUST be defined in terms of a volume definition (see volume section below)
	* If bloomHomePath is not specified, bloomfilter files for index will be stored inline,
		inside bucket directories.
	* CAUTION: Path must be writable.
	* Must restart splunkd after changing this parameter; index reload will not suffice.

createBloomfilter = true|false
       * Controls whether to create bloomfilter files for the index.
       * TRUE: bloomfilter files will be created. FALSE: not created.
       * Defaults to true.

summaryHomePath = <path on index server>
       * An absolute path where transparent summarization results for data in this index 
         should be stored. Must be different for each index and may be on any disk drive. 
       * May contain a volume reference (see volume section below).
       * Volume reference must be used if data retention based on data size is desired.
       * If not specified it defaults to a directory 'summary' in the same location as homePath
          * For example, if homePath is "/opt/splunk/var/lib/splunk/index1/db",
            then summaryHomePath would be "/opt/splunk/var/lib/splunk/index1/summary".
       * CAUTION: Path must be writable.
       * Must restart splunkd after changing this parameter; index reload will not suffice.

tstatsHomePath = <path on index server>
       * Location where datamodel acceleration TSIDX data for this index should be stored
       * If specified, MUST be defined in terms of a volume definition (see volume section below)
       * If not specified it defaults to volume:_splunk_summaries/$_index_name/datamodel_summary,
         where $_index_name is the name of the index
       * CAUTION: Path must be writable.
       * Must restart splunkd after changing this parameter; index reload will not suffice.

maxBloomBackfillBucketAge = <nonnegative integer>[smhd]|infinite
       * If a (warm or cold) bloomfilter-less bucket is older than this, we shall not create its bloomfilter when we come across it
       * Defaults to 30d.
       * When set to 0, bloomfilters are never backfilled
       * When set to "infinite", bloomfilters are always backfilled
       * NB that if createBloomfilter=false, bloomfilters are never backfilled regardless of the value of this parameter
       * Highest legal value in computed seconds is 2 billion, or 2000000000, which is approximately 68 years.

enableOnlineBucketRepair = true|false
	* Controls asynchronous "online fsck" bucket repair, which runs concurrently with Splunk
	* When enabled, you do not have to wait until buckets are repaired, to start Splunk
	* When enabled, you might observe a slight performance degradation
    * Defaults to true.

# The following options can be set either per index or globally (as defaults for all indexes).
# Defaults set globally are overridden if set on a per-index basis.

maxWarmDBCount = <nonnegative integer>
	* The maximum number of warm buckets.
	* Warm buckets are located in the <homePath> for the index. 
	* If set to zero, it will not retain any warm buckets (will roll them to cold as soon as it can)
	* Defaults to 300.
	* Highest legal value is 4294967295

maxTotalDataSizeMB = <nonnegative integer>
	* The maximum size of an index (in MB). 
	* If an index grows larger than the maximum size, the oldest data is frozen.
	* This parameter only applies to hot, warm, and cold buckets.  It does not apply to thawed buckets.
	* Defaults to 500000.
	* Highest legal value is 4294967295

rotatePeriodInSecs = <positive integer>
	* Controls the service period (in seconds): how often splunkd performs certain housekeeping tasks.  Among these tasks are:
	*	* Check if a new hotdb needs to be created.
	*	* Check if there are any cold DBs that should be frozen.
	* 	* Check whether buckets need to be moved out of hot and cold DBs, due to respective
		  size constraints (i.e., homePath.maxDataSizeMB and coldPath.maxDataSizeMB)
    * This value becomes the default value of the rotatePeriodInSecs attribute for all volumes (see rotatePeriodInSecs in the Volumes section)
	* Defaults to 60.
	* Highest legal value is 4294967295

frozenTimePeriodInSecs = <nonnegative integer>
	* Number of seconds after which indexed data rolls to frozen.
	* If you do not specify a coldToFrozenScript, data is deleted when rolled to frozen.
	* IMPORTANT: Every event in the DB must be older than frozenTimePeriodInSecs before it will roll. Then, the DB 
	  will be frozen the next time splunkd checks (based on rotatePeriodInSecs attribute).
	* Defaults to 188697600 (6 years).
	* Highest legal value is 4294967295

warmToColdScript = <script path> 
	* Specifies a script to run when moving data from warm to cold. 
	* This attribute is supported for backwards compatibility with versions older than 4.0.  Migrating data across 
	  filesystems is now handled natively by splunkd.  
	* If you specify a script here, the script becomes responsible for moving the event data, and Splunk-native data 
	  migration will not be used.
	* The script must accept two arguments:
	 * First: the warm directory (bucket) to be rolled to cold.
	 * Second: the destination in the cold path.
	* Searches and other activities are paused while the script is running.
	* Contact Splunk Support (http://www.splunk.com/page/submit_issue) if you need help configuring this setting.
	* The script must be in $SPLUNK_HOME/bin or a subdirectory thereof.
	* Defaults to empty.

coldToFrozenScript = [path to script interpreter] <path to script>
        * Specifies a script to run when data will leave the splunk index system.  
          * Essentially, this implements any archival tasks before the data is
            deleted out of its default location.
        * Add "$DIR" (quotes included) to this setting on Windows (see below
          for details).
        * Script Requirements:
          * The script must accept one argument:
            * An absolute path to the bucket directory to archive.
          * Your script should work reliably.
            * If your script returns success (0), Splunk will complete deleting
              the directory from the managed index location.
            * If your script return failure (non-zero), Splunk will leave the
              bucket in the index, and try calling your script again several
              minutes later.  
            * If your script continues to return failure, this will eventually
              cause the index to grow to maximum configured size, or fill the
              disk.
          * Your script should complete in a reasonable amount of time.
            * If the script stalls indefinitely, it will occupy slots.
            * These slots will not be available for other freeze scripts.
            * This means that a stalling script for index1 may prevent freezing
              of index2.
        * If the string $DIR is present in this setting, it will be expanded to
          the absolute path to the directory.  
        * If $DIR is not present, the directory will be added to the end of the
          invocation line of the script.
          * This is important for Windows.  
            * For historical reasons, the entire string is broken up by
              shell-pattern expansion rules.
            * Since windows paths frequently include spaces, and the windows
              shell breaks on space, the quotes are needed for the script to
              understand the directory.
        * If your script can be run directly on your platform, you can specify
          just the script.
          * Examples of this are:
            * .bat and .cmd files on Windows
            * scripts set executable on UNIX with a #! shebang line pointing to
              a valid interpreter.
        * You can also specify an explicit path to an interpreter and the script.
            * Example:  /path/to/my/installation/of/python.exe path/to/my/script.py

        * Splunk ships with an example archiving script in that you SHOULD NOT USE
          $SPLUNK_HOME/bin called coldToFrozenExample.py
          * DO NOT USE the example for production use, because:
            * 1 - It will be overwritten on upgrade.
            * 2 - You should be implementing whatever requirements you need in
                  a script of your creation.  If you have no such requirements,
                  use coldToFrozenDir
        * Example configuration: 
            * If you create a script in bin/ called our_archival_script.py, you could use:
            UNIX:
                coldToFrozenScript = "$SPLUNK_HOME/bin/python" "$SPLUNK_HOME/bin/our_archival_script.py"
            Windows:
                coldToFrozenScript = "$SPLUNK_HOME/bin/python" "$SPLUNK_HOME/bin/our_archival_script.py" "$DIR"
        * The example script handles data created by different versions of
          splunk differently. Specifically data from before 4.2 and after are
          handled differently. See "Freezing and Thawing" below:
        * The script must be in $SPLUNK_HOME/bin or a subdirectory thereof.

coldToFrozenDir = <path to frozen archive>
        * An alternative to a coldToFrozen script - simply specify a destination path for the frozen archive
        * Splunk will automatically put frozen buckets in this directory
        * For information on how buckets created by different versions are
          handled, see "Freezing and Thawing" below.
        * If both coldToFrozenDir and coldToFrozenScript are specified, coldToFrozenDir will take precedence
	* Must restart splunkd after changing this parameter; index reload will not suffice.
	* May NOT contain a volume reference.

# Freezing and Thawing (this should move to web docs
4.2 and later data:  
  * To archive: remove files except for the rawdata directory, since rawdata
    contains all the facts in the bucket.
  * To restore: run splunk rebuild <bucket_dir> on the archived bucket, then
    atomically move the bucket to thawed for that index
4.1 and earlier data:
  * To archive: gzip the .tsidx files, as they are highly compressable but not
    recreateable
  * To restore: unpack the tsidx files within the bucket, then atomically move
    the bucket to thawed for that index

compressRawdata = true|false
	* This parameter is ignored. The splunkd process always compresses raw data.

maxConcurrentOptimizes = <nonnegative integer>
	* The number of concurrent optimize processes that can run against the hot DB.
	* This number should be increased if: 
	  * There are always many small tsidx files in the hot DB.
	  * After rolling, there are many tsidx files in warm or cold DB.
	* Must restart splunkd after changing this parameter; index reload will not suffice.
	* Defaults to 6
	* Highest legal value is 4294967295

maxDataSize = <positive integer>|auto|auto_high_volume
	* The maximum size in MB for a hot DB to reach before a roll to warm is triggered.
	* Specifying "auto" or "auto_high_volume" will cause Splunk to autotune this parameter (recommended).
	* You should use "auto_high_volume" for high-volume indexes (such as the main
	  index); otherwise, use "auto".  A "high volume index" would typically be
	  considered one that gets over 10GB of data per day.
	* Defaults to "auto", which sets the size to 750MB.
	* "auto_high_volume" sets the size to 10GB on 64-bit, and 1GB on 32-bit systems.
	* Although the maximum value you can set this is 1048576 MB, which corresponds to 1 TB, a reasonable 
	  number ranges anywhere from 100 to 50000.  Before proceeding with any higher value, please seek
      approval of Splunk Support.
	* If you specify an invalid number or string, maxDataSize will be auto tuned.
	* NOTE: The maximum size of your warm buckets may slightly exceed 'maxDataSize', due to post-processing and 
	  timing issues with the rolling policy.

rawFileSizeBytes = <positive integer>
        * Deprecated in version 4.2 and later. We will ignore this value.
        * Rawdata chunks are no longer stored in individual files.
        * If you really need to optimize the new rawdata chunks (highly unlikely), edit rawChunkSizeBytes

rawChunkSizeBytes = <positive integer>
	* Target uncompressed size in bytes for individual raw slice in the rawdata journal of the index.
	* Defaults to 131072 (128KB).
	* If 0 is specified, rawChunkSizeBytes will be set to the default value.
	* NOTE: rawChunkSizeBytes only specifies a target chunk size. The actual chunk size may be slightly larger 
	  by an amount proportional to an individual event size.
	* WARNING: This is an advanced parameter. Only change it if you are instructed to do so by Splunk Support.
	* Must restart splunkd after changing this parameter; index reload will not suffice.
	* Highest legal value is 18446744073709551615

minRawFileSyncSecs = <nonnegative decimal>|disable
	* How frequently we force a filesystem sync while compressing journal slices.  During this
	  interval, uncompressed slices are left on disk even after they are compressed.  Then we
	  force a filesystem sync of the compressed journal and remove the accumulated uncompressed files.
	* If 0 is specified, we force a filesystem sync after every slice completes compressing.
	* Specifying "disable" disables syncing entirely: uncompressed slices are removed as soon as compression is complete
	* Defaults to "disable".
	* Some filesystems are very inefficient at performing sync operations, so only enable this if
	  you are sure it is needed
	* Must restart splunkd after changing this parameter; index reload will not suffice.
	* No exponent may follow the decimal.
	* Highest legal value is 18446744073709551615

maxMemMB = <nonnegative integer>
	* The amount of memory to allocate for indexing. 
	* This amount of memory will be allocated PER INDEX THREAD, or, if indexThreads is set to 0, once per index.
	* IMPORTANT:  Calculate this number carefully. splunkd will crash if you set this number higher than the amount
	  of memory available.
	* Defaults to 5.
	* The default is recommended for all environments.
	* Highest legal value is 4294967295
   
blockSignSize = <nonnegative integer>
    * Setting was REMOVED in 6.2 GA. Please do not configure

maxHotSpanSecs = <positive integer>
	* Upper bound of timespan of hot/warm buckets in seconds.
	* Defaults to 7776000 seconds (90 days).
	* NOTE: If you set this too small, you can get an explosion of hot/warm
	  buckets in the filesystem.
	* If you set this parameter to less than 3600, it will be automatically reset to
      3600, which will then activate snapping behavior (see below).
	* This is an advanced parameter that should be set
	  with care and understanding of the characteristics of your data.
	* If set to 3600 (1 hour), or 86400 (1 day), becomes also the lower bound
	  of hot bucket timespans.  Further, snapping behavior (i.e. ohSnap)
	  is activated, whereby hot bucket boundaries will be set at exactly the hour
	  or day mark, relative to local midnight.
	* Highest legal value is 4294967295

maxHotIdleSecs = <nonnegative integer>
	* Provides a ceiling for buckets to stay in hot status without receiving any data.
	* If a hot bucket receives no data for more than maxHotIdleSecs seconds, Splunk rolls it to warm.
	* This setting operates independently of maxHotBuckets, which can also cause hot buckets to roll.
	* A value of 0 turns off the idle check (equivalent to infinite idle time).
	* Defaults to 0.
	* Highest legal value is 4294967295

maxHotBuckets = <positive integer>
	* Maximum hot buckets that can exist per index.
	* When maxHotBuckets is exceeded, Splunk rolls the least recently used (LRU) hot bucket to warm.
	* Both normal hot buckets and quarantined hot buckets count towards this total.
	* This setting operates independently of maxHotIdleSecs, which can also cause hot buckets to roll.
	* Defaults to 3.
	* Highest legal value is 4294967295

quarantinePastSecs = <positive integer>
	* Events with timestamp of quarantinePastSecs older than "now" will be
	  dropped into quarantine bucket.
	* Defaults to 77760000 (900 days).
	* This is a mechanism to prevent the main hot buckets from being polluted with
	  fringe events.
	* Highest legal value is 4294967295

quarantineFutureSecs = <positive integer>
	* Events with timestamp of quarantineFutureSecs newer than "now" will be
	  dropped into quarantine bucket.
	* Defaults to 2592000 (30 days).
	* This is a mechanism to prevent main hot buckets from being polluted with
	  fringe events.
	* Highest legal value is 4294967295

maxMetaEntries = <nonnegative integer>
        * Sets the maximum number of unique lines in .data files in a bucket, which may help to reduce memory consumption
        * If exceeded, a hot bucket is rolled to prevent further increase
        * If your buckets are rolling due to Strings.data hitting this limit, the culprit may be the 'punct' field
          in your data.  If you do not use punct, it may be best to simply disable this (see props.conf.spec)
        * There is a delta between when maximum is exceeded and bucket is rolled.
          This means a bucket may end up with epsilon more lines than specified, 
          but this is not a major concern unless excess is significant
        * If set to 0, this setting is ignored (it is treated as infinite)
		* Highest legal value is 4294967295

syncMeta = true|false
	* When "true", a sync operation is called before file descriptor is closed on metadata file updates.
	* This functionality was introduced to improve integrity of metadata files, especially in regards 
	  to operating system crashes/machine failures.
	* Defaults to true.
	* NOTE: Do not change this parameter without the input of a Splunk support professional.
	* Must restart splunkd after changing this parameter; index reload will not suffice.

serviceMetaPeriod = <positive integer>
	* Defines how frequently metadata is synced to disk, in seconds.
	* Defaults to 25 (seconds).
	* You may want to set this to a higher value if the sum of your metadata file sizes is larger than many 
	  tens of megabytes, to avoid the hit on I/O in the indexing fast path.
	* Highest legal value is 4294967295

partialServiceMetaPeriod = <positive integer>
	* Related to serviceMetaPeriod.  If set, it enables metadata sync every
	  <integer> seconds, but only for records where the sync can be done
	  efficiently in-place, without requiring a full re-write of the metadata
	  file.  Records that require full re-write will be synced at serviceMetaPeriod.
	* <integer> specifies how frequently it should sync.  Zero means that this
	  feature is turned off and serviceMetaPeriod is the only time when metadata
	  sync happens.
	* If the value of partialServiceMetaPeriod is greater than serviceMetaPeriod,
	  this setting will have no effect.
	* By default it is turned off (zero).
	* This parameter is ignored if serviceOnlyAsNeeded = true (the default).
	* Highest legal value is 4294967295

throttleCheckPeriod = <positive integer>
	* Defines how frequently Splunk checks for index throttling condition, in seconds.
	* In seconds; defaults to 15
	* NOTE: Do not change this parameter without the input of a Splunk Support professional.
	* Highest legal value is 4294967295

maxTimeUnreplicatedWithAcks = <nonnegative decimal>
        * Important if you have enabled acks on forwarders and have replication enabled (via Clustering)
        * This parameter puts an upper limit on how long events can sit unacked in a raw slice
	* In seconds; defaults to 60
        * To disable this, you can set to 0, but this is NOT recommended!!!
        * NOTE: This is an advanced parameter; make sure you understand the settings on all your forwarders before changing this.  This number should not exceed ack timeout configured on any forwarders, and should indeed be set to at most half of the minimum value of that timeout.  You can find this setting in outputs.conf readTimeout setting, under tcpout stanza.
	* Highest legal value is 2147483647

maxTimeUnreplicatedNoAcks = <nonnegative decimal>
        * Important only if replication is enabled for this index, otherwise ignored
        * This parameter puts an upper limit on how long an event can sit in raw slice.  
        * if there are any ack''d events sharing this raw slice, this paramater will not apply (maxTimeUnreplicatedWithAcks will be used instead)
	* In seconds; defaults to 60
	* Highest legal value is 2147483647
        * To disable this, you can set to 0; please be careful and understand the consequences before changing this parameter

isReadOnly = true|false
	* Set to true to make an index read-only.
	* If true, no new events can be added to the index, but the index is still searchable.
	* Defaults to false.
	* Must restart splunkd after changing this parameter; index reload will not suffice.

homePath.maxDataSizeMB = <nonnegative integer>
	* Specifies the maximum size of homePath (which contains hot and warm buckets).
	* If this size is exceeded, Splunk will move buckets with the oldest value of latest time (for a given bucket)
	  into the cold DB until homePath is below the maximum size.
	* If this attribute is missing or set to 0, Splunk will not constrain size of homePath.
	* Defaults to 0.
	* Highest legal value is 4294967295

coldPath.maxDataSizeMB = <nonnegative integer>
	* Specifies the maximum size of coldPath (which contains cold buckets).
	* If this size is exceeded, Splunk will freeze buckets with the oldest value of latest time (for a given bucket) 
	  until coldPath is below the maximum size.
	* If this attribute is missing or set to 0, Splunk will not constrain size of coldPath
	* If we freeze buckets due to enforcement of this policy parameter, and
	  coldToFrozenScript and/or coldToFrozenDir archiving parameters are also
	  set on the index, these parameters *will* take into effect
	* Defaults to 0.
	* Highest legal value is 4294967295

disableGlobalMetadata = true|false
	* NOTE: This option was introduced in 4.3.3, but as of 5.0 it is obsolete and ignored if set.
	* It used to disable writing to the global metadata.  In 5.0 global metadata was removed.

repFactor = <nonnegative integer>|auto
        * Only relevant if this instance is a clustering slave (but see note about "auto" below).
        * See server.conf spec for details on clustering configuration.
        * Value of 0 turns off replication for this index.
        * If set to "auto", slave will use whatever value the master is configured with
		* Highest legal value is 4294967295

minStreamGroupQueueSize = <nonnegative integer>
	* Minimum size of the queue that stores events in memory before committing
	  them to a tsidx file.  As Splunk operates, it continually adjusts this
	  size internally.  Splunk could decide to use a small queue size and thus
	  generate tiny tsidx files under certain unusual circumstances, such as
	  file system errors.  The danger of a very low minimum is that it can
	  generate very tiny tsidx files with one or very few events, making it
	  impossible for splunk-optimize to catch up and optimize the tsidx files
	  into reasonably sized files.
	* Defaults to 2000.
	* Only set this value if you have been advised to by Splunk Support.
	* Highest legal value is 4294967295

streamingTargetTsidxSyncPeriodMsec = <nonnegative integer>
        * Period we force sync tsidx files on streaming targets.  This setting is needed
          for multi-site clustering where streaming targets may be primary.
        * if set to 0, we never sync (equivalent to infinity)

#******************************************************************************	
# Volume settings.  This section describes settings that affect the volume-
# optional and volume-mandatory parameters only.
#
# All volume stanzas begin with "volume:". For example:
#   [volume:volume_name]
#   path = /foo/bar
#
# These volume stanzas can then be referenced by individual index parameters,
# e.g. homePath or coldPath.  To refer to a volume stanza, use the
# "volume:" prefix. For example, to set a cold DB to the example stanza above,
# in index "hiro", use:
#   [hiro]
#   coldPath = volume:volume_name/baz
# This will cause the cold DB files to be placed under /foo/bar/baz.  If the
# volume spec is not followed by a path (e.g. "coldPath=volume:volume_name"),
# then the cold path would be composed by appending the index name to the
# volume name ("/foo/bar/hiro").
#
# Note: thawedPath may not be defined in terms of a volume.  
# Thawed allocations are manually controlled by Splunk administrators,
# typically in recovery or archival/review scenarios, and should not
# trigger changes in space automatically used by normal index activity.
#******************************************************************************	

path = <path on server>
	* Required. 
	* Points to the location on the file system where all databases that use this volume will 
	  reside.  You must make sure that this location does not overlap with that of any other 
	  volume or index database.

maxVolumeDataSizeMB = <nonnegative integer>
	* Optional. 
	* If set, this attribute limits the total size of all databases 
	  that reside on this volume to the maximum size specified, in MB.  Note that
	  this it will act only on those indexes which reference this volume, not
	  on the total size of the path set in the path attribute of this volume.
	* If the size is exceeded, Splunk will remove buckets with the oldest value of latest time (for a given bucket)
 	  across all indexes in the volume, until the volume is below the maximum size.  This is the trim operation.
	  Note that this can cause buckets to be chilled [moved to cold] directly from a hot DB, if those 
	  buckets happen to have the least value of latest-time (LT) across all indexes in the volume.
	* Highest legal value is 4294967295

rotatePeriodInSecs = <nonnegative integer>
	* Optional. 
	* Specifies period of trim operation for this volume.
	* If not set, the value of global rotatePeriodInSecs attribute is inherited.
	* Highest legal value is 4294967295
