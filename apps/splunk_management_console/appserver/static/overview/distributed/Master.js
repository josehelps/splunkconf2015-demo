/**
 * Created by ykou on 7/22/14.
 */
define([
    'jquery',
    'underscore',
    'views/Base',
    "splunkjs/mvc/searchmanager",
    "splunkjs/mvc/postprocessmanager",
    "splunkjs/mvc/singleview",
    "splunkjs/mvc/utils",
    'splunk.util',
    'util/console'
],
    function(
        $,
        _,
        BaseView,
        SearchManager,
        PostProcessManager,
        SingleView,
        utils,
        splunkUtil,
        console
        ) {
        var RED_COLOR = '#d85d3c';
        var IF_OPEN_NEW_TAB = '_blank';
        var DMC_BASE_SEARCH_ID = 'instances-and-machine-count';

        var DMC_TOOLTIP_DELAY = '\'{"show": "750", "hide": "0"}\'';

        var DMC_INDEXER_TOTAL_INDEXING_RATE_DOC = _('Snapshot, aggregated across all 6.2 or later indexers.').t();
        var DMC_INDEXER_AVERAGE_INDEXING_RATE_DOC = _('Snapshot, averaged across all 6.2 or later indexers.').t();
        var DMC_INDEXER_CPU_DOC = _('Snapshot machine-wide CPU usage averaged across all indexers.').t();
        var DMC_INDEXER_MEMORY_DOC = _('Snapshot machine-wide physical memory usage averaged across all indexers.').t();
        var DMC_SEARCH_HEAD_TOTAL_SEARCHES_DOC = _('Snapshot search concurrency aggregated across all search heads.').t();
        var DMC_SEARCH_HEAD_AVERAGE_SEARCHES_DOC = _('Snapshot search concurrency averaged across all search heads.').t();
        var DMC_SEARCH_HEAD_CPU_DOC = _('Snapshot machine-wide CPU usage averaged across all search heads.').t();
        var DMC_SEARCH_HEAD_MEMORY_DOC = _('Snapshot machine-wide physical memory usage averaged across all search heads.').t();
        var DMC_CLUSTER_MASTER_BUCKETS_DOC = _('Total number of bucket copies, aggregated across all cluster peers').t();
        var DMC_CLUSTER_MASTER_RAWDATA_SIZE_DOC = _('Represents a unique set of all compressed rawdata in replicated indexes.').t();
        var DMC_CLUSTER_MASTER_CPU_DOC = _('Snapshot machine-wide CPU usage averaged across all cluster masters.').t();
        var DMC_CLUSTER_MASTER_MEMORY_DOC = _('Snapshot machine-wide physical memory usage averaged across all cluster masters.').t();
        var DMC_LICENSE_MASTER_WARNINGS_DOC = _('Number of license slaves with at least one hard warning.').t();
        var DMC_LICENSE_MASTER_LICENSE_USAGE_DOC = _('License usage and capacity aggregated across all license masters.').t();
        var DMC_LICENSE_MASTER_CPU_DOC = _('Snapshot machine-wide CPU usage averaged across all license masters.').t();
        var DMC_LICENSE_MASTER_MEMORY_DOC = _('Snapshot machine-wide physical memory usage averaged across all license masters.').t();
        var DMC_DEPLOYMENT_SERVER_CPU_DOC = _('Snapshot machine-wide CPU usage averaged across all deployment servers.').t();
        var DMC_DEPLOYMENT_SERVER_MEMORY_DOC = _('Snapshot machine-wide physical memory usage averaged across all deployment servers.').t();
        var DMC_KV_STORE_COLLECTION_SIZE_DOC = _('Size on disk of all collections aggregated across all instances hosting a KV store.').t();
        var DMC_KV_STORE_COLLECTION_COUNT_DOC = _('Distinct count of collections across all instances hosting a KV store.').t();
        var DMC_KV_STORE_CPU_DOC = _('Snapshot machine-wide CPU usage averaged across all instances hosting a KV store.').t();
        var DMC_KV_STORE_MEMORY_DOC = _('Snapshot machine-wide physical memory usage averaged across all instances hosting a KV store.').t();

		var DMC_SUB_TITLE = _('The Distributed Management Console monitors important aspects of your Splunk Enterprise deployment. ').t();
		var DMC_DISTR_MODE = _('Mode: distributed').t();
		
        var loadingImageUrl = splunkUtil.make_url("/static/img/skins/default/loading_white.gif");

        var SET_SPINNER = {
            'background-image': 'url(' + loadingImageUrl + ')',
            'background-repeat': 'no-repeat',
            'background-size': '20px 20px'
        };
        var REMOVE_SPINNER = {
            'background': 'none'
        };

        // General drilldowns

        var getFullPath = function(path) {
            var root = utils.getPageInfo().root;
            var locale = utils.getPageInfo().locale;
            return (root ? '/'+root : '') + '/' + locale + path;
        };

        var drilldownToIndexingPerformance = function(role) {
            var r = role || 'indexer';
            return function(e) {
                var isNewTab = IF_OPEN_NEW_TAB;
                if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) {
                    isNewTab = '_blank';
                }
                window.open(getFullPath('/app/splunk_management_console/indexing_performance_deployment?form.group=dmc_group_' + r), isNewTab);
            };
        };

        var drilldownToSearchActivity = function(role) {
            var r = role || 'search_head';
            return function(e) {
                var isNewTab = IF_OPEN_NEW_TAB;
                if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) {
                    isNewTab = '_blank';
                }
                window.open(getFullPath('/app/splunk_management_console/search_activity_deployment?form.group=dmc_group_' + r), isNewTab);
            };
        };

        var drilldownToResourceUsage = function(role) {
            var url = '/app/splunk_management_console/resource_usage_deployment';
            if (role) {
                url += '?form.group=dmc_group_' + role;
            }
            return function(e) {
                var isNewTab = IF_OPEN_NEW_TAB;
                if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) {
                    isNewTab = '_blank';
                }
                window.open(getFullPath(url), isNewTab);
            };
        };

        var drilldownToLicenseUsage = function() {
            return function(e) {
                var isNewTab = IF_OPEN_NEW_TAB;
                if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) {
                    isNewTab = '_blank';
                }
                window.open(getFullPath('/app/splunk_management_console/Licensing'), isNewTab);
            };
        };

        var drilldownToKVStoreView = function() {
            return function(e) {
                var isNewTab = IF_OPEN_NEW_TAB;
                if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) {
                    isNewTab = '_blank';
                }
                window.open(getFullPath('/app/splunk_management_console/kv_store_deployment'), isNewTab);
            };
        };

        var drilldownToInstancesView = function(group) {
            var urlGroup = group ? '?group=' + group : '';
            return function(e) {
                var isNewTab = IF_OPEN_NEW_TAB;
                if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) {
                    isNewTab = '_blank';
                }
                window.open(getFullPath('/app/splunk_management_console/managementconsole_instances' + urlGroup), isNewTab);
            };
        };

        /**
         * @param $el           (jQuery Object) a jQuery Object you want to attach the viz to.
         * @param value         (Number)        a percentage number, could be larger than 100.
         * @param beforeLabel   (String)        text shows on the left side of bar
         * @param afterLabel    (String)        text shows on the right side of bar
         */
        var applyProgressBarViz = function($el, value, afterLabel, drilldown) {
            if ((value == null) || (value == undefined)) { return; }
            $el.find('.smc-progress-bar').attr(
                { 'aria-valuenow': value }
            ).css(
                { 'width': value + '%' }
            );
            if (value >= 100) {
                $el.find('.smc-progress-bar').css('background-color', RED_COLOR);
            }
            $el.find('.smc-viz-after-label').text(afterLabel).css(REMOVE_SPINNER);
            $el.click(drilldown);
        };

        /**
         *
         * @param model (Object) a SplunkJS search result object, get from searchManager.data('preview') or similar thing.
         * @param <others>  (String)
         */
        var CPUAndMemViz = function(model, CPUField, CPUSelector, MemField, MemSelector, role, searchManager) {
            model.on('data', function() {
                var dataModel = model.collection().models[0];

                var cpu_pct = dataModel.get(CPUField);
                var mem_pct = dataModel.get(MemField);

                applyProgressBarViz($(CPUSelector), cpu_pct, cpu_pct + ' %', drilldownToResourceUsage(role));
                applyProgressBarViz($(MemSelector), mem_pct, mem_pct + ' %', drilldownToResourceUsage(role));
            });

            searchManager.on('search:done search:error search:failed', function() {
                $(CPUSelector).find('.smc-viz-after-label').css(REMOVE_SPINNER);
                $(MemSelector).find('.smc-viz-after-label').css(REMOVE_SPINNER);
            });
        };

        var instanceMachineCountView = function(options) {
             var PLURAL = {
                ' Indexer': _(' Indexers').t(),
                ' Search Head': _(' Search Heads').t(),
                ' Cluster Master': _(' Cluster Masters').t(),
                ' Deployment Server': _(' Deployment Servers').t(),
                ' License Master': _(' License Masters').t(),
                ' KV Store': _(' KV Stores').t()
            };
            options = options || {};
            var searchManager = options.searchManager,
                instanceField = options.instanceField,
                machineField = options.machineField,
                instanceSelector = options.instanceSelector,
                machineSelector = options.machineSelector,
                group = options.group;

            var $instance = $(instanceSelector);
            var $machine = $(machineSelector);
            searchManager.on('search:done', function(properties) {
                if (properties && ((properties.content.resultPreviewCount || 0) <= 0)) {
                    $instance.parents('.smc-distributed-mode-panel').hide();
                    return;
                }
                var model = searchManager.data('preview');
                model.on('error', function() {
                    console.log('model error:', model);
                });
                model.on('data', function() {
                    var data = model.collection().models[0];
                    var instanceCount = data.get(instanceField);
                    var machineCount = data.get(machineField);
                    $instance.text(instanceCount).css(REMOVE_SPINNER);
                    if (instanceCount != 1) {
                        var instanceText = $instance.siblings('.smc-maybe-plural').text();
                        $instance.siblings('.smc-maybe-plural').text(PLURAL[instanceText]);
                    }
                    if (instanceCount <= 0 || !instanceCount) {
                        // show panel if there's at least one machine
                        $instance.parents('.smc-distributed-mode-panel').hide();
                    }
                    $machine.text(machineCount).css(REMOVE_SPINNER);
                    if (machineCount > 1) {
                        $machine.siblings('.smc-maybe-plural').text(_(' Machines').t());
                    }
                    $instance.click(drilldownToInstancesView(group));
                    $machine.click(drilldownToInstancesView(group));
                });
            });
        };

        var downCount = function(options) {
            options = options || {};
            var searchManager = options.searchManager,
                downField = options.downField,
                downSelector = options.downSelector,
                group = options.group;

            var $down = $(downSelector);
            searchManager.on('search:done', function(properties) {
                var model = searchManager.data('preview');
                model.on('error', function() {
                    console.log('model error:', model);
                });
                model.on('data', function() {
                    var data = model.collection().models[0];
                    var downCount = data.get(downField);
                    if (downCount > 0) {
                        $down.text(downCount).css(REMOVE_SPINNER);
                        if (downCount > 1) {
                            $down.siblings('.smc-maybe-plural').text(_(' instances unreachable').t());
                        }
                        $down.parents('.smc-warning-section').show();
                    }
                    $down.click(drilldownToInstancesView(group));
                });
            });
            searchManager.on('search:cancelled search:error search:failed', function() {
                console.log('search not finished!', searchManager);
            });
        };

        return BaseView.extend({
            initialize: function() {
                BaseView.prototype.initialize.apply(this, arguments);
                this.$el.html(this.compiledTemplate());
                this.$el.appendTo($('#smc-distributed-mode-view-container'));

                this.$el.find('.smc-loading-zone').css(SET_SPINNER);
                this._createSearch();
                this._createView();
            },
            _createSearch: function() {
                // Note that setting a splunk_server_group to a dmc_group is equivalent to looking for it in the asset table
                var instanceMachineCountSearch = new SearchManager({
                    id: DMC_BASE_SEARCH_ID,
                    search: '| inputlookup assets.csv \
                        | stats dc(serverName) as instance_count dc(machine) as machine_count by search_group \
                        | where match(search_group,"dmc_group_") \
                        | eval count = "count" \
                        | chart format=$VAL$_$AGG$ values(instance_count) AS instance_count values(machine_count) AS machine_count over count by search_group',
                    cancelOnUnload: true,
                    app: utils.getCurrentApp()
                });
                instanceMachineCountView({
                    searchManager: instanceMachineCountSearch,
                    instanceField: 'dmc_group_indexer_instance_count',
                    machineField: 'dmc_group_indexer_machine_count',
                    instanceSelector: '#smc-indexer-instance-count',
                    machineSelector: '#smc-indexer-machine-count',
                    group: 'dmc_group_indexer'
                });
                instanceMachineCountView({
                    searchManager: instanceMachineCountSearch,
                    instanceField: 'dmc_group_search_head_instance_count',
                    machineField: 'dmc_group_search_head_machine_count',
                    instanceSelector: '#smc-search-head-instance-count',
                    machineSelector: '#smc-search-head-machine-count',
                    group: 'dmc_group_search_head'
                });
                instanceMachineCountView({
                    searchManager: instanceMachineCountSearch,
                    instanceField: 'dmc_group_cluster_master_instance_count',
                    machineField: 'dmc_group_cluster_master_machine_count',
                    instanceSelector: '#smc-cluster-master-instance-count',
                    machineSelector: '#smc-cluster-master-machine-count',
                    group: 'dmc_group_cluster_master'
                });
                instanceMachineCountView({
                    searchManager: instanceMachineCountSearch,
                    instanceField: 'dmc_group_license_master_instance_count',
                    machineField: 'dmc_group_license_master_machine_count',
                    instanceSelector: '#smc-license-master-instance-count',
                    machineSelector: '#smc-license-master-machine-count',
                    group: 'dmc_group_license_master'
                });
                instanceMachineCountView({
                    searchManager: instanceMachineCountSearch,
                    instanceField: 'dmc_group_deployment_server_instance_count',
                    machineField: 'dmc_group_deployment_server_machine_count',
                    instanceSelector: '#smc-deployment-server-instance-count',
                    machineSelector: '#smc-deployment-server-machine-count',
                    group: 'dmc_group_deployment_server'
                });
                instanceMachineCountView({
                    searchManager: instanceMachineCountSearch,
                    instanceField: 'dmc_group_kv_store_instance_count',
                    machineField: 'dmc_group_kv_store_machine_count',
                    instanceSelector: '#smc-kv-store-instance-count',
                    machineSelector: '#smc-kv-store-machine-count',
                    group: 'dmc_group_kv_store'
                });

                // RESOURCE USAGE SEARCHES

                // Note that setting a splunk_server_group to a dmc_group is equivalent to looking for it in the asset table
                var resourceUsageSearch = new SearchManager({
                    id: "resource-and-status-search",
                    search: '| inputlookup assets.csv \
| join type=outer serverName [ \
| rest splunk_server_group=dmc_group_* /services/server/status/resource-usage/hostwide \
| eval cpu_pct = cpu_system_pct + cpu_user_pct \
| eval mem_used_pct = mem_used / mem * 100 \
| fields cpu_pct mem_used_pct splunk_server \
| rename splunk_server as serverName \
] \
| join type=outer peerURI [ \
| rest splunk_server=local /services/search/distributed/peers \
| fields title status \
| rename title as peerURI \
] \
| eval status=if(status="Down",1,0) \
| stats dc(serverName) as instances dc(machine) as machines sum(status) as num_down avg(cpu_pct) as cpu avg(mem_used_pct) as mem by search_group \
| eval cpu=round(cpu, 2) \
| eval mem=round(mem, 2)',
                    cancelOnUnload: true,
                    app: utils.getCurrentApp()
                }, { tokens: true, tokenNamespace: "submitted"});

                var indexersPostProcess = new PostProcessManager({
                    id: "indexers-post-process",
                    search: 'search search_group="dmc_group_indexer"',
                    managerid: 'resource-and-status-search'
                });
                CPUAndMemViz(indexersPostProcess.data('preview'), 'cpu', '#smc-indexer-cpu-usage-viz', 'mem', '#smc-indexer-memory-usage-viz', 'indexer', resourceUsageSearch);
                downCount({
                    searchManager: indexersPostProcess,
                    downField: 'num_down',
                    downSelector: '#smc-indexer-down-count',
                    group: 'dmc_group_indexer'
                });

                var searchHeadsPostProcess = new PostProcessManager({
                    id: "search-heads-post-process",
                    search: 'search search_group="dmc_group_search_head"',
                    managerid: 'resource-and-status-search'
                });
                CPUAndMemViz(searchHeadsPostProcess.data('preview'), 'cpu', '#smc-search-head-cpu-usage', 'mem', '#smc-search-head-memory-usage', 'search_head', resourceUsageSearch);
                downCount({
                    searchManager: searchHeadsPostProcess,
                    downField: 'num_down',
                    downSelector: '#smc-search-head-down-count',
                    group: 'dmc_group_search_head'
                });

                var clusterMastersPostProcess = new PostProcessManager({
                    id: "cluster-masters-post-process",
                    search: 'search search_group="dmc_group_cluster_master"',
                    managerid: 'resource-and-status-search'
                });
                CPUAndMemViz(clusterMastersPostProcess.data('preview'), 'cpu', '#smc-cluster-master-cpu-usage', 'mem', '#smc-cluster-master-memory-usage', 'cluster_master', resourceUsageSearch);
                downCount({
                    searchManager: clusterMastersPostProcess,
                    downField: 'num_down',
                    downSelector: '#smc-cluster-master-down-count',
                    group: 'dmc_group_cluster_master'
                });

                var licenseMastersPostProcess = new PostProcessManager({
                    id: "license-masters-post-process",
                    search: 'search search_group="dmc_group_license_master"',
                    managerid: 'resource-and-status-search'
                });
                CPUAndMemViz(licenseMastersPostProcess.data('preview'), 'cpu', '#smc-license-master-cpu-usage', 'mem', '#smc-license-master-memory-usage', 'license_master', resourceUsageSearch);
                downCount({
                    searchManager: licenseMastersPostProcess,
                    downField: 'num_down',
                    downSelector: '#smc-license-master-down-count',
                    group: 'dmc_group_license_master'
                });

                var deploymentServersPostProcess = new PostProcessManager({
                    id: "deployment-servers-post-process",
                    search: 'search search_group="dmc_group_deployment_server"',
                    managerid: 'resource-and-status-search'
                });
                CPUAndMemViz(deploymentServersPostProcess.data('preview'), 'cpu', '#smc-deployment-server-cpu-usage', 'mem', '#smc-deployment-server-memory-usage', 'deployment_server', resourceUsageSearch);
                downCount({
                    searchManager: deploymentServersPostProcess,
                    downField: 'num_down',
                    downSelector: '#smc-deployment-server-down-count',
                    group: 'dmc_group_deployment_server'
                });

                var kvStoresPostProcess = new PostProcessManager({
                    id: "kv-stores-post-process",
                    search: 'search search_group="dmc_group_kv_store"',
                    managerid: 'resource-and-status-search'
                });
                CPUAndMemViz(kvStoresPostProcess.data('preview'), 'cpu', '#smc-kv-store-cpu-usage', 'mem', '#smc-kv-store-memory-usage', 'kv_store', resourceUsageSearch);
                downCount({
                    searchManager: kvStoresPostProcess,
                    downField: 'num_down',
                    downSelector: '#smc-kv-store-down-count',
                    group: 'dmc_group_kv_store'
                });

                // INDEXER SEARCHES
                new SearchManager({
                    id: "indexer-processing-rate-search",
                    search: '| rest splunk_server_group=dmc_group_indexer /services/server/introspection/indexer \
                    | fields average_KBps splunk_server \
                    | eval average_KBps=round(average_KBps,2) \
                    | stats sum(average_KBps) as total_KBps avg(average_KBps) as average_KBps \
                    | eval average_KBps = round(average_KBps, 2) \
                    | eval total_MBps   = round(total_KBps / 1024, 2) \
                    | eval average_MBps = round(average_KBps / 1024, 2) \
                    | eval total_unit   = if(total_KBps > 1024, " MB/s", " KB/s") \
                    | eval average_unit = if(average_KBps > 1024, " MB/s", " KB/s") \
                    | eval total    = if(total_KBps > 1024, total_MBps, total_KBps) \
                    | eval average  = if(average_KBps > 1024, average_MBps, average_KBps) \
                    | eval total    = total.total_unit \
                    | eval average  = average.average_unit ',
                    cancelOnUnload: true,
                    app: utils.getCurrentApp()
                });


                // SEARCH HEAD SEARCHES
                new SearchManager({
                    id: "search-head-process-search",
                    search: "| rest splunk_server_group=dmc_group_search_head /services/server/status/resource-usage/splunk-processes \
                    | stats dc(search_props.sid) as search_count by splunk_server \
                    | stats sum(search_count) as total avg(search_count) as average \
                    | eval average = round(average, 0) ",
                    cancelOnUnload: true,
                    app: utils.getCurrentApp()
                });

                // CLUSTER MASTER SEARCHES
                new SearchManager({
                    id: 'cluster-peers-and-buckets',
                    search: '| rest splunk_server_group=dmc_group_cluster_master /services/cluster/master/peers',
                    cancelOnUnload: true,
                    app: utils.getCurrentApp()
                });

                new SearchManager({
                    id: 'cluster-indexes-and-bucket-sizes',
                    search: '| rest splunk_server_group=dmc_group_cluster_master /services/cluster/master/indexes',
                    cancelOnUnload: true,
                    app: utils.getCurrentApp()
                });

                new PostProcessManager({
                    id: 'peers-searchable',
                    search: 'search is_searchable = 1 | stats count',
                    managerid: 'cluster-peers-and-buckets'
                });

                new PostProcessManager({
                    id: 'buckets-count',
                    search: 'stats sum(bucket_count) as total_buckets',
                    managerid: 'cluster-peers-and-buckets'
                });

                new PostProcessManager({
                    id: 'indexes-searchable',
                    search: 'search is_searchable = 1 | stats count',
                    managerid: 'cluster-indexes-and-bucket-sizes'
                });

                new PostProcessManager({
                    id: 'total-bucket-size',
                    search: ' eval index_size = round(index_size / 1024 / 1024 / 1024, 2) | stats sum(index_size) as total_index_size_gb',
                    managerid: 'cluster-indexes-and-bucket-sizes'
                });

                // LICENSE MASTER SEARCHES
                var licenseMasterUsageSearch = new SearchManager({
                    id: 'license-master-usage-search',
                    search: '| rest splunk_server_group=dmc_group_license_master /services/licenser/pools \
                             | join type=outer stack_id splunk_server [ \
                                 rest splunk_server_group=dmc_group_license_master /services/licenser/groups \
                                 | search is_active=1 \
                                 | eval stack_id = stack_ids \
                                 | fields splunk_server stack_id is_active] \
                             | search is_active=1 \
                             | fields splunk_server, stack_id, used_bytes \
                             | join type=outer stack_id splunk_server [ \
                                 rest splunk_server_group=dmc_group_license_master /services/licenser/stacks \
                                 | eval stack_id = title \
                                 | eval stack_quota = quota \
                                 | fields splunk_server stack_id stack_quota] \
                             | stats sum(used_bytes) as used_bytes sum(stack_quota) as stack_quota \
                             | eval usedMB  = round(used_bytes/1024/1024, 2) \
                             | eval usedGB  = round(used_bytes/1024/1024/1024, 2) \
                             | eval totalMB = round(stack_quota/1024/1024, 0) \
                             | eval totalGB = round(stack_quota/1024/1024/1024, 0) \
                             | eval used  = if(totalMB > 1024, usedGB, usedMB) \
                             | eval total = if(totalMB > 1024, totalGB, totalMB) \
                             | eval unit  = if(totalMB > 1024, "GB", "MB") \
                             | eval usage_pct = round(used / total, 3)*100 \
                             | eval output = used. " / " .total." ".unit \
                             | fields usage_pct, output',
                    cancelOnUnload: true,
                    app: utils.getCurrentApp()
                });
                var licenseMasterModel = licenseMasterUsageSearch.data('preview');
                licenseMasterModel.on('data', function() {
                    var dataModel = licenseMasterModel.collection().models[0];
                    var usage_pct = dataModel.get('usage_pct');
                    var afterLabel = dataModel.get('output');

                    applyProgressBarViz($('#smc-license-master-license-usage'), usage_pct, afterLabel, drilldownToLicenseUsage());
                });
                licenseMasterUsageSearch.on('search:done search:failed search:error', function() {
                    $('#smc-license-master-license-usage').find('.smc-viz-after-label').css(REMOVE_SPINNER);
                });

                new SearchManager({
                    id: 'license-master-warnings-search',
                    search: '| rest splunk_server_group=dmc_group_license_master /services/licenser/slaves \
                    | mvexpand active_pool_ids \
                    | where warning_count>0 \
                    | eval pool=active_pool_ids \
                    | join type=outer pool [rest splunk_server_group=dmc_group_license_master /services/licenser/pools \
                        | eval pool=title \
                        | fields pool stack_id] \
                    | eval in_violation=if(warning_count>4 OR (warning_count>2 AND stack_id=="free"),"yes","no") \
                    | fields label, title, pool, warning_count, in_violation \
                    | fields - _timediff \
                    | rename label as "Slave" title as "GUID" pool as "Pool" warning_count as "Hard Warnings" in_violation AS "In Violation?" \
                    | stats count',
                    cancelOnUnload: true,
                    app: utils.getCurrentApp()
                });

                // DEPLOYMENT SERVER SEARCHES
                new SearchManager({
                    id: 'deployment-server-client-count-search',
                    search: '| rest splunk_server_group=dmc_group_deployment_server /services/deployment/server/clients \
    | stats count',
                    cancelOnUnload: true,
                    app: utils.getCurrentApp()
                });

                new SearchManager({
                    id: 'deployment-server-application-count-search',
                    search: '| rest splunk_server_group=dmc_group_deployment_server /services/deployment/server/applications \
                | stats count',
                    cancelOnUnload: true,
                    app: utils.getCurrentApp()
                });

                // KV STORE SERVER SEARCHES
                new SearchManager({
                    id: 'kv-store-collections-info-search',
                    search: '| rest splunk_server_group=dmc_group_kv_store /services/server/introspection/kvstore/collectionstats \
                    | mvexpand data \
                    | spath input=data \
                    | fields splunk_server, ns, size',
                    cancelOnUnload: true,
                    app: utils.getCurrentApp()
                });

                new PostProcessManager({
                    id: 'kv-store-collections-size',
                    search: ' stats first(size) as size by ns, splunk_server | stats sum(size) as size | eval sizeMB = round(size/1024/1024, 2)',
                    managerid: 'kv-store-collections-info-search'
                });

                new PostProcessManager({
                    id: 'kv-store-collections-count',
                    search: ' stats dc(ns) as collections',
                    managerid: 'kv-store-collections-info-search'
                });

            },


            _createView: function() {
                // //
                // // VIEWS: VISUALIZATION ELEMENTS
                // //

                // INDEXERS

                var totalIndexingRate = new SingleView({
                    "id": "totalIndexingRate",
                    "underLabel": _('Total').t(),
//                    'afterLabel': _('KB/s').t(),
                    "refresh.time.visible": "False",
                    "managerid": "indexer-processing-rate-search",
                    "field": "total",
                    "el": $('#smc-total-indexing-rate')
                }, {tokens: true}).render();
                totalIndexingRate.$el.click(drilldownToIndexingPerformance('indexer'));

                var averageIndexingRate = new SingleView({
                    "id": "averageIndexingRate",
                    'underLabel': _('Average').t(),
//                    'afterLabel': _('KB/s').t(),
                    "refresh.time.visible": "False",
                    "managerid": "indexer-processing-rate-search",
                    "field": "average",
                    "el": $('#smc-average-indexing-rate')
                }, {tokens: true}).render();
                averageIndexingRate.$el.click(drilldownToIndexingPerformance('indexer'));

                // SEARCH HEADS

                var totalSearches = new SingleView({
                    "id": "totalSearches",
                    'underLabel': _('Total').t(),
                    "refresh.time.visible": "False",
                    "managerid": "search-head-process-search",
                    "field": "total",
                    "el": $('#smc-total-searches')
                }, {tokens: true}).render();
                totalSearches.$el.click(drilldownToSearchActivity('search_head'));

                var medianSearches = new SingleView({
                    "id": "medianSearches",
                    'underLabel': _('Average').t(),
                    "refresh.time.visible": "False",
                    "managerid": "search-head-process-search",
                    "field": "average",
                    "el": $('#smc-average-searches')
                }, {tokens: true}).render();
                medianSearches.$el.click(drilldownToSearchActivity('search_head'));

                // CLUSTER MASTER

                new SingleView({
                    'id': 'peers-searchable-view',
                    'underLabel': _('Peers Searchable').t(),
                    'refresh.time.visible': 'False',
                    'managerid': 'peers-searchable',
                    'field': 'count',
                    'el': $('#smc-cluster-master-peer-searchable-count')
                }, {tokens: true}).render();

                new SingleView({
                    'id': 'index-searchable-view',
                    'underLabel': _('Indexes Searchable').t(),
                    'refresh.time.visible': 'False',
                    'managerid': 'indexes-searchable',
                    'field': 'count',
                    'el': $('#smc-cluster-master-index-searchable-count')
                }, {tokens: true}).render();

                new SingleView({
                    'id': 'bucket-count-view',
                    'underLabel': _('Bucket Copies').t(),
                    'refresh.time.visible': 'False',
                    'managerid': 'buckets-count',
                    'field': 'total_buckets',
                    'el': $('#smc-cluster-master-bucket-count')
                }, {tokens: true}).render();

                new SingleView({
                    'id': 'bucket-size-view',
                    'afterLabel': _('GB').t(),
                    'underLabel': _('Rawdata Size').t(),
                    'refresh.time.visible': 'False',
                    'managerid': 'total-bucket-size',
                    'field': 'total_index_size_gb',
                    'el': $('#smc-cluster-master-total-bucket-size')
                }, {tokens: true}).render();

                // LICENSE MASTER

                var licenseMasterHardWarning = new SingleView({
                    "id": "licenseMasterHardWarning",
                    "refresh.time.visible": "False",
                    "managerid": "license-master-warnings-search",
                    "el": $('#smc-license-master-last-month-warning')
                }, {tokens: true}).render();
                licenseMasterHardWarning.$el.click(drilldownToLicenseUsage());

                // DEPLOYMENT SERVERS

                new SingleView({
                    "id": "clientCount",
                    'underLabel': _('Clients').t(),
                    "refresh.time.visible": "False",
                    "managerid": "deployment-server-client-count-search",
                    "el": $('#smc-deployment-server-client-count')
                }, {tokens: true}).render();

                new SingleView({
                    "id": "appCount",
                    'underLabel': _('Apps').t(),
                    "refresh.time.visible": "False",
                    "managerid": "deployment-server-application-count-search",
                    "el": $('#smc-deployment-server-app-count')
                }, {tokens: true}).render();

                // KV STORE SERVERS

                var kvStoreSize = new SingleView({
                    "id": "kvStoreSize",
                    "underLabel": _("Size of Collections (MB)").t(),
                    "refresh.time.visible": "False",
                    "managerid": "kv-store-collections-size",
                    "field": "sizeMB",
                    "el": $('#smc-kv-store-size')
                }, {tokens: true}).render();
                kvStoreSize.$el.click(drilldownToKVStoreView());
                
                var kvStoreCollections = new SingleView({
                    "id": "kvStoreCollections",
                    "underLabel": _("Collections").t(),
                    "refresh.time.visible": "False",
                    "managerid": "kv-store-collections-count",
                    "field": "collections",
                    "el": $('#smc-kv-store-collections')
                }, {tokens: true}).render();
                kvStoreCollections.$el.click(drilldownToKVStoreView());

				// NOTE: need to manualy call this, otherwise tooltip will not show.
                $('.smc-tooltip-link').tooltip();
            },
            render: function() {

            },
            template:
                '<div class="smc-distributed-mode-row">\
                    <div class="smc-distributed-mode-panel smc-indexers-panel">\
                        <div class="smc-panel-title-section">\
                            <div class="row-fluid">\
                                <div class="span9">\
                                    <div class="smc-panel-title"><span id="smc-indexer-instance-count" class="smc-loading-zone">&nbsp;&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' Indexer').t() + '</span></div>\
                                    <div class="smc-panel-title-description">' + _('on ').t() + '<span id="smc-indexer-machine-count" class="smc-loading-zone">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' Machine').t() + '</span></div>\
                                </div>\
                                <div class="span3">\
                                    <object class="smc-panel-icon" type="image/svg+xml" data="/static/app/splunk_management_console/icons/Indexer.svg"></object>\
                                </div>\
                            </div>\
                        </div>\
                        <div class="smc-warning-section"><span id="smc-indexer-down-count" class="smc-loading-zone">&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' instance unreachable').t() + '</span></div>\
                        <div class="smc-panel-label">' + _('INDEXING RATE').t() + '</div>\
                        <div class="row-fluid">\
                            <div class="span6 smc-single-value">\
                                <div id="smc-total-indexing-rate" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_INDEXER_TOTAL_INDEXING_RATE_DOC + '"></div>\
                            </div>\
                            <div class="span6 smc-single-value">\
                                <div id="smc-average-indexing-rate" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_INDEXER_AVERAGE_INDEXING_RATE_DOC + '"></div>\
                            </div>\
                        </div>\
                        <div class="smc-panel-label">' + _('RESOURCE USAGE').t() + '</div>\
                        <div id="smc-indexer-cpu-usage-viz" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_INDEXER_CPU_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('CPU').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                        <div id="smc-indexer-memory-usage-viz" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_INDEXER_MEMORY_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('Memory').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                    </div>\
                    <div class="smc-distributed-mode-panel smc-search-heads-panel">\
                        <div class="smc-panel-title-section">\
                            <div class="row-fluid">\
                                <div class="span9">\
                                    <div class="smc-panel-title"><span id="smc-search-head-instance-count" class="smc-loading-zone">&nbsp;&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' Search Head').t() + '</span></div>\
                                    <div class="smc-panel-title-description">' + _('on ').t() + '<span id="smc-search-head-machine-count" class="smc-loading-zone">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' Machine').t() + '</span></div>\
                                </div>\
                                <div class="span3">\
                                    <object class="smc-panel-icon" type="image/svg+xml" data="/static/app/splunk_management_console/icons/SearchHead.svg"></object>\
                                </div>\
                            </div>\
                        </div>\
                        <div class="smc-warning-section"><span id="smc-search-head-down-count" class="smc-loading-zone">&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' instance unreachable').t() + '</span></div>\
                        <div class="smc-panel-label">' + _('CONCURRENT SEARCHES').t() + '</div>\
                        <div class="row-fluid">\
                            <div class="span6 smc-single-value">\
                                <div id="smc-total-searches" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_SEARCH_HEAD_TOTAL_SEARCHES_DOC + '"></div>\
                            </div>\
                            <div class="span6 smc-single-value">\
                                <div id="smc-average-searches" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_SEARCH_HEAD_AVERAGE_SEARCHES_DOC + '"></div>\
                            </div>\
                        </div>\
                        <div class="smc-panel-label">' + _('RESOURCE USAGE').t() + '</div>\
                        <div id="smc-search-head-cpu-usage" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_SEARCH_HEAD_CPU_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('CPU').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                        <div id="smc-search-head-memory-usage" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_SEARCH_HEAD_MEMORY_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('Memory').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                    </div>\
                    <div class="smc-distributed-mode-panel smc-cluster-master-panel">\
                        <div class="smc-panel-title-section">\
                            <div class="row-fluid">\
                                <div class="span9">\
                                    <div class="smc-panel-title"><span id="smc-cluster-master-instance-count" class="smc-loading-zone">&nbsp;&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' Cluster Master').t() + '</span></div>\
                                    <div class="smc-panel-title-description">' + _('on ').t() + '<span id="smc-cluster-master-machine-count" class="smc-loading-zone">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' Machine').t() + '</span></div>\
                                </div>\
                                <div class="span3">\
                                    <object class="smc-panel-icon" type="image/svg+xml" data="/static/app/splunk_management_console/icons/ClusterMaster.svg"></object>\
                                </div>\
                            </div>\
                        </div>\
                        <div class="smc-warning-section"><span id="smc-cluster-master-down-count" class="smc-loading-zone">&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' instance unreachable').t() + '</span></div>\
                        <div class="smc-panel-label">' + _('STATUS').t() + '</div>\
                        <div class="row-fluid">\
                            <div class="span3 smc-single-value">\
                                <div id="smc-cluster-master-peer-searchable-count"></div>\
                            </div>\
                            <div class="span3 smc-single-value">\
                                <div id="smc-cluster-master-index-searchable-count"></div>\
                            </div>\
                            <div class="span3 smc-single-value">\
                                <div id="smc-cluster-master-bucket-count" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_CLUSTER_MASTER_BUCKETS_DOC + '"></div>\
                            </div>\
                            <div class="span3 smc-single-value">\
                                <div id="smc-cluster-master-total-bucket-size" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_CLUSTER_MASTER_RAWDATA_SIZE_DOC + '"></div>\
                            </div>\
                        </div>\
                        <div class="smc-panel-label">' + _('RESOURCE USAGE').t() + '</div>\
                        <div id="smc-cluster-master-cpu-usage" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_CLUSTER_MASTER_CPU_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('CPU').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                        <div id="smc-cluster-master-memory-usage" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_CLUSTER_MASTER_MEMORY_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('Memory').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                    </div>\
                    <div class="smc-distributed-mode-panel smc-license-master-panel">\
                        <div class="smc-panel-title-section">\
                            <div class="row-fluid">\
                                <div class="span9">\
                                    <div class="smc-panel-title"><span class="single-result smc-loading-zone" id="smc-license-master-instance-count">&nbsp;&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' License Master').t() + '</span></div>\
                                    <div class="smc-panel-title-description">' + _('on ').t() + '<span class="single-result smc-loading-zone" id="smc-license-master-machine-count">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' Machine').t() + '</span></div>\
                                </div>\
                                <div class="span3">\
                                    <object class="smc-panel-icon" type="image/svg+xml" data="/static/app/splunk_management_console/icons/LicenseServer.svg"></object>\
                                </div>\
                            </div>\
                        </div>\
                        <div class="smc-warning-section"><span class="single-result smc-loading-zone" id="smc-license-master-down-count">&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' instance unreachable').t() + '</span></div>\
                        <div class="smc-panel-label">' + _('SLAVES WITH WARNINGS').t() + '</div>\
                        <div class="row-fluid">\
                            <div class="span12 smc-single-value">\
                                <div id="smc-license-master-last-month-warning" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_LICENSE_MASTER_WARNINGS_DOC + '"></div>\
                            </div>\
                        </div>\
                        <div class="smc-panel-label">' + _('LICENSE USAGE').t() + '</div>\
                        <div id="smc-license-master-license-usage" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_LICENSE_MASTER_LICENSE_USAGE_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('Today').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                        <div class="smc-panel-label">' + _('RESOURCE USAGE').t() + '</div>\
                        <div id="smc-license-master-cpu-usage" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_LICENSE_MASTER_CPU_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('CPU').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                        <div id="smc-license-master-memory-usage" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_LICENSE_MASTER_MEMORY_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('Memory').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                    </div>\
                    <div class="smc-distributed-mode-panel smc-deployment-server-panel">\
                        <div class="smc-panel-title-section">\
                            <div class="row-fluid">\
                                <div class="span9">\
                                    <div class="smc-panel-title"><span class="single-result smc-loading-zone" id="smc-deployment-server-instance-count">&nbsp;&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' Deployment Server').t() + '</span></div>\
                                    <div class="smc-panel-title-description">' + _('on ').t() + '<span class="single-result smc-loading-zone" id="smc-deployment-server-machine-count">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' Machine').t() + '</span></div>\
                                </div>\
                                <div class="span3">\
                                    <object class="smc-panel-icon" type="image/svg+xml" data="/static/app/splunk_management_console/icons/DeploymentServer.svg"></object>\
                                </div>\
                            </div>\
                        </div>\
                        <div class="smc-warning-section"><span class="single-result smc-loading-zone" id="smc-deployment-server-down-count">&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' instance unreachable').t() + '</span></div>\
                        <div class="smc-panel-label">' + _('DEPLOYMENT').t() + '</div>\
                        <div class="row-fluid">\
                            <div class="span6 smc-single-value">\
                                <div id="smc-deployment-server-client-count"></div>\
                            </div>\
                            <div class="span6 smc-single-value">\
                                <div id="smc-deployment-server-app-count"></div>\
                            </div>\
                        </div>\
                        <div class="smc-panel-label">' + _('RESOURCE USAGE').t() + '</div>\
                        <div id="smc-deployment-server-cpu-usage" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_DEPLOYMENT_SERVER_CPU_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('CPU').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                        <div id="smc-deployment-server-memory-usage" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_DEPLOYMENT_SERVER_MEMORY_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('Memory').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                    </div>\
                    <div class="smc-distributed-mode-panel smc-kv-store-panel">\
                        <div class="smc-panel-title-section">\
                            <div class="row-fluid">\
                                <div class="span9">\
                                    <div class="smc-panel-title"><span class="single-result smc-loading-zone" id="smc-kv-store-instance-count">&nbsp;&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' KV Store').t() + '</span></div>\
                                    <div class="smc-panel-title-description">' + _('on ').t() + '<span class="single-result smc-loading-zone" id="smc-kv-store-machine-count">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' Machine').t() + '</span></div>\
                                </div>\
                                <div class="span3">\
                                    <object class="smc-panel-icon" type="image/svg+xml" data="/static/app/splunk_management_console/icons/KVStore.svg"></object>\
                                </div>\
                            </div>\
                        </div>\
                        <div class="smc-warning-section"><span class="single-result smc-loading-zone" id="smc-kv-store-down-count">&nbsp;&nbsp;</span><span class="smc-maybe-plural">' + _(' instance unreachable').t() + '</span></div>\
                        <div class="smc-panel-label">' + _('USAGE').t() + '</div>\
                        <div class="row-fluid">\
                            <div class="span6 smc-single-value">\
                                <div id="smc-kv-store-size" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_KV_STORE_COLLECTION_SIZE_DOC + '"></div>\
                            </div>\
                            <div class="span6 smc-single-value">\
                                <div id="smc-kv-store-collections" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_KV_STORE_COLLECTION_COUNT_DOC + '"></div>\
                            </div>\
                        </div>\
                        <div class="smc-panel-label">' + _('RESOURCE USAGE').t() + '</div>\
                        <div id="smc-kv-store-cpu-usage" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_KV_STORE_CPU_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('CPU').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                        <div id="smc-kv-store-memory-usage" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_KV_STORE_MEMORY_DOC + '">\
                            <div class="row-fluid smc-viz-row">\
                                <div class="span3 smc-viz-before-label">' + _('Memory').t() + '</div>\
                                <div class="smc-viz-bar span6"">\
                                    <div class="smc-progress">\
                                        <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;"></div>\
                                    </div>\
                                </div>\
                                <div class="span3 smc-viz-after-label smc-loading-zone"></div>\
                            </div>\
                        </div>\
                    </div>\
                </div>'
        });
    }
);
