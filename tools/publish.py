import subprocess
import os
import sys

def check_git_installed():
    """Verifica se o Git está instalado"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except:
        print("Erro: Git não encontrado. Por favor, instale o Git primeiro.")
        return False

def check_repo_exists():
    """Verifica se já existe um repositório git"""
    return os.path.exists(".git")

def configure_git():
    """Configura credenciais do Git"""
    try:
        subprocess.run(["git", "config", "--global", "user.name", "givanildo"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "givanildobrunetta@gmail.com"], check=True)
        return True
    except Exception as e:
        print(f"Erro ao configurar Git: {e}")
        return False

def publish_repo():
    """Publica o repositório no GitHub"""
    try:
        if not check_git_installed():
            return False
            
        print("\nPublicando projeto no GitHub...")
        
        # Configura Git se necessário
        if not check_repo_exists():
            configure_git()
            
            # Inicializa repositório
            subprocess.run(["git", "init"], check=True)
            
        # Adiciona arquivos
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit
        subprocess.run([
            "git", "commit", "-m", "Primeira versão do Monitor CAN Bus John Deere"
        ], check=True)
        
        # Configura branch principal
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        
        # Adiciona remote
        try:
            subprocess.run([
                "git", "remote", "add", "origin", 
                "https://github.com/givanildo/jd-bus.git"
            ], check=True)
        except:
            # Remote já pode existir
            pass
            
        # Push
        print("\nEnviando para GitHub...")
        result = subprocess.run([
            "git", "push", "-u", "origin", "main"
        ], capture_output=True, text=True)
        
        if "Authentication failed" in result.stderr:
            print("\nErro de autenticação. Por favor:")
            print("1. Acesse https://github.com/settings/tokens")
            print("2. Gere um novo token com permissão 'repo'")
            print("3. Use o token como senha ao fazer push")
            return False
            
        print("\nProjeto publicado com sucesso!")
        print("Acesse: https://github.com/givanildo/jd-bus")
        return True
        
    except Exception as e:
        print(f"\nErro ao publicar: {e}")
        return False

def main():
    print("""
╔════════════════════════════════════════════╗
║     Monitor CAN Bus - John Deere           ║
║     Publicação no GitHub                   ║
╚════════════════════════════════════════════╝
    """)
    
    if publish_repo():
        print("\nProcesso finalizado com sucesso!")
    else:
        print("\nFalha na publicação. Verifique os erros acima.")

if __name__ == "__main__":
    main() 