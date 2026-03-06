import cv2

detect = cv2.CascadeClassifier("haarcascade_frontalface_default.xml") # This loads a face detection model.
imp_img = cv2.VideoCapture("elon1.jpg") # This loads the image. 

res, img = imp_img.read() # This reads the image from the file. the res is True or False if the image was loaded
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # This converts the image to black and white.  Because face detection works better on grayscale images.

faces = detect.detectMultiScale(gray, 1.3, 5) # Now the computer tries to find faces in the picture. the 1.3 is how much the image size reduces each step and the 5 is how many times a face must be detected before it is accepted

for (x, y, w, h) in faces: # Loop through each face found. 
    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2) # Draw a rectangle around the face, the (255, 0, 0) is the color of the rectangle and the 2 is the thickness of the rectangle

cv2.imshow("Elon Musk", img) # Display the image with the rectangle around the face
cv2.waitKey(0) # Wait for a key to be pressed
imp_img.release() # Release the image
cv2.destroyAllWindows() # Close all windows