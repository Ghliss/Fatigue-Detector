#Importation de la bibliothèque OpenCV pour les fonctions de traitement d'image de base
import cv2
# Numpy pour les fonctions liées aux tableaux
import numpy as np
# Dlib pour les modules basés sur le deep learning et la détection des points de repère du visage
import dlib
#face_utils pour les opérations de conversion de base
from imutils import face_utils
from playsound import playsound
#Initialisation de la caméra et prise d'instance
cap = cv2.VideoCapture(0)

#Initialisation du détecteur de visage et du détecteur de point de repère
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

#marquage d'état pour l'état normal
sleep = 0
drowsy = 0
active = 0
status=""
color=(0,0,0)

def compute(ptA,ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

def blinked(a,b,c,d,e,f):
    up = compute(b,d) + compute(c,e)
    down = compute(a,f)
    ratio = up/(2.0*down)

    #Vérifier s'il s'agit d'un clignement des yeux
    if(ratio>0.25):
        return 2
    elif(ratio>0.2 and ratio<=0.25):
        return 1
    else:
        return 0


while True:
    _, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = detector(gray)
    
    #visage détecté dans le tableau des visages
    for face in faces:
        x1 = face.left()
        y1 = face.top()
        x2 = face.right()
        y2 = face.bottom()

        face_frame = frame.copy()
        cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        landmarks = predictor(gray, face)
        landmarks = face_utils.shape_to_np(landmarks)

        #Les chiffres sont en fait les points de repère qui montreront l'œil
        left_blink = blinked(landmarks[36],landmarks[37], 
            landmarks[38], landmarks[41], landmarks[40], landmarks[39])
        right_blink = blinked(landmarks[42],landmarks[43], 
            landmarks[44], landmarks[47], landmarks[46], landmarks[45])
        
        #Maintenant, jugez quoi faire pour les clignements des yeux
        if(left_blink==0 or right_blink==0):
            sleep+=1
            drowsy=0
            active=0
            if(sleep>3):
                status="Endormi!!!"
                color = (255,0,0)
                playsound('warning.wav')

        elif(left_blink==1 or right_blink==1):
            sleep=0
            active=0
            drowsy+=1
            if(drowsy>2):
                status="Somnolent!"
                color = (0,0,255)

        else:
            drowsy=0
            sleep=0
            active+=1
            if(active>2):
                status="Active :)"
                color = (0,255,0)
                
        cv2.putText(frame, status, (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color,3)

        for n in range(0, 68):
            (x,y) = landmarks[n]
            cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)

    cv2.imshow("Detecteur de fatigue", frame)
    
    if cv2.waitKey(33) == ord('a'):
        break