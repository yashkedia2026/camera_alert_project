# camera_alert/motion_detector.py
import cv2

class MotionDetector:
    def __init__(self):
        self.previous_frame = None

    def detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.previous_frame is None:
            self.previous_frame = gray
            return False

        delta = cv2.absdiff(self.previous_frame, gray)
        self.previous_frame = gray
        thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
        movement = cv2.countNonZero(thresh)
        return movement 