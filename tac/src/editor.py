import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, GtkSource, Pango

class SimpleTextEditor(Gtk.Box):
    def __init__(self, paragraph_data):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.paragraph_data = paragraph_data
        
        try:
            # TextView simples se GtkSource não funcionar
            try:
                self.buffer = GtkSource.Buffer()
                self.view = GtkSource.View(buffer=self.buffer)
            except:
                self.buffer = Gtk.TextBuffer()
                self.view = Gtk.TextView(buffer=self.buffer)
            
            self.buffer.set_text(paragraph_data.get('content', ''))
            self.buffer.connect('changed', self.on_text_changed)
            
            self.view.set_wrap_mode(Gtk.WrapMode.WORD)
            self.view.set_border_width(10)
            
            # Scroll
            scroll = Gtk.ScrolledWindow()
            scroll.add(self.view)
            scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scroll.set_size_request(-1, 150)
            self.pack_start(scroll, True, True, 0)
            
            self.apply_formatting()
            
        except Exception as e:
            print(f"Erro ao inicializar SimpleTextEditor: {e}")
    
    def on_text_changed(self, buffer):
        try:
            start, end = buffer.get_bounds()
            self.paragraph_data['content'] = buffer.get_text(start, end, False)
        except Exception as e:
            print(f"Erro ao processar mudança de texto: {e}")
    
    def apply_formatting(self):
        try:
            fmt = self.paragraph_data.get('formatting', {})
            
            font_desc = Pango.FontDescription()
            font_desc.set_family(fmt.get('font', 'Sans'))
            font_desc.set_size(int(fmt.get('font_size', 12)) * Pango.SCALE)
            self.view.override_font(font_desc)
            
        except Exception as e:
            print(f"Erro ao aplicar formatação: {e}")
