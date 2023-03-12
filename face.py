import cv2
import mediapipe as mp
import time
import pymongo

class FaceDetector():
    def __init__(self, minDetectionCon=1, model_selection=2):
        self.minDetectionCon = minDetectionCon
        self.model_selection = model_selection
        self.mpFaceDetection = mp.solutions.face_detection
        self.mpDraw = mp.solutions.drawing_utils
        self.faceDetection = [self.mpFaceDetection.FaceDetection(model_selection)]
        self.client = pymongo.MongoClient("mongodb+srv://mohamedmejimar:78XJFrYs5ZiAyWyo@face.itrtvix.mongodb.net/test")
        self.db = self.client["mydatabase"]
        self.collection = self.db["face"]
        self.present_students = []
        self.student_ids = self.fetch_student_ids()

    def fetch_student_ids(self):
        student_ids = []
        for doc in self.db['students'].find({}, {'_id': 0, 'student_id': 1}):
            student_ids.append(doc['student_id'])
        return student_ids

    def findFaces(self, img, draw=True):
       imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
       faces = []
       for detection in self.faceDetection:
        self.results = detection.process(imgRGB)
        if self.results.detections:
            for detection in self.results.detections:
                bboxC = detection.location_data.relative_bounding_box
                ih, iw, ic = img.shape
                bbox = int(bboxC.xmin * iw), int(bboxC.ymin * ih), \
                       int(bboxC.width * iw), int(bboxC.height * ih)
                faces.append({"bbox": bbox})
                if draw:
                    self.mpDraw.draw_detection(img, detection)
                    x, y, w, h = bbox
                    cv2.putText(img, "present", (x + w//2, y - h//2), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 2)
                    student_id = self.get_student_id(bbox)
                    if student_id is not None and student_id not in self.present_students:
                        self.present_students.append(student_id)
                        print("Student {} is present".format(student_id))
                
            if self.collection.count_documents({}) == 0: # check if any faces are already stored in the database
                face_data = {"faces": faces}
                self.collection.insert_one(face_data)

        return img


    def get_student_id(self, bbox):
        # Implement a function to get the student id based on their face bbox
        # For example, you can match the bbox with a list of known student bboxes and return the corresponding id
        # If the bbox doesn't match any known student bboxes, return None
        # You can also store the student ids in a database or a file and read from it here
        return None

def main():
    pTime = 0
    cTime = 60
    cap = cv2.VideoCapture(0)
    detector = FaceDetector()
    while True:
        success, img = cap.read()
        img = detector.findFaces(img)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)),(10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 2)
       
        cv2.imshow("Image", img)
        cv2.waitKey(1)

     

    # Check for absent students every 10 seconds
        if int(cTime) % 10 == 0:
            all_students =detector.student_ids # Get all student ids from the database
            print(all_students)
            absent_students = list(set(all_students) - set(detector.present_students)) # Get absent students by subtracting present students from all students
            if len(absent_students) > 0:
             print("Absent students: ", absent_students)
            # You can also update a database or file with the absent students here
             detector.present_students.clear() # Reset present students list


cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
