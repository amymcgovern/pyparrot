"""
    This is a simple web server to let the user see the vision that is being processed by ffmpeg.  It
    essentially replaces the role of VLC.  Note that there are several user parameters that should be
    set to run this program.

    This does not replace the vision process!  This is a separate process just to run a web server that
    lets you see what the mambo is seeing.

	orig author: Igor Maculan - n3wtron@gmail.com
	A Simple mjpg stream http server

	Updated for python3 including png streaming and
	graceful error handling - Taner Davis
"""
import cv2
import os.path
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

"""
	Location on your computer where you want to start reading files from to start
	streaming. You'll need keep the %03d in the file name to ensure that the stream
	can keep finding new photos made from the stream. This allows the program to fill
	in image numbers like 004 or 149.

	Note: this will not loop at 999, the program will look for 1000 after 999.
"""
#IMAGE_PATH = "/Users/Leo/Desktop/pyparrot-1.2.1/Test file/images/image_%03d.png"
IMAGE_PATH = "/Users/amy/repos/pyparrot/images/image_%03d.png"

"""
	The URL or website name you would like to stream to. Unless you have a strong reason
	to change this, keep this as "127.0.0.1"
"""
HOST_NAME = "127.0.0.1"

"""
	The port youd like to stream to locally. Unless you have a strong reason to change
	this, keep this as 9090.
"""
PORT_NUMBER = 9090

"""
	Set this according to how we want to stream:
		Stream in color 					-> >0 (1, 2, 873, etc.)
		Stream in black and white 			-> 0
		Stream in color with transparency	-> <0 (-1, -6, -747, etc.)
"""
STREAMING_IMAGE_TYPE = 1


class CamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """
            When we go to the URL to see the stream, we need to decide if we need to build
            the screen or if we need to start loading images to view.

            "GET / HTTP/1.1" - The request when we want to build the webpage
                Note: self.path here is the first, lone "/"

            "GET /cam.mjpg HTTP/1.1" - The request to start viewing the images for the stream
                Note: self.path here is "/cam.mjpg"
        """
        # If we haven't built the page yet, let's do that. Happens we first load the page.
        if self.path.endswith('.html') or self.path == "/":
            # Send HTTP Success (200) to let the browser know it's okay to continue and build the page.
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # Create html for image source using the host name and port provided in the program code
            self.wfile.write('<html><head></head><body>'.encode())
            self.wfile.write(('<img src="http://%s:%d/cam.mjpg"/>' % (HOST_NAME, PORT_NUMBER)).encode())
            self.wfile.write('</body></html>'.encode())
            # Page built. Let's bail.
            return
        if self.path.endswith('.mjpg'):
            # Send HTTP Success (200) to let browser know to take page headers and start showing images
            self.send_response(200)
            self.send_header('Content-type', 'multipart/x-mixed-replace; boundary=--pngboundary')
            self.end_headers()
            # The name of the first picture will be 1, but the leading zeros are handled in the IMAGE_PATH variable
            index = 1
            while True:
                try:
                    # Create path name with the index
                    path = IMAGE_PATH % (index)
                    # If our file doesn't exist, don't try to read it just yet.
                    if (not os.path.exists(path)) and (not os.path.isfile(path)):
                        print("File %s doesn't exist. Trying again." % (path))
                        # Go back to the try above
                        continue
                    # File exists. Let's try to read the image
                    img = cv2.imread(path, STREAMING_IMAGE_TYPE)
                    #print("Reading image with index of %d" % (index))
                    # Increase index by one to read the next image file next time
                    index = index + 1
                    # Encode the read png image as a buffer of bytes and write the image to our page
                    r, buf = cv2.imencode(".png", img)
                    self.wfile.write("--pngboundary\r\n".encode())
                    self.send_header('Content-type', 'image/png')
                    self.send_header('Content-length', str(len(buf)))
                    self.end_headers()
                    self.wfile.write(bytearray(buf))
                    self.wfile.write('\r\n'.encode())
                except cv2.error:
                    """
                        This can happen when the png is created from the stream, but it hasn't been completely
                        filled in. This will throw an error through opencv about trying to read an empty image.
                        Catch it here and return to the try statement above to keep the program from exiting.
                    """
                    print("Trying to read an empty png. Let's wait and try again.")
                    continue
                except KeyboardInterrupt:
                    """
                        This happens when we input a kill command of some sort like command+c. Let the user know
                        we have successfully receive the exit command, and stop reading images to the web page.
                    """
                    print("Leaving the stream")
                    break
            return


def main():
    """
        Builds an http page to see images in a stream as they are created in the IMAGE_PATH specified above.
    """
    try:
        # Build a server that will allow us to access it/send requests through a browser
        server = HTTPServer(('', PORT_NUMBER), CamHandler)
        print("Server started at \"http://%s:%d\"" % (HOST_NAME, PORT_NUMBER))
        # Keep the server up until we close it below through a Keyboad Interruption
        server.serve_forever()
    # Command+c/Command+z will stop the server once the webpage above is also stopped.
    except KeyboardInterrupt:
        server.socket.close()
        print("Terminated Vision program successfully")


"""
	Convenience naming methodology to let use call the entire script through command line.
"""
if __name__ == '__main__':
    main()
