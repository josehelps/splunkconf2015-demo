import splunk
import splunk.admin as admin
import splunk.appbuilder as appbuilder
import re
import splunk.appserver.mrsparkle.lib.i18n as i18n

HTTP_POST_TEMPLATE   = "template"
HTTP_POST_LABEL      = "label"
HTTP_POST_DESC       = "description"
HTTP_POST_VISIBLE    = "visible"
HTTP_POST_AUTHOR     = "author"
HTTP_POST_CONFIGURED = "configured"


DEFAULT_TEMPLATE = "barebones"

class LocalAppsHandler(admin.MConfigHandler):
    def __init__(self, scriptMode, ctxInfo):
        admin.MConfigHandler.__init__(self, scriptMode, ctxInfo)
        # This handler already lists upon create/edit, turn this off.
        self.shouldAutoList = False

    '''
    Set up supported arguments
    '''
    def setup(self):
            
        if self.requestedAction == admin.ACTION_CREATE:
            # Let the C++ handler do all the validation work.
            self.supportedArgs.addOptArg('*')

    '''
    Create a new application
    '''
    def handleCreate(self, confInfo):
        args = self.callerArgs.data
        
        # Sanity checking for app ID: no special chars and shorter than 100 chars
        appName = self.callerArgs.id
        if not appName or len(appName) == 0:
            raise admin.ArgValidationException(_('App folder name is not set.'))
        
        if re.search('[^A-Za-z0-9._-]', appName):
            raise admin.ArgValidationException(_('App folder name cannot contain spaces or special characters.'))
            
        if len(appName) > 100:
            raise admin.ArgValidationException(_('App folder name cannot be longer than 100 characters.'))

        kwargs = {
            'label'       : _getFieldValue(args, HTTP_POST_LABEL, appName, maxLen=100),
            'visible'     : _getFieldValue(args, HTTP_POST_VISIBLE, 'true'),
            'author'      : _getFieldValue(args, HTTP_POST_AUTHOR, '', maxLen=100),
            'description' : _getFieldValue(args, HTTP_POST_DESC, '', maxLen=500),
            'configured'  : _getFieldValue(args, HTTP_POST_CONFIGURED, '0'),
        }
        template = _getFieldValue(args, HTTP_POST_TEMPLATE, DEFAULT_TEMPLATE)
        
        try:    
            url = appbuilder.createApp(appName, template, **kwargs)
            appbuilder.addUploadAssets(appName)
        except splunk.RESTException, e:
            raise admin.InternalException(e.msg)
            
        confInfo[appName].append('name', appName)
        for field in kwargs:
            confInfo[appName].append(field, kwargs[field])
            
    '''
    Controls local applications
    '''
    def handleEdit(self, confInfo):
        appName = self.callerArgs.id
        appbuilder.addUploadAssets(appName)

    '''
    Handles other commands
    '''
    def handleCustom(self, confInfo):
        action = self.customAction

        actionType = self.requestedAction
        
        # Create a package of an application
        if self.customAction == 'package':
            appName = self.callerArgs.id
            try:
                url, path = appbuilder.packageApp(appName)
                
                confInfo['Package'].append('name', appName)
                confInfo['Package'].append('url', url)
                confInfo['Package'].append('path', path)
                
            except splunk.RESTException, e:
                raise admin.ArgValidationException(e.msg)

    '''
    This handler is overridden by UIAppsHandler
    '''
    def handleList(self, confInfo):
        pass

        
def _getFieldValue(args, fieldName, defaultVal=None, maxLen=None):
    value = args[fieldName][0] or defaultVal if fieldName in args else defaultVal
    if value and maxLen and len(value) > maxLen:
        raise admin.ArgValidationException(i18n.ungettext('App %(fieldName)s cannot be longer than %(maxLen)s character.', 
                                                          'App %(fieldName)s cannot be longer than %(maxLen)s characters.',
                                                          maxLen) % {'fieldName' : fieldName, 'maxLen' : maxLen} )
    return value 
        
# initialize the handler, and add the actions it supports.    
admin.init(LocalAppsHandler, admin.CONTEXT_NONE)
