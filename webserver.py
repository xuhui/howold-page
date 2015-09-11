'''
I DO NOT KNOW PYTHON AT ALL
BELOW CODE WAS PASTED FROM GOOGLE
ENJOY
'''

# should be clean, no idea which library should be imported which should not
import requests
import os,json,sys,urllib,urllib2,re
import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import cv
import re
import threading

capture = cv.CaptureFromCAM(-1)
img = cv.QueryFrame(capture)

class MyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.path = re.sub('[^.a-zA-Z0-9]', "",str(self.path))

            # serve pages, but htmL please
            if self.path.endswith(".html"):
                f = open(curdir + sep + self.path)
                self.send_response(200)
                self.send_header('Content-type',        'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            # below code is pasted from google, i know multipart but not know motion-jpeg, that easy?
            if self.path.endswith(".mjpeg"):
                self.send_response(200)
                self.wfile.write("Content-Type: multipart/x-mixed-replace; boundary=--aaboundary")
                self.wfile.write("\r\n\r\n")
                while 1:
                    img = cv.QueryFrame(capture)
                    cv2mat = cv.EncodeImage(".jpeg", img, (cv.CV_IMWRITE_JPEG_QUALITY, 75))
                    JpegData = cv2mat.tostring()
                    self.wfile.write("--aaboundary\r\n")
                    self.wfile.write("Content-Type: image/jpeg\r\n")
                    self.wfile.write("Content-length: "+str(len(JpegData))+"\r\n\r\n" )
                    self.wfile.write(JpegData)
                    self.wfile.write("\r\n\r\n\r\n")
                    time.sleep(0.05)
                return

            # for picture, serve the correct content-type. mjpEg please
            if self.path.endswith(".jpeg"):
                f = open(curdir + sep + self.path)
                self.send_response(200)
                self.send_header('Content-type','image/jpeg')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return

            # just give back the home.html whenever not known request happens, yes i just wanna make it work firstly
            f = open(curdir + sep + 'home.html')
            self.send_response(200)
            self.send_header('Content-type',        'text/html')
            self.end_headers()
            self.wfile.write(f.read())
            f.close()
            return
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

def wait_keyboard():
    while 1:
        raw_input()
        print 'capturing...'
        b = '<div style="font-size:xx-large;">one moment... </div>\n'
        f0 = open(os.path.join(curdir,"result.html"), 'w+')
        f0.write(b)
        f0.close()
        img = cv.QueryFrame(capture)
        tmpfilename = "tmp.jpeg"
        cv.SaveImage(tmpfilename, img)
        path = os.path.join(curdir, tmpfilename)
        print 'posting to microsoft...'
        r = requests.post('http://how-old.net/Home/Analyze?isTest=False', files = {tmpfilename: open(path, 'rb')})
        b = '<div style="font-size:xx-large;">\n'
        try:
                js = r.json().decode('string_escape')
                js = js.replace('"AnalyticsEvent":"','"AnalyticsEvent":').replace('","Face',',"Face').replace("Female", "Girl").replace("Male", "Boy")
                w = json.loads(js)
                u = w['Faces']
                if len(u) == 0:
                        b += 'No face detected'
                for face in u:
                        b += str(face['attributes']['gender']) + ', ' + str(face['attributes']['age']) + ' years old<br />\n'
        except:
                b += 'Failed'
        b += '\n<div>'
        f0 = open(os.path.join(curdir,"result.html"), 'w+')
        f0.write(b)
        f0.close()

def main():
    snap = threading.Thread(target = wait_keyboard)
    snap.daemon = True
    snap.start()
    try:
        server = ThreadedHTTPServer(('localhost', 8080), MyHandler)
        print 'started httpserver...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    main()

