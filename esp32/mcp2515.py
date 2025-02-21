from machine import SPI, Pin
import time

class MCP2515:
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
    
    def reset(self):
        """Reset do MCP2515"""
        self.cs.value(0)
        self.spi.write(bytes([0xC0]))  # RESET command
        self.cs.value(1)
    
    def read_can_message(self):
        """Lê mensagem CAN se disponível"""
        if self.int_pin.value() == 0:  # Mensagem disponível
            # Implementar leitura da mensagem
            pass
        return None 