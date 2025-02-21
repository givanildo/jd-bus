# Monitor CAN Bus John Deere

Sistema de monitoramento de implementos agrícolas John Deere via CAN Bus utilizando ESP32 e protocolo J1939.

## Estrutura do Projeto

```
.
├── esp32_code/           # Código para o ESP32
│   ├── boot.py          # Configuração inicial do ESP32
│   └── main.py          # Código principal do ESP32
├── web_app/             # Aplicação web Streamlit
│   ├── app.py           # Aplicação principal
│   └── requirements.txt # Dependências Python
└── README.md            # Este arquivo
```

## Requisitos de Hardware

- ESP32
- Módulo MCP2515 CAN Bus
- Conexões físicas:
  - ESP32 -> MCP2515:
    - GPIO5 -> CS
    - GPIO18 -> SCK
    - GPIO19 -> MISO
    - GPIO23 -> MOSI
    - 3.3V -> VCC
    - GND -> GND

## Configuração do Ambiente

### 1. ESP32

1. Instale o Thonny IDE:
   - Baixe em: https://thonny.org/

2. Instale o MicroPython no ESP32:
   - Baixe o firmware em: https://micropython.org/download/esp32/
   - Use o Thonny para instalar o firmware

3. Carregue os arquivos do ESP32:
   - Copie `boot.py` e `main.py` para o ESP32 usando Thonny

### 2. Aplicação Web

1. Crie um ambiente virtual Python:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\\Scripts\\activate   # Windows
```

2. Instale as dependências:
```bash
cd web_app
pip install -r requirements.txt
```

3. Execute a aplicação:
```bash
streamlit run app.py
```

## Uso

1. Conecte o ESP32 ao implemento agrícola via CAN Bus

2. Ao ligar, o ESP32 criará um ponto de acesso WiFi:
   - SSID: JohnDeere_Monitor
   - Senha: 12345678

3. Conecte-se ao AP e acesse o portal captivo:
   - Abra o navegador
   - Selecione sua rede WiFi
   - Digite a senha
   - O ESP32 se conectará à rede

4. Execute a aplicação web Streamlit:
   - Insira o IP do ESP32
   - Visualize os dados em tempo real

## Funcionalidades

- Monitoramento em tempo real de:
  - Velocidade do Motor (RPM)
  - Temperatura do Líquido de Arrefecimento
  - Pressão do Óleo
  - Nível de Combustível
  - E outros parâmetros J1939

- Gráficos e gauges interativos
- Filtragem de parâmetros
- Histórico de dados
- Status da conexão

## Contribuição

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## Contato

Givanildo Brunetta - givanildobrunetta@gmail.com

Link do projeto: https://github.com/givanildo/monitor-can-bus-john-deere 