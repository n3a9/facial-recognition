import sys
sys.path.append('/usr/local/lib/python3.6/site-packages')
sys.path.append('/usr/local/Cellar/opencv/3.4.1_2/lib/python3.6/site-packages')

import json
import multiprocessing
import pickle
import face_recognition
import re
import time
from threading import Thread
import cv2
import numpy as np
from PIL import Image

class dotdict(dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class FaceRecognition:
    def __init__(self):
        self.known_encodings = []
        self.load_encodings()
        self.last_frames = []
        self.LAST_FRAME_NUM = 10

    def clear_faces(self):
        self.known_encodings = []
        self.save_encodings()
        print("Cleared known faces")

    def encoding(self, file):
        image = face_recognition.load_image_file(file)
        return face_recognition.face_encodings(image)[0]

    def load_encodings(self):
        try:
            with open('encodings.pickle', 'rb') as f:
                self.known_encodings = pickle.load(f)
                print("Loaded {} item(s)".format(len(self.known_encodings)))
        except FileNotFoundError:
            pass

    def save_encodings(self):
        with open('encodings.pickle', 'wb') as f:
            pickle.dump(self.known_encodings, f)

    def train_face(self, face_img, info):
        encoded = self.encoding(face_img)
        self.known_encodings.append((info, encoded))
        self.save_encodings()

    def recognize_faces(self, img):
        img = face_recognition.load_image_file(img)
        face_locations = face_recognition.face_locations(img) # (top, right) (bottom, left)
        face_encodings = face_recognition.face_encodings(img, face_locations, 2)
        encodings = [x[1] for x in self.known_encodings]
        ret = []
        idx = 0
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(encodings, face_encoding)
            if True in matches:
                match_index = matches.index(True)
                match_name = self.known_encodings[match_index][0]["name"]
            else:
                match_index = -1
                match_name = "(unknown)"
            loc = face_locations[idx]
            obj = {
                "name": match_name,
                "top": loc[0],
                "right": loc[1],
                "bottom": loc[2],
                "left": loc[3],
                "unknown": (match_index != -1)
            }
            ret.append(obj)
            idx += 1
        return ret

    def recognize_frame(self, frame_img):
        if len(self.last_frames) == self.LAST_FRAME_NUM:
            self.last_frames = self.last_frames[1:]
        rec_arr = self.recognize_faces(frame_img)
        self.last_frames.append(rec_arr)
        return rec_arr

    def webcam(self):
        SCALING_FACTOR = 5.0
        video_capture = cv2.VideoCapture(0)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1024)
        while True:
            ret, frame = video_capture.read()
            frame = cv2.flip(frame, 1)
            small_frame = cv2.resize(frame, (0, 0), fx=1.0/SCALING_FACTOR, fy=1.0/SCALING_FACTOR)
            cv2.imwrite("tmp.jpg", small_frame)
            rec_arr = fr.recognize_frame("tmp.jpg")
            for obj in rec_arr:
                obj = dotdict(obj)
                obj.top *= int(SCALING_FACTOR)
                obj.left *= int(SCALING_FACTOR)
                obj.right *= int(SCALING_FACTOR)
                obj.bottom *= int(SCALING_FACTOR)
                cv2.rectangle(frame, (obj.left, obj.top), (obj.right, obj.bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (obj.left, obj.bottom - 35), (obj.right, obj.bottom), (0, 0, 255), cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, obj.name, (obj.left + 6, obj.bottom - 6), font, 1.0, (255, 255, 255), 1)
                cv2.imshow('Video', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'): break

if __name__ == '__main__':
    fr = FaceRecognition()
    fr.clear_faces()
    
    # Train faces
    
    fr.webcam()

