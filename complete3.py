import cv2
import mediapipe as mp
import math
import pyautogui
import numpy as np
import time

# Biến scroll
Sensitivity_scroll = 2.0  
DEADZONE = 40             


# Biến toàn cục
Pos_y = 0
last_time = 0
min_time = 0.5
status_scroll = False

# Biến tích lũy (QUAN TRỌNG ĐỂ MƯỢT)
accumulator = 0.0

# Tham số chuột
Smooth = 5
CLX, CLY = 0, 0
PLX, PLY = 0, 0
frame_r = 100

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Lấy kích thước màn hình
screen_w, screen_h = pyautogui.size()

cap = cv2.VideoCapture(0)
# Set độ phân giải cố định để tính toán Pos_y chuẩn xác
cap.set(3, 640)
cap.set(4, 480)

print("khoi dong camera... !")

with mp_hands.Hands(
    model_complexity=0,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7) as hands:
    
    while cap.isOpened():
        success, image = cap.read()
        if not success: continue

        #Lấy tỉ lệ màn hình camera
        h,w,_=image.shape
        image.flags.writeable=False
        image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        image = cv2.flip(image, 1)
        results= hands.process(image)
        
        image.flags.writeable=True
        image=cv2.cvtColor(image,cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:

                mp_draw.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS)
                #lấy địa chỉ các điểm
                lm_tro=hand_landmarks.landmark[8]
                lm_cai=hand_landmarks.landmark[4]
                lm_giua=hand_landmarks.landmark[12]
                
                #tính tỉ lệ các điểm
                x0, y0 = int(hand_landmarks.landmark[0].x * w), int(hand_landmarks.landmark[0].y * h)
                x9, y9 = int(hand_landmarks.landmark[9].x * w), int(hand_landmarks.landmark[9].y * h)
                x16, y16 = int(hand_landmarks.landmark[16].x * w), int(hand_landmarks.landmark[16].y * h)
                x4, y4 = int(hand_landmarks.landmark[4].x * w), int(hand_landmarks.landmark[4].y * h)
                #tính tỉ lệ khoảng cách giữa các điểm như ơ dưới
                palm_size = math.hypot(x9 - x0, y9 - y0)
                pinch_dist = math.hypot(x16 - x4, y16 - y4)
                try:
                    ratio = pinch_dist / palm_size
                except:
                    pass
                
                if ratio < 0.25:
                    if (time.time()- last_time > min_time) :
                        status_scroll= not status_scroll
                        last_time=time.time()
                        if (status_scroll):
                            print ("Khởi động chế độ scroll...!")
                            Pos_y=lm_tro.y * screen_h
                            accumulator=0
                        else:
                            print ("tắt chế độ scroll...!")

                # tính vị trí chuột
                real_X = np.interp(lm_tro.x * w, (frame_r, w - frame_r), (0, screen_w))
                real_y = np.interp(lm_tro.y * h, (frame_r, h - frame_r), (0, screen_h))
                
                CLX = PLX + (real_X - PLX) / Smooth
                CLY = PLY + (real_y - PLY) / Smooth
                PLX, PLY = CLX, CLY

                # ------------- PHÂN CHIA CHỨC NĂNG -----
                #di chuột
                if not status_scroll:
                    cv2.rectangle(image, (frame_r, frame_r), (w - frame_r, h - frame_r), (255, 0, 255), 2)
                    try: pyautogui.moveTo(CLX, CLY)
                    except: pass
                # Thao tác chuột
                else:
                    
                    
                    # Tính giới hạn vùng chết
                    pos_up = Pos_y - DEADZONE
                    pos_down = Pos_y + DEADZONE
                    
                    cv2.putText(image, "SCROLL MODE", (50, 80), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)

                    # Lấy vị trí tay hiện tại (Pixel Camera)
                    current_y = int(lm_tro.y * h)
                    # Biến tính lượng scroll cần thiết
                    speed = 0

                    if current_y < pos_up:
                        dist = pos_up - current_y
                        speed = dist * Sensitivity_scroll
                        
                        cv2.putText(image, "UP", (w-100, 80), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

                    elif current_y > pos_down:
                        dist = current_y - pos_down
                        speed = -(dist * Sensitivity_scroll) # Số âm để xuống
                        
                        cv2.putText(image, "DOWN", (w-100, 80), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                    
                    else:
                        speed = 0
                        cv2.putText(image, "STOP", (w-100, 80), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 2)

                    # Cộng dồn giá trị lẻ vào kho
                    accumulator += speed
                    steps = int(accumulator)
                    if steps != 0:
                        pyautogui.scroll(steps)
                        accumulator -= steps 
                        print (steps)
                        if speed == 0:
                            accumulator = 0

        cv2.imshow('Scroll', image)
        if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()