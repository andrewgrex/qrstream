"""
script to read a stream of QR codes from a webcam

this script expects base64 encoded data in the QR codes

note that extension of the filepath should match that of the original file 
you encoded as multiple QR codes

"""

import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2
import time
import argparse
import warnings
import base64
import logging
import sys


def get_valid_cams():
    """
    function to get valid webcams using cv2.VideoCapture

    return: all available webcams
    """
    valid_cams = []
    for i in range(8):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            valid_cams.append(i)
    return valid_cams


def decode(im):
    """
    extract the data from the qr code from the webcam image

    """
    decodedObjects = pyzbar.decode(im)
    return decodedObjects


def webcam_qr_reader(webcam_number=None, resolution=(1024,768)):
    """
    function to use identify and extract data from qr codes as seen
    through a webcam
    """
    
    logging.debug(f"identifying webcams...")
    valid_cams = get_valid_cams()
    logging.debug(f"identified {len(valid_cams)} webcams...")

    if valid_cams:
        if (not webcam_number) or (webcam_number not in valid_cams):
            logging.debug(f"specified webcam ({webcam_number}) not found, defaulting to the first found=({valid_cams[0]})")
            webcam_number = valid_cams[0]
    else:
        logging.critical(f"no valid cams identified... aborting run!")
        sys.exit(0)


    logging.debug(f"beginning video capture...")
    cap = cv2.VideoCapture(webcam_number)

    cap.set(3,resolution[0])
    cap.set(4,resolution[1])

    time.sleep(2)

    cap.set(15, -8.0)

    time.sleep(2)

    chunked_data_stream = []
    previous_index = None
    counter = 0
    font = cv2.FONT_HERSHEY_SIMPLEX
    t0 = time.time()

    while(cap.isOpened()):
        # Capture frame-by-frame
        ret, frame = cap.read()
        # Our operations on the frame come here
        im = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
             
        decoded_objects = decode(im)
        if len(decoded_objects)>0:
            if len(decoded_objects)>1:
                logging.warning("only expecting one qr code, but multiple found! choosing first qr code")

        for decodedObject in decoded_objects:  
            points = decodedObject.polygon
         
            # if the points do not form a quad, find convex hull
            if len(points) > 4 : 
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                hull = list(map(tuple, np.squeeze(hull)))
            else : 
                hull = points;
             
            # Number of points in the convex hull
            n = len(hull)
            
            # Draw the convext hull
            for j in range(0,n):
                cv2.line(frame, hull[j], hull[ (j+1) % n], (255,0,0), 3)

            x = decodedObject.rect.left
            y = decodedObject.rect.top

            barCode = str(decodedObject.data)
            cv2.putText(frame, barCode, (x, y), font, 1, (0,255,255), 2, cv2.LINE_AA)

            decoded_data = base64.b64decode(decodedObject.data)

            # extract qr data index (big endian, 8 bytes long int repr)
            current_data_index = (int.from_bytes(decoded_data[:8], "big"))
            
            # append to chunked data stream
            if previous_index is None or previous_index!=current_data_index:

                # check data ingestion is sequential
                if isinstance(previous_index, int) and previous_index+1 != current_data_index:
                    print(f"[ERROR] current index ({current_data_index}) does not immediately follow previous index ({previous_index})!!")

                # append data minus the first 8 bytes (the data index)
                chunked_data_stream.append(decoded_data[8:])
                print(f"[INFO] qr code index #{current_data_index}; len: {len(decoded_data[8:])}")
                t0 = time.time()

                # update previous index
                previous_index = current_data_index
        
        # Display the resulting frame
        cv2.imshow('frame',frame)
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord('s'): # wait for 's' key to save 
            cv2.imwrite('Capture.png', frame)     
        # break out if there hasn't been a QR code in the past 2 seconds
        if (time.time() - t0 > 2) and len(chunked_data_stream):
            break
                   
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

    return chunked_data_stream


if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description='Read QR codes from screen')
    parser.add_argument('-fp', '--filepath', type=str, help='filepath to write to')
    args = parser.parse_args()

    chunked_data_stream = webcam_qr_reader()

    with open(args.filepath, 'wb') as f:
        f.write(b''.join(chunked_data_stream))
