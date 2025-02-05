import a_utils
import socket
import sys
from pathlib import Path

HOST = "127.0.0.1"
PORT = 65300

_fpath = Path('files/client')

conn = None
command = ''
action = ''
filename = ''

def get_cmd_params():
    global command, HOST

    if(len(sys.argv) != 3):
        invalid_action_response()

    HOST = sys.argv[1]
    command = sys.argv[2]

def connect():
    global conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # para impedir que um programa mal finalizado bloqueie a porta 
    conn.connect((HOST, PORT))

def send_command():
    global action, filename, command
    action, filename = a_utils.command_split(command)

    if action == 'listar':
        listar_action()
    else:
        if action == 'excluir':
            excluir_action()
        elif action == 'enviar':
            enviar_action()
        elif action == 'baixar':
            baixar_action()
        else:
            invalid_action_response()

def invalid_action_response():
    print('Ação inválida, siga o padrão abaixo:')
    print('''
        python client.py ip-do-servidor “listar”
        python client.py ip-do-servidor “excluir arquivo.txt”
        python client.py ip-do-servidor “enviar arquivo.txt”
        python client.py ip-do-servidor “baixar  arquivo.txt”
        ''')
    
    exit()

def listar_action():
    a_utils.send_msg(conn, "success", command)

    print("Lista do servidor: ")
    response = a_utils.get_msg(conn)
    
    if response["status"] == "success":
        print(response["message"])

def excluir_action():
    a_utils.send_msg(conn, "success", command)

    print('Esperando servidor responder...')
    response = a_utils.get_msg(conn)
    
    if response["status"] == "error":
        print("Operação impossível: ")
        print(response["message"])
        exit()
    
    print(response["message"])

def enviar_action():
    file_path = str(_fpath.absolute().resolve()) + '/' + filename

    if not a_utils.is_valid_file(file_path):
        print("Arquivo inválido para ser enviado")
        exit()
    
    a_utils.send_msg(conn, "success", command)
    
    a_utils.send_file(conn, file_path)

def baixar_action():
    a_utils.send_msg(conn, "success", command)

    response = a_utils.get_msg(conn)

    if response['status'] != 'success':
        print(response["message"])
        return

    file_path = str(_fpath.absolute().resolve()) + '/' + filename
    save_path = a_utils.choose_save_path(file_path)
    
    a_utils.receive_file(conn, save_path)



#------------main------------

def main():

    get_cmd_params()

    try:
        connect()
    except ConnectionRefusedError:
        print("Conexão recusada, o Ip está correto?")
        exit()
    except Exception as e:
        a_utils.ealert(e)
        exit()

    send_command()


if __name__ == "__main__":
    main()