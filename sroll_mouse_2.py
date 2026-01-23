import cv2
import mediapipe as mp
import pyautogui # Thư viện điều khiển chuột

# --- KHỞI TẠO ---
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

# Lấy kích thước màn hình camera (để vẽ dòng kẻ cho chuẩn)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Tính toán vị trí pixel của 2 đường kẻ phân chia vùng
line_up_y = int(height * UP_THRESHOLD)
line_down_y = int(height * DOWN_THRESHOLD)

print("Đang khởi động camera...")

with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      continue

    # Xử lý ảnh
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image) #1. Ngăn thứ nhất: multi_hand_landmarks

    # Chuẩn bị vẽ
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # --- LOGIC CUỘN TRANG ---
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        # Lấy tọa độ đầu ngón trỏ (Điểm số 8)
        landmark_tro = hand_landmarks.landmark[8]
        
        # Lấy giá trị Y (độ cao) của ngón trỏ
        y_pos = landmark_tro.y 

        # Kiểm tra vị trí để cuộn
        if y_pos < 0.3:
            # Nếu ngón tay ở vùng TRÊN -> Cuộn LÊN
            print("Lên!")
            pyautogui.scroll(50) #dùng để sroll giá trị ở trong là để chỉnh tốc độ, hiểu giống như vector vận tốc, duong thì đi lên, còn âm thì đi xuống
            cv2.putText(image, "LEN", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
        elif y_pos > 0.7:
            # Nếu ngón tay ở vùng DƯỚI -> Cuộn XUỐNG
            # Lưu ý: scroll số âm là đi xuống
            print("Xuống!")
            pyautogui.scroll(-50)  #dùng để sroll giá trị ở trong là để chỉnh tốc độ, hiểu giống như vector vận tốc, duong thì đi lên, còn âm thì đi xuống
            cv2.putText(image, "XUONG", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        else:
             cv2.putText(image, "DUNG", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # Vẽ khung xương tay
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS)

    # --- VẼ GIAO DIỆN HỖ TRỢ ---
    # Vẽ đường kẻ màu xanh lá cây để phân chia vùng
    # Dòng kẻ trên
    cv2.line(image, (0, line_up_y), (width, line_up_y), (0, 255, 0), 2)
    # Dòng kẻ dưới
    cv2.line(image, (0, line_down_y), (width, line_down_y), (0, 0, 255), 2)

    # Lật ảnh và hiển thị
    cv2.imshow('Scroll Control', cv2.flip(image, 1))
    
    if cv2.waitKey(5) & 0xFF == 27:
      break

cap.release()
cv2.destroyAllWindows()



"""
--------------HƯỚNG DẪN SỬ DỤNG---------------
Công cụ này cho phép bạn lướt Web, đọc tài liệu mà không cần chạm vào chuột, chỉ cần dùng ngón tay trước Camera.

1. Cách Khởi Động
Bước 1: Mở chương trình (Chạy file main.py).
Bước 2: Đợi khoảng 3-5 giây để Camera bật lên.
Bước 3: QUAN TRỌNG: Dùng chuột thật Click 1 lần vào cửa sổ bạn muốn điều khiển (Ví dụ: Trình duyệt Chrome, Youtube, file Word...).
Lưu ý: Nếu không click vào, máy tính sẽ không biết bạn muốn cuộn trang nào.

2. Giao Diện Điều Khiển
Trên màn hình Camera sẽ xuất hiện 2 đường kẻ ngang chia màn hình làm 3 vùng:
Vùng Trên (Trên vạch Xanh): Vùng cuộn lên.
Vùng Giữa: Vùng nghỉ (an toàn).
Vùng Dưới (Dưới vạch Đỏ): Vùng cuộn xuống.

Nhấn Esc trên bàn phím để xóa 
"""