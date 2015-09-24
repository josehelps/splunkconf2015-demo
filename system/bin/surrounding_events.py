#   Version 4.0
#

from splunk.clilib import cli_common, control_api
from splunk.appserver import Util, Template, html, SearchFormatter, SearchAgent
import logging as logger
import os, traceback
import xml.etree.cElementTree as et


def get(requestObject) :
    requestArgs = _flattenRequestArgs(requestObject)    
    
    requestObject.setHeader('content-type', 'text/html')
    t = _getTemplate("surrounding_events.html", requestArgs)
    
    
    searchCommand = _getSearchCommand(requestArgs)
    
    #tack the extra output clause back onto q
    searchCommand += "| outputxml format::raw maxlines::10000"

    requestArgs["q"] = searchCommand

    # get the proper search agent
    searchAgent = SearchAgent.Factory(requestArgs, requestObject.getSession())

    # return the output from search agent
    agentResponse = searchAgent.run()
     
    if( searchAgent.messages ):
        messagesBlock = html.HTMLList()
        for message in searchAgent.messages:
            messagesBlock.append( html.Raw( message["text"] ) )
            messagesBlock.append( html.br() )
        messagesBlock.append( html.br() )
        t.messages = messagesBlock
    else:
        t.messages = html.Raw("")
    
    parsedResponse = et.fromstring(agentResponse)
    
    eventsBlock = html.HTMLList()

    cdIndex = ""
    decIndex = ""
    
    for rNode in parsedResponse.findall(".//cols"):
        for cNode in rNode.findall(".//col"):
            if cNode.text == "_decoration":
                decIndex = cNode.attrib["cd"]
            elif cNode.text == "_cd":
                cdIndex = cNode.attrib["cd"]
    
    for rNode in parsedResponse.findall(".//r") : 
        thisEventId = "0:0000000"
        thisDecoration = ""
        try : 
            for mNode in rNode.findall(".//m") : 
                if mNode.attrib["col"] == cdIndex : 
                    thisEventId = mNode.text
                elif mNode.attrib["col"] == decIndex : 
                    thisDecoration = mNode.text
                
        except Exception, e: 
            logger.debug("could not get thisEventId")
            traceback.print_exc()
            

        for vNode in rNode.findall(".//v") :         
            logger.debug("****" * 20)
            logger.debug(vNode.text)
            preElement = html.pre()[vNode.text]

            # the class is needed for the CSS highlighting, but an ID is also used by the JS, for the scroll-to behaviour. 
            thisClass = "resultRow " + thisDecoration 
            thisId = ""
            if (thisEventId == requestArgs["eventId"]) :
                thisClass += " selectedRow"
                thisId = "selectedItem"
           
            innerDiv = html.div(class_=thisClass, id="events" + thisEventId)[preElement]
            resultRowDiv = html.div(id=thisId)[innerDiv]

            eventsBlock.append(resultRowDiv)

    t.events = eventsBlock
    
    if( not requestArgs.has_key("server") ):
        t.server = ""

    t.run(requestObject)
    return ""

    
    

def export(requestObject) :

    requestArgs = _flattenRequestArgs(requestObject)    
    searchCommand = _getSearchCommand(requestArgs)

    requestObject.setHeader("Content-type", "text/plain")
    requestObject.setHeader("Content-disposition", "attachment; filename=source.txt;")
    
    #tack the extra output clause back onto q
    searchCommand += "| outputtext"
    requestArgs["q"] = searchCommand
    
    # get the proper search agent
    searchAgent = SearchAgent.Factory(requestArgs, requestObject.getSession())

    # return the output from search agent
    agentResponse = searchAgent.run()

    parsedResponse = et.fromstring(agentResponse)

    try :
        resultsNode = parsedResponse.findall(".//results")[0] 
        return resultsNode.text

    except Exception,e : 
        logger.error("Show source did not return expected results. ")
        return agentResponse

##################
# Internal functions that arent intended to be accessed via the endpoints.
##################

def _getTemplate(fileNameStr,requestArgs) : 
    path = [os.environ["SPLUNK_HOME"]]
    path.append("share/splunk")
    try :
        frontEndName = cli_common.confSettings["web"]["settings"]
        if not frontend_name: frontend_name = 'oxiclean'
    except Exception, e : 
        frontend_name = 'oxiclean'
    frontend_dirname = 'search_' + frontend_name
    path.append(frontend_dirname);
    path.append('static/html')
    path.append(fileNameStr)

    t = Template.Template("/".join(path))
    for key in requestArgs : 
        t.__setattr__(key, requestArgs[key])
    return t


def _getSearchCommand(requestArgs) :
    searchCommand = ["|"]
    remote = False
    if( requestArgs.has_key("server") ):
        remote = True
        searchCommand.append( "remote " + requestArgs["server"] + " [ ");
    searchCommand.append("surrounding")
    searchCommand.append("id::" + requestArgs["eventId"])
    searchCommand.append("index::" + requestArgs["eventIndex"])
    searchCommand.append("searchkeys=\"" + requestArgs["q"] + "\"")
    searchCommand.append("readlevel::2")
    searchCommand.append("maxresults::" + requestArgs["num"])
    searchCommand.append("timeBefore::60")
    searchCommand.append("timeAfter::60")
    if( remote ):
        searchCommand.append( " ]" )

    return " ".join(searchCommand)

def _flattenRequestArgs(requestObject) : 
    # generate flattened request args dict
    requestArgs = {}
    for key in requestObject.args:
        requestArgs[key] = requestObject.args[key][0]
    return requestArgs
