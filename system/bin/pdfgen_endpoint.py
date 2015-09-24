from urlparse import urlparse 

import sys
import lxml.etree as et
import logging
import urllib
import time
import json
import cStringIO
import re
import xml.sax.saxutils as su

import splunk
import splunk.rest as rest
import splunk.entity as entity
import splunk.auth
import splunk.models.dashboard as sm_dashboard
import splunk.models.dashboard_panel as sm_dashboard_panel
import splunk.models.saved_search as sm_saved_search
import splunk.search
import splunk.search.searchUtils
from splunk.util import normalizeBoolean

import splunk.pdf.pdfgen_views as pv
import splunk.pdf.pdfgen_utils as pu
import splunk.pdf.pdfgen_chart as pc

import splunk.pdf.pdfrenderer as pdfrenderer

logger = pu.getLogger()

ERROR_MSG = _("Unable to render PDF.")
DEFAULT_FEED_COUNT = 1000
DEFAULT_TIMEOUT = 3600 # in seconds
DEFAULT_MAX_ROWS_PER_TABLE = 1000
DEFAULT_INCLUDE_SPLUNK_LOGO = True
DEFAULT_PAPER_SIZE =   'letter'
DEFAULT_PAPER_ORIENTATION = 'portrait'

# Change the default lxml parsing to not allow imported entities
import splunk.lockdownlxmlparsing

class ArgError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.value)

class TimeoutError(Exception):
    def __str__(self):
        return repr(self.value)

class PDFGenHandler(splunk.rest.BaseRestHandler):
    _args = {}
    _deletePdfFileAfterSettingResponse = True
    _timeoutTime = None

    _views = []
    _inputSids = {}
    
    _title = "Untitled"
    _dashboardName = None
    _dashboardXml = None
    _reportName = None
    _viewType = None
    _paperSize = DEFAULT_PAPER_SIZE
    _namespace = None
    _owner = None
    _timeoutDuration = DEFAULT_TIMEOUT
    _maxRowsPerTable = DEFAULT_MAX_ROWS_PER_TABLE
    _includeSplunkLogo = DEFAULT_INCLUDE_SPLUNK_LOGO
    _cidFontList = None
    _now = None
    _timestampStr = ""
    _searchStr = None
    _et = ''
    _lt = ''
    _inactiveViews = None

    _touchSearchJobsLastTime = None
    _pdfBuffer = None
    _pdfRenderer = None

    VIEW_TYPE_DASHBOARD = 'dashboard'
    VIEW_TYPE_REPORT =    'report'
    VIEW_TYPE_SEARCH = 'search'

    ARG_INPUT_DASHBOARD = 'input-dashboard'
    ARG_INPUT_DASHBOARD_XML = 'input-dashboard-xml'
    ARG_INPUT_REPORT = 'input-report'
    ARG_INPUT_SEARCH = 'input-search'
    ARG_INPUT_ET = 'et'
    ARG_INPUT_LT = 'lt'
    ARG_INPUT_PAPERSIZE = 'paper-size'
    ARG_INPUT_SID = 'sid'
    ARG_INPUT_NAMESPACE = 'namespace'
    ARG_INPUT_OWNER = 'owner'
    ARG_INPUT_TIMEOUT = 'timeout'
    ARG_INPUT_MAX_ROWS_PER_TABLE = 'max-rows-per-table'
    ARG_INPUT_INCLUDE_SPLUNK_LOGO = 'include-splunk-logo'
    ARG_INPUT_NOW = 'now'
    ARG_CACHE_BUSTER = '_'   
    ARG_CSRF_FORM_KEY = 'splunk_form_key'
    
    _validArgs = [
        ARG_INPUT_DASHBOARD,
        ARG_INPUT_DASHBOARD_XML,
        ARG_INPUT_REPORT,
        ARG_INPUT_SEARCH,
        ARG_INPUT_ET,
        ARG_INPUT_LT,
        ARG_INPUT_PAPERSIZE,
        ARG_INPUT_SID,
        ARG_INPUT_NAMESPACE,
        ARG_INPUT_OWNER,
        ARG_INPUT_TIMEOUT,
        ARG_INPUT_MAX_ROWS_PER_TABLE,
        ARG_INPUT_INCLUDE_SPLUNK_LOGO,
        ARG_INPUT_NOW,
        ARG_CACHE_BUSTER,
        ARG_CSRF_FORM_KEY
        ]
    
    SID_VALIDATOR_STR="sid_([0-9]+)"
    sidRE=re.compile(SID_VALIDATOR_STR)

    POLLING_WAIT_TIME = 0.5
    TOUCH_SEARCH_INTERVAL = 10

    ALERT_ACTIONS_ENTITY = '/configs/conf-alert_actions'
    LIMITS_ENTITY = '/configs/conf-limits'
    WEB_ENTITY = '/configs/conf-web'

    def handle_GET(self):
        self._handleRequest()

    def handle_POST(self):
        self._handleRequest()

    def _handleRequest(self):
        logger.debug("pdfgen/render request: " + str(self.request))

        if not self._initialize():
            return

        if not self._render():
            return

        self._respond()

    def _initialize(self):
        try:
            self._initParameters()

            if self._viewType == self.VIEW_TYPE_DASHBOARD:
                # handle Xml vs. entity name
                logger.debug("dashboardName=%s dashboardXml=%s" % (self._dashboardName, self._dashboardXml))
                if self._dashboardName != None:
                    (self._title, self._views) = pv.getDashboardTitleAndPanels(
                        dashboard_name=self._dashboardName, 
                        namespace=self._namespace, 
                        owner=self._owner, 
                        sessionKey=self.sessionKey)
                elif self._dashboardXml != None:
                    (self._title, self._views) = pv.getDashboardTitleAndPanelsFromXml(
                        dashboardXml=self._dashboardXml, 
                        namespace=self._namespace, 
                        owner=self._owner, 
                        sessionKey=self.sessionKey)
            elif self._viewType == self.VIEW_TYPE_REPORT:
                self._views.append(pv.Report(savedSearchName=self._reportName, namespace=self._namespace, owner=self._owner, sessionKey=self.sessionKey))
                self._title = self._reportName
            elif self._viewType == self.VIEW_TYPE_SEARCH:
                self._title = self._reportName
                self._views.append(pv.SearchReport(search=self._searchStr, et=self._et, lt=self._lt, title=self._title, namespace=self._namespace, owner=self._owner, sessionKey=self.sessionKey))

            self._handlePresetSearchIDs()
            
            # instantiate the pdfRenderer object with a file-like object
            self._pdfBuffer = cStringIO.StringIO()
            self._pdfRenderer = pdfrenderer.PDFRenderer(title=self._title, outputFile=self._pdfBuffer, paperSize=self._paperSize, timestamp=self._timestampStr, includeSplunkLogo=self._includeSplunkLogo, cidFontList=self._cidFontList)
            return True
        except ArgError as e:
            self.response.setStatus(400)
            self.response.write(e.message)
        except Exception as e:
            errorMsg = "Bailing out of Integrated PDF Generation. Exception raised while preparing to render \"%s\" to PDF. %s" % (self._title, e)
            import traceback
            logger.error("%s\n%s" % (errorMsg, traceback.format_exc()))
            self._outputError([errorMsg])
        return False

    def _render(self):
        try:
            self._inactiveViews = self._views[:]
            for _ in range(3):
                self._startNextSearch()

        except Exception as e:
            errorMsg = "Exception raised while trying to prepare \"%s\" for rendering to PDF. %s" % (self._title, e)
            import traceback
            logger.error("%s\n%s" % (errorMsg, traceback.format_exc()))
            self._outputError([errorMsg])
            return False

        # iterate over views and render each to the pdf
        viewPrepErrors = []
        for i, view in enumerate(self._views):
            try:
                self._keepAllSearchesAlive()
                self._checkForTimeout()
               
                isLastView = (i == len(self._views) - 1) 
                self._renderView(self._pdfRenderer, view, lastView = isLastView)
                
                self._startNextSearch()

            except TimeoutError:
                errorMsg = "Timeout while trying to prepare \"%s\" for rendering to PDF." % self._title
                self._outputTimeoutError(errorMsg)
                return
            except Exception as e:
                errorMsg = "Exception raised while trying to prepare \"%s\" for rendering to PDF. %s" % (self._title, e)
                logger.error(errorMsg)
                viewPrepErrors.append(errorMsg)

        # if we weren't able to render any views successfully, output an error as response to endpoint
        if len(viewPrepErrors) == len(self._views):
            self._outputError(viewPrepErrors)
            logger.error("No views prepared without exceptions. Bailing out of Integrated PDF Generation.")
            return False
            
        try:
            self._pdfRenderer.save()
        except Exception as e:
            errorMsg = []
            errorMsg.append("Exception raised while trying to render \"%s\" to PDF." % (self._title))

            # SPL-80872 - [PDF] Cannot render PDF report of A5 size if the table is too big
            if "too large on page" in e.message:
                errorMsg.append("Please try using a larger paper size than %s." % (self._paperSize))

            errorMsg.append("%s" % (e))
            import traceback
            logger.error("%s\n%s" % (errorMsg, traceback.format_exc()))
            self._outputError(errorMsg)
            return False

        return True

    def _respond(self):
        # save and write out the file
        try:
            self.response.write(self._pdfBuffer.getvalue())
            self.response.setHeader('content-type', 'application/pdf')
            # override normal cache-control header to fix problem on ie6-ie8 (see SPL-50739)
            self.response.setHeader('cache-control', 'max-age=0, must-revalidate')
            self.response.setStatus(200)
            self._pdfBuffer.close()
        except Exception as e:
            errorMsg = "Exception raised while trying to respond. Bailing out of Integrated PDF Generation. Rendering \"%s\" to PDF. %s" % (self._title, e)
            logger.error(errorMsg)
            self._outputError([errorMsg])
            return False
        return True

    def _outputTimeoutError(self, message):
        self.response.write("PDF Generation timed out: %s" % message)
        self.response.setHeader('content-type', 'text/html')
        self.response.setStatus(408)

    def _outputError(self, errorDetailsArray):
        outputErrorMsg = ERROR_MSG + "<br/><ul>"
        for errorDetail in errorDetailsArray:
            outputErrorMsg = outputErrorMsg + "<li>" + su.escape(errorDetail) + "</li>"
        outputErrorMsg = outputErrorMsg + "</ul>"
        self.response.write(outputErrorMsg)
        self.response.setHeader('content-type', 'text/html')
        self.response.setStatus(400)

    def _initParameters(self):
        self._owner=self.request['userName']
        self._initArgs()
        self._initWebDefaults()
        self._initLimitsDefaults()       
        self._initAlertActionsDefaults()
 
        # initialize view type
        if self.ARG_INPUT_DASHBOARD in self.args:
            self._dashboardName = self.args.get(self.ARG_INPUT_DASHBOARD)
            self._viewType = self.VIEW_TYPE_DASHBOARD
        elif self.ARG_INPUT_DASHBOARD_XML in self.args:
            self._dashboardXml = urllib.unquote(self.args.get(self.ARG_INPUT_DASHBOARD_XML))
            self._viewType = self.VIEW_TYPE_DASHBOARD
            logger.debug("pdfgen/render xml=%s" % self._dashboardXml)
        elif self.ARG_INPUT_REPORT in self.args:
            self._reportName = self.args.get(self.ARG_INPUT_REPORT)
            self._viewType = self.VIEW_TYPE_REPORT 
        elif self.ARG_INPUT_SEARCH in self.args:
            self._searchStr = self.args.get(self.ARG_INPUT_SEARCH, "No search query specified")
            self._et = self.args.get(self.ARG_INPUT_ET, 0)
            self._lt = self.args.get(self.ARG_INPUT_LT, '')

            # if et or lt is 0.000 change it to 0
            if float(self._et)==0.0:
                logger.debug("_et was %s, updating it to '0'" % self._et)
                self._et = '0'

            if self._lt and float(self._lt)==0.0:
                logger.debug("_lt was %s, updating it to '0'" % self._lt)
                self._lt = '0'

            self._reportName = 'Splunk search results'
            self._viewType = self.VIEW_TYPE_SEARCH

        # initialize papersize
        if self.ARG_INPUT_PAPERSIZE in self.args:
            paperSizeArg = self.args.get(self.ARG_INPUT_PAPERSIZE).lower()
            if paperSizeArg in pdfrenderer.PAPERSIZES:
                self._paperSize = paperSizeArg
            else:
                raise ArgError("Paper size " + paperSizeArg + " not valid")
        logger.debug("pdf-init paper-size=%s" % self._paperSize)

        # initialize include-splunk-logo
        self._includeSplunkLogo = normalizeBoolean(self.args.get(self.ARG_INPUT_INCLUDE_SPLUNK_LOGO, self._includeSplunkLogo))
        logger.debug("pdf-init include-splunk-logo=%s" % self._includeSplunkLogo)

        # initialize max-row-per-table
        if self.ARG_INPUT_MAX_ROWS_PER_TABLE in self.args:
            maxRowsPerTableArg = self.args.get(self.ARG_INPUT_MAX_ROWS_PER_TABLE)
            try:
                self._maxRowsPerTable = int(maxRowsPerTableArg)
            except:
                raise ArgError("max-rows-per-table=%s is invalid, must be an integer" % maxRowsPerTableArg)
        logger.debug("pdf-init max-rows-per-table=%s" % (str(self._maxRowsPerTable)))

        # initialize timeout
        if self.ARG_INPUT_TIMEOUT in self.args:
            self._timeoutDuration = int(self.args.get(self.ARG_INPUT_TIMEOUT))
        logger.debug("pdf-init timeoutDuration=%s" % self._timeoutDuration)
        self._startTimeoutClock()

        # initialize time of report
        self._initTimeOfReport()

        # check for SIDs
        if self._viewType is self.VIEW_TYPE_REPORT:
            if self.ARG_INPUT_SID in self.args:
                self._inputSids[0] = self.args.get(self.ARG_INPUT_SID)
        else:
            for argK, argV in self.args.items():
                if self.ARG_INPUT_SID in argK:
                    # we want the panel sequence number which is retrieved from "sid_<seqNum>"
                    match = self.sidRE.match(argK)
                    if match != None and len(match.groups(0)) > 0:
                        seqNum = match.groups(0)[0]
                        if len(seqNum) > 0:
                            self._inputSids[int(seqNum)] = argV
                            logger.debug("sid seqNum=%s value=%s" % (seqNum, argV))

        # get namespace/owner
        self._namespace = self.args.get(self.ARG_INPUT_NAMESPACE)
        if self.ARG_INPUT_OWNER in self.args:
            self._owner = self.args.get(self.ARG_INPUT_OWNER)

        self._validateParameters()

        self._timestampStr = splunk.search.searchUtils.getFormattedTimeForUser(
            sessionKey=self.sessionKey,
            user = self._owner,
            namespace = self._namespace,
            now = self._now
            )

    def _initTimeOfReport(self):
        # 1) try to use get time-of-report from the request args
        # 2) if not possible, get current UTC epoch time
        if self.ARG_INPUT_NOW in self.args:
            nowStr = self.args.get(self.ARG_INPUT_NOW)
            try:
                self._now = float(nowStr)
            except:
                logger.warning("invalid now argument passed to pdfgen/render arg=%s" % nowStr)
        if self._now is None:
            self._now = time.time() 

        logger.info("pdf time-of-report=%s" % self._now)

    def _validateParameters(self):
        # raise ArgError if there are problems with any parameters
        if self._dashboardName is None and self._reportName is None and self._dashboardXml is None:
            raise ArgError("PDF endpoint must be called with one of the following args: 'input-dashboard=<dashboard-id>' or 'input-report=<report-id>' or 'input-dashboard-xml=<dashboard-xml>'")

    def _initArgs(self):
        for arg in self.args:
            logger.debug("Testing argument arg=%s value=%s" % (arg, self.args[arg]))
            if arg not in self._validArgs:
                # check for sid_N for dashboards
                if self.sidRE.match(arg) is None:            
                    logger.warn("Invalid argument passed to pdfgen/render. arg=%s value=%s" % (arg, self.args[arg]))

    def _initAlertActionsDefaults(self):
        """ use alertActions entity to determine default papersize
            return in form of "<size>" or "<size>-landscape"
        """
        paperSize = DEFAULT_PAPER_SIZE
        paperOrientation = DEFAULT_PAPER_ORIENTATION
        try:
            settings = entity.getEntity(self.ALERT_ACTIONS_ENTITY, 'email', sessionKey=self.sessionKey)
            # paperSize is 'letter', 'legal', 'A4', etc
            paperSize = settings.get('reportPaperSize') or DEFAULT_PAPER_SIZE
            # paperOrientation is 'portrait' or 'landscape'
            paperOrientation = settings.get('reportPaperOrientation') or DEFAULT_PAPER_ORIENTATION
            self._includeSplunkLogo = normalizeBoolean(settings.get('reportIncludeSplunkLogo', self._includeSplunkLogo))
            cidFontListString = settings.get('reportCIDFontList', '') or ''
            self._cidFontList = cidFontListString.split(' ')
        except Exception as e:
            logger.error("Could not access or parse email stanza of alert_actions.conf. Error=%s" % str(e))

        if paperOrientation == 'landscape':
            self._paperSize = paperSize + '-landscape'
        else:    
            self._paperSize = paperSize


    def _initLimitsDefaults(self):
        """ use limits entity to determine defaults
        """
        try:
            settings = entity.getEntity(self.LIMITS_ENTITY, 'pdf', sessionKey=self.sessionKey)
            logger.debug("limitsPDFStanza=%s" % (str(settings)))
            self._maxRowsPerTable = int(settings.get('max_rows_per_table', self._maxRowsPerTable))
            self._timeoutDuration = int(settings.get('render_endpoint_timeout', self._timeoutDuration))
        except Exception as e:
            logger.error("Could not access or parse pdf stanza of limits.conf. Error=%s" % str(e))
            
    def _initWebDefaults(self):
        defaultSplunkdConnectionTimeout = 30
        try:
            settings = entity.getEntity(self.WEB_ENTITY, 'settings', sessionKey=self.sessionKey)
            splunkdConnectionTimeout = int(settings.get('splunkdConnectionTimeout', defaultSplunkdConnectionTimeout))
            if splunkdConnectionTimeout < defaultSplunkdConnectionTimeout:
                splunkdConnectionTimeout = defaultSplunkdConnectionTimeout

            splunk.rest.SPLUNKD_CONNECTION_TIMEOUT = splunkdConnectionTimeout
        except ValueError, e:
            logger.error("Exception while trying to get splunkdConnectionTimeout from web.conf e=%s" % e)
            splunk.rest.SPLUNKD_CONNECTION_TIMEOUT = defaultSplunkdConnectionTimeout
        except TypeError, e:
            logger.error("Exception while trying to get splunkdConnectionTimeout from web.conf e=%s" % e)
            splunk.rest.SPLUNKD_CONNECTION_TIMEOUT = defaultSplunkdConnectionTimeout
        finally:    
            logger.info("splunkdConnectionTimeout=%s" % splunk.rest.SPLUNKD_CONNECTION_TIMEOUT)
 
    #
    # handling searches
    #

    def _handlePresetSearchIDs(self):
        if len(self._inputSids) > 0:
            for view in self._views:
                index = view.getViewIndex()
                if index in self._inputSids.keys():
                    try:
                        searchJobObj = splunk.search.SearchJob(self._inputSids[index], hostPath=None, sessionKey=self.sessionKey)
                    except Exception as e:
                        logger.warning("Nonexistent search job object for sid: " + self._inputSids[index])
                        searchJobObj = None

                    if searchJobObj != None:
                        if searchJobObj.isExpired():
                            logger.warning("Expired search job object for sid: " + self._inputSids[index])
                        else:
                            view.setSearchJobObj(searchJobObj)

    def _startNextSearch(self):
        if len(self._inactiveViews) == 0:
            return

        view = self._inactiveViews.pop(0)
        if view.getSearchJobObj() is None and view.requiresSearchJobObj():
            # start the search!
            logger.debug("dispatching search for view: %s" % view.getTitle())
            if not view.dispatchSearch(overrideNowTime=self._now, maxRowsPerTable=self._maxRowsPerTable):
                logger.error("could not dispatch search for view: %s" % view.getTitle())
    
    def _keepAllSearchesAlive(self):
        currentTime = time.time()
        logger.debug("currentTime = %s self._touchSearchJobsLastTime = %s" % (currentTime, self._touchSearchJobsLastTime))
        if self._touchSearchJobsLastTime is not None:
            delta = currentTime - self._touchSearchJobsLastTime
            if delta < self.TOUCH_SEARCH_INTERVAL:
                return

        self._touchSearchJobsLastTime = currentTime
        for view in self._views:
            view.touchSearchJob()

    #
    # Timeout
    #

    def _startTimeoutClock(self):
        currentTime = int(time.time())
        self._timeoutTime = currentTime + self._timeoutDuration 
        logger.debug("PDF timeout setup: currentTime=%s timeoutDuration=%s timeoutTime=%s" % (currentTime, self._timeoutDuration, self._timeoutTime))

    def _checkForTimeout(self):
        currentTime = int(time.time())
        timedOut = currentTime > self._timeoutTime
        if timedOut:
            logger.info("PDF timeout. timeoutDuration = %s timeoutTime = %s currentTime = %s" % (self._timeoutDuration, self._timeoutTime, currentTime))
            for view in self._views:
                view.cancelSearch()
            raise TimeoutError()         

    #
    # Rendering
    #

    def _renderView(self, pdfRenderer, view, lastView=False):
        """ render an individual panel """
        if view.requiresSearchJobObj(): 
            while not view.isSearchComplete() and not view.isRealtime():
                time.sleep(self.POLLING_WAIT_TIME)
                
                self._keepAllSearchesAlive()
                self._checkForTimeout()

        pdfRenderer.conditionalPageBreak()
        self._renderViewHeader(pdfRenderer, view)

        types = view.getRenderTypes()

        for type in types:
            if type == 'chart':
                self._renderChart(pdfRenderer, view)
            elif type == 'map':
                self._renderMap(pdfRenderer, view)
            elif type == 'table':
                self._renderTable(pdfRenderer, view)
            elif type == 'event':
                self._renderEvents(pdfRenderer, view)
            elif type == 'single':
                self._renderSingle(pdfRenderer, view)
            elif type == 'list':
                self._renderList(pdfRenderer, view)
            elif type == 'html':
                self._renderHtml(pdfRenderer, view)
            else:
                pdfRenderer.renderText("No render option for type '%s'" % type)
                logger.warning("PDFGenHandler::_renderView> No render option for type = '%s'" % type)

        if not lastView:
            pdfRenderer.spaceBetween()

    def _renderViewHeader(self, pdf_renderer, view):
        title = view.getTitle()
        if title is not None and len(title) > 0:
            pdf_renderer.renderText("%s" % title, style = pdf_renderer.TITLE_STYLE, escapeText=True)
            pdf_renderer.spaceBetween(0.1 * pdf_renderer.ONE_INCH)
            
        subtitle = view.getSubtitle()
        if subtitle is not None and len(subtitle) > 0:
            pdf_renderer.renderText("%s" % subtitle, style=pdf_renderer.SUBTITLE_STYLE, escapeText=True)
            pdf_renderer.spaceBetween(0.1 * pdf_renderer.ONE_INCH)
            
        description = view.getDescription()
        if description is not None and len(description) > 0:
            pdf_renderer.renderText(description)

    def _renderTable(self, pdfRenderer, view):
        """ render a table of results """
        # get options
        options = view.getOptions()
        displayRowNumbers = False
        if "displayRowNumbers" in options:
            displayRowNumbers = normalizeBoolean(options['displayRowNumbers'])

        # build 2-d list of lists
        data = []
        resultsExist = False

        # get results object
        results = view.getSearchJobResults()
        
        # determine field set
        explicitFieldList = view.getSearchFieldList()
        fieldOrder = []
        if len(explicitFieldList) > 0:
            for field in explicitFieldList:
                if field in results.fieldOrder and field not in fieldOrder:
                    fieldOrder.append(field)
            if len(fieldOrder) == 0:
                logger.warning("%s: results.fieldOrder does not contain any explicitly specified fields: %s" % (view.getTitle(), explicitFieldList))
                return 
        else:
            fieldOrder = self._renderTable_restrictFields(results.fieldOrder)

        if len(fieldOrder) == 0:
            pdfRenderer.renderText("No results found.")
            return

        results = view.getSearchJobResults()
        for i, result in enumerate(results):
            if i >= self._maxRowsPerTable:
                break

            if (i > 0) and ((i % 100) == 0):
                self._keepAllSearchesAlive()    

            resultsExist = True

            # not every result row in the results list will contain a cell for every column in the table
            # fill in missing cells with the empty string
            values = []
            for field in fieldOrder:
                if field in result.fields:
                    fieldValues = result.get(field, None)
                    logger.debug("fieldValues=%s len(fieldValues)=%s isinstance(fieldValues, splunk.search.RawEvent)=%s$" % (fieldValues, len(fieldValues), isinstance(fieldValues, splunk.search.RawEvent)))
                    fieldValuesStr = ""
                    if isinstance(fieldValues, splunk.search.RawEvent):
                        fieldValuesStr = fieldValues
                    elif len(fieldValues) > 1:
                        fieldValueStrings = [str(x) for x in fieldValues]
                        if "##__SPARKLINE__##".startswith(fieldValueStrings[0]):
                            fieldValuesStr = ','.join(fieldValueStrings) 
                        else:
                            fieldValuesStr = '\n'.join(fieldValueStrings)
                        logger.debug("fieldValueStrings=%s fieldValuesStr=%s" % (fieldValueStrings, fieldValuesStr))
                    else:
                        fieldValuesStr = fieldValues[0]
                    values.append(fieldValuesStr)
                else:
                    values.append("")

            data.append(values)

        columnWidths = []
        if fieldOrder[0] == "_time":
            columnWidths.append(1.33 * pdfRenderer.ONE_INCH)

        if resultsExist:
            pdfRenderer.renderTable(data, headerRow = fieldOrder, columnWidths=columnWidths, displayLineNumbers=displayRowNumbers)
        else:
            logger.warning("PDFGenHandler::_renderTable> no results for table")
            pdfRenderer.renderText("No results found.")

    def _renderTable_restrictFields(self, inputFieldOrder):
        """ restrict the fields that are output in tables
            do not display any fields that start with an underscore
            except for _raw and _time
            position _time, if present, at the front of fieldOrder, and
            position _raw, if present, at the end of fieldOrder
            ---
            for the time being, if _time and _raw are both present,
            do not show any other field
        """
        timeFieldPresent = "_time" in inputFieldOrder
        rawFieldPresent = "_raw" in inputFieldOrder

        # do not include any fields that start with '_'
        publicFields = []
        for field in inputFieldOrder:
            if len(field) > 0 and field[0] != '_':
                publicFields.append(field)

        # build up output fieldOrder
        fieldOrder = []

        # always show _time first
        if timeFieldPresent:
            fieldOrder.append("_time")

        # if both _time and _raw present, do not show other fields
        if timeFieldPresent == False or rawFieldPresent == False:
            for field in publicFields:
                fieldOrder.append(field)

        # always show _raw last
        if rawFieldPresent:
            fieldOrder.append("_raw")

        logger.debug("PDFGenHandler::_renderTable_restrictFields> inputFieldOrder=" + str(inputFieldOrder) + " fieldOrder=" + str(fieldOrder))

        return fieldOrder

    def _renderList(self, pdfRenderer, view):
        """ render a list display """

        # build 2-d list of lists
        data = []
        resultsExist = False

        results = view.getSearchJobResults()
        fieldOrder = results.fieldOrder

        # get options
        optionsDict = view.getOptions()
        labelField = optionsDict.get("labelField", None)
        valueField = optionsDict.get("valueField", None)
        initialSort = optionsDict.get("initialSort", labelField)
        initialSortDir = optionsDict.get("initialSortDir", "asc")

        # validate options
        if labelField is None or valueField is None:
            logger.warning("PDFGenHandler::_renderList> missing either labelField or valueField in list")
            return

        # build up 2-d data set
        data = []
        for result in results:
            label = str(result.get(labelField, default=""))
            value = str(result.get(valueField, default=""))

            logger.debug("PDFGenHandler::_renderList> label, value: " + label + ", " + value)

            if label != "" or value != "":
                row = [label, value]
                data.append(row)

        # sort by initialSort and initialSortDir
        sortIndex = 0
        if initialSort == valueField:
            sortIndex = 1
        sortDescending = initialSortDir.lower() == "desc"

        data = sorted(data, key=lambda row: row[sortIndex], reverse=sortDescending)
        logger.debug("PDFGenHandler::_renderList> data: " +str(data))

        # render the data as lines of text
        if len(data) > 0:
            for row in data:
                pdfRenderer.renderText(row[0] + " " + row[1])
        else:
            pdfRenderer.renderText("No results for list")


    def _renderSingle(self, pdfRenderer, view):
        """ render a SingleValue display """
        resultsExist = False
        singleValue = ""
        classValue = "none"
        classColor = "black"
        optionsDict = view.getOptions()
        logger.debug("_renderSingle optionsDict='%s'" % optionsDict)

        classColors = {
            "none": "#999999",
            "low": "#00b932",
            "elevated": "#ffb800",
            "severe": "#ff1f24",
            "guarded": "#4da6df",
            "high": "#ff7e00"
            }

        results = view.getSearchJobResults()
        try:
            result = results[0]
            logger.debug("_renderSingle result='%s' result.fields='%s' result.fields.data='%s' results.fieldOrder='%s'" % (result, result.fields, result.fields.data, results.fieldOrder))
            resultsExist = True
            if "field" in optionsDict:
                singleValue = result.fields.data[optionsDict["field"]]
            else:
                singleValue = result.fields.data[results.fieldOrder[0]]

            if "classField" in optionsDict:
                classValue = str(result.fields.data[optionsDict["classField"]])
                if classValue in classColors:
                    classColor = classColors[classValue]    

        except IndexError:
            resultsExist = False

        if resultsExist:
            beforeLabel = ""
            afterLabel = ""
            underLabel = ""
            if "beforeLabel" in optionsDict:
                beforeLabel = optionsDict["beforeLabel"] + " "
            if "afterLabel" in optionsDict:
                afterLabel = " " + optionsDict["afterLabel"]
            if "underLabel" in optionsDict:
                underLabel = "<br/>%s" % optionsDict["underLabel"].upper()
            pdfRenderer.renderText("%s<font color='%s' size='18'><b>%s</b></font>%s%s" % 
                (beforeLabel, classColor, str(singleValue), afterLabel, underLabel), 
                style=pdfRenderer.CENTER_STYLE, 
                escapeText=False)

    def _renderChart(self, pdfRenderer, view):
        """ render a chart from the results """
        props = {"exportMode":"true","enableChartClick":"false","enableLegendClick":"false"}
        props = dict(props.items() + view.getChartProps().items())

        self._renderSvgBasedViz(pdfRenderer, view, props, mode="chart")

    def _renderMap(self, pdfRenderer, view):
        """ render a map from the results """
        geoFilterArguments = []
        mapProps = view.getMapProps()
        mapFitBounds = mapProps.get('map.fitBounds')
        dataFitBounds = mapProps.get('data.bounds')

        fitBounds = None
        if dataFitBounds:
            fitBounds = dataFitBounds
        elif mapFitBounds:
            fitBounds = mapFitBounds

        if fitBounds:
            fitBounds = fitBounds.replace('(', '')
            fitBounds = fitBounds.replace(')', '')

            fitBoundsArray = [bound.strip() for bound in fitBounds.split(',')]
            if len(fitBoundsArray) == 4:
                geoFilterArguments.append('south=%s' % fitBoundsArray[0])
                geoFilterArguments.append('west=%s' % fitBoundsArray[1])
                geoFilterArguments.append('north=%s' % fitBoundsArray[2])
                geoFilterArguments.append('east=%s' % fitBoundsArray[3])

        if 'maxClusters' in mapProps:
            geoFilterArguments.append('maxclusters=%s' % mapProps['maxClusters'])

        geoFilterPostProcess = 'geofilter %s' % ' '.join(geoFilterArguments)
        logger.debug("Rendering Map in PDF. postprocess = %s geoFilterArguments=%s" % (geoFilterPostProcess, geoFilterArguments))
        view.getSearchJobObj().setFetchOptions(search=geoFilterPostProcess)

        self._renderSvgBasedViz(pdfRenderer, view, mapProps, mode="map")

    def _renderSvgBasedViz(self, pdfRenderer, view, props, mode):
        # set the fetch option output_mode to 'json_cols'
        #  this will cause the data returned by getFeed to be
        #  pre-populated into the columnar form that the charting code wants
        # set the fetch option time_format to '%FT%T.%Q%:z'
        #  this is the only time format that is accepted by charting
        # set the show_metadata flag to true for chart mode only
        #  this will populate the metadata for each field, which certain chart types need to render correctly
        if mode == "chart":
            view.getSearchJobObj().setFetchOptions(output_mode="json_cols", time_format="%FT%T.%Q%:z", show_metadata="true")
        else:
            view.getSearchJobObj().setFetchOptions(output_mode="json_cols", time_format="%FT%T.%Q%:z")
        feedCount = DEFAULT_FEED_COUNT
        if 'data.count' in props:
            feedCount = props['data.count']

        feed = view.getSearchJobFeed(feedCount=feedCount)
        logger.debug("_renderSvgBasedViz> feed: " + str(feed) + ", " + str(type(feed)))
        
        if feed is None or len(feed.strip()) == 0:
            logger.warning("_renderSvgBasedViz> feed: " + str(feed) + ", " + str(type(feed)))

            pdfRenderer.renderText("No results found.")
            return

        feed = json.loads(feed)

        # extract columns and fields from the search results
        data = feed['columns']
        fields = feed['fields']

        if len(data) == 0:
            pdfRenderer.renderText("No results found.")
            return            

        # set up the SVG viz object
        svgBasedViz = None
        if mode == "chart":    
            svgBasedViz = pc.Chart(data, fields, props)
        elif mode == "map":
            svgBasedViz = pc.Map(data, fields, props)

        # build the SVG viz 
        buildSuccess = svgBasedViz.build()
        if buildSuccess:
            svgString = svgBasedViz.getSvg()
            pdfRenderer.renderSvgString(svgString, title=None)
        else:
            logger.error("SVG based viz building error")

    def _renderEvents(self, pdfRenderer, view):
        """ render a listing of events """
        # get options -- TODO: should be refactored with _renderTable (and beyond: should have a generalized system for getting options)
        options = view.getOptions()
        displayRowNumbers = False
        if "displayRowNumbers" in options:
            displayRowNumbers = normalizeBoolean(options['displayRowNumbers'])

        data = []
        events = view.getSearchJobEvents()
        for i, event in enumerate(events):
            if i >= self._maxRowsPerTable:
                break
    
            if (i > 0) and ((i % 100) == 0):
                self._keepAllSearchesAlive()    

            data.append([str(event.time), event.raw])

        if len(data) == 0:
            pdfRenderer.renderText("No matching events found.")
        else:
            # only set column widths for the line number and timestamp columns, setting None
            # for the last column provides for automatically setting its width
            colWidths = [pdfRenderer.ONE_INCH * 1.3, None]

            # we want to hard wrap the raw event column only
            colHardWraps = [False, True]

            pdfRenderer.renderTable(data, columnWidths=colWidths, columnHardWraps=colHardWraps, columnVAlignments=['TOP','TOP'], displayLineNumbers=displayRowNumbers)


    def _renderHtml(self, pdfRenderer, view):
        title = view.getTitle()
        if title is None:
            title = "Untitled panel"

        options = view.getOptions()
        logger.debug("PDFGenHandler::_renderHtml> options: " + str(options))
        if pu.PP_RAW_CONTENT not in options or options[pu.PP_RAW_CONTENT] is None or len(options[pu.PP_RAW_CONTENT]) == 0:
            logger.warning("PDFGenHandler::_renderHtml> rawContent key not in optionsDict for view: " + title)
            return

        pdfRenderer.renderHtml(options[pu.PP_RAW_CONTENT])

         









