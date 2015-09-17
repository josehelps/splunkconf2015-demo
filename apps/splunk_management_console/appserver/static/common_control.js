// this is to control the 'host' and 'server_name' token
require(
    [
        'splunkjs/mvc',
        'uri/route',
        'splunkjs/mvc/sharedmodels',
        'splunkjs/mvc/simplexml/ready!'
    ],
    function(
        mvc,
        route,
        sharedModels
    ) {
        // TODO: for some reason both defaultModel and submittedModel are needed
        var submittedModel = mvc.Components.getInstance('submitted');
        var defaultModel = mvc.Components.getInstance('default');

        // switch between snapshot and historical
        // make sure data-item=token-name 
        $('#link-switcher-view').on('click', 'a', function(e) {
            e.preventDefault();
            var $target = $(e.target);
            if ($target.hasClass('active')) { return ;}

            // remove siblings tokens
            $target.siblings('a.btn-pill').removeClass('active');
            $target.siblings('a.btn-pill').each(function(index, element) {
                var item = $(element).data('item');
                defaultModel.unset(item);
                submittedModel.unset(item);
            });

            // set token for clicked pill
            $target.addClass('active');
            defaultModel.set($target.data('item'), true);
            submittedModel.set($target.data('item'), true);
        });

        // workaround: hide panel background to make it looks like a section title
        $('#snapshot_section_title').parent().parent().parent().parent().css({'background-color': 'inherit', 'border': 'none'});
        $('#historical_section_title').parent().parent().parent().parent().css({'background-color': 'inherit', 'border': 'none'});
        $('#snapshot_section_title').parent().css({'padding': '0px'});
        $('#historical_section_title').parent().css({'padding': '0px'});
        $('.input-timerangepicker').parent().appendTo($('#historical_section_title'));

        // close drilldown panel
        $('#smc-close-drilldown').on('click', function(e) {
            e.preventDefault();
            submittedModel.unset('top10drilldown');
            defaultModel.unset('top10drilldown');
        });

        // process class learnMore link
        var application = sharedModels.get('app');
        var learnMoreLink = route.docHelp(
            application.get('root'),
            application.get('locale'),
            'app.management_console.resource_usage_process_class'
        );
        $('.dmc_process_class_learn_more').attr('href', learnMoreLink);
    }
);