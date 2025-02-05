import os
import json

def ealert(e):
    print("Programa falhou: ")
    print(e)

def closeit(conn):
    print("Fechando conexão.")
    conn.close()

def get_msg(conn, size=1024):
    data = conn.recv(size)

    if not data:
        return {"status":"error", 
                "message":"Conexão quebrada"}; 
    
    response = json.loads(data.decode('utf-8'))
    return response

def send_msg(conn, status, msg):
    # status : success | error
    # data : qualquer string
    # {"status": "success", "data": ["arquivo1.txt", "arquivo2.pdf"]}
    msg = {
        "status": status,
        "message" : msg
    }

    msg = json.dumps(msg).encode('utf-8')

    conn.sendall(msg)

def raw_send(conn, data):
    conn.sendall(data)

def raw_get(conn, size = 2048):
    return conn.recv(size)

def command_split(command):
    command = command.split(maxsplit=1)
    action = command[0]
    file = ''
    if(len(command) == 2):
        file = command[1]
    
    return action, file

def is_valid_file(file_path):
    if os.path.exists(file_path):
        return True
    else:
        return False
    
def send_file(conn, file_path):
    file_size = os.path.getsize(file_path)
    send_msg(conn, "start_file_sending", str(file_size))

    response = get_msg(conn)

    if response["status"] != "start_file_sending_ok": 
        print("Não foi possível proseguir com o envio de arquivo.")
        return -1

    with open(file_path, "rb") as file:
        while True:
            data = file.read(1024)

            if not data:
                break

            raw_send(conn, data)

    print(f"Arquivo {file_path} enviado com sucesso.")
    
def receive_file(conn, save_path):
    response = get_msg(conn)
    
    if response["status"] != "start_file_sending":
        return -1
    
    file_size = int(response["message"])

    send_msg(conn, "start_file_sending_ok", "ok")

    with open(save_path, "wb") as file:
        received_size = 0
        while received_size < file_size:

            data = raw_get(conn, 2048)
            
            if not data:
                break

            file.write(data)
            received_size += len(data)
    
    print(f"Arquivo {save_path} recebido com sucesso.")


def choose_save_path(file_path):
    file_name_without_extension = os.path.splitext(file_path)[0]
    exten = os.path.splitext(file_path)[1]

    while is_valid_file(file_name_without_extension + exten):
        file_name_without_extension += 'new'
    
    file_path = file_name_without_extension + exten

    return file_path