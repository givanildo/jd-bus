import sys
import subprocess
import pkg_resources
import time
import os
import signal

def check_python_version():
    """Verifica versão do Python"""
    if sys.version_info < (3, 8):
        print("Erro: Python 3.8 ou superior é necessário")
        sys.exit(1)

def get_required_packages():
    """Lê requirements.txt e retorna lista de pacotes"""
    req_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                           'web_app', 'requirements.txt')
    
    required = []
    with open(req_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                required.append(line)
    return required

def get_installed_packages():
    """Retorna dicionário de pacotes instalados"""
    installed = {}
    for pkg in pkg_resources.working_set:
        installed[pkg.key] = pkg.version
    return installed

def install_missing_packages(required):
    """Instala pacotes faltantes"""
    print("\nVerificando dependências...")
    
    installed = get_installed_packages()
    to_install = []
    
    for req in required:
        pkg_name = req.split('==')[0]
        required_version = req.split('==')[1] if '==' in req else None
        
        if pkg_name.lower() not in installed:
            to_install.append(req)
        elif required_version and installed[pkg_name.lower()] != required_version:
            print(f"Atualizando {pkg_name} para versão {required_version}")
            to_install.append(req)
    
    if to_install:
        print("\nInstalando pacotes necessários...")
        for pkg in to_install:
            print(f"Instalando {pkg}")
            try:
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", pkg
                ])
            except subprocess.CalledProcessError as e:
                print(f"Erro ao instalar {pkg}: {e}")
                sys.exit(1)
        print("\nTodos os pacotes foram instalados!")
    else:
        print("Todas as dependências já estão instaladas!")

def install_requirements():
    """Instala as dependências necessárias"""
    try:
        print("\nVerificando e instalando dependências...")
        requirements_path = os.path.join('web_app', 'requirements.txt')
        
        subprocess.check_call([
            sys.executable, 
            "-m", 
            "pip", 
            "install", 
            "-r", 
            requirements_path
        ])
        print("Dependências instaladas com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao instalar dependências: {e}")
        return False

def run_streamlit():
    """Executa a aplicação Streamlit"""
    try:
        print("\nIniciando aplicação web...")
        app_path = os.path.join('web_app', 'app.py')
        
        if not os.path.exists(app_path):
            print(f"Erro: Arquivo {app_path} não encontrado!")
            return False
            
        print("\nPara parar a aplicação, pressione Ctrl+C")
        
        # Cria processo do Streamlit
        process = subprocess.Popen([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            app_path,
            "--server.address", "localhost",
            "--server.port", "8501"
        ])
        
        def signal_handler(signum, frame):
            print("\nEncerrando aplicação...")
            process.terminate()
            process.wait(timeout=5)
            print("Aplicação encerrada!")
            sys.exit(0)
            
        # Registra handler para Ctrl+C
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Aguarda processo
        process.wait()
        
        return True
        
    except KeyboardInterrupt:
        print("\nEncerrando aplicação...")
        if 'process' in locals():
            process.terminate()
            process.wait(timeout=5)
        print("Aplicação encerrada!")
        return True
    except Exception as e:
        print(f"Erro ao executar aplicação: {e}")
        return False

def main():
    try:
        print("""
╔════════════════════════════════════════════╗
║     Monitor CAN Bus - John Deere           ║
║     Instalação e Execução                  ║
╚════════════════════════════════════════════╝
        """)
        
        # Instala dependências
        if not install_requirements():
            print("Falha ao instalar dependências. Abortando...")
            return
            
        # Executa aplicação
        run_streamlit()
        
    except KeyboardInterrupt:
        print("\nProcesso interrompido pelo usuário")
    except Exception as e:
        print(f"\nErro inesperado: {e}")
    finally:
        print("\nFinalizado!")

if __name__ == "__main__":
    main() 