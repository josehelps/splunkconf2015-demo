define(
	[
		'underscore',
		'jquery',
		'splunkjs/mvc',
		'splunkjs/mvc/utils',
		'splunkjs/mvc/headerview',
		'splunkjs/mvc/footerview',
		'models/services/server/ServerInfo',
		'splunkjs/mvc/searchmanager',
		'splunkjs/mvc/postprocessmanager',
		'splunkjs/mvc/singleview',
		"splunkjs/mvc/chartview"
	],
	function(
		_,
		$,
		mvc,
		utils,
		HeaderView,
		FooterView,
		ServerInfoModel,
		SearchManager,
		PostProcessManager,
		SingleView,
		ChartView
	) {
        var DMC_INDEXING_RATE_DOC = _('Snapshot.').t();
        var DMC_DISK_USAGE_DOC = _('Disk usage and capacity aggregated across all partitions that Splunk uses.').t();
        var DMC_SEARCH_CONCURRENCY_DOC = _('Snapshot.').t();
        var DMC_CPU_USAGE_DOC = _('Machine-wide.').t();
        var DMC_MEMORY_USAGE_DOC = _('Physical memory.').t();
        var DMC_KV_STORE_COLLECTION_SIZE_DOC = _('Aggregated size on disk.').t();
        var DMC_KV_STORE_COLLECTION_COUNT_DOC = _('Distinct count of collections.').t();

        var DMC_TOOLTIP_DELAY = '\'{"show": "750", "hide": "0"}\'';
	
        var hoverOnSingleValue = function() {
            $(this).css({
                'text-decoration': 'underline',
                'cursor': 'pointer'
            });
        };

        var hoverOffSingleValue = function() {
            $(this).css({
                'text-decoration': 'none',
                'cursor': 'default'
            });
        };

        var hoverOnViz = function() {
            $(this).css({
                'cursor': 'pointer'
            });
        };

        var getFullPath = function(path) {
            var root = utils.getPageInfo().root;
            var locale = utils.getPageInfo().locale;
            return (root ? '/'+root : '') + '/' + locale + path;
        };

        var drilldownToIndexingPerformance = function() {
            return function(e) {
                var isNewTab = '_self';
                if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) {
                    isNewTab = '_blank';
                }
                window.open(getFullPath('/app/splunk_management_console/indexing_performance_instance'), isNewTab);
            };
        };

        var drilldownToSearchActivity = function() {
            return function(e) {
                var isNewTab = '_self';
                if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) {
                    isNewTab = '_blank';
                }
                window.open(getFullPath('/app/splunk_management_console/search_activity_instance'), isNewTab);
            };
        };

        var drilldownToResourceUsage = function() {
            return function(e) {
                var isNewTab = '_self';
                if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) {
                    isNewTab = '_blank';
                }
                window.open(getFullPath('/app/splunk_management_console/resource_usage_instance'), isNewTab);
            };
        };

        var drilldownToLicenseUsage = function() {
            return function(e) {
                var isNewTab = '_self';
                if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) {
                    isNewTab = '_blank';
                }
                window.open(getFullPath('/app/splunk_management_console/Licensing'), isNewTab);
            };
        };

        var drilldownToKVStoreView = function(role) {
            return function(e) {
                var isNewTab = '_self';
                if (e.metaKey || e.ctrlKey || e.altKey || e.shiftKey) {
                    isNewTab = '_blank';
                }
                window.open(getFullPath('/app/splunk_management_console/kv_store_instance'), isNewTab);
            };
        };

//		// TODO refactor
//		var getFullPath = function(path) {
//	        var root = utils.getPageInfo().root;
//	        return (root ? '/'+root : '') + path;
//	    };

		// TODO i18n
		var template = '\
		<div class="dashboard-body container-fluid main-section-body" data-role="main">\
	        <div class="dashboard-header clearfix">\
	            <h2>' + _("Splunk Enterprise Server").t() + ' <span class="splunk-version"></span></h2>\
	            <h3 class="os-details"></h3>\
	            <h3><span class="do-i18n">' + _("Mode: standalone").t() + ' </span><a class="go-to-setup"></a></h3>\
	        </div>\
	        <div>\
		        <div class="row-fluid smc-standalone-row">\
		        	<div class="span6 smc-standalone-cell">\
	        			<div class="smc-panel-label do-i18n">' + _("INDEXING RATE").t() + '</div>\
	            		<div id="indexing-rate-element" class="smc-single-value smc-standalone-single-value smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_INDEXING_RATE_DOC + '"></div>\
	            	</div>\
	            	<div class="span6 smc-standalone-cell">\
	            		<div class="smc-panel-label do-i18n">' + _("LICENSE USAGE").t() + '</div>\
	        			<div id="license-usage-element">\
	        				<div class="row-fluid smc-viz-row">\
	        					<div class="do-i18n span3 smc-viz-before-label">' + _("Today").t() + '</div>\
	        					<div class="smc-viz-bar span6">\
				        			<div class="smc-progress">\
									  <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;">\
									    <span class="smc-sr-only">0%</span>\
									  </div>\
									</div>\
								</div>\
								<div class="smc-percent-used span3 smc-viz-after-label"></div>\
							</div>\
						</div>\
						<div class="smc-panel-label do-i18n">' + _("DISK USAGE").t() + '</div>\
						<div id="disk-usage-element" class="smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_DISK_USAGE_DOC + '">\
							<div class="row-fluid smc-viz-row">\
								<div class="do-i18n span3 smc-viz-before-label">' + _("Disk").t() + '</div>\
								<div class="smc-viz-bar span6">\
				        			<div class="smc-progress">\
									  <div class="smc-progress-bar" role="progressbar" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100" style="width: 0%;">\
									    <span class="smc-sr-only">0%</span>\
									  </div>\
									</div>\
								</div>\
								<div class="smc-percent-used span3 smc-viz-after-label"></div>\
							</div>\
						</div>\
	            	</div>\
	            </div>\
	             <div class="row-fluid smc-standalone-row">\
		        	<div class="span6 smc-standalone-cell">\
			        	<div class="smc-panel-label do-i18n">' + _("CONCURRENT SEARCHES").t() + '</div>\
			            <div id="concurrent-searches-element" class="smc-single-value smc-standalone-single-value smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_SEARCH_CONCURRENCY_DOC + '"></div>\
			        </div>\
			        <div class="span6 smc-standalone-cell">\
			        	<div class="smc-panel-label do-i18n">' + _("CONCURRENT SEARCHES BY TYPE").t() + '</div>\
			            <div id="searches-by-type-element" class="smc-chart"></div>\
		           	</div>\
		        </div>\
		        <div class="row-fluid smc-standalone-row">\
		        	<div class="span6 smc-standalone-cell">\
	        			<div class="smc-panel-label do-i18n smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_CPU_USAGE_DOC + '">' + _("CPU USAGE").t() + '</div>\
			            <div id="splunk-cpu-usage-element" class="smc-single-value smc-standalone-single-value"></div>\
			            <div id="cpu-usage-element" class="smc-single-value smc-standalone-single-value"></div>\
			        </div>\
			        <div class="span6 smc-standalone-cell">\
			        	<div class="smc-panel-label do-i18n smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_CPU_USAGE_DOC + '">' + _("CPU USAGE BY PROCESS").t() + '</div>\
	            		<div id="cpu-usage-by-process-element" class="smc-chart"></div>\
	            	</div>\
	           	</div>\
	           	<div class="row-fluid smc-standalone-row">\
		        	<div class="span6 smc-standalone-cell">\
	        			<div class="smc-panel-label do-i18n smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_MEMORY_USAGE_DOC + '">' + _("MEMORY USAGE").t() + '</div>\
	            		<div id="splunk-mem-usage-element" class="smc-single-value smc-standalone-single-value"></div>\
	            		<div id="mem-usage-element" class="smc-single-value smc-standalone-single-value"></div>\
	            	</div>\
	            	<div class="span6 smc-standalone-cell">\
			        	<div class="smc-panel-label do-i18n smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_MEMORY_USAGE_DOC + '">' + _("MEMORY USAGE BY PROCESS").t() + '</div>\
	            		<div id="mem-usage-by-process-element" class="smc-chart"></div>\
	            	</div>\
	            </div>\
	            <div class="row-fluid smc-standalone-row smc-standalone-kv-store-panel">\
		        	<div class="span12 smc-standalone-cell">\
	        			<div class="smc-panel-label do-i18n">' + _("KV STORE").t() + '</div>\
	            		<div id="kv-store-size" class="smc-single-value smc-standalone-single-value smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_KV_STORE_COLLECTION_SIZE_DOC + '"></div>\
	            		<div id="kv-store-collections" class="smc-single-value smc-standalone-single-value smc-tooltip-link" data-toggle="tooltip" data-delay=' + DMC_TOOLTIP_DELAY + ' title="' + DMC_KV_STORE_COLLECTION_COUNT_DOC + '"></div>\
	            	</div>\
	            </div>\
	        </div>\
	        <div id="smc-alerts-view-standalone-container"></div>\
	    </div>\
		';
		var $template = $(_.template(template, {_: _}));
        // NOTE: need to manualy call this, otherwise tooltip will not show.
        $template.find('.smc-tooltip-link').tooltip();


		var computeMemory = function(memMb) {
			var units = 'MB';
			var mem = parseInt(memMb, 10);

			if (mem > 1024) {
				mem = mem/1024;
				units = 'GB';
			}

			mem = Math.round(mem*100)/100;

			return {
				mem: mem,
				units: units
			};
		};

		// TODO this is more like initialize, less like render
		var render = function($el) {
			var serverInfoModel = new ServerInfoModel();
			$template.appendTo($el);


			serverInfoModel.fetch().done(function() {
		
	            new SearchManager({
	            	id: 'resource-usage-by-process-search',
	            	search: '| rest splunk_server=local /services/server/status/resource-usage/splunk-processes\
| eval sid = \'search_props.sid\' \
| `dmc_classify_processes`\
| eval x="cpu_usage" | stats sum(pct_memory) as mem_used sum(normalized_pct_cpu) as cpu_used by process_class\
| append [\
| rest splunk_server=local /services/server/status/resource-usage/hostwide \
| fields cpu_idle_pct mem mem_used \
| eval mem_idle_pct=round((mem-mem_used)/mem,2)*100 \
| fields - mem mem_used \
| eval cpu_system_pct=0 \
| eval mem_system_pct=0 \
| transpose \
| eval process_class=if(column="cpu_idle_pct" OR column="mem_idle_pct","Idle","Other Machine Processes") \
| rename "row 1" as value \
| eval mem_used=if(column="mem_idle_pct" OR column="mem_system_pct",value,NULL) \
| eval cpu_used=if(column="cpu_idle_pct" OR column="cpu_system_pct",value,NULL) \
| stats first(cpu_used) as cpu_used first(mem_used) as mem_used by process_class\
] \
| eventstats sum(mem_used) as sum_mem_used sum(cpu_used) as sum_cpu_used \
| eval mem_used=if(process_class="Other Machine Processes",100-sum_mem_used,mem_used) \
| eval cpu_used=if(process_class="Other Machine Processes",100-sum_cpu_used,cpu_used)\
					'
	            });
				
				new PostProcessManager({
					id: 'total-cpu-mem-usage-search',
					managerid: 'resource-usage-by-process-search',
					search: '| search process_class="Idle" | eval total_cpu=(100-cpu_used)."%" | eval total_mem=(100-mem_used)."%" | eval total_splunk_cpu=(sum_cpu_used-cpu_used)."%" | eval total_splunk_mem=(sum_mem_used-mem_used)."%"'
				});
				new PostProcessManager({
					id: 'cpu-resource-usage-search',
					managerid: 'resource-usage-by-process-search',
					search: '| fields process_class cpu_used'
				});
				new PostProcessManager({
					id: 'mem-resource-usage-search',
					managerid: 'resource-usage-by-process-search',
					search: '| fields process_class mem_used | eval process_class=if(process_class="Idle","Free",process_class)'
				});

				
				// INDEXING RATE
				new SearchManager({
					id: 'indexing-rate-search',
					search: '| rest splunk_server=local /services/server/introspection/indexer | fields average_KBps splunk_server | eval average_KBps=round(average_KBps,2)." KB/s"'
				});

				// DISK USAGE
				var diskUsageManager = new SearchManager({
					id: 'disk-usage-search',
					search: '| rest splunk_server=local /services/server/status/partitions-space | eval free = if(isnotnull(available), available, free) | stats sum(capacity) as total_capacity sum(free) as total_free'
				});

				// Searches by type and total concurrent searches
				// TODO some parser error if i break this into multilines
				new SearchManager({
					id: 'search-counts-by-type',
					search: '| rest splunk_server=local /services/server/status/resource-usage/splunk-processes | search search_props.sid=* | stats dc(search_props.sid) AS count by search_props.type | eventstats sum(count) as Total'
				});

				// LICENSE USAGE
				// TODO refactor 
				var licenseUsageManager = new SearchManager({
					id: 'license-usage-search',
					search: '| rest splunk_server=local /services/licenser/pools | rename title AS Pool | search [rest splunk_server=local /services/licenser/groups | search is_active=1 | eval stack_id=stack_ids | fields stack_id] | join type=outer stack_id [rest splunk_server=local /services/licenser/stacks | eval stack_id=title | eval stack_quota=quota | fields stack_id stack_quota] | stats sum(used_bytes) as used max(stack_quota) as total | eval usedGB=round(used/1024/1024/1024,2) | eval totalGB=round(total/1024/1024/1024,2)'
				});

                // KVSTORE: if there's no kv_store role, just removed the corresponding DOM
                var kvStoreRoleSearch = new SearchManager({
                    id: 'kv-store-role-search',
                    search: '| inputlookup assets.csv | search search_group = "dmc_group_kv_store"'
                });
                kvStoreRoleSearch.on('search:done', function(properties) {
                    if (properties.content.resultPreviewCount == 0) {
                        $template.find('.smc-standalone-kv-store-panel').remove();
                    }
                });


		// KVSTORE SEARCHES
                new SearchManager({
                    id: 'kv-store-collections-info-search',
                    search: '| rest splunk_server=local /services/server/introspection/kvstore/collectionstats \
                    | mvexpand data \
                    | spath input=data \
                    | fields splunk_server, ns, size',
                    cancelOnUnload: true,
                    app: utils.getCurrentApp()
                });

                new PostProcessManager({
                    id: 'kv-store-collections-size',
                    search: ' stats sum(size) as size | eval sizeMB = round(size/1024/1024, 2)',
                    managerid: 'kv-store-collections-info-search'
                });

                new PostProcessManager({
                    id: 'kv-store-collections-count',
                    search: ' stats dc(ns) as collections',
                    managerid: 'kv-store-collections-info-search'
                });


				var RESOURCE_USAGE_FIELD_COLORS = "{ \"Free\": 0xCCCCCC, \"Idle\": 0xCCCCCC, \"Other Machine Processes\": 0x999999 }";
				var SERIES_COLORS = "[0x5479af, 0x87a1c7, 0xa1b5d3, 0xbbc9df, 0xd4ddeb]";

				// VIEWS

				// INDEXING
				var indexingRate = new SingleView({
					id: 'indexing-rate-element',
					managerid: 'indexing-rate-search',
					underLabel: _('Total').t(),
					field: 'average_KBps',
					el: $template.find('#indexing-rate-element')
				});
                indexingRate.$el.click(drilldownToIndexingPerformance()).hover(hoverOnSingleValue, hoverOffSingleValue);

                var licenseUsageResultsModel = licenseUsageManager.data('results');
				licenseUsageResultsModel.on('data', function() {
					var usage = licenseUsageResultsModel.data();
					var totalGB = usage.rows[0][usage.fields.indexOf('totalGB')];
					var usedGB = usage.rows[0][usage.fields.indexOf('usedGB')];
					var usedPct = Math.round((usedGB/totalGB)*100);

					var $licenseUsage = $template.find('#license-usage-element');
					$licenseUsage.find('.smc-progress-bar').attr(
						{ 'aria-valuenow': usedPct }
					).css(
						{ 'width': usedPct + '%' }
					);
					$licenseUsage.find('.smc-percent-used').text(usedPct + '%');

					if (usedPct === 100) {
						$licenseUsage.find('.smc-progress-bar').css('background-color', 'red');
					}
					$licenseUsage.find('.smc-sr-only').text(usedPct + '%');

                    $licenseUsage.click(drilldownToLicenseUsage()).hover(hoverOnViz);
                });

				var diskUsageResultsModel = diskUsageManager.data('results');
				diskUsageResultsModel.on('data', function() {
					var usage = diskUsageResultsModel.data();
					var total = usage.rows[0][usage.fields.indexOf('total_capacity')];
					var free = usage.rows[0][usage.fields.indexOf('total_free')];
					var usedPct = Math.round(( (total - free)/total) * 100);

					var $diskUsage = $template.find('#disk-usage-element');
					$diskUsage.find('.smc-progress-bar').attr(
						{ 'aria-valuenow': usedPct }
					).css(
						{ 'width': usedPct + '%' }
					);
					$diskUsage.find('.smc-percent-used').text(usedPct + '%');
					if (usedPct === 100) {
						$diskUsage.find('.smc-progress-bar').css('background-color', 'red');
					}
					$diskUsage.find('.smc-sr-only').text(usedPct + '%');
                    $diskUsage.click(drilldownToResourceUsage()).hover(hoverOnViz);
				});
				

				var totalSearchView = new SingleView({
					id: 'concurrent-searches-element',
					managerid: 'search-counts-by-type',
					underLabel: 'Searches',
					field: 'Total',
					el: $template.find('#concurrent-searches-element') 
				});
                totalSearchView.$el.click(drilldownToSearchActivity()).hover(hoverOnSingleValue, hoverOffSingleValue);
				var searchPieViz = new ChartView({
					id: 'searches-by-type-element',
					managerid: 'search-counts-by-type',
					type: "pie",
					"charting.seriesColors": SERIES_COLORS,
					el: $template.find('#searches-by-type-element')
				}).render();
                searchPieViz.$el.click(drilldownToSearchActivity()).hover(hoverOnViz);


	            // CPU: hostwide
				var totalCPUView = new SingleView({
	            	id: 'cpu-usage-element',
	            	managerid: 'total-cpu-mem-usage-search',
	            	underLabel: _('All Processes').t(),
	            	field: 'total_cpu',
	            	el: $template.find('#cpu-usage-element')
	            });
                totalCPUView.$el.click(drilldownToResourceUsage()).hover(hoverOnSingleValue, hoverOffSingleValue);
	            // CPU: splunk processes
	            var splunkCPUUsageView = new SingleView({
	            	id: 'splunk-cpu-usage-element',
	            	managerid: 'total-cpu-mem-usage-search',
	            	underLabel: _('Splunk Enterprise').t(),
	            	field: 'total_splunk_cpu',
	            	el: $template.find('#splunk-cpu-usage-element')
	            });
                splunkCPUUsageView.$el.click(drilldownToResourceUsage()).hover(hoverOnSingleValue, hoverOffSingleValue);
	            var CPUPieView = new ChartView({
	            	id: 'cpu-usage-by-process-element',
	            	managerid: 'cpu-resource-usage-search',
	            	type: 'pie',
	            	"charting.fieldColors": RESOURCE_USAGE_FIELD_COLORS,
	            	"charting.seriesColors": SERIES_COLORS,
	            	el: $template.find('#cpu-usage-by-process-element')
	            }).render();
                CPUPieView.$el.click(drilldownToResourceUsage()).hover(hoverOnViz);
	            // Memory usage: hostwide
	            var totalMemView = new SingleView({
	            	id: 'mem-usage-element',
	            	managerid: 'total-cpu-mem-usage-search',
	            	field: 'total_mem',
	            	underLabel: _('All Processes').t(),
	            	el: $template.find('#mem-usage-element')
	            });
                totalMemView.$el.click(drilldownToResourceUsage()).hover(hoverOnSingleValue, hoverOffSingleValue);
	            // Memory usage: splunk processes
	            var splunkMemView = new SingleView({
	            	id: 'splunk-mem-usage-element',
	            	managerid: 'total-cpu-mem-usage-search',
	            	field: 'total_splunk_mem',
	            	underLabel: _('Splunk Enterprise').t(),
	            	el: $template.find('#splunk-mem-usage-element')
	            });
                splunkMemView.$el.click(drilldownToResourceUsage()).hover(hoverOnSingleValue, hoverOffSingleValue);
                var memPieView = new ChartView({
	            	id: 'mem-usage-by-process-element',
	            	managerid: 'mem-resource-usage-search',
	            	type: 'pie',
	            	"charting.fieldColors": RESOURCE_USAGE_FIELD_COLORS,
	            	"charting.seriesColors": SERIES_COLORS,
	            	el: $template.find('#mem-usage-by-process-element')
	            }).render();
                memPieView.$el.click(drilldownToResourceUsage()).hover(hoverOnViz);

	            // KV Store 
	            var kvStoreSize = new SingleView({
                    id: "kv-store-size",
                    underLabel: _("Size of Collections (MB)").t(),
                    managerid: "kv-store-collections-size",
                    field: "sizeMB",
                    el: $template.find('#kv-store-size')
                }).render();
                kvStoreSize.$el.click(drilldownToKVStoreView()).hover(hoverOnSingleValue, hoverOffSingleValue);
                
                var kvStoreCollections = new SingleView({
                    id: "kv-store-collections",
                    underLabel: _("Collections").t(),
                    managerid: "kv-store-collections-count",
                    field: "collections",
                    el: $template.find('#kv-store-collections')
                }).render();
                kvStoreCollections.$el.click(drilldownToKVStoreView()).hover(hoverOnSingleValue, hoverOffSingleValue);

                var kvStoreOplogSize = new SingleView({
                    id: "kv-store-oplog-size",
                    underLabel: _("Oplog Size (MB)").t(),
                    managerid: "kv-store-oplog-size-search",
                    field: "oplogsizeMB",
                    el: $template.find('#kv-store-oplog-size')
                }, {tokens: true}).render();
                kvStoreCollections.$el.click(drilldownToKVStoreView()).hover(hoverOnSingleValue, hoverOffSingleValue);

                var memory = computeMemory(serverInfoModel.entry.content.get('physicalMemoryMB'));

				$template.find('.splunk-version').text(serverInfoModel.entry.content.get('version'));
				$template.find('.os-details').text(
					serverInfoModel.entry.content.get('os_name') + ', ' +
					memory.mem + ' ' + memory.units + ' Physical Memory, ' +
					serverInfoModel.entry.content.get('numberOfCores') + ' CPU Cores'
				);
				$template.find('a.go-to-setup').attr('href', getFullPath('/app/splunk_management_console/managementconsole_configure')).text(_('change').t());
			});
		};

		return {
			render: render
		};
	}
);
