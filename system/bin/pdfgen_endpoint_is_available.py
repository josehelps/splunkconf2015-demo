import splunk.rest
import splunk.pdf.availability as pdf_availability

class PDFGenHandlerIsAvailable(splunk.rest.BaseRestHandler):
    def handle_GET(self):
        viewId = None
        owner = None
        namespace = None

        if 'viewId' in self.args:
            viewId = self.args['viewId']
        if 'owner' in self.args:
            owner = self.args['owner']
        if 'namespace' in self.args:
            namespace = self.args['namespace']

        pdfService = pdf_availability.which_pdf_service(sessionKey=self.sessionKey, viewId=viewId, owner=owner, namespace=namespace) 

        self.response.setStatus(200)
        self.response.write(pdfService)
