# This work contains trade
#secrets and confidential material of Splunk Inc., and its use or disclosure in
#whole or in part without the express written permission of Splunk Inc. is prohibited.


import splunk.clilib.cli_common  as comm
import splunk.clilib.bundle_paths as bundle_paths
import logging as logger
import splunk.appserver.Template as Template
import splunk.appserver.html as html
import xml.sax.saxutils as su

import splunk.appserver.SearchService as SearchService
from splunk.appserver.V3RestHandlers import Saved as Saved

# if field is required, set default value to None
knownFields = {'query':None, 'name':'', 'tags':''} # removed for now -- 'priority':'5', 'example':'', 'description':''

# /////////////////////////////////////////////////////////////////////////////
# UI handling methods
# /////////////////////////////////////////////////////////////////////////////

def add(requestObject):
    '''
    i.e. http://localhost:8000/v3/custom/addeventtype.add?...
    '''
    # set output as html
    requestObject.setHeader('content-type', 'text/html')

    vals = {}
    # set field values, including default vals
    for field,defaultval in knownFields.items():
        if field in requestObject.args:
            vals[field] = requestObject.args[field][0].strip()
        elif defaultval == None:
            return "<html><body><h1>Error: missing required field: %s</h1></body></html>" % field
        else:
            vals[field] = defaultval

    # special case example, by stripping off 'example:'
    ##  if vals['example'].lower().startswith('example:'):
    ##     vals['example'] = vals['example'][8:].strip()

    session = requestObject.getSession()
    authString = session.sessionNamespaces['authXml']
    name = vals['name']
    if _addToConf(vals, authString, requestObject):
        message = 'Event type successfully saved'
        templ = Template.Template(bundle_paths.make_path('addeventtype_done.html'))
    else:
        if (name == ''):
            message = 'Please provide an event type name'
        else:
            message = 'Error: Unable to save event type'
        templ = Template.Template(bundle_paths.make_path('addeventtype.html'))
        templ.query       = html.Raw(su.quoteattr(vals['query']))        
        #templ.example     = vals['example']
        templ.name        = vals['name']
        #templ.description = vals['description']
        templ.tags        = vals['tags']
        #templ.priority    = vals['priority']
        
    message = html.Raw('<p class="message">%s</p>' % message) 
    templ.message = message
   
    return templ.get_string()


def _addToConf(vals, authString, reqObj):

    # check for a name
    if vals['name'] == '':
        return False

    # stuff the items from val into the reqObj args dictionary.
    for attr, val in vals.items():
        if not reqObj.args.has_key(attr):
            reqObj.args[attr] = []
        reqObj.args[attr].append(val)

    # set this is an eventtype
    reqObj.args['isEventType'] = []
    reqObj.args['isEventType'].append('1')
    
    # call the Saved.process_set method
    try:
        logger.debug("Saving event type" + vals['name'] )
        sessNS = reqObj.getSession().sessionNamespaces
        savedSearch = Saved(reqObj, reqObj.getSession(), SearchService.gSearchService)
        savedSearch.process_set()
        return True
    except:
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    vals = {'name':'myname', 'query':'this is my query', 'example':'this is an example', 'tags':'my,tag,are,cool', 'priority':'4', 'description':'my desc'}
    result = _addToConf(vals, comm.getAuthInfo('admin','changeme'))
    print 'result: %s' % result
