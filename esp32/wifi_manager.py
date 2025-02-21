import network
import json
from time import sleep

class WiFiManager:
    def __init__(self, ap_ssid="JohnDeere-AP", ap_password="12345678"):
        self.ap_ssid = ap_ssid
        self.ap_password = ap_password
        self.ap = None
        self.station = None
        self.config_file = 'wifi_config.json'
        
        # Primeiro tenta conectar na rede salva
        if not self.try_connect_saved():
            # Se não conseguir conectar, inicia o AP
            self.start_ap()

    def start_ap(self):
        """Inicia o Access Point"""
        print("\nIniciando Access Point...")
        self.ap = network.WLAN(network.AP_IF)
        self.ap.active(True)
        self.ap.config(essid=self.ap_ssid, 
                      password=self.ap_password,
                      authmode=network.AUTH_WPA_WPA2_PSK)
        
        # Aguarda AP iniciar
        retry = 0
        while not self.ap.active() and retry < 10:
            sleep(0.5)
            retry += 1
            
        if self.ap.active():
            print('Access Point ativo')
            print('SSID:', self.ap_ssid)
            print('Senha:', self.ap_password)
            print('IP do AP:', self.ap.ifconfig()[0])
        else:
            print('Falha ao iniciar Access Point')
        return self.ap

    def connect_wifi(self, ssid, password):
        """Conecta a uma rede WiFi"""
        print(f"\nTentando conectar à rede: {ssid}")
        
        # Mantém AP ativo durante a conexão
        if not self.station:
            self.station = network.WLAN(network.STA_IF)
        
        self.station.active(True)
        sleep(1)
        
        # Tenta conectar
        try:
            self.station.connect(ssid, password)
            
            # Aguarda conexão com timeout
            timeout = 0
            while not self.station.isconnected() and timeout < 20:
                print('Tentando conectar...')
                sleep(1)
                timeout += 1
            
            if self.station.isconnected():
                ip = self.station.ifconfig()[0]
                print('\nConectado com sucesso!')
                print(f'IP: {ip}')
                
                # Salva configuração e IP
                self.save_config(ssid, password, ip)
                
                # Mantém AP ativo por mais 10 segundos
                sleep(10)
                
                if self.ap and self.ap.active():
                    print("Desativando AP...")
                    self.ap.active(False)
                
                return True
                
            print('\nFalha na conexão')
            return False
            
        except Exception as e:
            print(f'Erro ao conectar: {e}')
            return False

    def try_connect_saved(self):
        """Tenta conectar usando configuração salva"""
        config = self.load_config()
        if config:
            print("\nConfiguração WiFi encontrada, tentando conectar...")
            return self.connect_wifi(config['ssid'], config['password'])
        print("\nNenhuma configuração WiFi encontrada")
        return False

    def save_config(self, ssid, password, ip=None):
        """Salva configuração WiFi"""
        try:
            config = {
                'ssid': ssid, 
                'password': password,
                'last_ip': ip
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
            print("Configuração WiFi salva")
        except:
            print("Erro ao salvar configuração WiFi")

    def load_config(self):
        """Carrega configuração WiFi"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except:
            return None

    def scan_networks(self):
        """Busca redes WiFi disponíveis"""
        if not self.station:
            self.station = network.WLAN(network.STA_IF)
        
        self.station.active(True)
        print("\nBuscando redes WiFi...")
        try:
            networks = self.station.scan()
            return [net[0].decode() for net in networks]
        except:
            print("Erro ao buscar redes")
            return []

    def get_status(self):
        """Retorna status das conexões"""
        return {
            'ap_active': self.ap.active() if self.ap else False,
            'ap_ip': self.ap.ifconfig()[0] if self.ap and self.ap.active() else None,
            'sta_connected': self.station.isconnected() if self.station else False,
            'sta_ip': self.station.ifconfig()[0] if self.station and self.station.isconnected() else None
        } 