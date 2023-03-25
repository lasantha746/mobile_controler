from flask import Flask, render_template, request, session, Response
import cv2
import numpy as np
import time
import HandTracking as ht
import pyautogui
from ppadb.client import Client as AdbClient
import os





app = Flask(__name__)


def control_mobile(comment):


    client = AdbClient(host="127.0.0.1", port=5037)  # Default is "127.0.0.1" and 5037
    devices = client.devices()

    response=None

    if len(devices) == 0:
        print('No devices')
        response="No Device"


    else:
        device = devices[0]
        device.shell(comment)
        response="Conect Device"


    return response


cap = cv2.VideoCapture(0)  # use 0 for web camera
#  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
# for local webcam use cv2.VideoCapture(0)

def gen_frames():  # generate frame by frame from camera

    ### Variables Declaration
    pTime = 0  # Used to calculate frame rate
    width = 640  # Width of Camera
    height = 480  # Height of Camera
    frameR = 100  # Frame Rate
    smoothening = 5  # Smoothening Factor
    prev_x, prev_y = 0, 0  # Previous coordinates
    curr_x, curr_y = 0, 0  # Current coordinates

    cap.set(3, width)  # Adjusting size
    cap.set(4, height)

    detector = ht.handDetector(maxHands=1)  # Detecting one hand at max
    screen_width, screen_height = pyautogui.size()  # Getting the screen size
    while True:
        success, img = cap.read()
        img = detector.findHands(img)  # Finding the hand
        lmlist, bbox = detector.findPosition(img)  # Getting position of hand

        if len(lmlist) != 0:
            x1, y1 = lmlist[8][1:]
            x2, y2 = lmlist[12][1:]


            fingers = detector.fingersUp()  # Checking if fingers are upwards
            cv2.rectangle(img, (frameR, frameR), (width - frameR, height - frameR), (255, 0, 255),
                          2)  # Creating boundary box
            if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:  # cursor, one finger
                x3 = np.interp(x1, (frameR, width - frameR), (0, screen_width))
                y3 = np.interp(y1, (frameR, height - frameR), (0, screen_height))

                curr_x = prev_x + (x3 - prev_x) / smoothening
                curr_y = prev_y + (y3 - prev_y) / smoothening

                pyautogui.moveTo(screen_width - curr_x, curr_y)  # Moving the cursor
                cv2.circle(img, (x1, y1), 7, (255, 0, 255), cv2.FILLED)
                prev_x, prev_y = curr_x, curr_y

            if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:  # click tow finger
                length, img, lineInfo = detector.findDistance(8, 12, img)

                if length < 40:  # If both fingers are really close to each other //lenth cheack
                    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                    pyautogui.click()  # Perform Click

            if fingers[1] == 0 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:  # Right
                control_mobile('input touchscreen swipe 410 830 135 830')
                # time.sleep(1)

            if fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:  # Left
                control_mobile('input touchscreen swipe 290 830 630 830')
                # time.sleep(1)

            if fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 1:  # Jump
                control_mobile('input touchscreen swipe 355 830 355 480')
                # time.sleep(1)

            if fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:  # Down
                control_mobile('input touchscreen swipe 355 830 355 1320')
                # time.sleep(1)


        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
        # cv2.imshow("Image", img)
        # cv2.waitKey(1)

        # frame = Virtual_Mouse.main(camera)
        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result




@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html',check_device=control_mobile(None))


@app.route('/connect_mobile')
def connect_mobile():
    os.startfile("C:\\Users\\hp\\Desktop\\mobile_control\\scrcpy-win64-v2.0\\scrcpy.exe")
    return render_template('index.html', check_device=control_mobile(None))


if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0')