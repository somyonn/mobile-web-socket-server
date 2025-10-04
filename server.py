import os
import socket
from datetime import datetime
from email.parser import BytesParser
from email.policy import default

class SocketServer:
    def __init__(self):
        self.bufsize = 1024  # 버퍼 크기 설정
        self.DIR_PATH = './request'
        self.createDir(self.DIR_PATH)

    def createDir(self, path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError:
            print("Error: Failed to create the directory.")

    def save_binary_file(self, data):
        # 현재 시간으로 파일명 생성
        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"{self.DIR_PATH}/{now}.bin"
        with open(filename, 'wb') as f:
            f.write(data)
        print(f"Saved binary data to {filename}")
        return filename

    def save_image_file(self, image_bytes, ext="jpg"):
        now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-image")
        filename = f"{self.DIR_PATH}/{now}.{ext}"
        with open(filename, 'wb') as f:
            f.write(image_bytes)
        print(f"Saved image file to {filename}")
        return filename

    def parse_multipart(self, data):
        # HTTP 요청 헤더와 바디 분리
        try:
            header_body_split = data.split(b'\r\n\r\n', 1)
            headers = header_body_split[0]
            body = header_body_split[1]
        except IndexError:
            return None, None

        # 멀티파트를 이메일 파싱기로 파싱
        parser = BytesParser(policy=default)
        msg = parser.parsebytes(data)
        image_bytes = None

        # 멀티파트 내 각 파트 확인
        if msg.is_multipart():
            for part in msg.iter_parts():
                content_disposition = part.get("Content-Disposition", None)
                if content_disposition and 'filename' in content_disposition:
                    image_bytes = part.get_payload(decode=True)
                    # 확장자 추출
                    filename = part.get_filename()
                    ext = filename.split('.')[-1] if filename else "jpg"
                    return image_bytes, ext

        return None, None

    def run(self, ip, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((ip, port))
        self.sock.listen(10)
        print("Start the socket server...")
        print("\"Ctrl+C\" for stopping the server!\r\n")

        try:
            while True:
                clnt_sock, req_addr = self.sock.accept()
                clnt_sock.settimeout(5.0)
                print("Request message...\r\n")

                # 요청 데이터 수신 (간단히 최대 10KB로 고정)
                data = b""
                try:
                    while True:
                        part = clnt_sock.recv(self.bufsize)
                        if not part:
                            break
                        data += part
                        if len(data) > 10240:
                            break
                except socket.timeout:
                    pass

                # 요청 데이터 저장 (.bin 파일)
                self.save_binary_file(data)

                # 이미지 파일 데이터 분리 및 저장 시도
                image_bytes, ext = self.parse_multipart(data)
                if image_bytes:
                    self.save_image_file(image_bytes, ext)

                # 응답 전송
                response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nReceived"
                clnt_sock.sendall(response)

                # 클라이언트 소켓 닫기
                clnt_sock.close()

        except KeyboardInterrupt:
            print("\r\nStop the server...")

        self.sock.close()


if __name__ == "__main__":
    server = SocketServer()
    server.run("127.0.0.1", 8000)
