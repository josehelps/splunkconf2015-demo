/**
 * Created by rtran 7/25/14.
 */
define([
    'jquery',
    'underscore',
    'backbone',
    'views/Base',
    'splunkjs/mvc/searchmanager',
    'splunkjs/mvc/tableview',
    'splunkjs/mvc/utils',
    'splunkjs/mvc/dropdownview',
    'models/search/Job',
    'models/services/search/jobs/Result',
    'collections/services/saved/Searches',
    'views/shared/controls/SyntheticSelectControl',
    'views/managementconsole/table/controls/EditAlertsDialog',
    '../../../../app/splunk_management_console/util',
    'splunk.util',
    'splunk.config',
    'uri/route'
    ],
    function(
        $,
        _,
        Backbone,
        BaseView,
        SearchManager,
        TableView,
        utils,
        DropdownView,
        SearchJobModel,
        ResultModel,
        SavedSearchesCollection,
        SyntheticSelectControl,
        EditAlertsDialog,
        dmcUtil,
        util,
        config,
        route
        ){
            var root = (config.MRSPARKLE_ROOT_PATH.indexOf("/") === 0 ? config.MRSPARKLE_ROOT_PATH.substring(1) : config.MRSPARKLE_ROOT_PATH);

            return BaseView.extend({
                initialize: function(attributes, options) {
                    BaseView.prototype.initialize.apply(this, arguments);
                    this.$el.html(this.compiledTemplate());
                    this.$el.appendTo(options.$container);

                    this.alertsFiredSearch = this._alertsSearchManager();

                    this.alertsTableView = this._alertsTableView();

                    var customInstanceRenderer = TableView.BaseCellRenderer.extend({
                        canRender: function(cellData) {
                            return cellData.field === "Instance";
                        },

                        render: function($td, cellData) {
                            var sid = cellData.value;
                            var searchJob = new SearchJobModel({id: sid});
                            searchJob.fetch().done(function() {
                                var link_id = searchJob.entry.links.get("results");
                                var result = new ResultModel({id: link_id});
                                result.fetch().done(function() {
                                    var instance_str = "";
                                    for(var i=0; i<result.results.length; i++) {
                                        if(instance_str === "") {
                                            instance_str += result.results.models[i].get("Instance")[0];
                                        } else {
                                            instance_str += "</br>" + result.results.models[i].get("Instance")[0];
                                        }
                                    }
                                     $td.html(instance_str);
                                });
                            });
                        }
                    }); 

                    this.customInstanceCellRenderer = new customInstanceRenderer;
                    this.alertsTableView.addCellRenderer(this.customInstanceCellRenderer);
                    this.alertsTableView.render();

                    this.dropDownFilter = this._dropdownFilter();

                    this._bindCountListener();
                    this._bindFilterListener();
                    this._initializeEditButtonListener();
                    this._initializeRowDrilldown();

                    this.render();
                },
                _alertsSearchManager: function() {
                    // search to grab all triggered alerts (defaulted to filter within last hour)
                    return new SearchManager({
                        id: 'alerts-fired-search',
                        search: '| `dmc_get_all_triggered_alerts(1440)`',
                        cancelOnUnload: true,
                        app: utils.getCurrentApp()
                    }); 
                },
                _alertsTableView: function() {
                    // splunkjs table to display alerts
                    return new TableView({
                        "id": "alerts-table",
                        "managerid": "alerts-fired-search",
                        "el": $("#alerts-fired-table-view"),
                        "wrap": "true",
                        "drilldown": "row",
                        "drilldownRedirect": false,
                        "pageSize": 5
                    });
                },
                _initializeRowDrilldown: function() {
                    // event for table drilldown to redirect to triggered alerts scoped to the one selected.
                    this.$(".shared-resultstable-resultstablemaster").on("click", ".shared-resultstable-resultstablerow", function() {
                        // navigate DOM to retrieve alert name
                        var alert_name = $(this).children().first().text().trim();

                        // construct the alert_id for the route url. double encoding necessary (lol)
                        var alert_id = encodeURI(encodeURI('/servicesNS/nobody/splunk_management_console/alerts/fired_alerts/'+alert_name));

                        // monster helper method to construct url
                        window.open(route.triggeredAlerts(root, config.LOCALE, 'splunk_management_console', {'data': {'app': 'splunk_management_console', 'owner': 'admin', 'serverity': '*', 'alerts_id': alert_id}}), "_blank");
                    });
                },
                _dropdownFilter: function() {
                    return new SyntheticSelectControl({
                        model: null,
                        modelAttribute: null,
                        label: _('Filter by Last:').t(),
                        defaultValue: '1440',
                        items: [
                            { value: '60',  label: _('1 Hour').t()  },
                            { value: '240',  label: _('4 Hours').t()  },
                            { value: '1440',  label: _('24 Hours').t()  },
                            { value: '4320',  label: _('3 days').t()  },
                            { value: '10080',  label: _('7 days').t()  }
                        ],
                        save: false,
                        elastic: true,
                        menuWidth: "narrow",
                        toggleClassName: 'btn-pill',
                        popdownOptions: {attachDialogTo:'body'}
                    });
                },
                _bindCountListener: function() {
                    // count number of triggered alerts and replace number in DOM
                    this.alertsFiredSearch.on("search:done", function(properties) {
                        var count = properties.content.resultPreviewCount;
                        if(count === 1) {
                            $('#smc-alerts-title').html(_("Alert").t());
                        } else {
                            $('#smc-alerts-title').html(_("Alerts").t());
                        }
                        $('#smc-alerts-count').html(count);
                    });
                },
                _bindFilterListener: function() {
                    // re-render alerts table when filter value is changed
                    this.dropDownFilter.on('change', function(value) {
                        this.alertsFiredSearch.set('search', '| `dmc_get_all_triggered_alerts('+value+')`');
                    }.bind(this)); 
                },
                _initializeEditButtonListener: function() {
                    // creates a modal to enable or disable alerts
                    $('.control-options').on("click", "#edit-alerts-btn", function(e) {
                        e.preventDefault();
                        var savedSearchesCollection = new SavedSearchesCollection();
                        savedSearchesCollection.fetch({
                          data: {
                            app: 'splunk_management_console',
                            owner: 'nobody',
                            search: 'name="DMC Alert*"'
                          },
                          success: function(collection) {
                            var modal = new EditAlertsDialog({
                                collection: { 
                                    alerts: collection 
                                },
                                onHiddenRemove: true
                            });
                            $('body').append(modal.render().el);
                            modal.show();
                          },
                          error: function() {
                            throw new Error("Savedsearch fetch failed");
                          }
                        });
                    });
                },
                render: function() {
                    this.$('.control-options').append(this.dropDownFilter.render().el);
                    this.$('#triggered-alerts-link').attr('href', route.triggeredAlerts(root, config.LOCALE, 'splunk_management_console'));

                    return this;
                },
                needsSetup: function() {
                    this.$('.control-options').remove();
                    this.$('#smc-alerts-count').remove();
                    this.$('.details-row').html(
                        '<h3 class="icon-alert"> ' +
                            _("Alerts require setup. Please ").t() + 
                            ' <a href="' + dmcUtil.getFullPath('/app/splunk_management_console/managementconsole_configure') + '">set up</a>' +
                            _(" your instance first.").t() +
                        '</h3>'
                    ).css('text-align', 'center');
                },
                template: 
                    '<div class="smc-alerts-panel smc-distributed-mode-row smc-distributed-mode-alerts-panel">\
                        <div class="smc-alerts-title-section">\
                            <div class="row-fluid">\
                                <div class="span9">\
                                    <div class="smc-panel-title">\
                                        <span id="smc-alerts-count">0</span>\
                                        <span id="smc-alerts-title">' + _("Alerts").t() + '</span>\
                                    </div>\
                                    <div class="control-options">\
                                        <a class="btn-pill" id="edit-alerts-btn" href="#">' + _('Enable or Disable').t() + '</a>\
                                        <a class="btn-pill" id="triggered-alerts-link" href="#">' + _('Manage triggered alerts').t() + '</a>\
                                    </div>\
                                </div>\
                                <div class="span3">\
                                    <object class="smc-panel-icon" type="image/svg+xml" data="' + util.make_url("/static/app/splunk_management_console/icons/Alert.svg") + '"></object>\
                                </div>\
                            </div>\
                        </div>\
                        <div class="panel-element-row details-row">\
                            <div class="dashboard-element html" id="alerts-fired-table-view"></div>\
                        </div>\
                    </div>'
        });
    }
);
