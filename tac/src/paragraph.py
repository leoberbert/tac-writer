import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, GtkSource, Pango, GObject

# Configurar traduções como fallback
try:
    _ = _
except NameError:
    def _(text):
        return text

class ParagraphEditor(Gtk.Frame):
    __gtype_name__ = 'ParagraphEditor'
    
    def __init__(self, paragraph_data, **kwargs):
        super().__init__(**kwargs)
        self.paragraph_data = paragraph_data
        
        try:
            # Box principal
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.add(main_box)
            
            # Header com tipo e botões
            header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            header.set_margin_left(10)
            header.set_margin_right(10)
            header.set_margin_top(5)
            header.set_margin_bottom(5)
            header.get_style_context().add_class('header-bar')
            
            # Label do tipo
            type_label = Gtk.Label(self.get_type_label())
            type_label.get_style_context().add_class('title')
            header.pack_start(type_label, False, False, 0)
            
            # Spacer
            header.pack_start(Gtk.Box(), True, True, 0)
            
            # Botão de formatação
            format_btn = Gtk.Button(label=_("Formatação"))
            format_btn.connect('clicked', self.on_format_clicked)
            header.pack_start(format_btn, False, False, 0)
            
            # Botão remover
            remove_btn = Gtk.Button()
            remove_btn.add(Gtk.Image.new_from_icon_name('list-remove-symbolic', Gtk.IconSize.BUTTON))
            remove_btn.connect('clicked', self.on_remove_clicked)
            header.pack_start(remove_btn, False, False, 0)
            
            main_box.pack_start(header, False, False, 0)
            
            # Editor de texto
            self.editor = TextEditor(paragraph_data)
            main_box.pack_start(self.editor, True, True, 0)
            
        except Exception as e:
            print(f"Erro ao inicializar ParagraphEditor: {e}")
            import traceback
            traceback.print_exc()
    
    def get_type_label(self):
        types = {
            'topic': _("Tópico Frasal"),
            'argument': _("Argumentação"),
            'argument_quote': _("Argumentação com Citação"),
            'conclusion': _("Conclusão")
        }
        return types.get(self.paragraph_data['type'], _("Parágrafo"))
    
    def on_format_clicked(self, button):
        print("Botão de formatação clicado")
        try:
            dialog = FormatDialog(self.get_toplevel(), self.paragraph_data['formatting'])
            response = dialog.run()
            
            if response == Gtk.ResponseType.APPLY:
                self.paragraph_data['formatting'] = dialog.get_formatting()
                self.editor.apply_formatting()
            
            dialog.destroy()
        except Exception as e:
            print(f"Erro ao abrir diálogo de formatação: {e}")
    
    def on_remove_clicked(self, button):
        # Confirmar remoção
        dialog = Gtk.MessageDialog(
            transient_for=self.get_toplevel(),
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=_("Remover este parágrafo?")
        )
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            # Remove da interface
            parent = self.get_parent()
            if parent:
                parent.remove(self)

class TextEditor(Gtk.Box):
    def __init__(self, paragraph_data):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.paragraph_data = paragraph_data
        
        try:
            # Buffer de texto
            self.buffer = GtkSource.Buffer()
            self.buffer.set_text(paragraph_data.get('content', ''))
            self.buffer.connect('changed', self.on_text_changed)
            
            # Visualização
            self.view = GtkSource.View(buffer=self.buffer)
            self.view.set_wrap_mode(Gtk.WrapMode.WORD)
            self.view.set_border_width(10)
            self.view.set_auto_indent(True)
            self.view.set_indent_on_tab(True)
            
            # Scroll
            scroll = Gtk.ScrolledWindow()
            scroll.add(self.view)
            scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scroll.set_size_request(-1, 150)
            self.pack_start(scroll, True, True, 0)
            
            self.apply_formatting()
            
        except Exception as e:
            print(f"Erro ao inicializar TextEditor: {e}")
            import traceback
            traceback.print_exc()
    
    def on_text_changed(self, buffer):
        try:
            start, end = buffer.get_bounds()
            self.paragraph_data['content'] = buffer.get_text(start, end, False)
        except Exception as e:
            print(f"Erro ao processar mudança de texto: {e}")
    
    def apply_formatting(self):
        try:
            fmt = self.paragraph_data.get('formatting', {})
            
            # Configurar fonte
            font_desc = Pango.FontDescription()
            font_desc.set_family(fmt.get('font', 'Sans'))
            font_desc.set_size(int(fmt.get('font_size', 12)) * Pango.SCALE)
            self.view.override_font(font_desc)
            
            # Espaçamento entre linhas
            line_spacing = fmt.get('line_spacing', 1.5)
            self.view.set_pixels_below_lines(int(line_spacing * 5))
            
            # Recuos
            if self.paragraph_data.get('type') == 'argument_quote':
                quote_indent = fmt.get('quote_indent', 4.0)
                self.view.set_left_margin(int(quote_indent * 20))
            else:
                first_indent = fmt.get('first_indent', 0.0)
                self.view.set_left_margin(int(first_indent * 20))
                
        except Exception as e:
            print(f"Erro ao aplicar formatação: {e}")

class FormatDialog(Gtk.Dialog):
    def __init__(self, parent, formatting):
        super().__init__(title=_("Formatação de Texto"), transient_for=parent, flags=0)
        self.formatting = formatting.copy()
        
        try:
            self.add_buttons(
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_APPLY, Gtk.ResponseType.APPLY
            )
            
            content_area = self.get_content_area()
            grid = Gtk.Grid()
            grid.set_column_spacing(12)
            grid.set_row_spacing(12)
            grid.set_margin_left(12)
            grid.set_margin_right(12)
            grid.set_margin_top(12)
            grid.set_margin_bottom(12)
            content_area.add(grid)
            
            row = 0
            
            # Fonte
            lbl_font = Gtk.Label(_("Fonte:"))
            lbl_font.set_halign(Gtk.Align.START)
            self.font_btn = Gtk.FontButton()
            font_name = f"{formatting.get('font', 'Sans')} {formatting.get('font_size', 12)}"
            self.font_btn.set_font_name(font_name)
            grid.attach(lbl_font, 0, row, 1, 1)
            grid.attach(self.font_btn, 1, row, 1, 1)
            row += 1
            
            # Espaçamento
            lbl_spacing = Gtk.Label(_("Espaçamento:"))
            lbl_spacing.set_halign(Gtk.Align.START)
            adj = Gtk.Adjustment(value=formatting.get('line_spacing', 1.5), lower=1.0, upper=3.0, step_increment=0.1)
            self.spacing_spin = Gtk.SpinButton(adjustment=adj, digits=1)
            grid.attach(lbl_spacing, 0, row, 1, 1)
            grid.attach(self.spacing_spin, 1, row, 1, 1)
            row += 1
            
            # Recuo primeira linha
            lbl_first_indent = Gtk.Label(_("Recuo primeira linha (cm):"))
            lbl_first_indent.set_halign(Gtk.Align.START)
            adj = Gtk.Adjustment(value=formatting.get('first_indent', 0.0), lower=0, upper=10, step_increment=0.5)
            self.first_indent_spin = Gtk.SpinButton(adjustment=adj, digits=1)
            grid.attach(lbl_first_indent, 0, row, 1, 1)
            grid.attach(self.first_indent_spin, 1, row, 1, 1)
            row += 1
            
            # Recuo citação
            lbl_quote_indent = Gtk.Label(_("Recuo citação (cm):"))
            lbl_quote_indent.set_halign(Gtk.Align.START)
            adj = Gtk.Adjustment(value=formatting.get('quote_indent', 4.0), lower=0, upper=10, step_increment=0.5)
            self.quote_indent_spin = Gtk.SpinButton(adjustment=adj, digits=1)
            grid.attach(lbl_quote_indent, 0, row, 1, 1)
            grid.attach(self.quote_indent_spin, 1, row, 1, 1)
            
            self.show_all()
            
        except Exception as e:
            print(f"Erro ao inicializar FormatDialog: {e}")
            import traceback
            traceback.print_exc()
    
    def get_formatting(self):
        try:
            font_desc = Pango.FontDescription.from_string(self.font_btn.get_font_name())
            
            return {
                'font': font_desc.get_family(),
                'font_size': font_desc.get_size() // Pango.SCALE,
                'line_spacing': self.spacing_spin.get_value(),
                'first_indent': self.first_indent_spin.get_value(),
                'quote_indent': self.quote_indent_spin.get_value()
            }
        except Exception as e:
            print(f"Erro ao obter formatação: {e}")
            return self.formatting
