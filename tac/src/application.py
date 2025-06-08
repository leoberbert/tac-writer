import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sys

class TacApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.github.tac_app')
        self.window = None
        print("TacApplication inicializada")

    def do_activate(self):
        print("Ativando aplicação...")
        try:
            if not self.window:
                from window import MainWindow
                self.window = MainWindow(application=self)
                print("Janela principal criada")
            self.window.show_all()
            print("Janela apresentada")
        except Exception as e:
            print(f"Erro ao ativar aplicação: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
