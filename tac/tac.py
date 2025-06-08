# ========== tac.py ==========
#!/usr/bin/env python3
"""
TAC - Text Analysis and Creation
Ponto de entrada principal da aplicação
Adaptado para GTK 3 e BigLinux/Cinnamon
"""

import sys
import os
from pathlib import Path

def main():
    """Função principal de inicialização"""
    # Adiciona o diretório src ao PYTHONPATH
    current_dir = Path(__file__).parent.resolve()
    src_dir = current_dir / "src"
    
    # Verifica se o diretório src existe
    if not src_dir.exists():
        print(f"Erro: Diretório 'src' não encontrado em {current_dir}")
        print("Estrutura esperada:")
        print("  tac/")
        print("  ├── tac.py")
        print("  └── src/")
        print("      ├── main.py")
        print("      ├── config.py")
        print("      └── ...")
        return 1
    
    # Adiciona src ao path se ainda não estiver
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    try:
        # Importa e executa o main
        from main import main as tac_main
        return tac_main(sys.argv)
        
    except ImportError as e:
        print(f"Erro de importação: {e}")
        print(f"Diretório atual: {current_dir}")
        print(f"Diretório src: {src_dir}")
        
        # Lista arquivos disponíveis para debug
        if src_dir.exists():
            py_files = list(src_dir.glob('*.py'))
            print(f"Arquivos Python encontrados: {[f.name for f in py_files]}")
        else:
            print("Diretório src não existe")
        return 1
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())


# ========== src/main.py ==========
"""
TAC - Main Application Module
Módulo principal com configuração de traduções e inicialização
Adaptado para GTK 3 e ambiente BigLinux/Cinnamon
"""

import gettext
import locale
import sys
import os
from pathlib import Path

def setup_translations():
    """Configura o sistema de traduções"""
    try:
        # Configurar caminhos absolutos
        base_dir = Path(__file__).resolve().parent.parent
        locale_dir = base_dir / "po"
        
        print(f"Configurando traduções...")
        print(f"Diretório base: {base_dir}")
        print(f"Diretório de locales: {locale_dir}")
        
        # Definir domínio de tradução
        domain = 'tac'
        
        if locale_dir.exists():
            # Configurar gettext
            locale.bindtextdomain(domain, str(locale_dir))
            gettext.bindtextdomain(domain, str(locale_dir))
            gettext.textdomain(domain)
            
            # Tentar configurar locale do sistema
            try:
                locale.setlocale(locale.LC_ALL, '')
            except locale.Error:
                print("Aviso: Não foi possível configurar locale do sistema")
            
            # Carregar tradução para português brasileiro
            try:
                lang = gettext.translation(
                    domain, 
                    localedir=str(locale_dir), 
                    languages=['pt_BR', 'pt', 'en'], 
                    fallback=True
                )
                lang.install()
                print("Traduções carregadas com sucesso")
                return True
            except Exception as e:
                print(f"Erro ao carregar traduções específicas: {e}")
                
        # Fallback - usar gettext padrão
        import builtins
        builtins.__dict__['_'] = gettext.gettext
        print("Usando traduções padrão (fallback)")
        return False
        
    except Exception as e:
        print(f"Erro na configuração de traduções: {e}")
        # Configurar fallback básico
        import builtins
        builtins.__dict__['_'] = lambda x: x  # Passthrough simples
        return False

def check_gtk_availability():
    """Verifica se GTK 3 está disponível"""
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
        
        # Verifica versão do GTK
        gtk_version = f"{Gtk.get_major_version()}.{Gtk.get_minor_version()}.{Gtk.get_micro_version()}"
        print(f"GTK versão detectada: {gtk_version}")
        
        if Gtk.get_major_version() < 3:
            print("Erro: É necessário GTK 3.0 ou superior")
            return False
            
        return True
        
    except ImportError as e:
        print(f"Erro: GTK 3 não está disponível: {e}")
        print("No BigLinux, instale com: sudo pacman -S gtk3 python-gobject")
        return False
    except Exception as e:
        print(f"Erro ao verificar GTK: {e}")
        return False

def main(args):
    """Função principal da aplicação"""
    print("=== Iniciando TAC - Text Analysis and Creation ===")
    print(f"Python: {sys.version}")
    print(f"Plataforma: {sys.platform}")
    
    try:
        # 1. Configurar traduções
        setup_translations()
        
        # 2. Verificar disponibilidade do GTK
        if not check_gtk_availability():
            return 1
        
        # 3. Importar e inicializar aplicação
        print("Importando módulos da aplicação...")
        try:
            from application import TacApplication
        except ImportError as e:
            print(f"Erro: Não foi possível importar TacApplication: {e}")
            print("Verifique se o arquivo 'application.py' existe no diretório src/")
            return 1
        
        # 4. Criar e executar aplicação
        print("Criando instância da aplicação...")
        app = TacApplication()
        
        print("Executando aplicação TAC...")
        result = app.run(args)
        
        print("Aplicação finalizada.")
        return result
        
    except KeyboardInterrupt:
        print("\nAplicação interrompida pelo usuário.")
        return 0
    except Exception as e:
        print(f"Erro crítico durante inicialização: {e}")
        import traceback
        traceback.print_exc()
        return 1
