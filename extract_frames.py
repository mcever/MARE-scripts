import cv2
import os

def extract_frames(lid, frames):
    video_path = str(lid) + .'VOB'
    dest = str(lid)
    if not os.path.isdir(dest):
        os.mkdir(dest)
    else:
        print('warning: {} already exists'.format(dest))

    # Opens the Video file
    cap= cv2.VideoCapture(video_path)
    i=0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        if i in frames:
            print(i)
            # cv2.imwrite( os.path.join(dest, '{}_{}.png'.format(lid, i)), frame)
        i+=1

    cap.release()
    cv2.destroyAllWindows()
