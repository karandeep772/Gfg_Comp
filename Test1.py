import cv2
import time

# Open the camera (use the correct index for your camera)
camera_index = 1  # Change if necessary
cap = cv2.VideoCapture(camera_index)

img_saved = False  # Flag to check if the image has already been saved

while True:
    ret, current_frame = cap.read()
    
    if not ret:
        print("Failed to grab frame")
        break

    # Display the current frame
    cv2.imshow("Camera", current_frame)

    # Save the image only once
    img_path = r'C:\Users\anmol\OneDrive\Desktop\HardWar\captured_image.png'  # Absolute path
    cv2.imwrite(img_path, current_frame)
    print(f"Image saved at: {img_path}")
    img_saved = True  # Set the flag to True to prevent further saving

    # Check for keypress to quit
    if cv2.waitKey(1) == ord('q'):  # Press 'q' to quit
        break

    time.sleep(5)

# Release the camera and close windows
cap.release()
cv2.destroyAllWindows()
