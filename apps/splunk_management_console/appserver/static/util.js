define(
	[
		"splunkjs/mvc/utils"
	],
	function(utils) {

		return {
			getFullPath: function(path) {
		        var root = utils.getPageInfo().root;
		        var locale = utils.getPageInfo().locale;
		        return (root ? '/'+root : '') + '/' + locale + path;
		    }
		};
	}
);