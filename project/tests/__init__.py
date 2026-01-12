import collections
import socket
import threading
import unittest

from ..package import i,o

TEST_PORT=53535
TEST_ADDRESS=("127.0.0.1",TEST_PORT,)

class Tests(unittest.TestCase):
    
    def _assert_receives(self, recv:i.ReceiverIf[bytes], expected:list[str]):

        remaining = collections.deque(expected)
        def handler(msg_bytes:bytes):
            msg = msg_bytes.decode('utf-8')
            self.assertTrue(remaining)
            self.assertEqual(msg, remaining.popleft())
            print(f'Got message: {msg}')
            print(f'{len(remaining)} messages remaining')
            return bool(remaining)
        t = threading.Thread(target=lambda: recv.recv_while(handler))
        t.start()
        return t

    def test(self):
        
        server = socket.socket()
        server.bind(TEST_ADDRESS)
        server.listen(1)
        rsock_pointer:list[socket.socket|None] = [None]
        recv_pointer:list[i.Receiver|None] = [None]
        def get_receiver():
            rsock, addr = server.accept()
            rsock_pointer[0] = rsock
            recv_pointer[0] = i.util.receiver_from_socket(rsock)
            server.close()
        rt = threading.Thread(target=get_receiver)
        rt.start()
        ssock = socket.socket()
        ssock.connect(TEST_ADDRESS)
        sender = o.util.sender_from_socket(ssock)
        rt.join()
        recver = recv_pointer[0]
        assert recver is not None
        expected_messages = ['Hello', 'World', 'This', 'Is', 'A', 'Test']
        t = self._assert_receives(recver, expected_messages)
        for msg in expected_messages:
            sender.send(msg.encode('utf-8'))
        t.join()
        rsock = rsock_pointer[0]
        assert rsock is not None
        rsock.close()
        ssock.close()
