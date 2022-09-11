from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


class HomePage(Screen):
    pass


class AjustesPage(Screen):
    pass


GUI = Builder.load_file("main.kv") #tem que ficar depois de todas as classes de paginas, para que elas sejam criadas
# Antes de cliar o APP.
class MainApp(App):

    def build(self):
        return GUI


MainApp().run()