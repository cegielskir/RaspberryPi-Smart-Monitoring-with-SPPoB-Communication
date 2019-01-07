import numpy as np
import cv2
import imutils
import datetime
import time
from imutils.video import VideoStream

_PATH = 'video_cap/resources/trained_models/haarcascade_frontalface_default.xml'


class VideoCap:
    def __init__(self, function_name, x_min, y_min, x_max, y_max, video_path):
        self.face_haar_cascade = None if function_name != 'face-recognition' else cv2.CascadeClassifier(_PATH)
        self.func_name = function_name
        self.fun = getattr(VideoCap, self.functions[function_name][0])
        self.args = []
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.first_frame = None
        self.video_path = video_path
        self.cap = cv2.VideoCapture(0)
        self.tracker = cv2.TrackerMIL_create()
            
    def run(self):
        
        frame_width = int(self.cap.get(3))
        frame_height = int(self.cap.get(4))
        if self.video_path is not None:
            out = cv2.VideoWriter(self.video_path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10, (frame_width, frame_height))
        self.get_arguments()
        
        i = 0
        while i < 70:
            frame = self.cap.read()
            i+=1
        
        while True:
            ##time.sleep(0.25)
            frame = self.cap.read()
            frame = frame[1]
            
            if frame is None:
                break
            
            try:
                cut_frame = frame[self.x_min:self.x_max, self.y_min:self.y_max]
                (f_frame, thresh, frame_delta, gray, text, do_continue) = self.fun(self, cut_frame, *self.args)
                frame[self.x_min:self.x_max, self.y_min:self.y_max] = f_frame
            except cv2.error:
                print("Improperly defined resolution bounds or parameter values")
                break
            if do_continue == True:
                continue
            else:
                # draw the text and timestamp on the frame
                cv2.putText(frame, "Beer Status: {}".format(text), (10, 20),
		    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
		(10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 255), 1)
                if text != "Beer is safe" and self.video_path is not None:
                    out.write(frame)
                cv2.imshow('frame', frame)
                cv2.imshow('gray', gray)
                cv2.imshow('first frame', self.first_frame)
                cv2.imshow('Frame delta', frame_delta)

            if cv2.waitKey(1) % 0xFF == ord('q'):
                break
        self.cap.release()
        cv2.destroyAllWindows()
    def get_arguments(self):
        arguments = self.functions[self.func_name][1:]
        if arguments.__len__() != 0:
            print("Input user defined function arguments :)")
            for arg in arguments:
                self.args.append(int(input("Please, input " + str(arg) + " parameter value: ")))

    def _none_filter(self, frame):
        return frame

    def _threshhold_filter(self,
                           frame,
                           threshold,
                           max_value=255,
                           threshold_type=cv2.THRESH_BINARY):

        _, threshold_frame = cv2.threshold(frame, threshold, max_value, threshold_type)
        return threshold_frame
    
    def _motion_detection(self, frame):

        text = "Beer is safe"
        
        #convert frame to grayscale, and blur it
        ##frame = imutils.resize(frame, width=500)
        ##frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if self.first_frame is None:
            self.first_frame = gray
            return (frame, None, None, None, None, True)
	    
        # compute the absolute difference between the current frame and
	# first frame
        frame_delta = cv2.absdiff(self.first_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
 
	# dilate the thresholded image to fill in holes, then find contours
	# on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if imutils.is_cv2() else cnts[1]
 
        #print(cnts)
        
        largest = max(map(lambda x: int(cv2.contour.Area(x)), cnts))
        
        status = 'motion'
    
        if cv2.contourArea(cnts[largest]) > 1000:
            (x,y,w,h) = cv2.boundingRect(cnts[0])
            (x,y,w,h) = (int(x), int(y), int(w), int(h))
            box = (x,y,w,h)
            ok = self.tracker.init(frame,box)
            status = 'tracking'
            
            
        if status == 'tracking':
            ok, box = self.tracker.update(frame)
            
            if ok:
                p1 = (int(box[0]), int(box[1]))
                p2 = (int(box[0] + box[2]),int(box[1] + box[3]))
                cv2.rectangle(frame,p1,p2,(0,0,255),10)
    
	# loop over the contours
        #for c in cnts:
		# if the contour is too small, ignore it
         #   if cv2.contourArea(c) < 500:
          #      continue
 
		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
          #  (x, y, w, h) = cv2.boundingRect(c)
           # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
          #  text = "ALERT !!! BEER IS IN DANGER !!!"
		
	
        return (frame, thresh, frame_delta, gray, text, False)



    """
    Dictionary of available video effects.
        @key: function name used in arg_parser
        @value: list of [class function name, user-defined arguments]
    """
    functions = {
        'motion-detection' : ['_motion_detection']
    }
