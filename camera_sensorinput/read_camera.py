import cv2


class ReadCamera:

    def __init__(self):
        self.cap = cv2.VideoCapture("/home/manuel/PREN/workspaces/informatik/object_detection/darknet/images/distance.mp4")
        self.cap.set(4, 832)
        self.cap.set(3, 832)

    def get_frame(self):
        ret, frame_read = self.cap.read()
        frame_read = cv2.rotate(frame_read, cv2.ROTATE_90_CLOCKWISE)
        return frame_read

    def close(self):
        self.cap.release()
