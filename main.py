import threading
import winsound
import mail 
import cv2
import imutils
import numpy as np

# Khởi tạo quay video từ camera mặc định
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# Đặt chiều rộng và chiều cao khung hình để quay video
cap.set(cv2.CAP_PROP_FRAME_WIDTH,640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

# Chụp khung hình đầu tiên từ máy ảnh
_, start_frame = cap.read()

# Thay đổi kích thước frame bắt đầu thành chiều rộng = 500 pixel
start_frame = imutils.resize(start_frame, width=500)

# Chuyển đổi frame bắt đầu sang thang độ xám
start_frame = cv2.cvtColor(start_frame, cv2.COLOR_BGR2GRAY)

# Áp dụng độ Gaussian Blur cho frame bắt đầu thang độ xám để giảm nhiễu
start_frame = cv2.GaussianBlur(start_frame, (21, 21), 0)

alarm = False
alarm_mode = False
alarm_counter=0

def beep_alarm():
    global alarm
    for _ in range(5):
        if not alarm_mode:
            break
        print("CẢNH BÁO!")
        winsound.Beep(2000, 1000)
    alarm = False

# Vòng lặp chính để xử lý video
while True:
    _, frame = cap.read() # Chụp khung hình từ camera
    frame = imutils.resize(frame, width=500) # Thay đổi kích thước khung thành chiều rộng 500 pixel

    # Phát hiện chuyển động và xử lý cảnh báo khi chế độ cảnh báo được kích hoạt
    if alarm_mode:
        frame_bw = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Chuyển khung hình sang thang độ xám
        frame_bw = cv2.GaussianBlur(frame_bw, (5,5), 0) # Áp dụng Gaussian Blur để giảm nhiễu
        # Tính chênh lệch tuyệt đối giữa frame hiện tại và frame bắt đầu
        difference = cv2.absdiff(frame_bw, start_frame)

        # Áp dụng ngưỡng nhị phân cho hình ảnh khác biệt
        threshold =  cv2.threshold(difference, 25, 255, cv2.THRESH_BINARY)[1]
        # Cập nhật frame bắt đầu cho lần lặp tiếp theo
        start_frame = frame_bw
        # Kiểm tra xem tổng giá trị pixel trong ảnh có ngưỡng có vượt quá ngưỡng không
        if threshold.sum()>10000:
            alarm_counter += 1
            # Nếu các khung hình liên tiếp có chuyển động vượt quá ngưỡng
            if alarm_counter > 20:
                if not alarm:
                    alarm= True
                    # Bắt đầu một luồng mới để phát tiếng bíp báo động
                    threading.Thread(target=beep_alarm).start()   
                    # Bắt đầu một luồng mới để gửi email kèm hình ảnh            
                    threading.Thread(target=mail.send_email, args=(frame, frame, frame)).start()

        else:
            if alarm_counter > 0:
                # Giảm bộ đếm báo động nếu không phát hiện chuyển động
                alarm_counter -= 1

        cv2.imshow("Phat hien chuyen dong", threshold) 
    # Hiển thị khung đen khi cảnh báo được kích hoạt nhưng không ở chế độ cảnh báo
    elif not alarm_mode and alarm:
        black_frame = np.zeros_like(frame)
        cv2.imshow("Phat hien chuyen dong", black_frame)

    else:
        cv2.imshow("Phat hien chuyen dong",frame)

    # Kiểm tra các sự kiện nhấn phím
    key_pressed = cv2.waitKey(38)
    # Bật/tắt chế độ cảnh báo bằng phím 't'
    if key_pressed == ord("t"):
        alarm_mode = not alarm_mode
        alarm_counter = 0
    # Thoát khỏi chương trình bằng phím 'q'
    if key_pressed == ord("q"):
        alarm_mode = False
        break
    
cap.release()
cv2.destroyAllWindows()