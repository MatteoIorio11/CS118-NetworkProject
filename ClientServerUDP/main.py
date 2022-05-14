from Server import Server


def main():
    server = Server('localhost', 20000)
    server.start_server()

if __name__ == "__main__":
    main()