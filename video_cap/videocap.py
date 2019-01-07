import numpy as np
import cv2
import imutils
import datetime
import time
from imutils.video import VideoStream
import os

_PATH = 'video_cap/resources/trained_models/haarcascade_frontalface_default.xml'

alarm = None

class VideoCap:
    def __init__(self, function_name, x_min, y_min, x_max, y_max, video, alarm):
        self.func_name = function_name
        self.fun = getattr(VideoCap, self.functions[function_name][0])
        self.args = []
        self.x_min = y_min
        self.x_max = y_max
        self.y_min = x_min
        self.y_max = x_max
        self.first_frame = None
        self.cap = cv2.VideoCapture(0)
        self.tracker = cv2.TrackerMIL_create()
        if video == '0':
            self.video = False
        else:
            self.video = True
        if alarm == '0':
            self.alarm = False
        else:
            self.alarm = True
        self.last_frame = None
        self.last_move_time = datetime.datetime.now() - datetime.timedelta(1)
        self.new_video = False
        self.last_file_date = None
        
            
    def run(self):
        
        frame_width = int(self.cap.get(3))
        frame_height = int(self.cap.get(4))
        self.get_arguments()
        file = None
        
        
        #initialization of the camera
        #it has to take some empty frames to work properly
        i = 0
        while i < 70:
            frame = self.cap.read()
            i+=1
        
        i = 0
        while True:
            
            i = i + 1
            if i == 10:
                i = 0
            time.sleep(0.1)
            frame = self.cap.read()
            frame = frame[1]
            
            if frame is None:
                break
            
            try:
                cut_frame = frame[self.x_min:self.x_max, self.y_min:self.y_max]
                (f_frame, thresh, frame_delta, gray, text, do_continue, x1, y1, x2, y2) = self.fun(self, cut_frame, *self.args)
                frame[self.x_min:self.x_max, self.y_min:self.y_max] = f_frame
            except cv2.error:
                print("Improperly defined resolution bounds or parameter values")
                break
            
            if self.new_video == False and self.video == True and self.last_move_time + datetime.timedelta(0, 5) < datetime.datetime.now():
                    if file != None:
                        os.rename(file.name, "./movecords/" + self.last_file_path + "_V.txt")
                        file.close()
                    self.last_file_path = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")  
                    file = open("./movecords/" + self.last_file_path + ".txt", "w+")
                    datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
                    out = cv2.VideoWriter("./video/" + datetime.datetime.now().strftime("%I-%M-%S%p") + ".avi", cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))
                    self.new_video = True
            
            if do_continue == True:
                continue
            else:
                # draw the text and timestamp on the frame
                cv2.putText(frame, "Room Status: {}".format(text), (10, 20),
		    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
    
                if i == 5 and self.video == True and (text == "Motion Detected" or
                                           self.last_move_time + datetime.timedelta(0, 5) > datetime.datetime.now()):
                    if x1 > 0:
                        coords = str(int(x1)) + " " + str(int(y1)) + " " + str(int(x2)) + " " + str(int(y2))
                        file.write("%s\r\n" % coords)
                        
                    
                    self.new_video = False
                    out.write(frame)
                    
                if self.alarm == 1:
                    pass
                
                cv2.imshow('Live', frame)
                #cv2.imshow('gray', gray)
                #cv2.imshow('first frame', self.first_frame)
                #cv2.imshow('frame_delta', frame_delta)

            if cv2.waitKey(1) % 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()
        if file != None:
            file.close()
    def get_arguments(self):
        arguments = self.functions[self.func_name][1:]
        if arguments.__len__() != 0:
            print("Input user defined function arguments")
            for arg in arguments:
                self.args.append(int(input("Please, input " + str(arg) + " parameter value: ")))

   
    
    def _motion_detection(self, frame):
        text = "No Move"

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.first_frame is None:
            self.first_frame = gray
            self.last_frame = gray
            return (frame, None, None, None, None, True, -1, -1, -1, -1)
        else:
            self.last_frame = self.first_frame
            self.first_frame = gray
	    
        # compute the absolute difference between the current frame and
	# first frame
        frame_delta = cv2.absdiff(self.last_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
 
	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=10)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
    
        max_contour_area = 0
        max_c = 0
        for c in cnts:
	    # if the contour is too small, ignore it
            if cv2.contourArea(c) < 800 and cv2.contourArea(c) < max_contour_area:
                continue
                
            max_contour_area = cv2.contourArea(c)
            max_c = c
		#compute the bounding box for the contour, draw it on the frame,
		#and update the text
        x1 = -1
        y1 = -1
        x2 = -1
        y2 = -1
        
        if max_contour_area > 0:
            if self.last_move_time + datetime.timedelta(0,5) < datetime.datetime.now():
                pass
            self.last_move_time = datetime.datetime.now()
            (x, y, w, h) = cv2.boundingRect(max_c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Move Detected"
            x1 = 255*(x)/640
            y1 = 255*(y)/480
            x2 = 255*(x+w)/640
            y2 = 255*(y+h)/480	
	
        return (frame, thresh, frame_delta, gray, text, False, x1, y1, x2, y2)


    functions = {
        'motion-detection' : ['_motion_detection']
    }
