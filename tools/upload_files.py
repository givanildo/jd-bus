import sys
import time
import subprocess
import os
from serial.tools import list_ports
import serial

def find_esp32_port():
    """Encontra a porta COM do ESP32"""
    ports = list(list_ports.comports())
    for port in ports:
        # Adiciona mais identificadores comuns de ESP32
        if any(id in port.description for id in ["CP210", "CH340", "USB Serial"]):
            return port.device
    return None

def flash_micropython(port):
    """Instala o MicroPython no ESP32"""
    firmware_path = "D:/Documentos/CAN_BUS/teste-5/esp32/firmware/ESP32_GENERIC-20241129-v1.24.1.bin"
    
    if not os.path.exists(firmware_path):
        print(f"Erro: Firmware não encontrado em {firmware_path}")
        print("Verifique se o arquivo está na pasta correta.")
        return False
        
    try:
        # Instalar/atualizar esptool
        print("\nVerificando esptool...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "esptool"
        ], check=True)
        
        # Apagar flash
        print("\nApagando flash do ESP32...")
        subprocess.run([
            sys.executable, "-m", "esptool", 
            "--port", port, 
            "--baud", "460800",  # Aumenta velocidade do erase
            "erase_flash"
        ], check=True)
        time.sleep(2)
        
        # Instalar firmware
        print("\nInstalando MicroPython...")
        subprocess.run([
            sys.executable, "-m", "esptool",
            "--port", port,
            "--baud", "460800",
            "write_flash",
            "--flash_size=detect", "0x1000",
            firmware_path
        ], check=True)
        
        print("\nMicroPython instalado com sucesso!")
        print("Aguardando reinicialização do ESP32...")
        time.sleep(3)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\nErro durante instalação do MicroPython: {e}")
        return False
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        return False

def transfer_files(port):
    """Transfere os arquivos Python para o ESP32"""
    try:
        # Instalar/atualizar mpremote
        print("\nVerificando mpremote...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", "mpremote"
        ], check=True)
        
        # Lista de arquivos para transferir
        base_dir = "D:/Documentos/CAN_BUS/teste-5"
        files = [
            (f"{base_dir}/esp32/boot.py", ":boot.py"),
            (f"{base_dir}/esp32/main.py", ":main.py"),
            (f"{base_dir}/esp32/can_handler.py", ":can_handler.py"),
            (f"{base_dir}/esp32/wifi_manager.py", ":wifi_manager.py"),
            (f"{base_dir}/esp32/web_server.py", ":web_server.py")
        ]
        
        # Verificar se todos os arquivos existem
        missing_files = [f for f, _ in files if not os.path.exists(f)]
        if missing_files:
            print("\nArquivos não encontrados:")
            for f in missing_files:
                print(f"- {f}")
            print("\nVerifique se os arquivos estão na pasta correta:")
            print(f"{base_dir}/esp32/")
            return False
        
        # Transferir arquivos
        print("\nTransferindo arquivos...")
        for local_file, remote_file in files:
            print(f"Enviando {os.path.basename(local_file)}...")
            try:
                subprocess.run([
                    sys.executable, "-m", "mpremote",
                    f"connect", port,
                    "cp",
                    local_file,
                    remote_file
                ], check=True)
                time.sleep(1)
            except subprocess.CalledProcessError as e:
                print(f"Erro ao enviar {local_file}: {e}")
                return False
            
        print("\nTodos os arquivos transferidos com sucesso!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\nErro durante transferência de arquivos: {e}")
        return False
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        return False

def monitor_serial(port):
    """Monitora a saída serial do ESP32"""
    try:
        print("\nMonitorando saída serial (Ctrl+C para sair)...")
        print("Aguardando mensagens do ESP32...")
        
        with serial.Serial(port, 115200, timeout=1) as ser:
            while True:
                if ser.in_waiting:
                    try:
                        line = ser.readline().decode('utf-8').strip()
                        if line:  # Só mostra se não estiver vazio
                            print(line)
                    except UnicodeDecodeError:
                        pass  # Ignora caracteres inválidos
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\nMonitoramento interrompido pelo usuário")
    except Exception as e:
        print(f"\nErro durante monitoramento: {e}")

def main():
    try:
        # 1. Encontrar porta do ESP32
        print("Procurando ESP32...")
        port = find_esp32_port()
        if not port:
            print("ESP32 não encontrado! Verifique se:")
            print("1. O dispositivo está conectado")
            print("2. O driver USB está instalado")
            print("3. A porta COM está disponível")
            return
        print(f"ESP32 encontrado na porta: {port}")
        
        # 2. Instalar MicroPython
        print("\nIniciando instalação do MicroPython...")
        if not flash_micropython(port):
            print("Erro durante instalação do MicroPython")
            return
            
        # 3. Transferir arquivos
        print("\nIniciando transferência dos arquivos...")
        if not transfer_files(port):
            print("Erro durante transferência dos arquivos")
            return
        
        print("\nProcesso concluído com sucesso!")
        print("O ESP32 irá reiniciar automaticamente.")
        print("Procure pelo ponto de acesso 'JohnDeere_Monitor' em alguns segundos.")
        
        # 4. Monitorar saída serial
        monitor_serial(port)
        
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        print(f"Detalhes: {str(e)}")

if __name__ == "__main__":
    main() 