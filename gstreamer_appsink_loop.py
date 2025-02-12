import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import cv2 
# print GStreamer version
print(Gst.version())
# print OpenCV version
print(cv2.__version__)