# ========== src/config.py ==========
"""
TAC - Configuration Module
Configurações da aplicação
Adaptado para GTK 3 e padrões do BigLinux
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

class TacConfig:
    """Classe para gerenciar configurações da aplicação"""
    
    def __init__(self):
        self._setup_directories()
        self._load_defaults()
    
    def _setup_directories(self):
        """Configura os diretórios da aplicação seguindo padrões XDG"""
        # Diretório principal de dados
        self.DATA_DIR = Path.home() / ".local" / "share" / "tac"
        
        # Diretório de configurações
        self.CONFIG_DIR = Path.home() / ".config" / "tac"
        
        # Diretório de cache
        self.CACHE_DIR = Path.home() / ".cache" / "tac"
        
        # Criar diretórios se não existirem
        for directory in [self.DATA_DIR, self.CONFIG_DIR, self.CACHE_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_defaults(self):
        """Carrega configurações padrão"""
        self.defaults = {
            # Interface
            'window_width': 1024,
            'window_height': 768,
            'window_maximized': False,
            
            # Editor
            'font_family': 'Liberation Sans',
            'font_size': 12,
            'line_spacing': 1.5,
            'show_line_numbers': True,
            'word_wrap': True,
            'highlight_current_line': True,
            
            # Formatação
            'default_paragraph_indent': 0.0,
            'quote_indent': 4.0,
            'page_margins': {
                'top': 2.5,
                'bottom': 2.5,
                'left': 3.0,
                'right': 3.0
            },
            
            # Idioma
            'language': 'pt_BR',
            
            # Comportamento
            'auto_save': True,
            'auto_save_interval': 300,  # 5 minutos
            'backup_files': True,
            'recent_files_limit': 10,
            
            # Tema (para GTK 3)
            'use_dark_theme': False,
            'theme_name': 'Adwaita'
        }
    
    def get(self, key: str, default=None):
        """Obtém valor de configuração"""
        return self.defaults.get(key, default)
    
    def set(self, key: str, value: Any):
        """Define valor de configuração"""
        self.defaults[key] = value
    
    @property
    def config_file(self):
        """Caminho do arquivo de configuração"""
        return self.CONFIG_DIR / "tac.conf"
    
    def save_config(self):
        """Salva configurações em arquivo"""
        try:
            import json
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.defaults, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
    
    def load_config(self):
        """Carrega configurações do arquivo"""
        try:
            if self.config_file.exists():
                import json
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self.defaults.update(saved_config)
        except Exception as e:
            print(f"Erro ao carregar configurações: {e}")

# Instância global de configuração
config = TacConfig()

# Compatibilidade com código antigo
DATA_DIR = config.DATA_DIR
CONFIG_DIR = config.CONFIG_DIR
CACHE_DIR = config.CACHE_DIR
