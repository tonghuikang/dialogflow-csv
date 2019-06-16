# sudo apt-get install python3-pip
# pip3 install pandas

import time
import json
from urllib.request import urlretrieve
import random
import datetime
from http.server import *
from urllib.parse import urlparse
import os
from cgi import parse_header, parse_multipart


HOST_NAME = '0.0.0.0'

import sys
myargs = sys.argv
if '-p' in myargs:
    try: PORT_NUMBER = int(myargs[2])
    except Exception as e:
        print(e)
        PORT_NUMBER = 4000
else:
    PORT_NUMBER = 4000

    
def generateRandomHex():
    datetime_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-")
    return datetime_string + '%08x' % random.randrange(16**8)
    
    
class IngestHandler(BaseHTTPRequestHandler):
    
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'multipart/form-data')
        self.end_headers()
        
    def parse_POST(self):
        ctype, pdict = parse_header(self.headers['content-type'])
        pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
        if ctype == 'multipart/form-data':
            postvars = parse_multipart(self.rfile, pdict)
        elif ctype == 'application/x-www-form-urlencoded':
            length = int(self.headers['content-length'])
            postvars = parse_qs(
                    self.rfile.read(length), 
                    keep_blank_values=1)
        else:
            postvars = {}
        return postvars
        
    def do_POST(self):
        postvars = self.parse_POST()
        print(postvars)

        FILE_NAME = generateRandomHex()
        print(FILE_NAME)
        
        if postvars['sheetsID'] != None:
            
#             command = "wget --output-document temp/{}.csv https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet=intents".format(FILE_NAME, postvars['sheetsID'][0].decode('utf-8'))
#             print(command)
            
            urlretrieve("https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet=intents".format(postvars['sheetsID'][0].decode('utf-8')), 
                               filename="temp/{}.csv".format(FILE_NAME))
#             os.system(command)
            
            urlretrieve("https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet=entities".format(postvars['sheetsID'][0].decode('utf-8')), 
                               filename="temp/{}-ent.csv".format(FILE_NAME))
#             os.system(command)
            
#             command = "wget --output-document temp/{}-ent.csv https://docs.google.com/spreadsheets/d/{}/gviz/tq?tqx=out:csv&sheet=entities".format(FILE_NAME, postvars['sheetsID'][0].decode('utf-8'))
#             print(command)
#             os.system(command)
            
        else:
            with open('temp/{}.csv'.format(FILE_NAME), 'wb') as f:
                f.write(postvars['file-to-convert'][0])

            if postvars['ent-file-to-convert'] == [b'']:
                os.system("cp temp/template-ent-empty.csv temp/{}.csv".format(FILE_NAME + "-ent"))
                print("cp temp/template-ent-empty.csv temp/{}.csv".format(FILE_NAME + "-ent"))
            else:
                with open('temp/{}.csv'.format(FILE_NAME + "-ent"), 'wb') as f:
                    f.write(postvars['ent-file-to-convert'][0])
        
        # save a copy in our storage
        os.system("gsutil cp temp/{}.csv gs://dialogflow-csv-stash".format(FILE_NAME))
        os.system("python3 csv-to-df-comb.py -f {}".format(FILE_NAME))
        
        self.send_response(200)
        self.send_header('Content-type',  'binary')
        self.send_header('Content-Disposition', 'attachment; filename="output.zip"')
        self.end_headers()
        with open('temp/{}.zip'.format(FILE_NAME), 'rb') as file: 
            self.wfile.write(file.read()) # Read the file and send the contents
        
        os.system("rm temp/{}.csv".format(FILE_NAME))
        os.system("rm temp/{}.zip".format(FILE_NAME))
        os.system("rm -rf temp/{}".format(FILE_NAME))
        return True

    def do_PUT(self):
        postvars = self.parse_POST()
        print(postvars)

#         FILE_NAME = generateRandomHex()
#         print(FILE_NAME)
        

        
#         # save a copy in our storage
#         os.system("gsutil cp temp/{}.csv gs://dialogflow-csv-stash".format(FILE_NAME))
#         os.system("python3 csv-to-df-comb.py -f {}".format(FILE_NAME))
        
#         self.send_response(200)
#         self.send_header('Content-type',  'binary')
#         self.send_header('Content-Disposition', 'attachment; filename="output.zip"')
#         self.end_headers()
#         with open('temp/{}.zip'.format(FILE_NAME), 'rb') as file: 
#             self.wfile.write(file.read()) # Read the file and send the contents
        
#         os.system("rm temp/{}.csv".format(FILE_NAME))
#         os.system("rm temp/{}.zip".format(FILE_NAME))
#         os.system("rm -rf temp/{}".format(FILE_NAME))
#         return True

        
    
    def do_GET(self):
        '''
        Post this with the POST function in Postman
        {"data" : "Strawberry Shortcake"}
        and you will get this in return
        {"data": "Strawberry Shortcake.", "My Little Pony": ["Friendship is Magic", "Equestria Girls"]}
        '''
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            dict_loaded = json.loads(post_data.decode('utf-8'))
            print(dict_loaded)
        except:
            print("Invalid JSON Input")
            print(post_data)
        
        time_start = time.time()
        
        #####################################################
        ### YOUR ANALYSIS STARTS HERE - given dict_loaded ###
        #####################################################
        
        dict_loaded["My Little Pony"] = ["Friendship is Magic", "Equestria Girls"]
        dict_to_deliver = dict_loaded
        
        #########################################################
        ### YOUR ANALYSIS ENDS HERE - returns dict_to_deliver ###
        #########################################################
        
        print("\nAnalysis took:", time.time()-time_start)
        json_output = json.dumps(dict_to_deliver) 
        print("\nJSON Output")
        print(json_output)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        parsed_path = urlparse(self.path)
        self.wfile.write(json_output.encode())
        return True
        
#     def handle_http(self, status_code, path):
#         '''I don't understand what this part is for''' 
#         print("executing handle_http")
#         self.send_response(status_code)
#         self.send_header('Content-type', 'text/html')
#         self.end_headers()
#         content = '''
#         <html><head><title>Potato</title></head>
#         <body><p>This is a potato.</p>
#         <p>You accessed potato path: {}</p>
#         </body></html>
#         '''.format(path)
#         return bytes(content, 'UTF-8')

#     def respond(self, opts):
#         '''I don't understand what this part is for'''
#         print("executing respond")
#         response = self.handle_http(opts['status'], self.path)
#         self.wfile.write(response)
        
        
if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), IngestHandler)
    print(time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print(time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER))
