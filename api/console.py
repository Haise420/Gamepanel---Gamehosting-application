from .const import *
from io import BytesIO
import socket
import sys

class Console:

    def __init__(self, *, host, port=27016, password):
        self.host = host
        self.port = port
        self.password = password
        self.sock = None

    def connect(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(4)
            self.sock.connect((self.host, int(self.port)))

            if self.execute('stats') == 'Bad rcon_password.':
                raise ValueError('Bad password!')
        except Exception as e:
            # Log or raise an exception instead of printing
            raise ValueError(f'Error connecting: {str(e)}')

    def disconnect(self):
        try:
            if self.sock:
                self.sock.close()
        except Exception as e:
            # Log or raise an exception instead of printing
            raise ValueError(f'Error disconnecting: {str(e)}')

    def getChallenge(self):
        try:
            msg = BytesIO()
            msg.write(startBytes)
            msg.write(b'getchallenge')
            msg.write(endBytes)
            self.sock.send(msg.getvalue())

            response = BytesIO(self.sock.recv(packetSize))
            return str(response.getvalue()).split(" ")[1]
        except Exception as e:
            # Log or raise an exception instead of printing
            raise ValueError(f'Error getting challenge: {str(e)}')

    def execute(self, cmd):
        try:
            challenge = self.getChallenge()

            msg = BytesIO()
            msg.write(startBytes)
            msg.write('rcon '.encode())
            msg.write(challenge.encode())
            msg.write(b' ')
            msg.write(self.password.encode())
            msg.write(b' ')
            msg.write(cmd.encode())
            msg.write(endBytes)

            self.sock.send(msg.getvalue())
            response = BytesIO(self.sock.recv(packetSize))

            return response.getvalue()[5:-3].decode()
        except Exception as e:
            # Log or raise an exception instead of printing
            raise ValueError(f'Error executing command: {str(e)}')
