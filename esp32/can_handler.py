from machine import SPI, Pin
import time

class MCP2515:
    # Registradores MCP2515
    CNF1 = 0x2A
    CNF2 = 0x29
    CNF3 = 0x28
    CANINTE = 0x2B
    CANINTF = 0x2C
    RXB0CTRL = 0x60
    RXB0SIDH = 0x61
    RXB0D0 = 0x66
    
    def __init__(self, spi_bus=2, cs_pin=5, int_pin=4):
        """Inicializa o MCP2515"""
        self.cs = Pin(cs_pin, Pin.OUT)
        self.cs.value(1)  # CS é ativo baixo
        
        self.int_pin = Pin(int_pin, Pin.IN)
        
        # Configurar SPI
        self.spi = SPI(spi_bus, baudrate=10000000, polarity=0, phase=0)
        
        # Inicializar MCP2515
        self.reset()
        time.sleep_ms(100)
        
        # Configurar para 250kbps
        self.set_baud_rate()
        
        # Configurar filtros para J1939
        self.setup_filters()
        
        # Configurar modo normal
        self.set_mode('normal')
        
    def reset(self):
        """Reset do MCP2515"""
        self.cs.value(0)
        self.spi.write(bytes([0xC0]))  # RESET command
        self.cs.value(1)
        
    def set_mode(self, mode):
        """Define o modo de operação"""
        modes = {
            'normal': 0x00,
            'sleep': 0x20,
            'loopback': 0x40,
            'listen': 0x60,
            'config': 0x80
        }
        if mode not in modes:
            return
            
        self.write_register(0x0F, modes[mode])  # CANCTRL register
        
    def set_baud_rate(self):
        """Configura baudrate para 250kbps"""
        # Coloca em modo configuração
        self.set_mode('config')
        
        # Configurações para 250kbps com clock 8MHz
        self.write_register(self.CNF1, 0x00)
        self.write_register(self.CNF2, 0x90)
        self.write_register(self.CNF3, 0x02)
        
    def setup_filters(self):
        """Configura filtros para J1939"""
        # Aceita todas as mensagens J1939 (PGN)
        self.write_register(self.RXB0CTRL, 0x60)  # Recebe todas as mensagens
        
    def write_register(self, addr, value):
        """Escreve em um registro"""
        self.cs.value(0)
        self.spi.write(bytes([0x02, addr, value]))  # Write command
        self.cs.value(1)
        
    def read_register(self, addr):
        """Lê um registro"""
        self.cs.value(0)
        self.spi.write(bytes([0x03, addr]))  # Read command
        result = self.spi.read(1)
        self.cs.value(1)
        return result[0]
        
    def read_rx_buffer(self):
        """Lê buffer de recepção"""
        self.cs.value(0)
        self.spi.write(bytes([0x90]))  # Read RX buffer command
        data = self.spi.read(13)  # Lê ID + DLC + 8 bytes de dados
        self.cs.value(1)
        return data
        
    def parse_j1939_message(self, buffer):
        """Converte buffer em mensagem J1939"""
        if not buffer or len(buffer) < 13:
            return None
            
        # Extrai ID e PGN
        id_high = buffer[0]
        id_low = buffer[1]
        can_id = (id_high << 8) | id_low
        pgn = (can_id >> 8) & 0x1FFFF
        
        # Extrai dados
        dlc = buffer[4] & 0x0F
        data = list(buffer[5:5+dlc])
        
        return {
            "pgn": f"0x{pgn:04X}",
            "data": data,
            "timestamp": time.ticks_ms(),
            "source": can_id & 0xFF,
            "priority": (can_id >> 26) & 0x7
        }
        
    def read_message(self):
        """Lê mensagem CAN se disponível"""
        if self.int_pin.value() == 0:  # Mensagem disponível
            buffer = self.read_rx_buffer()
            message = self.parse_j1939_message(buffer)
            
            # Limpa flag de interrupção
            self.write_register(self.CANINTF, 0)
            
            return message
            
        return None 