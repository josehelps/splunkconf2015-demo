require([
    'underscore',
    'jquery',
    'splunkjs/mvc/sharedmodels',
    'splunkjs/mvc/simplexml',
    'splunkjs/mvc/utils',
    'splunk.util'
], function(_, $, SharedModels, SimpleXml, Utils, SplunkUtil) {
    var REDIRECT_VIEWS = [
        'indexing_performance_deployment',
        'search_activity_deployment',
        'resource_usage_deployment',
        'kv_store_deployment'
    ];
    var NOT_AVAILABLE_VIEW = 'standalone';
    var thisPage = Utils.getPageInfo().page;
    var APP = SharedModels.get('app').get('app');
    var currentApp = SharedModels.get('appLocal');
    var appUrlPrefix = '/app/' + encodeURIComponent(APP);

    var invokeStandalone = function() {
        $('.preload .dashboard-header:after').css('display', 'none');
        $('.dashboard-header .edit-dashboard-menu').css('display', 'none');
        $('.empty-dashboard').css('visibility', 'hidden');
        $('.dashboard-header .description').append(
            $('<span> </span><a href="' + 
                SplunkUtil.make_url(appUrlPrefix + '/managementconsole_configure') +
                '" class="icon-external" target="_blank">' + _(" Switch to distributed mode").t() + '</a>'
            )
        );
    };

    if (_.contains(REDIRECT_VIEWS, thisPage)) {
        $('.dashboard-body > :not(.dashboard-header)').css('visibility', 'hidden');
        currentApp.dfd.done(function() {
            var configured = currentApp.entry.content.get('configured');

            if (!configured) {
                if ($('.dashboard-header h2').length === 0) {
                    $('.dashboard-header').append('<h2>' + _("Not available in standalone mode.").t() + '</h2>');
                }
                if ($('.dashboard-header p.description').length === 0) {
                    $('.dashboard-header').append(
                        '<p class="description">' + _("The page you have requested is not available in standalone mode.").t() + '</p>'
                    );
                }

                invokeStandalone();
            } else {
                $('.dashboard-body > :not(.dashboard-header)').css('visibility', 'visibile');
            }
        });
    }

    if (thisPage === "standalone") {
        invokeStandalone();
    }
});