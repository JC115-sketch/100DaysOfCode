from asyncio import exceptions
import mimetypes
from genericpath import isfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import os

class ServerException(Exception):
    pass

class RequestHandler(BaseHTTPRequestHandler): # 'self' inherits from BaseHTTPRequestHandler
    '''Handle HTTP requests by returning a fixed page'''
    
    # Page to send back
    Page = '''\
    <html>
    <body>
    <table>
    <tr>    <td>Header</td> 
    <tr>  <td>Date and time</td>  <td>{date_time}</td>    </tr>
    <tr>  <td>Client host</td>    <td>{client_host}</td>  </tr>
    <tr>  <td>Client port</td>    <td>{client_port}s</td> </tr>
    <tr>  <td>Command</td>        <td>{command}</td>      </tr>
    <tr>  <td>Path</td>           <td>{path}</td>         </tr>
    </table>
    </body>
    </html>
    '''

    Error_Page = '''\
    <html>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    '''

    Listing_Page = '''\
    <html>
    <body>
    <ul>
    {0}
    </ul>
    </body>
    </html>
    '''

    # Cases = [case_no_file(), case_cgi_file(), case_existing_file(), case_directory_index_file(), case_directory_no_index_file(), case_always_fail()] # 'handler' becomes an instance of case_no_file()

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)

    def run_cgi(self, full_path):
        cmd = "python " + full_path
        child_stdin, child_stdout = os.popen2(cmd)
        child_stdin.close()
        data = child_stdout.read()
        child_stdout.close()
        self.send_content(data)

    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets))
            self.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

    def do_GET(self):
        try:
            
            self.full_path = os.getcwd() + self.path

            cases = [
            case_no_file(),
            case_cgi_file(),
            case_existing_file(),
            case_directory_index_file(),
            case_directory_no_index_file(),
            case_always_fail()]

            # how to handle
            for case in cases:
                if case.test(self):
                    case.act(self)
                    break
                # handler = case() # handler is equal to each case function called
                # if handler.test(self): # if the test is true then act
                    # handler.act(self) # case() creates instance of class - handler is an instance of that class
                     # 'self' = requesthandler class instance inherited from BaseHTTPRequestHandler

        except Exception as msg:
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader: # 'read-binary' 
                content = reader.read()
            self.send_content(content, 200, full_path)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)

    def create_page(self):
        values = { 
            'date_time' : self.date_time_string(),
            'client_host' : self.client_address[0],
            'client_port' : self.client_address[1],
            'command' : self.command,
            'path' : self.path            
            }
        page = self.Page.format(**values) # substitutions determined by '{}' brackets
        return page

    # Handle a GET request
   # def send_content(self, content, status=200):
    #    self.send_response(status) # response code - 'connected'
    #    self.send_header("Content-Type", "text/html") # content-type header - telling client to interpret text as html
    #    self.send_header("Content-Length", str(len(self.content))) # telling client the length of the content/text
    #    self.end_headers() # blank line before the body/page
    #    self.wfile.write(content.encode("utf-8"))

    def send_content(self, content, status=200, full_path=None):
        self.send_response(status)

        if full_path:
            mime_type, _ = mimetypes.guess_type(full_path)
        else:
            mime_type = "text/html"

        self.send_header("Content-Type", mime_type or "application/octet-stream")

        if isinstance(content, str):
            content = content.encode("utf-8")

        self.send_header("Content-Length", str(len(content)))
        self.end_headers()

        self.wfile.write(content)

class case_no_file(object): # 'object' argument is just python2 base class
    '''File or directory does not exist.'''

    def test(self, handler): # 'self' is case object (case_no_file) and 'handler' is the RequestHandler instance
        return not os.path.exists(handler.full_path) # 'path' and 'full_path' are defined in BaseHTTPRequestHandler which RequestHandler inhertis from

    def act(self, handler):
        raise ServerException("'{0}' not found".format(handler.path))

class case_existing_file(object):
    '''File Exists'''

    def test(self, handler):
        return os.path.isfile(handler.full_path)

    def act(self, handler):
        handler.handle_file(handler.full_path) 

class case_always_fail(object):
    '''Base case if nothing else worked.'''

    def test(self, handler):
        return True

    def act(self, handler):
        raise ServerException("Unknown object '{0}'".format(handler.path))

class case_directory_index_file(object):
    '''Serve index.html page for a directory'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and \
            os.path.isfile(self.index_path(handler))

    def act(self, handler):
        handler.handle_file(self.index_path(handler)) # serve index.html

class case_directory_no_index_file(object):
    '''Serve listing for a directory without an index.html page'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and not \
    os.path.isfile(self.index_path(handler))

    def act(self, handler):
        pass

class case_cgi_file(object):
    '''Something runnable'''

    def test(self, handler):
        return os.path.isfile(handler.full_path) and \
            handler.full_path.endswith('.py') # string method

    def act(self, handler):
        handler.run_cgi(handler.full_path)


if __name__ == '__main__':

    serverAddress = ('', 8080) # address as a tuple - '' = run on current machine
    server = HTTPServer(serverAddress, RequestHandler)
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