import cv2
import numpy as np
try:
    import mediapipe.python.solutions.face_detection as mp_face_detection
    import mediapipe.python.solutions.pose as mp_pose
    print("Imports successful")
    
    face_detector = mp_face_detection.FaceDetection(model_selection=1)
    pose_detector = mp_pose.Pose()
    print("Detectors initialized")
    
    # Create a dummy image
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    results = face_detector.process(img)
    print("Face detector process works")
    
except Exception as e:
    print(f"Error: {e}")
