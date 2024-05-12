import cv2
import dlib
import json
import numpy as np
from scipy.spatial import procrustes
from tkinter import messagebox


def get_point():
    # face detection model
    face_cascade = cv2.CascadeClassifier('data\\haarcascade_frontalface_default.xml')
    predictor_path = 'data\\shape_predictor_68_face_landmarks.dat'
    # key point prediction model
    predictor = dlib.shape_predictor(predictor_path)

    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()

    cap.release()
    cv2.destroyAllWindows()

    if not ret:
        messagebox.showerror("Error", "Failed to grab frame")
        return None

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        messagebox.showerror("Error", "No face found")
        return None

    # find the biggest face
    x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])

    # drawing rectangle
    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # convert rectangle to dlib object
    dlib_objet = dlib.rectangle(left=x, top=y, right=x+w, bottom=y+h)

    landmarks = predictor(gray, dlib_objet)

    face_landmarks = []

    for i in range(0, 68):
        point = landmarks.part(i)
        face_landmarks.append((point.x, point.y))

    for point in face_landmarks:
        cv2.circle(frame, point, 2, (0, 255, 0), -1)

    cv2.imshow("aa", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return face_landmarks


def recognize_face(user):
    file_path = f'face_data\\{user}.json'

    with open(file_path, 'r') as f:
        face_landmarks_known = json.load(f)

    face_landmarks_unknown = get_point()

    matrix1 = np.array(face_landmarks_known)
    matrix2 = np.array(face_landmarks_unknown)

    mtx1, mtx2, disparity = procrustes(matrix1, matrix2)

    distance = np.mean(np.sqrt(np.sum((mtx1 - mtx2) ** 2, axis=1)))

    threshold = 0.009
    if distance < threshold:
        return 1
    else:
        return


def clear_window(window):
    for widget in window.winfo_children():
        widget.destroy()
