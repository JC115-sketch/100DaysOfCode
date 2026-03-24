from http.server import BaseHTTPServer

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    '''Handle HTTP requests by returning a fixed page'''

    # Page to send back
    Page = '''\
    <html>
    <body>
    <p> Hello, web!<\p>
    </body>
    </html>
    '''

    # Handle a GET request
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(self.Page)))
        self.end_headers()
        self.wfile.write(self.Page)

if __name__ == '__main__':

    serverAddress = ('', 8080) # address as a tuple - '' = run on current machine
    server = BaseHTTPServer.HTTPServer(serverAddress, RequestHandler)
    server.serve_forever()


# httpd = HTTPServer(('', 8000), SimpleHTTPRequestHandler)
# httpd.serve_forever()

## BaseHTTPRequestHandler - takes care of parsing the incoming HTTP request and deciding which method it contains
# if the method is GET - the class calls a method named do_GET - we override this in RequestHandler

# GET - request/fetch information
# POST - submit the form data/upload files
# HTTP - header = key/value pair 
# Accept: text/html
# Accept-Language: en, fr
# If-Modified-Since: 16-May-2005
# status code - number indicating what happened when the request was processed 200 = 'everything worked' 
# http is stateless - the server doesn't remember anything between one request and the next
# a 'cookie' or short character string that represents the session - browser uses the cookie to lookup what the user was doing