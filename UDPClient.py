# Client code to receive video frames over UDP
import cv2, socket
import numpy as np
import base64
import time

BUFF_SIZE = 65536
# Create a UDP socket at client side
socket_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket_client.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, BUFF_SIZE)
Host_Name = socket.gethostname()
Host_IP = '10.77.53.222'  # got it from socket.gethostbyname(Host_Name)
print(Host_IP)
Port = 9999
RTTime_list = []
# Receive video packets and decode it using base64
def video_receiving():
    fps, st, frames_number, cnt = (0, 0, 20, 0)
    while True:
        start_time = time.time()
        first_user_sent = "RTT::Bob"
        socket_client.sendto(base64.b64encode(first_user_sent.encode('ascii')), (Host_IP, Port))
        packet_data,_ = socket_client.recvfrom(BUFF_SIZE)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print("Spent time : " + str(elapsed_time))
        RTTime_list.append(elapsed_time)
        received_msg = base64.b64decode(packet_data, ' /').decode('ascii').split('::')
        img_data = np.fromstring(received_msg[1], dtype=np.uint8, sep=' ')
        frame = cv2.putText(cv2.imdecode(img_data, 1), 'FPS: ' + str(fps), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("RECEIVING VIDEO", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('Q'):
            quit_message = 'QUIT::Bob'
            socket_client.sendto(base64.b64encode(quit_message.encode('ascii')), (Host_IP,Port))
            socket_client.close()
            break
        if cnt == frames_number:
            try:
                fps = round(frames_number/(time.time() -st))
                st = time.time()
                cnt = 0
            except:
                pass
        cnt += 1
# Send credentials to the server and request starting streaming
user1_login_message = 'LOGIN::Bob::1234'
try:
    socket_client.sendto(base64.b64encode(user1_login_message.encode("ascii")), (Host_IP, Port))
    received_packet, _ =socket_client.recvfrom(BUFF_SIZE)
    packet_data = base64.b64decode(received_packet, ' /').decode('ascii')
    received_msg = packet_data.split('::')
    print(received_msg)
    if received_msg[0] == 'MESSAGE':
        if received_msg[1] == 'AUTHORIZE':
            video_receiving()
        elif received_msg[1] == 'UNAUTHORIZE':
            print('Wrong password!!!')
except socket.error as error:
    print(error)
if len(RTTime_list) == 0:
    print('RTT list is empty! Timeout from first sent request!')
else:
    avg_RTTime = np.average(RTTime_list)
    max_RTTime = max(RTTime_list)
    min_RTTime = min(RTTime_list)
    print('Average Round-Trip Time:' + str(avg_RTTime))
    print('Maximal Round-Trip Time:' + str(max_RTTime))
    print('Minimal Round-Trip Time:' + str(min_RTTime))
# Close the socket
print('Сlosing socket')
socket_client.close