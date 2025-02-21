import socket
import json

class WebServer:
    def __init__(self, wifi_manager, can_handler):
        self.wifi_manager = wifi_manager
        self.can_handler = can_handler
        self.socket = None
        self.can_data = []
        self.monitoring = True  # Começa monitorando automaticamente
    
    def start(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', 80))
        self.socket.listen(5)
        print('Servidor web iniciado na porta 80')
    
    def handle_request(self, client):
        try:
            request = client.recv(1024).decode()
            
            # Verifica se está no modo AP ou Station
            status = self.wifi_manager.get_status()
            is_ap_mode = status['ap_active']
            
            if "GET /scan" in request:
                networks = self.wifi_manager.scan_networks()
                self.send_json_response(client, {"networks": networks})
                
            elif "POST /connect" in request:
                body = request.split('\r\n\r\n')[1]
                config = json.loads(body)
                success = self.wifi_manager.connect_wifi(config['ssid'], config['password'])
                
                # Carrega configuração salva para pegar o IP
                saved_config = self.wifi_manager.load_config()
                new_ip = saved_config.get('last_ip') if saved_config else None
                
                self.send_json_response(client, {
                    "status": "success" if success else "error",
                    "ip": new_ip,
                    "ssid": config['ssid']
                })
                    
            elif "GET /status" in request:
                self.send_json_response(client, self.wifi_manager.get_status())
                
            elif "GET /data" in request:
                data = self.can_handler.read_message()
                if data:
                    self.can_data.append(data)
                    if len(self.can_data) > 100:  # Mantém apenas últimas 100 mensagens
                        self.can_data.pop(0)
                self.send_json_response(client, {
                    "current": data,
                    "history": self.can_data
                })
                
            else:
                if is_ap_mode:
                    self.send_ap_page(client)
                else:
                    self.send_monitor_page(client)
            
        except Exception as e:
            print(f"Erro ao processar requisição: {e}")
        finally:
            client.close()
    
    def send_json_response(self, client, data):
        response = json.dumps(data)
        client.send('HTTP/1.1 200 OK\n')
        client.send('Content-Type: application/json\n')
        client.send('Connection: close\n\n')
        client.send(response)
    
    def send_ap_page(self, client):
        """Página de configuração do WiFi (modo AP)"""
        html = """<!DOCTYPE html>
        <html>
        <head>
            <title>Configuração WiFi - John Deere Monitor</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { 
                    font-family: Arial; 
                    margin: 0;
                    padding: 20px;
                    background: #367C2B;
                    color: white;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }
                h1 { 
                    text-align: center;
                    color: #FFDE00;
                }
                .logo {
                    text-align: center;
                    margin-bottom: 20px;
                }
                .wifi-form {
                    max-width: 400px;
                    margin: 0 auto;
                }
                select, input {
                    width: 100%;
                    padding: 12px;
                    margin: 8px 0;
                    border: none;
                    border-radius: 5px;
                    background: white;
                    box-sizing: border-box;
                    font-size: 16px;
                }
                .btn {
                    background: #FFDE00;
                    color: #367C2B;
                    padding: 12px 20px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    width: 100%;
                    font-weight: bold;
                    font-size: 16px;
                    margin-top: 15px;
                }
                .btn:hover {
                    background: #FFE534;
                }
                #status {
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 5px;
                    display: none;
                    text-align: center;
                    line-height: 1.5;
                }
                .success { 
                    background: #4CAF50;
                    color: white;
                }
                .error { 
                    background: #f44336;
                    color: white;
                }
                .pending {
                    background: #FFC107;
                    color: #333;
                }
                small {
                    font-size: 0.85em;
                    opacity: 0.9;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="logo">
                    <h1>John Deere Monitor</h1>
                    <p>Configuração de Rede WiFi</p>
                </div>
                
                <div class="wifi-form">
                    <select id="ssid">
                        <option value="">Buscando redes...</option>
                    </select>
                    <input type="password" id="password" placeholder="Senha da rede">
                    <button class="btn" onclick="connectWifi()">Conectar</button>
                    <div id="status"></div>
                </div>
            </div>

            <script>
                let statusElement;
                
                window.onload = function() {
                    statusElement = document.getElementById('status');
                    // Busca redes disponíveis
                    updateNetworks();
                    // Verifica status atual
                    checkCurrentStatus();
                }

                function updateNetworks() {
                    fetch('/scan')
                        .then(response => response.json())
                        .then(data => {
                            const select = document.getElementById('ssid');
                            select.innerHTML = '';
                            data.networks.forEach(net => {
                                const option = document.createElement('option');
                                option.value = option.text = net;
                                select.add(option);
                            });
                        })
                        .catch(error => showStatus('Erro ao buscar redes', false));
                }

                function checkCurrentStatus() {
                    fetch('/status')
                        .then(response => response.json())
                        .then(status => {
                            if (status.sta_connected) {
                                showStatus(`Conectado à rede WiFi<br>IP Local: ${status.sta_ip}`, true);
                            }
                        });
                }

                function connectWifi() {
                    const ssid = document.getElementById('ssid').value;
                    const password = document.getElementById('password').value;
                    
                    if (!ssid || !password) {
                        showStatus('Preencha todos os campos', false);
                        return;
                    }

                    showStatus(`
                        Conectando à rede: ${ssid}<br>
                        Por favor, aguarde...
                    `, 'pending');
                    
                    fetch('/connect', {
                        method: 'POST',
                        body: JSON.stringify({ssid, password})
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            showStatus(`
                                Conexão em andamento...<br>
                                Aguarde alguns segundos e verifique<br>
                                o novo dispositivo adicionado à sua rede local
                            `, 'pending');
                        } else {
                            showStatus(`
                                Falha na conexão<br>
                                Verifique a senha e tente novamente
                            `, false);
                        }
                    })
                    .catch(() => {
                        showStatus(`
                            Conexão em andamento...<br>
                            Aguarde alguns segundos e verifique<br>
                            o novo dispositivo adicionado à sua rede local
                        `, 'pending');
                    });
                }

                function showStatus(message, type) {
                    if (!statusElement) return;
                    
                    statusElement.innerHTML = message;
                    statusElement.className = '';
                    statusElement.style.display = 'block';
                    
                    if (type === true) {
                        statusElement.classList.add('success');
                    } else if (type === false) {
                        statusElement.classList.add('error');
                    } else if (type === 'pending') {
                        statusElement.classList.add('pending');
                    }
                }
            </script>
        </body>
        </html>
        """
        client.send('HTTP/1.1 200 OK\n')
        client.send('Content-Type: text/html; charset=utf-8\n')
        client.send('Connection: close\n\n')
        client.send(html)
    
    def send_monitor_page(self, client):
        """Página de monitoramento CAN (modo Station)"""
        html = """<!DOCTYPE html>
        <html>
        <head>
            <title>Monitor CAN Bus - John Deere</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                body { 
                    font-family: Arial; 
                    margin: 0;
                    padding: 20px;
                    background: #367C2B;
                    color: white;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }
                .header {
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 1px solid rgba(255,255,255,0.2);
                }
                h1 { 
                    color: #FFDE00;
                    margin: 0;
                    font-size: 2.2em;
                }
                .status-bar {
                    background: rgba(255,255,255,0.15);
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    text-align: center;
                    font-size: 1.1em;
                }
                .data-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .data-card {
                    background: rgba(255,255,255,0.1);
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid rgba(255,255,255,0.2);
                    transition: all 0.3s ease;
                }
                .data-card:hover {
                    transform: translateY(-5px);
                    background: rgba(255,255,255,0.15);
                }
                .data-card h3 {
                    color: #FFDE00;
                    margin: 0 0 15px 0;
                    font-size: 1.3em;
                }
                .value { 
                    font-size: 28px;
                    color: white;
                    font-weight: bold;
                    text-align: center;
                    font-family: monospace;
                }
                .data-history {
                    background: rgba(0,0,0,0.2);
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 20px;
                    height: 300px;
                    overflow-y: auto;
                }
                .data-history h2 {
                    color: #FFDE00;
                    margin: 0 0 15px 0;
                }
                .history-item {
                    background: rgba(255,255,255,0.1);
                    padding: 10px;
                    margin: 5px 0;
                    border-radius: 5px;
                    font-family: monospace;
                }
                .history-item:hover {
                    background: rgba(255,255,255,0.15);
                }
                .connected { color: #4CAF50; }
                .disconnected { color: #f44336; }
                
                /* Scrollbar personalizada */
                ::-webkit-scrollbar {
                    width: 10px;
                }
                ::-webkit-scrollbar-track {
                    background: rgba(255,255,255,0.1);
                    border-radius: 5px;
                }
                ::-webkit-scrollbar-thumb {
                    background: #FFDE00;
                    border-radius: 5px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Monitor CAN Bus John Deere</h1>
                    <p>Sistema de Monitoramento de Implementos Agrícolas</p>
                </div>
                
                <div class="status-bar" id="status-bar">
                    Verificando conexão...
                </div>
                
                <div class="data-grid" id="data-grid">
                    <!-- Dados dinâmicos serão inseridos aqui -->
                </div>
                
                <div class="data-history">
                    <h2>Histórico de Mensagens</h2>
                    <div id="data-history">
                        <!-- Histórico será inserido aqui -->
                    </div>
                </div>
            </div>

            <script>
                function updateStatus() {
                    fetch('/status')
                        .then(response => response.json())
                        .then(status => {
                            const statusBar = document.getElementById('status-bar');
                            const isConnected = status.sta_connected;
                            statusBar.innerHTML = `
                                Status da Conexão: 
                                <span class="${isConnected ? 'connected' : 'disconnected'}">
                                    ${isConnected ? 'Conectado' : 'Desconectado'}
                                </span> |
                                IP: ${status.sta_ip || 'N/A'}
                            `;
                        });
                }
                
                function updateData() {
                    fetch('/data')
                        .then(response => response.json())
                        .then(data => {
                            if (data.current) {
                                updateDataGrid(data.current);
                                updateHistory(data.history);
                            }
                        });
                }
                
                function updateDataGrid(data) {
                    const grid = document.getElementById('data-grid');
                    grid.innerHTML = `
                        <div class="data-card">
                            <h3>PGN (Parameter Group Number)</h3>
                            <div class="value">${data.pgn}</div>
                        </div>
                        <div class="data-card">
                            <h3>Dados Recebidos</h3>
                            <div class="value">${data.data.map(x => x.toString(16).padStart(2, '0')).join(' ')}</div>
                        </div>
                        <div class="data-card">
                            <h3>Origem</h3>
                            <div class="value">${data.source}</div>
                        </div>
                        <div class="data-card">
                            <h3>Prioridade</h3>
                            <div class="value">${data.priority}</div>
                        </div>
                    `;
                }
                
                function updateHistory(history) {
                    const historyDiv = document.getElementById('data-history');
                    historyDiv.innerHTML = history.map(msg => `
                        <div class="history-item">
                            [${new Date(msg.timestamp).toLocaleTimeString('pt-BR')}] 
                            PGN: ${msg.pgn} | 
                            Origem: ${msg.source} | 
                            Dados: ${msg.data.map(x => x.toString(16).padStart(2, '0')).join(' ')}
                        </div>
                    `).join('');
                    historyDiv.scrollTop = historyDiv.scrollHeight;
                }
                
                // Atualiza status a cada 5 segundos
                setInterval(updateStatus, 5000);
                // Atualiza dados CAN a cada 1 segundo
                setInterval(updateData, 1000);
                
                // Primeira atualização
                updateStatus();
                updateData();
            </script>
        </body>
        </html>
        """
        client.send('HTTP/1.1 200 OK\n')
        client.send('Content-Type: text/html; charset=utf-8\n')
        client.send('Connection: close\n\n')
        client.send(html) 