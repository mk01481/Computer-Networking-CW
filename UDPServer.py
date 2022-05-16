import cv2, imutils, socket
import base64
import threading

BUFF_SIZE = 65536

CLIENT = []
USERS = {'Bob': '1234',
         'John': '1234',
         'Lola':'1234',
         'Jack': '1234'
         }
#Adding some useful functions:
# Function for checking correct password of user
def password_verification(user, password):
    return password == USERS[user]
# Function for checking user in users dictionary
def user_checking(user):
    return user in USERS.keys()
# Create a server
socket_server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
socket_server.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
Host_Name =socket.gethostname()
Port = 9999
Host_IP = '10.77.53.222'  # got it from socket.gethostbyname(Host_Name)
print(Host_IP)
socket_location = (Host_IP,Port)

# Bind to server
socket_server.bind(socket_location)
print('Listening at address:', socket_location)
# Lets initialize video:
my_video = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# start streaming the video
def start_stream(client_addr,e,user):
    client_location = (client_addr,e)
    stream_width= 400
    fps, st, frames_to_count, cnt = (0,0,20,0)
    while my_video.isOpened():
        while user in CLIENT:
            _,frame =my_video.read()
            frame = imutils.resize(frame,width=stream_width)
            encoded_img,memory_buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
            video_packet = 'VIDEO::'
            for buf in memory_buffer:
                video_packet += f'{buf} '
            packet_message =base64.b64encode(video_packet.encode("ascii"))
            socket_server.sendto(packet_message,client_location)
        print(f'Stop broadcasting my video to user:{user}')
        break
# Function for receiving packet from client, and based on the packet received, the server respond to the client
def function_receive():
    while True:
        server_msg, client_location = socket_server.recvfrom(BUFF_SIZE)
        print('Connection from client : ',client_location)
        server_msg = base64.b64decode(server_msg,' /').decode('ascii').split('::')
        if server_msg[0] == 'LOGIN':
            print('LOGIN')
            if len(CLIENT) < 3:  #checking if we have less than 3 clients
                if server_msg[1] in CLIENT:
                    existed_msg = "MESSAGE::EXISTED"
                    socket_server.sendto(base64.b64encode(existed_msg.encode('ascii')),client_location)
                    print('This user already logged in!')
                else:
                    if user_checking(server_msg[1]):
                        if password_verification(server_msg[1],server_msg[2]):
                            authorize_msg = "MESSAGE::AUTHORIZE"
                            socket_server.sendto(base64.b64encode(authorize_msg.encode('ascii')), client_location)
                            print('Correct password!')
                            CLIENT.append(server_msg[1])
                            my_thread = threading.Thread(target=start_stream, args=(client_location[0],client_location[1],server_msg[1]))
                            my_thread.start()
                        else:
                            not_authorize_msg = "MESSAGE::UNAUTHORIZE"
                            socket_server.sendto(base64.b64encode(not_authorize_msg.encode('ascii')),client_location)
                            print("Wrong password, user is not authorized !!")
            else:
                full_msg = "MESSAGE::FULL"
                socket_server.sendto(base64.b64encode(full_msg.encode('ascii')),client_location)
        elif server_msg[0] == 'QUIT':
            CLIENT.remove(server_msg[1])
            print(f'{server_msg[1]} successfully quit the server!')
        else:
            print('Wrong format of the packet received!')
function_receive()
