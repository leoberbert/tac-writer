#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import os
from pathlib import Path

def export_to_odt(project, parent_window):
    """Exporta o projeto para formato ODT"""
    dialog = Gtk.FileChooserDialog(
        title=_("Exportar para ODT"),
        parent=parent_window,
        action=Gtk.FileChooserAction.SAVE
    )
    
    dialog.add_buttons(
        _("Cancelar"), Gtk.ResponseType.CANCEL,
        _("Salvar"), Gtk.ResponseType.OK
    )
    
    dialog.set_current_name(f"{project.name}.odt")
    
    # Adicionar filtros
    filter_odt = Gtk.FileFilter()
    filter_odt.set_name("Documentos ODT")
    filter_odt.add_pattern("*.odt")
    dialog.add_filter(filter_odt)
    
    filter_all = Gtk.FileFilter()
    filter_all.set_name("Todos os arquivos")
    filter_all.add_pattern("*")
    dialog.add_filter(filter_all)
    
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
        generate_odt(project, filename)
        
        # Mostrar mensagem de sucesso
        success_dialog = Gtk.MessageDialog(
            parent=parent_window,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            message_format=_("Exportação concluída")
        )
        success_dialog.format_secondary_text(
            _("Arquivo salvo em: {}").format(filename)
        )
        success_dialog.run()
        success_dialog.destroy()
    
    dialog.destroy()

def export_to_html(project, parent_window):
    """Exporta o projeto para formato HTML"""
    dialog = Gtk.FileChooserDialog(
        title=_("Exportar para HTML"),
        parent=parent_window,
        action=Gtk.FileChooserAction.SAVE
    )
    
    dialog.add_buttons(
        _("Cancelar"), Gtk.ResponseType.CANCEL,
        _("Salvar"), Gtk.ResponseType.OK
    )
    
    dialog.set_current_name(f"{project.name}.html")
    
    # Adicionar filtros
    filter_html = Gtk.FileFilter()
    filter_html.set_name("Documentos HTML")
    filter_html.add_pattern("*.html")
    filter_html.add_pattern("*.htm")
    dialog.add_filter(filter_html)
    
    filter_all = Gtk.FileFilter()
    filter_all.set_name("Todos os arquivos")
    filter_all.add_pattern("*")
    dialog.add_filter(filter_all)
    
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
        generate_html(project, filename)
        
        # Mostrar mensagem de sucesso
        success_dialog = Gtk.MessageDialog(
            parent=parent_window,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            message_format=_("Exportação concluída")
        )
        success_dialog.format_secondary_text(
            _("Arquivo salvo em: {}").format(filename)
        )
        success_dialog.run()
        success_dialog.destroy()
    
    dialog.destroy()

def export_to_txt(project, parent_window):
    """Exporta o projeto para formato TXT simples"""
    dialog = Gtk.FileChooserDialog(
        title=_("Exportar para TXT"),
        parent=parent_window,
        action=Gtk.FileChooserAction.SAVE
    )
    
    dialog.add_buttons(
        _("Cancelar"), Gtk.ResponseType.CANCEL,
        _("Salvar"), Gtk.ResponseType.OK
    )
    
    dialog.set_current_name(f"{project.name}.txt")
    
    # Adicionar filtros
    filter_txt = Gtk.FileFilter()
    filter_txt.set_name("Arquivos de texto")
    filter_txt.add_pattern("*.txt")
    dialog.add_filter(filter_txt)
    
    filter_all = Gtk.FileFilter()
    filter_all.set_name("Todos os arquivos")
    filter_all.add_pattern("*")
    dialog.add_filter(filter_all)
    
    response = dialog.run()
    if response == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
        generate_txt(project, filename)
        
        # Mostrar mensagem de sucesso
        success_dialog = Gtk.MessageDialog(
            parent=parent_window,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            message_format=_("Exportação concluída")
        )
        success_dialog.format_secondary_text(
            _("Arquivo salvo em: {}").format(filename)
        )
        success_dialog.run()
        success_dialog.destroy()
    
    dialog.destroy()

def generate_odt(project, filename):
    """Gera arquivo ODT (implementação simplificada)"""
    # Implementação básica - para produção, usar python-odf
    try:
        content = generate_odt_content(project)
        
        # Criar estrutura básica ODT
        import zipfile
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Criar estrutura de diretórios ODT
            (temp_path / 'META-INF').mkdir()
            (temp_path / 'Configurations2').mkdir(parents=True)
            
            # Arquivo manifest
            with open(temp_path / 'META-INF' / 'manifest.xml', 'w', encoding='utf-8') as f:
                f.write('''<?xml version="1.0" encoding="UTF-8"?>
<manifest:manifest xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0">
    <manifest:file-entry manifest:full-path="/" manifest:media-type="application/vnd.oasis.opendocument.text"/>
    <manifest:file-entry manifest:full-path="content.xml" manifest:media-type="text/xml"/>
</manifest:manifest>''')
            
            # Conteúdo principal
            with open(temp_path / 'content.xml', 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Criar arquivo ZIP
            with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zf:
                for file_path in temp_path.rglob('*'):
                    if file_path.is_file():
                        arcname = str(file_path.relative_to(temp_path))
                        zf.write(file_path, arcname)
        
    except Exception as e:
        print(f"Erro ao gerar ODT: {e}")
        # Fallback para arquivo XML simples
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(generate_odt_content(project))

def generate_odt_content(project):
    """Gera o conteúdo XML para ODT"""
    content = '''<?xml version="1.0" encoding="UTF-8"?>
<office:document-content 
    xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">
    <office:body>
        <office:text>
'''
    
    for paragraph in project.paragraphs:
        p_type = paragraph.get('type', 'paragraph')
        p_content = paragraph.get('content', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        if p_type == 'citation':
            content += f'            <text:p text:style-name="Citation">{p_content}</text:p>\n'
        else:
            content += f'            <text:p text:style-name="Standard">{p_content}</text:p>\n'
    
    content += '''        </office:text>
    </office:body>
</office:document-content>'''
    
    return content

def generate_html(project, filename):
    """Gera arquivo HTML"""
    html_content = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project.name}</title>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
        }}
        .paragraph {{
            margin-bottom: 1.5em;
            text-align: justify;
            text-indent: 2em;
        }}
        .citation {{
            margin: 2em 0;
            padding: 1em;
            border-left: 4px solid #ccc;
            background-color: #f9f9f9;
            font-style: italic;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 2em;
        }}
    </style>
</head>
<body>
    <h1>{project.name}</h1>
'''
    
    for paragraph in project.paragraphs:
        p_type = paragraph.get('type', 'paragraph')
        p_content = paragraph.get('content', '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        if p_type == 'citation':
            html_content += f'    <div class="citation">{p_content}</div>\n'
        else:
            html_content += f'    <p class="paragraph">{p_content}</p>\n'
    
    html_content += '''</body>
</html>'''
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_txt(project, filename):
    """Gera arquivo TXT simples"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{project.name}\n")
        f.write("=" * len(project.name) + "\n\n")
        
        for i, paragraph in enumerate(project.paragraphs):
            p_type = paragraph.get('type', 'paragraph')
            p_content = paragraph.get('content', '')
            
            if p_type == 'citation':
                f.write(f"[CITAÇÃO {i+1}]\n")
                f.write(f"{p_content}\n\n")
            else:
                f.write(f"{p_content}\n\n")

def show_export_dialog(project, parent_window):
    """Mostra diálogo de opções de exportação"""
    dialog = Gtk.Dialog(
        title=_("Exportar Documento"),
        parent=parent_window,
        flags=Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT
    )
    
    dialog.add_button(_("Cancelar"), Gtk.ResponseType.CANCEL)
    
    content_area = dialog.get_content_area()
    content_area.set_spacing(10)
    content_area.set_margin_left(20)
    content_area.set_margin_right(20)
    content_area.set_margin_top(10)
    content_area.set_margin_bottom(10)
    
    # Título
    title_label = Gtk.Label()
    title_label.set_markup(f"<b>{_('Escolha o formato de exportação:')}</b>")
    title_label.set_halign(Gtk.Align.START)
    content_area.pack_start(title_label, False, False, 0)
    
    # Botões de formato
    button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
    
    odt_btn = Gtk.Button(label=_("Exportar para ODT (LibreOffice)"))
    odt_btn.connect('clicked', lambda x: [dialog.destroy(), export_to_odt(project, parent_window)])
    button_box.pack_start(odt_btn, False, False, 0)
    
    html_btn = Gtk.Button(label=_("Exportar para HTML"))
    html_btn.connect('clicked', lambda x: [dialog.destroy(), export_to_html(project, parent_window)])
    button_box.pack_start(html_btn, False, False, 0)
    
    txt_btn = Gtk.Button(label=_("Exportar para TXT"))
    txt_btn.connect('clicked', lambda x: [dialog.destroy(), export_to_txt(project, parent_window)])
    button_box.pack_start(txt_btn, False, False, 0)
    
    content_area.pack_start(button_box, True, True, 0)
    
    dialog.show_all()
    dialog.run()
