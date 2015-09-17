import splunk.admin as admin
import splunk.appbuilder as appbuilder

ADMIN_ALL_OBJECTS = "admin_all_objects"

class AppTemplatesHandler(admin.MConfigHandler):
    def setup(self):
        self.setReadCapability(ADMIN_ALL_OBJECTS)
    
    '''
    Lists locally installed applications
    '''
    def handleList(self, confInfo):
        for template in appbuilder.getTemplates():
            confInfo[template].append('lol', 'wut')

admin.init(AppTemplatesHandler, admin.CONTEXT_APP_ONLY)
