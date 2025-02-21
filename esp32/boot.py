# Este arquivo apenas importa as bibliotecas necessárias
import network
import json
import os
from time import sleep

# Configurações do Access Point
AP_SSID = "JohnDeere_Monitor"
AP_PASSWORD = "12345678"

def create_ap():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=AP_SSID, password=AP_PASSWORD)
    while not ap.active():
        pass
    print('Access Point ativo')
    print('IP do AP:', ap.ifconfig()[0])
    return ap

def connect_wifi(ssid, password):
    station = network.WLAN(network.STA_IF)
    station.active(True)
    station.connect(ssid, password)
    
    # Aguarda conexão ou timeout
    timeout = 0
    while not station.isconnected() and timeout < 10:
        print('Tentando conectar...')
        sleep(1)
        timeout += 1
    
    if station.isconnected():
        print('Conectado à rede WiFi')
        print('IP:', station.ifconfig()[0])
        return True
    else:
        print('Falha na conexão')
        return False

# Inicializa o modo AP por padrão
ap = create_ap()

# Tenta carregar configurações salvas
try:
    with open('wifi_config.json', 'r') as f:
        config = json.load(f)
        if connect_wifi(config['ssid'], config['password']):
            ap.active(False)  # Desativa o AP após conexão bem-sucedida
except:
    print('Nenhuma configuração WiFi encontrada') 