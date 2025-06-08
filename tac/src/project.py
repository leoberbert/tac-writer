# ========== src/project.py ==========
"""
TAC - Project Management Module
Gerenciamento de projetos e documentos
Adaptado para GTK 3 com melhor tratamento de erros e funcionalidades
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
try:
    from .config import config
except ImportError:
    # Fallback para quando executado como script independente
    from config import config

class TacProject:
    """Representa um projeto TAC"""
    
    def __init__(self, name: str, project_id: str = None):
        self.id = project_id or str(uuid.uuid4())
        self.name = name
        self.created_at = datetime.now().isoformat()
        self.modified_at = self.created_at
        self.paragraphs = []
        self.metadata = {
            'author': '',
            'description': '',
            'tags': [],
            'version': '1.0'
        }
    
    def add_paragraph(self, ptype: str, content: str = "", formatting: Dict[str, Any] = None):
        """Adiciona um parágrafo ao projeto"""
        if formatting is None:
            formatting = self._default_formatting()
        
        paragraph = {
            'id': str(uuid.uuid4()),
            'type': ptype,
            'content': content,
            'formatting': formatting,
            'created_at': datetime.now().isoformat(),
            'order': len(self.paragraphs)
        }
        
        self.paragraphs.append(paragraph)
        self._update_modified_time()
        return paragraph['id']
    
    def remove_paragraph(self, paragraph_id: str) -> bool:
        """Remove um parágrafo pelo ID"""
        original_count = len(self.paragraphs)
        self.paragraphs = [p for p in self.paragraphs if p['id'] != paragraph_id]
        
        if len(self.paragraphs) < original_count:
            self._reorder_paragraphs()
            self._update_modified_time()
            return True
        return False
    
    def update_paragraph(self, paragraph_id: str, content: str = None, formatting: Dict[str, Any] = None) -> bool:
        """Atualiza um parágrafo"""
        for paragraph in self.paragraphs:
            if paragraph['id'] == paragraph_id:
                if content is not None:
                    paragraph['content'] = content
                if formatting is not None:
                    paragraph['formatting'].update(formatting)
                paragraph['modified_at'] = datetime.now().isoformat()
                self._update_modified_time()
                return True
        return False
    
    def reorder_paragraph(self, paragraph_id: str, new_position: int) -> bool:
        """Reordena um parágrafo"""
        paragraph = None
        for i, p in enumerate(self.paragraphs):
            if p['id'] == paragraph_id:
                paragraph = self.paragraphs.pop(i)
                break
        
        if paragraph:
            new_position = max(0, min(new_position, len(self.paragraphs)))
            self.paragraphs.insert(new_position, paragraph)
            self._reorder_paragraphs()
            self._update_modified_time()
            return True
        return False
    
    def get_paragraph(self, paragraph_id: str) -> Optional[Dict[str, Any]]:
        """Obtém um parágrafo pelo ID"""
        for paragraph in self.paragraphs:
            if paragraph['id'] == paragraph_id:
                return paragraph.copy()
        return None
    
    def get_word_count(self) -> int:
        """Conta palavras no projeto"""
        total_words = 0
        for paragraph in self.paragraphs:
            content = paragraph.get('content', '')
            words = content.split()
            total_words += len(words)
        return total_words
    
    def get_character_count(self, include_spaces: bool = True) -> int:
        """Conta caracteres no projeto"""
        total_chars = 0
        for paragraph in self.paragraphs:
            content = paragraph.get('content', '')
            if include_spaces:
                total_chars += len(content)
            else:
                total_chars += len(content.replace(' ', ''))
        return total_chars
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Exporta projeto para dicionário"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'metadata': self.metadata,
            'paragraphs': self.paragraphs,
            'statistics': {
                'word_count': self.get_word_count(),
                'character_count': self.get_character_count(),
                'paragraph_count': len(self.paragraphs)
            }
        }
    
    def _default_formatting(self) -> Dict[str, Any]:
        """Retorna formatação padrão"""
        return {
            'font_family': config.get('font_family', 'Liberation Sans'),
            'font_size': config.get('font_size', 12),
            'line_spacing': config.get('line_spacing', 1.5),
            'first_indent': config.get('default_paragraph_indent', 0.0),
            'quote_indent': config.get('quote_indent', 4.0),
            'alignment': 'left',
            'bold': False,
            'italic': False,
            'underline': False
        }
    
    def _reorder_paragraphs(self):
        """Reordena os números de ordem dos parágrafos"""
        for i, paragraph in enumerate(self.paragraphs):
            paragraph['order'] = i
    
    def _update_modified_time(self):
        """Atualiza timestamp de modificação"""
        self.modified_at = datetime.now().isoformat()

class TacProjectManager:
    """Gerenciador de projetos TAC"""
    
    def __init__(self):
        # Garantir que o diretório existe
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.projects_dir = config.DATA_DIR / "projects"
        self.projects_dir.mkdir(exist_ok=True)
        
        # Cache de projetos
        self._project_cache = {}
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """Lista todos os projetos disponíveis"""
        projects = []
        
        try:
            for file_path in self.projects_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # Informações básicas do projeto
                    project_info = {
                        'id': data.get('id', file_path.stem),
                        'name': data.get('name', file_path.stem),
                        'created_at': data.get('created_at', ''),
                        'modified_at': data.get('modified_at', ''),
                        'file_path': str(file_path),
                        'word_count': data.get('statistics', {}).get('word_count', 0),
                        'paragraph_count': len(data.get('paragraphs', []))
                    }
                    projects.append(project_info)
                    
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"Erro ao processar projeto {file_path.name}: {e}")
                except Exception as e:
                    print(f"Erro inesperado ao carregar {file_path.name}: {e}")
        
        except Exception as e:
            print(f"Erro ao listar projetos: {e}")
        
        # Ordenar por data de modificação (mais recente primeiro)
        projects.sort(key=lambda x: x.get('modified_at', ''), reverse=True)
        return projects
    
    def create_project(self, name: str, author: str = "", description: str = "") -> TacProject:
        """Cria um novo projeto"""
        if not name.strip():
            raise ValueError("Nome do projeto não pode estar vazio")
        
        project = TacProject(name.strip())
        project.metadata.update({
            'author': author.strip(),
            'description': description.strip()
        })
        
        # Salvar imediatamente
        self.save_project(project)
        
        # Adicionar ao cache
        self._project_cache[project.id] = project
        
        return project
    
    def load_project(self, project_identifier: str) -> Optional[TacProject]:
        """Carrega um projeto por ID ou nome"""
        # Verificar cache primeiro
        if project_identifier in self._project_cache:
            return self._project_cache[project_identifier]
        
        try:
            # Tentar carregar por ID
            file_path = self.projects_dir / f"{project_identifier}.json"
            if not file_path.exists():
                # Procurar por nome
                for file_path in self.projects_dir.glob("*.json"):
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if data.get('name') == project_identifier:
                            break
                    except:
                        continue
                else:
                    return None
            
            # Carregar projeto
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            project = TacProject(
                name=data['name'],
                project_id=data.get('id')
            )
            
            # Restaurar dados
            project.created_at = data.get('created_at', project.created_at)
            project.modified_at = data.get('modified_at', project.modified_at)
            project.paragraphs = data.get('paragraphs', [])
            project.metadata = data.get('metadata', project.metadata)
            
            # Adicionar ao cache
            self._project_cache[project.id] = project
            
            return project
            
        except Exception as e:
            print(f"Erro ao carregar projeto '{project_identifier}': {e}")
            return None
    
    def save_project(self, project: TacProject) -> bool:
        """Salva um projeto"""
        try:
            file_path = self.projects_dir / f"{project.id}.json"
            data = project.export_to_dict()
            
            # Criar backup se arquivo já existe
            if file_path.exists() and config.get('backup_files', True):
                backup_path = file_path.with_suffix('.json.bak')
                file_path.replace(backup_path)
            
            # Salvar projeto
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Atualizar cache
            self._project_cache[project.id] = project
            
            return True
            
        except Exception as e:
            print(f"Erro ao salvar projeto '{project.name}': {e}")
            return False
    
    def delete_project(self, project_identifier: str) -> bool:
        """Deleta um projeto"""
        try:
            # Carregar projeto para obter ID correto
            project = self.load_project(project_identifier)
            if not project:
                return False
            
            file_path = self.projects_dir / f"{project.id}.json"
            
            if file_path.exists():
                # Mover para lixeira ao invés de deletar permanentemente
                trash_dir = config.DATA_DIR / "trash"
                trash_dir.mkdir(exist_ok=True)
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                trash_path = trash_dir / f"{project.id}_{timestamp}.json"
                
                file_path.replace(trash_path)
                
                # Remover do cache
                if project.id in self._project_cache:
                    del self._project_cache[project.id]
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Erro ao deletar projeto: {e}")
            return False
    
    def duplicate_project(self, project_identifier: str, new_name: str) -> Optional[TacProject]:
        """Duplica um projeto"""
        try:
            original = self.load_project(project_identifier)
            if not original:
                return None
            
            # Criar novo projeto
            duplicate = TacProject(new_name)
            duplicate.paragraphs = [p.copy() for p in original.paragraphs]
            duplicate.metadata = original.metadata.copy()
            duplicate.metadata['description'] = f"Cópia de: {original.name}"
            
            # Gerar novos IDs para os parágrafos
            for paragraph in duplicate.paragraphs:
                paragraph['id'] = str(uuid.uuid4())
                paragraph['created_at'] = datetime.now().isoformat()
            
            # Salvar
            if self.save_project(duplicate):
                return duplicate
            
            return None
            
        except Exception as e:
            print(f"Erro ao duplicar projeto: {e}")
            return None
