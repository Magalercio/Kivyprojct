from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
import requests

GUI = Builder.load_file("main.kv") #tem que ficar depois de todas as classes de paginas, para que elas sejam criadas
# Antes de criar o APP.


class MainApp(App):
    id_usuario = 1
    def build(self):
        return GUI

    def on_start(self):
        requisicao = requests.get(f"https://aplicativovendaskiv-default-rtdb.firebaseio.com/{self.id_usuario}.json")
        requisicao_dic = requisicao.json()
        avatar = requisicao_dic['avatar']
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{avatar}"
        print(requisicao_dic)

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela


MainApp().run()


