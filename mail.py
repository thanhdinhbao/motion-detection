import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import cv2
import numpy as np
import os, sys

#Đọc dữ liệu từ file txt
path = os.path.dirname(os.path.abspath(sys.argv[0])) + '\\data_mail.txt'
with open(path, 'r') as file:
    data = []
    for line in file:
        cleaned_line = line.strip()
        data.append(cleaned_line)

#Thông tin gửi mail
sender_email = data[0]
sender_password = data[1]
recipient_email = data[2]
subject = 'Cảnh báo!' 
body = 'Phát hiện chuyển động!'

#Hàm gửi email cảnh báo
def send_email(frame1, frame2, frame3):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    frames = [frame1, frame2, frame3]
    for i, frame in enumerate(frames):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, frame_jpeg = cv2.imencode('.jpg', frame_rgb)
        image = MIMEImage(frame_jpeg.tobytes())
        image.add_header('Content-Disposition', 'attachment', filename=f'frame{i+1}.jpg')
        msg.attach(image)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
    print('Gửi email thành công.')

