#   Version 6.2.6 
#
# This file configures the KV Store collections for a given app in Splunk. 
#
# To learn more about configuration files (including precedence) please see the documentation
# located at http://docs.splunk.com/Documentation/Splunk/latest/Admin/Aboutconfigurationfiles


[<collection-name>]

enforceTypes = true|false
* Indicates whether to enforce data types when inserting data into the collection.
* When set to true, invalid insert operations fail.
* When set to false, invalid insert operations drop only the invalid field.
* Defaults to false.

field.<name> = number|bool|string|time
* Field type for a field called <name>.
* If the data type is not provided, it is inferred from the provided JSON data type.

accelerated_fields.<name> = <json>
* Acceleration definition for an acceleration called <name>.
* Must be a valid JSON document (invalid JSON is ignored).
* Example: 'acceleration.foo={"a":1, "b":-1}' is a compound acceleration that first 
  sorts 'a' in ascending order and then 'b' in descending order.
* If multiple accelerations with the same definition are in the same collection, 
  the duplicates are skipped.
* If the data within a field is too large for acceleration, you will see a warning
  when you try to create an accelerated field and the acceleration will not be created.
* An acceleration is always created on the _key.
* The order of accelerations is important. For example, an acceleration of { "a":1, "b":1 } 
  speeds queries on "a" and "a" + "b", but not on "b" alone.
* Multiple separate accelerations also speed up queries. For example, separate accelerations 
  { "a":1 } and { "b": 1 } will speed up queries on "a" + "b", but not as well as 
  a combined acceleration { "a":1, "b":1 }.
* Defaults to nothing (no acceleration).

profilingEnabled = true|false
* Indicates whether to enable logging of slow-running operations, as defined in 'profilingThresholdMs'.
* Defaults to false.

profilingThresholdMs = <zero or positive integer>
* The threshold for logging a slow-running operation, in milliseconds. 
* When set to 0, all operations are logged. 
* This setting is only used when 'profilingEnabled' is true. 
* This setting impacts the performance of the collection. 
* Defaults to 100.
