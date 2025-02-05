import a_utils
import socket
import re
import os
from pathlib import Path

HOST = "127.0.0.1"
PORT = 65300

_fpath = Path('files/server')  

server_socket = None
conn = None

def init_socket():
    global server_socket
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # para impedir que um programa mal finalizado bloqueie a porta
    server_socket.bind((HOST, PORT))
    
def listen_for_connection():
    global conn

    print(f"Server está esperando conexão em: {HOST}:{PORT}...")

    server_socket.listen()
    conn, addr = server_socket.accept()
    print("Conexão estabelecida com sucesso!")

def execute_command():
    response = a_utils.get_msg(conn)
    
    if response["status"] == 'error':
        print("Conexão inválida, voltando a escutar.")
        return

    command = response["message"]
    action, filename = a_utils.command_split(command)

    print(f"Processando comando: {command} -> Action: {action} -> File: {filename}")

    if action == 'listar':
        #listar
        a_utils.send_msg(conn, "success", list_folder_files())
        print("-Lista de arquivos enviada.")
        
        return

    else: 
        filename = sanitize_filename(filename)
        file_path = str(_fpath.absolute().resolve()) + '/' + filename
        
        if action == 'enviar':
            save_path = a_utils.choose_save_path(file_path)
            a_utils.receive_file(conn, save_path)
            print(f'-Arquivo recebido em: {save_path}')

            return
        
        # Testa se o arquivo é válido
        if not a_utils.is_valid_file( file_path ) or filename == ".gitkeep":
            print("-Arquivo inválido escolhido")
            a_utils.send_msg(conn, "error", "Arquivo inválido")
            return

        if action == 'excluir':
            os.remove(file_path)
            print('-Arquivo excluido com sucesso.')
            a_utils.send_msg(conn, "success", "Arquivo excluido com sucesso")

        elif action == 'baixar':
            a_utils.send_msg(conn, "success", "Iniciando envio do arquivo")

            a_utils.send_file(conn, file_path)

        else:
            print("-Ação inválida do cliente.")
            a_utils.send_msg(conn, "error", "Ação inválida")
        
        return

def sanitize_filename(filename):
    
    sanitized = re.sub(r'[\\/*?:"<>|]', ' ', filename)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    sanitized = re.sub(r'\.\.', '', sanitized)

    return sanitized

def list_folder_files():
    files = [file.name for file in _fpath.iterdir() if file.is_file()]
    files.remove('.gitkeep')

    files = ' '.join(files)

    if not files:
        files = '- empty -'

    return files

#------------main------------

def main():
    init_socket()

    while(True):
        try:
            listen_for_connection()
        except Exception as e:
            a_utils.ealert(e)
        
        print("-Esperando commando do cliente...")
        execute_command()


if __name__ == "__main__":
    main()















a_utils.closeit(conn)