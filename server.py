import pickle
from logger import Log
from request_parser import *


class Server:
    def __init__(self):
        self.cache_check_time = round(time())
        self.log = Log()

    def run(self):
        try:
            with open("cache", "rb") as file:
                self.log.cache = pickle.load(file)
        except FileNotFoundError:
            self.log.cache = {}
        self.check_cache()
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.bind(('127.127.127.127', 53))
        request_parser = RequestParser(self.log)
        while True:
            try:
                received, address = udp_socket.recvfrom(1024)
                request = binascii.hexlify(received).decode("utf-8")
                request = request_parser.parse_request(request)
                if request is not None:
                    udp_socket.sendto(binascii.unhexlify(request), address)
                self.check_cache()
            finally:
                self.change_cache()

    def check_cache(self):
        if round(time()) - self.cache_check_time > 60:
            for name, _type in self.log.keys():
                for item in self.log.get((name, _type)):
                    if not item.death_time > round(time()):
                        self.log.get((name, _type)).remove(item)
            self.change_cache()

    def change_cache(self):
        with open("cache", "wb") as file:
            pickle.dump(self.log.cache, file)


if __name__ == '__main__':
    server = Server()
    server.run()
