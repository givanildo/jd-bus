class J1939Decoder:
    # Dicionário de PGNs John Deere
    PGN_DICT = {
        0xFEF1: {
            'name': 'Motor',
            'params': {
                'rpm': {'start_byte': 0, 'length': 2, 'resolution': 0.125, 'unit': 'RPM', 'range': [0, 8000]},
                'torque': {'start_byte': 2, 'length': 1, 'resolution': 1, 'unit': '%', 'range': [0, 100]},
                'fuel_rate': {'start_byte': 3, 'length': 2, 'resolution': 0.1, 'unit': 'L/h', 'range': [0, 150]}
            }
        },
        0xF004: {
            'name': 'Implemento',
            'params': {
                'velocidade': {'start_byte': 0, 'length': 2, 'resolution': 0.001, 'unit': 'km/h', 'range': [0, 50]},
                'area_total': {'start_byte': 2, 'length': 4, 'resolution': 0.01, 'unit': 'ha', 'range': [0, 1000]},
                'profundidade': {'start_byte': 6, 'length': 1, 'resolution': 1, 'unit': 'cm', 'range': [0, 100]}
            }
        },
        0xFEE8: {
            'name': 'Fluidos',
            'params': {
                'nivel_combustivel': {'start_byte': 0, 'length': 1, 'resolution': 0.4, 'unit': '%', 'range': [0, 100]},
                'temp_motor': {'start_byte': 1, 'length': 1, 'resolution': 1, 'offset': -40, 'unit': '°C', 'range': [-40, 150]},
                'pressao_oleo': {'start_byte': 2, 'length': 1, 'resolution': 4, 'unit': 'kPa', 'range': [0, 1000]}
            }
        }
    }
    
    @staticmethod
    def decode_message(pgn_hex, data):
        """Decodifica mensagem CAN com base no PGN"""
        pgn = int(pgn_hex, 16)
        if pgn not in J1939Decoder.PGN_DICT:
            return None
            
        pgn_info = J1939Decoder.PGN_DICT[pgn]
        decoded = {'name': pgn_info['name'], 'values': {}}
        
        for param_name, param_info in pgn_info['params'].items():
            start = param_info['start_byte']
            length = param_info['length']
            resolution = param_info['resolution']
            
            # Extrai valor dos bytes
            value = 0
            for i in range(length):
                value |= data[start + i] << (8 * i)
                
            # Aplica resolução e offset
            final_value = value * resolution
            if 'offset' in param_info:
                final_value += param_info['offset']
                
            decoded['values'][param_name] = {
                'value': round(final_value, 2),
                'unit': param_info['unit'],
                'range': param_info['range']
            }
            
        return decoded 