from wifi_manager import WiFiManager
from can_handler import MCP2515
from web_server import WebServer
import time

def main():
    print("\nIniciando sistema...")
    
    # Inicializa o gerenciador WiFi
    wifi = WiFiManager()
    
    # Aguarda um pouco para garantir que o WiFi esteja estável
    time.sleep(2)
    
    # Inicializa o controlador CAN
    can = MCP2515()
    
    # Inicializa o servidor web
    server = WebServer(wifi, can)
    server.start()
    
    print("\nSistema iniciado!")
    status = wifi.get_status()
    if status['sta_connected']:
        print(f"Conectado à rede WiFi. IP: {status['sta_ip']}")
    else:
        print(f"Modo AP ativo. IP: {status['ap_ip']}")
    print("Aguardando conexões...")
    
    while True:
        try:
            # Aceita conexões
            client, addr = server.socket.accept()
            print(f'Cliente conectado de {addr}')
            
            # Processa requisição
            server.handle_request(client)
            
        except Exception as e:
            print(f"Erro: {e}")
        
        time.sleep(0.1)

if __name__ == "__main__":
    main() 