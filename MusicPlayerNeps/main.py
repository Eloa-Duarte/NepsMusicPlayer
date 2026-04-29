import csv
import queue
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

biblioteca = {}  # dict: title -> (artist, duration)
fila = queue.SimpleQueue()
historico = queue.LifoQueue()

ordem_musicas = []  # mantém ordem da biblioteca
indice_atual = -1
musica_atual = None
estado = "Pausado"

def carregar_musicas():
    global ordem_musicas
    try:
        with open("songs.csv", newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # pular cabeçalho

            for linha in reader:
                if len(linha) != 3:
                    print(f"Linha inválida ignorada: {linha}")
                    continue

                titulo, artista, duracao = linha

                try:
                    duracao = int(duracao)
                except:
                    print(f"Linha inválida ignorada: {linha}")
                    continue

                biblioteca[titulo] = (artista, duracao)
                ordem_musicas.append(titulo)

    except FileNotFoundError:
        print("Erro: songs.csv não encontrado!")

app = ttk.Window(title="NepsMusic Player", themename="darkly")

frame = ttk.Frame(app, padding=10)
frame.pack(fill=BOTH, expand=True)

# Biblioteca
tree_biblioteca = ttk.Treeview(frame, columns=("Artista", "Duração"), show="headings")
tree_biblioteca.heading("Artista", text="Artista")
tree_biblioteca.heading("Duração", text="Duração")
tree_biblioteca.grid(row=0, column=0, padx=5, pady=5)

# Fila
list_fila = ttk.Listbox(frame)
list_fila.grid(row=0, column=1, padx=5, pady=5)
# Status
label_status = ttk.Label(frame, text="Pausado: Nenhuma música")
label_status.grid(row=1, column=0, columnspan=3, pady=10)
# Histórico
list_historico = ttk.Listbox(frame)
list_historico.grid(row=0, column=2, padx=5, pady=5)

def atualizar_fila():
    list_fila.delete(0, "end")
    temp = []
    while not fila.empty():
        m = fila.get()
        temp.append(m)
        list_fila.insert("end", m)
    for m in temp:
        fila.put(m)

def tocar_pausar():
    global estado
    if estado == "Tocando":
        estado = "Pausado"
    else:
        estado = "Tocando"
    atualizar_status()

def atualizar_status():
    if musica_atual:
        label_status.config(text=f"{estado}: {musica_atual}")
    else:
        label_status.config(text="Pausado: Nenhuma música")

def atualizar_historico():
    list_historico.delete(0, "end")
    temp = []
    while not historico.empty():
        m = historico.get()
        temp.append(m)
    for m in reversed(temp):
        list_historico.insert("end", m)
    for m in temp:
        historico.put(m)

def proximo():
    global musica_atual, indice_atual

    if musica_atual:
        historico.put(musica_atual)

    if not fila.empty():
        musica_atual = fila.get()
    else:
        if indice_atual + 1 < len(ordem_musicas):
            indice_atual += 1
            musica_atual = ordem_musicas[indice_atual]
        else:
            musica_atual = None

    atualizar_status()
    atualizar_fila()
    atualizar_historico()

def voltar():
    global musica_atual

    if not historico.empty():
        musica_atual = historico.get()

    atualizar_status()
    atualizar_historico()

def adicionar_fila(event=None):
    selecionado = tree_biblioteca.focus()
    if not selecionado:
        return

    titulo = tree_biblioteca.item(selecionado)["text"]
    fila.put(titulo)
    atualizar_fila()

frame_botoes = ttk.Frame(app)
frame_botoes.pack(pady=10)

btn_play = ttk.Button(frame_botoes, text="Tocar/Pausar", command=tocar_pausar)
btn_play.grid(row=0, column=0, padx=5)

btn_next = ttk.Button(frame_botoes, text="Próximo", command=proximo)
btn_next.grid(row=0, column=1, padx=5)

btn_prev = ttk.Button(frame_botoes, text="Voltar", command=voltar)
btn_prev.grid(row=0, column=2, padx=5)

carregar_musicas()

for titulo, (artista, duracao) in biblioteca.items():
    tree_biblioteca.insert("", "end", text=titulo, values=(artista, duracao))

tree_biblioteca.bind("<Double-1>", adicionar_fila)

app.mainloop()