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

def configure_git():
    """Configura credenciais do Git"""
    try:
        subprocess.run(["git", "config", "--global", "user.name", "givanildo"], check=True)
        subprocess.run(["git", "config", "--global", "user.email", "givanildobrunetta@gmail.com"], check=True)
        return True
    except Exception as e:
        print(f"Erro ao configurar Git: {e}")
        return False

def prepare_repo():
    """Prepara repositório para publicação"""
    try:
        # Atualiza .gitignore
        with open('.gitignore', 'w') as f:
            f.write("""
# Python
__pycache__/
*.py[cod]
*$py.class
venv/
.env

# IDE
.vscode/
.idea/

# Outros
.DS_Store
            """)
        return True
    except Exception as e:
        print(f"Erro ao preparar repositório: {e}")
        return False

def publish_repo():
    """Publica o repositório no GitHub"""
    try:
        if not check_git_installed():
            return False
            
        print("\nPublicando projeto no GitHub...")
        
        # Configura Git
        configure_git()
        
        # Prepara repositório
        prepare_repo()
        
        # Verifica se já é um repositório git
        is_git_repo = os.path.exists(".git")
        if not is_git_repo:
            # Inicializa repositório
            subprocess.run(["git", "init"], check=True)
        
        # Adiciona arquivos
        subprocess.run(["git", "add", "."], check=True)
        
        # Commit
        subprocess.run([
            "git", "commit", "-m", "Atualização do Monitor CAN Bus John Deere"
        ], check=True)
        
        # Configura branch principal
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        
        # Remove remote origin se existir
        try:
            subprocess.run(["git", "remote", "remove", "origin"], check=True)
        except:
            pass
        
        # Adiciona remote
        subprocess.run([
            "git", "remote", "add", "origin", 
            "https://github.com/givanildo/jd-bus.git"
        ], check=True)
        
        # Push
        print("\nEnviando para GitHub...")
        subprocess.run(["git", "push", "-f", "origin", "main"], check=True)
        
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