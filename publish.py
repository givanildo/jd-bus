import os
import subprocess
import sys

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar comando: {e}")
        return False

def main():
    # Configurações do repositório
    repo_name = "monitor-can-bus-john-deere"
    username = "givanildo"
    email = "givanildobrunetta@gmail.com"

    # Verifica se git está instalado
    if not run_command("git --version"):
        print("Git não está instalado. Por favor, instale o Git primeiro.")
        sys.exit(1)

    # Configura git global
    run_command(f'git config --global user.name "{username}"')
    run_command(f'git config --global user.email "{email}"')

    # Inicializa repositório git
    if not os.path.exists(".git"):
        print("Inicializando repositório Git...")
        run_command("git init")

    # Adiciona arquivos
    print("Adicionando arquivos...")
    run_command("git add .")

    # Commit inicial
    print("Realizando commit inicial...")
    run_command('git commit -m "Commit inicial: Monitor CAN Bus John Deere"')

    # Cria repositório no GitHub via API
    print(f"Criando repositório {repo_name} no GitHub...")
    create_repo_cmd = f'''
    curl -X POST https://api.github.com/user/repos \
    -H "Authorization: token YOUR_GITHUB_TOKEN" \
    -d '{{"name":"{repo_name}","description":"Sistema de monitoramento de implementos John Deere via CAN Bus utilizando ESP32 e protocolo J1939","private":false}}'
    '''
    print("IMPORTANTE: Você precisa substituir 'YOUR_GITHUB_TOKEN' no arquivo publish.py pelo seu token do GitHub")
    print("Você pode gerar um token em: https://github.com/settings/tokens")
    
    # Adiciona remote e push
    print("Adicionando remote origin...")
    run_command(f"git remote add origin https://github.com/{username}/{repo_name}.git")
    
    print("Realizando push para o GitHub...")
    run_command("git push -u origin master")

    print("""
Projeto publicado com sucesso!
Próximos passos:
1. Acesse https://github.com/settings/tokens para gerar seu token
2. Substitua 'YOUR_GITHUB_TOKEN' neste arquivo pelo token gerado
3. Execute este script novamente
""")

if __name__ == "__main__":
    main() 