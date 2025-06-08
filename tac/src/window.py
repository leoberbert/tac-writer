import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GObject

# Configurar traduções como fallback
try:
    _ = _
except NameError:
    def _(text):
        return text

class MainWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'MainWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print("Inicializando MainWindow...")
        
        # Inicializar atributos essenciais primeiro
        self.project_manager = None
        self.current_project = None
        
        try:
            self.set_default_size(900, 700)
            self.set_title(_("TAC - Facilitador de Texto Acadêmico"))
            
            # Box principal
            self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.add(self.main_box)
            
            # Header Bar (usando Gtk.HeaderBar do GTK 3)
            self.header_bar = Gtk.HeaderBar()
            self.header_bar.set_show_close_button(True)
            self.header_bar.set_title(_("TAC - Facilitador de Texto Acadêmico"))
            self.set_titlebar(self.header_bar)
            
            # Menu button no header
            menu_button = Gtk.MenuButton()
            menu_button.set_direction(Gtk.ArrowType.DOWN)
            
            # Menu modelo
            menu_model = Gio.Menu()
            menu_model.append(_("Novo Projeto"), "app.new_project")
            menu_model.append(_("Abrir Projeto"), "app.open_project")
            menu_model.append(_("Salvar"), "app.save_project")
            menu_model.append(_("Exportar"), "app.export_project")
            
            menu_button.set_menu_model(menu_model)
            self.header_bar.pack_end(menu_button)
            
            # Botão inicial
            self.start_button = Gtk.Button(
                label=_("COMEÇAR A ESCREVER")
            )
            self.start_button.get_style_context().add_class('suggested-action')
            self.start_button.set_margin_top(20)
            self.start_button.set_margin_bottom(20)
            self.start_button.set_margin_left(20)
            self.start_button.set_margin_right(20)
            self.start_button.connect('clicked', self.on_start_writing)
            self.main_box.pack_start(self.start_button, False, False, 0)
            
            # Gerenciador de projetos - com tratamento de erro específico
            try:
                from project import TacProjectManager
                self.project_manager = TacProjectManager()
                print("TacProjectManager inicializado com sucesso")
            except ImportError as e:
                print(f"Erro ao importar TacProjectManager: {e}")
                self.project_manager = None
            except Exception as e:
                print(f"Erro ao inicializar TacProjectManager: {e}")
                self.project_manager = None
            
            print("MainWindow inicializada com sucesso")
            
        except Exception as e:
            print(f"Erro ao inicializar MainWindow: {e}")
            import traceback
            traceback.print_exc()
            # Garantir que os atributos essenciais existam mesmo com erro
            if not hasattr(self, 'project_manager'):
                self.project_manager = None
            if not hasattr(self, 'current_project'):
                self.current_project = None

    def on_start_writing(self, button):
        print("Botão 'Começar a escrever' clicado")
        # Verificar se project_manager existe
        if self.project_manager is None:
            print("Erro: project_manager não foi inicializado")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=_("Erro: Gerenciador de projetos não foi inicializado corretamente.")
            )
            dialog.run()
            dialog.destroy()
            return
        
        self.show_project_selector()

    def show_project_selector(self):
        print("Mostrando seletor de projeto...")
        # Limpa a janela atual
        for child in self.main_box.get_children():
            if child != self.header_bar:
                self.main_box.remove(child)
        
        # Cria interface de seleção de projeto
        self.project_selector = ProjectSelector(self)
        self.main_box.pack_start(self.project_selector, True, True, 0)
        self.show_all()
    
    def create_new_project(self):
        print("Criando novo projeto...")
        
        # Verificar se project_manager existe
        if self.project_manager is None:
            print("Erro: project_manager não foi inicializado")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=_("Erro: Gerenciador de projetos não foi inicializado.")
            )
            dialog.run()
            dialog.destroy()
            return
        
        dialog = Gtk.Dialog(
            title=_("Novo Projeto"),
            transient_for=self,
            flags=0
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        
        content_area = dialog.get_content_area()
        
        # Entry para nome do projeto
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        box.set_margin_left(10)
        box.set_margin_right(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        
        label = Gtk.Label(_("Nome do projeto:"))
        entry = Gtk.Entry()
        entry.set_text("Novo Projeto")
        
        box.pack_start(label, False, False, 0)
        box.pack_start(entry, False, False, 0)
        content_area.add(box)
        
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            project_name = entry.get_text().strip()
            if project_name:
                try:
                    self.current_project = self.project_manager.create_project(project_name)
                    self.show_editor_interface()
                except Exception as e:
                    print(f"Erro ao criar projeto: {e}")
                    error_dialog = Gtk.MessageDialog(
                        transient_for=self,
                        flags=0,
                        message_type=Gtk.MessageType.ERROR,
                        buttons=Gtk.ButtonsType.OK,
                        text=f"Erro ao criar projeto: {e}"
                    )
                    error_dialog.run()
                    error_dialog.destroy()
        
        dialog.destroy()
    
    def open_project(self, project_name):
        print(f"Abrindo projeto: {project_name}")
        
        # Verificar se project_manager existe
        if self.project_manager is None:
            print("Erro: project_manager não foi inicializado")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=_("Erro: Gerenciador de projetos não foi inicializado.")
            )
            dialog.run()
            dialog.destroy()
            return
        
        try:
            self.current_project = self.project_manager.load_project(project_name)
            self.show_editor_interface()
        except Exception as e:
            print(f"Erro ao abrir projeto {project_name}: {e}")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Erro ao abrir projeto: {e}"
            )
            dialog.run()
            dialog.destroy()
    
    def show_editor_interface(self):
        print("Mostrando interface do editor...")
        
        # Verificar se current_project existe
        if self.current_project is None:
            print("Erro: current_project não foi definido")
            return
        
        # Limpa a janela
        for child in self.main_box.get_children():
            self.main_box.remove(child)
        
        # Cria scroll window para o editor
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        
        # Box do editor
        self.editor_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.editor_box.set_margin_left(10)
        self.editor_box.set_margin_right(10)
        self.editor_box.set_margin_top(10)
        self.editor_box.set_margin_bottom(10)
        
        scrolled.add(self.editor_box)
        self.main_box.pack_start(scrolled, True, True, 0)
        
        # Adiciona parágrafos existentes
        for paragraph in self.current_project.paragraphs:
            try:
                from paragraph import ParagraphEditor
                editor = ParagraphEditor(paragraph)
                self.editor_box.pack_start(editor, False, False, 5)
            except Exception as e:
                print(f"Erro ao criar editor de parágrafo: {e}")
        
        # Toolbar para adicionar parágrafos
        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        toolbar.set_margin_top(10)
        
        add_topic_btn = Gtk.Button(label=_("+ Tópico"))
        add_topic_btn.connect('clicked', lambda x: self.add_paragraph('topic'))
        
        add_arg_btn = Gtk.Button(label=_("+ Argumentação"))
        add_arg_btn.connect('clicked', lambda x: self.add_paragraph('argument'))
        
        add_quote_btn = Gtk.Button(label=_("+ Citação"))
        add_quote_btn.connect('clicked', lambda x: self.add_paragraph('argument_quote'))
        
        add_concl_btn = Gtk.Button(label=_("+ Conclusão"))
        add_concl_btn.connect('clicked', lambda x: self.add_paragraph('conclusion'))
        
        save_btn = Gtk.Button(label=_("Salvar"))
        save_btn.get_style_context().add_class('suggested-action')
        save_btn.connect('clicked', self.on_save_project)
        
        toolbar.pack_start(add_topic_btn, False, False, 0)
        toolbar.pack_start(add_arg_btn, False, False, 0)
        toolbar.pack_start(add_quote_btn, False, False, 0)
        toolbar.pack_start(add_concl_btn, False, False, 0)
        toolbar.pack_end(save_btn, False, False, 0)
        
        self.editor_box.pack_start(toolbar, False, False, 0)
        
        self.show_all()
    
    def add_paragraph(self, ptype):
        print(f"Adicionando parágrafo tipo: {ptype}")
        
        # Verificar se current_project existe
        if self.current_project is None:
            print("Erro: current_project não foi definido")
            return
        
        try:
            self.current_project.add_paragraph(ptype)
            
            # Adiciona o editor do novo parágrafo
            from paragraph import ParagraphEditor
            paragraph = self.current_project.paragraphs[-1]
            editor = ParagraphEditor(paragraph)
            
            # Insere antes do toolbar
            toolbar_index = len(self.editor_box.get_children()) - 1
            self.editor_box.pack_start(editor, False, False, 5)
            self.editor_box.reorder_child(editor, toolbar_index)
            
            self.show_all()
        except Exception as e:
            print(f"Erro ao adicionar parágrafo: {e}")
    
    def on_save_project(self, button):
        # Verificar se current_project existe
        if self.current_project is None:
            print("Erro: current_project não foi definido")
            return
        
        try:
            self.current_project.save()
            print(f"Projeto '{self.current_project.name}' salvo com sucesso")
            
            # Feedback visual
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.INFO,
                buttons=Gtk.ButtonsType.OK,
                text=_("Projeto salvo com sucesso!")
            )
            dialog.run()
            dialog.destroy()
            
        except Exception as e:
            print(f"Erro ao salvar projeto: {e}")
            dialog = Gtk.MessageDialog(
                transient_for=self,
                flags=0,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text=f"Erro ao salvar: {e}"
            )
            dialog.run()
            dialog.destroy()

class ProjectSelector(Gtk.Box):
    def __init__(self, parent_window):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.parent_window = parent_window
        
        # Título
        title = Gtk.Label()
        title.set_markup(f"<big><b>{_('Selecione o tipo de parágrafo ou abra um projeto')}</b></big>")
        title.set_margin_top(20)
        title.set_margin_bottom(20)
        self.pack_start(title, False, False, 0)
        
        # Grid para botões de tipo de parágrafo
        grid = Gtk.Grid()
        grid.set_row_spacing(10)
        grid.set_column_spacing(10)
        grid.set_halign(Gtk.Align.CENTER)
        
        # Botões para tipos de parágrafos
        paragraph_types = [
            (_("Tópico Frasal"), "topic", _("Apresenta a ideia principal do parágrafo")),
            (_("Argumentação"), "argument", _("Desenvolve argumentos e ideias")),
            (_("Argumentação c/ Citação"), "argument_quote", _("Inclui citações de outros autores")),
            (_("Conclusão"), "conclusion", _("Finaliza o texto ou seção"))
        ]
        
        for i, (label, ptype, description) in enumerate(paragraph_types):
            btn = ParagraphTypeButton(label, ptype, description, self)
            grid.attach(btn, i % 2, i // 2, 1, 1)
        
        self.pack_start(grid, False, False, 20)
        
        # Separador
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        self.pack_start(separator, False, False, 20)
        
        # Seção de projetos existentes
        projects_label = Gtk.Label()
        projects_label.set_markup(f"<b>{_('Projetos Existentes')}</b>")
        self.pack_start(projects_label, False, False, 0)
        
        # Lista de projetos
        self.projects_listbox = Gtk.ListBox()
        self.projects_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.projects_listbox.connect('row-activated', self.on_project_selected)
        
        projects_scroll = Gtk.ScrolledWindow()
        projects_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        projects_scroll.set_min_content_height(200)
        projects_scroll.add(self.projects_listbox)
        
        self.pack_start(projects_scroll, True, True, 0)
        
        # Botão novo projeto
        new_project_btn = Gtk.Button(label=_("Criar Novo Projeto"))
        new_project_btn.get_style_context().add_class('suggested-action')
        new_project_btn.connect('clicked', lambda x: self.parent_window.create_new_project())
        new_project_btn.set_margin_top(10)
        self.pack_start(new_project_btn, False, False, 0)
        
        self.load_existing_projects()

    def load_existing_projects(self):
        try:
            # Verificar se project_manager existe
            if self.parent_window.project_manager is None:
                print("Aviso: project_manager não está disponível")
                return
            
            projects = self.parent_window.project_manager.list_projects()
            for project in projects:
                row = Gtk.ListBoxRow()
                
                box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
                box.set_margin_left(10)
                box.set_margin_right(10)
                box.set_margin_top(5)
                box.set_margin_bottom(5)
                
                name_label = Gtk.Label(project['name'])
                name_label.set_halign(Gtk.Align.START)
                name_label.get_style_context().add_class('title')
                
                file_label = Gtk.Label(project['file'])
                file_label.set_halign(Gtk.Align.START)
                file_label.get_style_context().add_class('dim-label')
                
                box.pack_start(name_label, False, False, 0)
                box.pack_start(file_label, False, False, 0)
                
                row.add(box)
                row.project_name = project['name']
                self.projects_listbox.add(row)
                
        except Exception as e:
            print(f"Erro ao carregar projetos existentes: {e}")

    def on_project_selected(self, listbox, row):
        try:
            self.parent_window.open_project(row.project_name)
        except Exception as e:
            print(f"Erro ao selecionar projeto: {e}")

class ParagraphTypeButton(Gtk.Button):
    def __init__(self, label, ptype, description, selector):
        super().__init__()
        self.ptype = ptype
        self.selector = selector
        
        # Box vertical para o conteúdo
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        
        # Label principal
        main_label = Gtk.Label(label)
        main_label.get_style_context().add_class('title')
        
        # Descrição
        desc_label = Gtk.Label(description)
        desc_label.set_line_wrap(True)
        desc_label.set_max_width_chars(30)
        desc_label.get_style_context().add_class('dim-label')
        
        box.pack_start(main_label, False, False, 0)
        box.pack_start(desc_label, False, False, 0)
        
        self.add(box)
        self.set_size_request(200, 80)
        self.connect('clicked', self.on_clicked)

    def on_clicked(self, button):
        print(f"Tipo de parágrafo selecionado: {self.ptype}")
        self.selector.parent_window.create_new_project()
        # Verificar se o projeto foi criado antes de continuar
        if self.selector.parent_window.current_project:
            self.selector.parent_window.current_project.add_paragraph(self.ptype)
            self.selector.parent_window.show_editor_interface()
        else:
            print("Erro: Projeto não foi criado corretamente")
