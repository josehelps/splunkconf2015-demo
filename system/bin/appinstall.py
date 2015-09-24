import splunk
import splunk.admin as admin
import splunk.appbuilder as appbuilder
import splunk.rest as rest
import splunk.clilib.bundle_paths as bundle_paths

import urllib

FORCE = 'update'

class AppInstallHandler(admin.MConfigHandler):
    def __init__(self, scriptMode, ctxInfo):
        admin.MConfigHandler.__init__(self, scriptMode, ctxInfo)
        # This handler already lists upon create/edit, turn this off.
        self.shouldAutoList = False

    def setup(self):
        if self.requestedAction == admin.ACTION_CREATE:
            self.supportedArgs.addOptArg(FORCE)
        else:
            # SPL-41076 - only doc Create, as that's all that's supported.
            self.docShowEntry = False
            
        self.setReadCapability(admin.CAP_NONE)
        self.setWriteCapability(admin.ADMIN_ALL_OBJECTS)            

    '''
    Install an application by url/local path
    '''
    def handleCreate(self, confInfo):
        location = self.callerArgs.id

        force = False
        if FORCE in self.callerArgs:
            force = bundle_paths.parse_boolean(self.callerArgs[FORCE][0])

        try:
            bundle, status = appbuilder.installApp(location, force)
        except splunk.RESTException, e:
            raise admin.InternalException(e.msg)
    
        upgraded = (status == bundle_paths.BundleInstaller.STATUS_UPGRADED)
    
        appName = bundle.name(raw=True) or ''
        confInfo[appName].append('name', appName)
        confInfo[appName].append('location', bundle.location() or '')
        confInfo[appName].append('status', 'upgraded' if upgraded else 'installed')
        confInfo[appName].append('source_location', location)

        if not upgraded:
            reloader = 'apps/local/_reload'
        else:
            reloader = 'apps/local/%s/_reload' % urllib.quote(bundle.name())
        rest.simpleRequest(reloader, sessionKey=self.getSessionKey())
        
    def handleList(self, confInfo):
        pass

admin.init(AppInstallHandler, admin.CONTEXT_APP_ONLY)
