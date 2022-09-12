from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *

GUI = Builder.load_file("main.kv") #tem que ficar depois de todas as classes de paginas, para que elas sejam criadas
# Antes de criar o APP.


class MainApp(App):

    def build(self):
        return GUI

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela


MainApp().run()