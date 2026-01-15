import collections
import socket
import threading
import unittest

from .. import package

TEST_PORT=53535
TEST_ADDRESS=("127.0.0.1",TEST_PORT,)

class Tests(unittest.TestCase):
    
    def _assert_receives(self, recv:package.Receiver[str], expected:list[str]):

        message_shortened = lambda m: repr(m) if len(m) < 20 else repr(m[:47] + f"...[{len(m) - 47} more bytes]")
        print(f'Expecting {len(expected)} messages')
        remaining = collections.deque(expected)
        def handler(msg:str):
            self.assertTrue(remaining)
            self.assertEqual(msg, remaining.popleft())
            print(f'Got message {len(expected) - len(remaining)} of {len(expected)}: {message_shortened(msg)}')
            print(f'{len(remaining)} messages remaining')
            return bool(remaining)
        t = threading.Thread(target=lambda: recv.recv_while(handler))
        t.start()
        return t

    def _test_send_messages(self, messages:list[str]):

        server = socket.socket()
        server.bind(TEST_ADDRESS)
        server.listen(1)
        rsock_pointer:list[socket.socket|None] = [None]
        recv_pointer:list[package.Receiver[str]|None] = [None]
        def get_receiver():
            rsock, addr = server.accept()
            rsock_pointer[0] = rsock
            recv_pointer[0] = package.util.receiver_from_socket(rsock).adapted(bytes.decode)
            server.close()
        rt = threading.Thread(target=get_receiver)
        rt.start()
        ssock = socket.socket()
        ssock.connect(TEST_ADDRESS)
        sender = package.util.sender_from_socket(ssock).adapted(str.encode)
        rt.join()
        recver = recv_pointer[0]
        assert recver is not None
        t = self._assert_receives(recver, messages)
        for msg in messages:
            sender.send(msg)
        t.join()
        rsock = rsock_pointer[0]
        assert rsock is not None
        rsock.close()
        ssock.close()

    def test(self):
        
        self._test_send_messages([
            'Hello', 
            'World',
            '', 
            'This', 
            'Is', 
            'A', 
            'Test'
        ])

    def test2(self):

        self._test_send_messages([
            'Short message',
            'This is a bit longer message that should still be sent without issues.',
            'A'*4096,
            'B'*8192,
            '',
            'Final message'
        ])
