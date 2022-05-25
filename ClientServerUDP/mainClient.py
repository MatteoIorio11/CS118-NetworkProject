from Client.Client import Client
import HeaderFactory

def main():
    client = Client()
    try:
        client.set_server_adress('localhost', 20000)
        menu = client.get_menu()
        while True:
            print(menu)
            print("AAAA")
            operation = int(input("Select an operation among the ones above: "))
            if operation == 1:
                print(client.get_files_on_server())
            elif operation == 2:
                file = input("Write the name of the file that you want to download ")
                client.download_file(file)
            elif operation == 3:
                file = input("Write the name of the file that you want to upload on the server ")
                client.upload(file)
            elif operation == 4:
                client.close_connection()
                break
            else:
                print("Wrong number")
        
    except Exception as info:
        print(info)
    finally:
        client.close_connection()


if __name__ == "__main__":
    main()