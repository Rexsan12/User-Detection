import cv2
import sys

# user has to input img
imagePath = "thani.jpeg"
cascPath = "haarcascade_frontalface_default.xml"

# include the haar cascade
faceCascade = cv2.CascadeClassifier(cascPath)

# Read the image
image = cv2.imread(imagePath)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# To Detect faces in the image
faces = faceCascade.detectMultiScale(
    gray,
    scaleFactor=1.1,
    minNeighbors=5,
    minSize=(30, 30),
    flags = cv2.CASCADE_SCALE_IMAGE
)

print("Detected {0} faces!".format(len(faces)))

# Draw a rectangle around the faces
for (x, y, w, h) in faces:
    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

cv2.imshow("Faces Detected", image)
cv2.waitKey(0)

try:
    # Setting up the camera
    camera = PiCamera()
    # Choosing the resolution of the picture, lower resolution gives lower prosessing time.
    camera.resolution = (250, 250)
    # Initialising the capture.
    rawCapture = PiRGBArray(camera)
    # Capturing the first initialising picture.
    camera.capture(rawCapture, format="bgr")

    # load the known faces and embeddings
    print("[INFO] loading encodings...")
    data = pickle.loads(
        open("/home/pi/Desktop/face-recognition-door-opener-raspberry-pi/faceornot.pickle", "rb").read())

    nrunknown = 0


    # Running all the time untill terminated
    # while True:
    def recogniceFaces():
        # Taking a picture.
        rawCapture = PiRGBArray(camera)
        camera.capture(rawCapture, format="bgr")
        print("capted")
        image = rawCapture.array

        # Keeps track of a person is approved or not.
        approved = False

        # load the input image and convert it from BGR to RGB
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)


        print("[INFO] opning wastage box")
        boxes = face_recognition.face_locations(rgb,
                                                model="hog")  # You can use hog or cnn. (hog is faster)
        encodings = face_recognition.face_encodings(rgb, boxes)


        users = []


        for encoding in encodings:

            matches = face_recognition.compare_faces(data["encodings"],
                                                     encoding)
            name = "Unknown"  # Putting the name to unknown if the person is not recognised.

            # check to see if we have found a match
            if True in matches:

                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                    # Approving the persons
                    if (name == "adne_ovrebo" or name == "thani") and approved == False:
                        print("Approved")  # Print to the terminal that the person is approved
                        approved = True  # Telling the program the person is approved.
                        door.unlock()  # If it gets approved two times the door unlocks.


                name = max(counts, key=counts.get)
            else:
                print("nothuman")
                global nrunknown
                nrunknown = nrunknown + 1
                # saving the unknown persons to the unknown folder
                cv2.imwrite("/home/pi/Desktop/face-recognition-door-opener-raspberry-pi/unknown/unknown" + str(
                    nrunknown) + ".jpg", image)

            # update the list of names
            users.append(name)

        # loop over the recognized faces
        for ((top, right, bottom, left), name) in zip(boxes, users):
            # draw the predicted face name on the image
            cv2.rectangle(image, (left, top), (right, bottom), (0, 255, 0), 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, (0, 255, 0), 2)


        rawCapture.truncate(0)
        cv2.imwrite("/home/pi/Desktop/thani.jpg", image)

        # Locks the door after x seconds if the dor opens
        if approved == True:

            sleep(10)
      
            door.lock()
            return "open wastage box."

except KeyboardInterrupt:
    servocontrol.close()
    print("terminated")