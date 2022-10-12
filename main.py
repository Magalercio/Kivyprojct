from kivy.app import App
from kivy.lang import Builder
from telas import *
from botoes import *
from bannervenda import BannerVenda
from bannervendedor import BannerVendedor
import requests
import os
from datetime import date
from functools import partial
from myfirebase import MyFirebase

GUI = Builder.load_file("main.kv")  # tem que ficar depois de todas as classes de paginas, para que elas sejam criadas


# Antes de criar o APP.


class MainApp(App):
    # Garantindo que não dê erro caso não selecionem corretamente na adição de vendas,
    # pois assim as variaveis existem mesmo que vazias.
    # por estar fora de função nao precisa colocar self, pos já é global dentro da classe.
    produto = None
    cliente = None
    unidade = None

    def build(self):
        self.firebase = MyFirebase()
        return GUI

    def on_start(self):

        # carregar as fotos de perfil
        arquivos = os.listdir("icones/fotos_perfil")
        pagina_foto_perfil = self.root.ids["fotoperfilpage"]
        lista_fotos = pagina_foto_perfil.ids["lista_fotos_perfil"]
        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_perfil/{foto}", on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)

        # carregar as fotos dos clientes

        arquivos = os.listdir("icones/fotos_clientes")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]

        for foto_cliente in arquivos:
            imagem = ImageButton(source=f"icones/fotos_clientes/{foto_cliente}",
                                 on_release=partial(self.selecionar_cliente, foto_cliente))
            label = LabelButton(text=foto_cliente.replace(".png", "").capitalize(),
                                on_release=partial(self.selecionar_cliente, foto_cliente))
            lista_clientes.add_widget(imagem)
            lista_clientes.add_widget(label)

        # carregar as fotos dos produtos

        arquivos = os.listdir("icones/fotos_produtos")
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]

        for foto_produto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_produtos/{foto_produto}",
                                 on_release=partial(self.selecionar_produto, foto_produto))
            label = LabelButton(text=foto_produto.replace(".png", "").capitalize(),
                                on_release=partial(self.selecionar_produto, foto_produto))
            lista_produtos.add_widget(imagem)
            lista_produtos.add_widget(label)

        # carregar data
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        label_data= pagina_adicionarvendas.ids["label_data"]
        label_data.text = f"Data: {date.today().strftime('%d/%m/%Y')}"


        # carrega as infos do usuários
        self.carregar_infos_usuario()

    def carregar_infos_usuario(self):
        try:
            # pegando usuario do refreshtoken.txt
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()
            local_id, id_token = self.firebase.trocar_token(refresh_token)
            self.local_id = local_id
            self.id_token = id_token

            # pegar informações do usuario
            requisicao = requests.get(f"https://aplicativovendaskiv-default-rtdb.firebaseio.com/{self.local_id}.json")
            requisicao_dic = requisicao.json()

            # preencher foto de perfil
            avatar = requisicao_dic['avatar']
            self.avatar = avatar
            foto_perfil = self.root.ids["foto_perfil"]
            foto_perfil.source = f"icones/fotos_perfil/{avatar}"

            # preencher ID único
            id_vendedor = requisicao_dic['id_vendedor']
            self.id_vendedor = id_vendedor
            pagina_ajustes = self.root.ids["ajustespage"]
            pagina_ajustes.ids['id_vendedor'].text = f"Seu ID Único: {id_vendedor}"

            # preencher total de vendas
            total_vendas = requisicao_dic['total_vendas']
            total_vendas = float(total_vendas)
            self.total_vendas = total_vendas
            pagina_homepage = self.root.ids["homepage"]
            pagina_homepage.ids['label_total_vendas'].text = "[color=#000000]Total de Vendas:[/color] [b]R$ {:.2f}[/b]" \
                .format(total_vendas)

            # preencher equipe
            self.equipe = requisicao_dic["equipe"]

            # preencher listas de vendas
            try:
                vendas = requisicao_dic['vendas'][1:]
                self.vendas = vendas
                pagina_homepage = self.root.ids["homepage"]
                lista_vendas = pagina_homepage.ids["lista_vendas"]
                for venda in vendas:
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente=venda['foto_cliente'],
                                         produto=venda['produto'], foto_produto=venda['foto_produto'],
                                         data=venda['data'], preco=venda['preco'], unidade=venda['unidade'],
                                         quantidade=venda['quantidade'])

                    lista_vendas.add_widget(banner)
            except:
                pass

            # preencher equipe de vendedores
            equipe = requisicao_dic["equipe"]
            lista_equipe = equipe.split(",")
            pagina_listavendedores = self.root.ids["listarvendedorespage"]
            lista_vendedores = pagina_listavendedores.ids['lista_vendedores']

            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)

            self.mudar_tela("homepage")
        except:
            pass

    def mudar_tela(self, id_tela):
        gerenciador_telas = self.root.ids["screen_manager"]
        gerenciador_telas.current = id_tela

    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids["foto_perfil"]
        foto_perfil.source = f"icones/fotos_perfil/{foto}"

        info = f'{{"avatar": "{foto}"}}'  # Chaves esta  dupla para o python entender que é chaves texto,
        # não um valor formatado.

        requisicao = requests.patch(f"https://aplicativovendaskiv-default-rtdb.firebaseio.com/{self.local_id}.json",
                                    data=info)
        self.mudar_tela("ajustespage")

    def adicionar_vendedor(self, id_vendedor_adcionado):
        link = f'https://aplicativovendaskiv-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"&equalTo=' \
               f'"{id_vendedor_adcionado}"'
        requisicao = requests.get(link)
        requisicao_dic = requisicao.json()

        pagina_adcionarvendedor = self.root.ids["adicionarvendedorpage"]
        mensagem_texto = pagina_adcionarvendedor.ids["mensagem_outrovendedor"]

        if requisicao_dic == {}:
            mensagem_texto.text = "Usuário não encontrado"

        else:
            equipe = self.equipe.split(",")
            if id_vendedor_adcionado in equipe:
                mensagem_texto.text = "Vendedor já faz parte da equipe"
            else:
                self.equipe = self.equipe + f",{id_vendedor_adcionado}"
                info = f'{{"equipe": "{self.equipe}"}}'
                requests.patch(f"https://aplicativovendaskiv-default-rtdb.firebaseio.com/{self.local_id}.json",
                               data=info)
                mensagem_texto.text = "Vendedor Adicionado com Sucesso"
                # adicionar o novo banner do vendedor recem adicionado
                pagina_listavendedores = self.root.ids["listarvendedorespage"]
                lista_vendedores = pagina_listavendedores.ids['lista_vendedores']
                banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adcionado)
                lista_vendedores.add_widget(banner_vendedor)

    def selecionar_cliente(self, foto, *args):
        # criando variavel interna para que seja aplicada na funcao de add_venda
        self.cliente = foto.replace(".png", "")
        # pintar de branco todas as outras opçoes
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_clientes = pagina_adicionarvendas.ids["lista_clientes"]
        pagina_adicionarvendas.ids["label_selecione_cliente"].color = (1, 1, 1, 1)

        for item in list(lista_clientes.children):
            item.color = (1, 1, 1, 1)  # como imagem não tem parametro 'color' eles não serão alterados, apenas textos

            # pintar de azul a letra do item que selecionamos
            """
            exemplo: argumento foto -> carrefour.png / Label -> Carrefour
            preciso trasformar o texto novamente em minusculo e com ".png" para que seja comparável com o arg foto
            mas se fizer isso direto com todos os itens, dará erro nas imagens, pra pular esse erro usaremos try/except.
            """
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_produto(self, foto, *args):
        # criando variavel interna para que seja aplicada na funcao de add_venda
        self.produto = foto.replace(".png", "")
        # pintar de branco todas as outras opçoes
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        lista_produtos = pagina_adicionarvendas.ids["lista_produtos"]
        pagina_adicionarvendas.ids["label_selecione_produto"].color = (1, 1, 1, 1)

        for item in list(lista_produtos.children):
            item.color = (1, 1, 1, 1)  # como imagem não tem parametro 'color' eles não serão alterados, apenas textos

            # pintar de azul a letra do item que selecionamos
            try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                    item.color = (0, 207/255, 219/255, 1)
            except:
                pass

    def selecionar_unidade(self, id_label, *args):
        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]

        # criando variavel interna para que seja aplicada na funcao de add_venda
        self.unidade = id_label.replace("unidades_","")
        # pintar todo mundo de branco
        pagina_adicionarvendas.ids["unidades_kg"].color = (1,1,1,1)
        pagina_adicionarvendas.ids["unidades_unidades"].color = (1, 1, 1, 1)
        pagina_adicionarvendas.ids["unidades_litros"].color = (1, 1, 1, 1)
        # pintar selecionado de azul
        pagina_adicionarvendas.ids[id_label].color = (0, 207/255, 219/255, 1)

    def adicionar_venda(self):
        # pegar todas as informacoes preenchidas na pagina de venda
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade

        pagina_adicionarvendas = self.root.ids["adicionarvendaspage"]
        data = pagina_adicionarvendas.ids["label_data"].text.replace("Data: ", "")
        preco = pagina_adicionarvendas.ids["preco_total"].text
        quantidade = pagina_adicionarvendas.ids["quantidade"].text

        # mudando para vermelho oq não foi selecionado.

        if not cliente:
            pagina_adicionarvendas.ids["label_selecione_cliente"].color = (1, 0, 0, 1)
        if not produto:
            pagina_adicionarvendas.ids["label_selecione_produto"].color = (1, 0, 0, 1)
        if not unidade:
            pagina_adicionarvendas.ids["unidades_kg"].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids["unidades_unidades"].color = (1, 0, 0, 1)
            pagina_adicionarvendas.ids["unidades_litros"].color = (1, 0, 0, 1)

        if not preco:
            pagina_adicionarvendas.ids["label_preco"].color = (1, 0, 0, 1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionarvendas.ids["label_preco"].color = (1, 0, 0, 1)

        if not quantidade:
            pagina_adicionarvendas.ids["label_quantidade"].color = (1, 0, 0, 1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionarvendas.ids["label_quantidade"].color = (1, 0, 0, 1)

        # dado que todos os campos foram preenchidos corretamente, vamos adicionar a venda ao banco de dados
        if cliente and produto and unidade and preco and quantidade and (type(preco) == float)\
                and (type(quantidade) == float):
            foto_produto = produto + ".png"
            foto_cliente = cliente + ".png"

            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", ' \
                   f'"foto_produto": "{foto_produto}", "data": "{data}", "unidade": "{unidade}", "preco": "{preco}",' \
                   f' "quantidade": "{quantidade}"}}'

            requests.post(f"https://aplicativovendaskiv-default-rtdb.firebaseio.com/{self.local_id}/vendas.json",
                          data= info)

            banner = BannerVenda(cliente=cliente, produto=produto, foto_cliente=foto_cliente, foto_produto=foto_produto,
                                 data=data, preco=preco, quantidade=quantidade, unidade=unidade)
            pagina_homepage = self.root.ids["homepage"]
            lista_vendas = pagina_homepage.ids["lista_vendas"]
            lista_vendas.add_widget(banner)



            requisicao = requests.get(f"https://aplicativovendaskiv-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json")
            total_vendas = float(requisicao.json())
            total_vendas += preco
            info=f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f"https://aplicativovendaskiv-default-rtdb.firebaseio.com/{self.local_id}.json", data=info)

            pagina_homepage = self.root.ids["homepage"]
            pagina_homepage.ids['label_total_vendas'].text = "[color=#000000]Total de Vendas:[/color] [b]R$ {:.2f}[/b]" \
                .format(total_vendas)

            self.mudar_tela("homepage")



        # zerando as variáveis para que não estajam pré selecionadas quando for dar mais de uma entrada.
        self.cliente = None
        self.produto = None
        self.unidade = None






MainApp().run()
