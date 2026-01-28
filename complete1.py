import cv2
import mediapipe as mp
import math
import pyautogui
import numpy
import time

# Hằng số cho scroll chuột 
Pos_y=0
Sensitivity_scroll=0.25
accumulator = 0.0
#biến số thời gian
last_time=0
min_time=0.5
status_scroll=False

#------ Các tham số chuột--------
#kiểu sẽ cho chuột đầm và chống rung 
Smooth=5

# biến lưu giá trị hiện tại
CLX,CLY=0 ,0       # Current Location
# biến lưu giá trị trước đó
PLX,PLY=0 ,0       # Previous Location
#""""


#phạm vi hoạt động 
frame_r=100 # tức tạo cái khung nhỏ hơn khung image cũ 100frame


mp_hands=mp.solutions.hands
mp_draw=mp.solutions.drawing_utils
mp_draw_style=mp.solutions.drawing_styles


#Lấy tỉ lệ màn hình bạn sử dụng
screen_w,screen_h=1920,1080



cap = cv2.VideoCapture(0)
print ("khởi động camera... !")
#---------------------------MAIN------------------------------------------
with mp_hands.Hands(
    model_complexity=0,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        success , image = cap.read()
        if not success :
            continue

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
                        
                
                
                
                
                #------------ thao tác di chuột-------------------
                #tính độ dịch chuyển ước tính
                real_X=numpy.interp(lm_tro.x * w,(frame_r,w-frame_r),(0,screen_w))
                real_y=numpy.interp(lm_tro.y * h,(frame_r,h-frame_r),(0,screen_h))
                #tính quãng đường thực tế 
                CLX=CLX + (real_X-PLX)/Smooth
                CLY=CLY + (real_y-PLY)/Smooth
                #điều khiển chuột đến địa chỉ mới
                if not status_scroll:
                    cv2.rectangle(image, (frame_r, frame_r), (w - frame_r, h - frame_r), (255, 0, 255), 2)
                    pyautogui.moveTo(CLX,CLY)

                        
                # cập nhật lại vị trí cũ thành vị trí hiện tại
                PLX=CLX 
                PLY=CLY

               
                # Biến tính lượng scroll cần thiết
                speed=0

                # -------------Thao tác scroll chuột-------------------
                if status_scroll and not (Pos_y<250 or Pos_y>800):
                    pos_up=Pos_y-100 
                    pos_down=Pos_y+100 
                    
                    
                    cv2.putText(image, "SCROLL MODE", (50, 80), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 1)
                    #CLY : vị trí hiện tại của trục Y
                    if (CLY < pos_up):
                        dist = pos_up - CLY
                        # Công thức tuyến tính: Khoảng cách * Độ nhạy
                        speed = (dist * Sensitivity_scroll)
        
                        cv2.putText(image, "UP", (480, 80), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
                    elif (CLY > pos_down):
                        dist = CLY - pos_down
                        speed = -(dist * Sensitivity_scroll)  

                        cv2.putText(image, "DOWN", (480, 80), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 255), 2)
                    else :
                        cv2.putText(image, "SAFE", (480, 80), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                    
                    #lưu các giá trị lẻ , nhỏ
                    accumulator+=speed
                    step=int(accumulator)
                    if step!=0:
                        pyautogui.scroll(step)
                        accumulator-=step
                        if speed == 0:
                            accumulator= 0
                #--------------------------Kết thúc thao tác di chuột--------------------------------
                
        
        cv2.imshow('Scroll', image)
        if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()
                

    
