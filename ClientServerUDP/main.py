from Server import Server
import yaml
import socket as sk

def main():
    server = Server()
    server.start_server()


if __name__ == "__main__":
    main()