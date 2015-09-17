require([
    'jquery',
    'underscore',
    'splunkjs/mvc',
    'views/shared/results_table/renderers/BaseCellRenderer',
    'splunkjs/mvc/tableview',
    'splunkjs/mvc/simplexml/ready!'
], function($, _, mvc, BaseCellRenderer, TableView) {

    var DataBarCellRenderer = BaseCellRenderer.extend({
        canRender: function(cell) {
            return (cell.field === 'percent');
        },
        render: function($td, cell) {
            $td.addClass('data-bar-cell').html(_.template('<div class="data-bar-wrapper"><div class="data-bar" style="width:<%- percent %>%"></div></div>', {
                percent: Math.min(Math.max(parseFloat(cell.value), 0), 100)
            }));
        }
    });

    mvc.Components.get('table1').getVisualization(function(tableView) {
        tableView.table.addCellRenderer(new DataBarCellRenderer());
        tableView.table.render();
    });


// use this code here to insert icons in pctLoad field

    var CustomIconRenderer = TableView.BaseCellRenderer.extend({
        canRender: function(cell) {
            return cell.field === 'pctLoad';
        },
        render: function($td, cell) {
            var num = cell.value;

            // Compute the icon base on the field value
            var icon;
            if(num > 75) {
                icon = 'alert-circle';
            } else if(num > 50) {
                icon = 'alert';
            } else {
                icon = 'check';
            }

            // Create the icon element and add it to the table cell
            $td.addClass('icon-inline numeric').html(_.template('<%- text %> <i class="icon-<%-icon%>"></i>', {
                icon: icon,
                text: cell.value
            }));
        }
    });

    mvc.Components.get('table2').getVisualization(function(tableView){
        // Register custom cell renderer
        tableView.table.addCellRenderer(new CustomIconRenderer());
        // Force the table to re-render
        tableView.table.render();
    });
	
});
