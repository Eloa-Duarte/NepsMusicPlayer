import csv
import queue
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

biblioteca = {}
fila = queue.SimpleQueue()
historico = queue.LifoQueue()

ordem_musicas = []
indice_atual = -1
musica_atual = None
estado = "Pausado"

def carregar_musicas():
    global ordem_musicas
    with open("songs.csv", newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
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

def sincronizar_indice():
    global indice_atual
    if musica_atual in ordem_musicas:
        indice_atual = ordem_musicas.index(musica_atual)

app = ttk.Window(title="NepsMusic Player", themename="darkly")

frame = ttk.Frame(app, padding=10)
frame.pack(fill=BOTH, expand=True)

tree_biblioteca = ttk.Treeview(
    frame,
    columns=("Título", "Artista", "Duração"),
    show="headings"
)

tree_biblioteca.heading("Título", text="Título")
tree_biblioteca.heading("Artista", text="Artista")
tree_biblioteca.heading("Duração", text="Duração")

tree_biblioteca.grid(row=0, column=0, padx=5, pady=5)

list_fila = ttk.Listbox(frame)
list_fila.grid(row=0, column=1, padx=5, pady=5)

list_historico = ttk.Listbox(frame)
list_historico.grid(row=0, column=2, padx=5, pady=5)

label_status = ttk.Label(frame, text="Pausado: Nenhuma música")
label_status.grid(row=1, column=0, columnspan=3, pady=10)

def atualizar_fila():
    list_fila.delete(0, "end")
    temp = []
    while not fila.empty():
        temp.append(fila.get())
    for m in temp:
        list_fila.insert("end", m)
        fila.put(m)

def atualizar_historico():
    list_historico.delete(0, "end")
    temp = []
    while not historico.empty():
        temp.append(historico.get())
    for m in reversed(temp):
        list_historico.insert("end", m)
    for m in reversed(temp):
        historico.put(m)

def atualizar_status():
    if musica_atual:
        label_status.config(text=f"{estado}: {musica_atual}")
    else:
        label_status.config(text="Pausado: Nenhuma música")

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

    sincronizar_indice()
    atualizar_status()
    atualizar_fila()
    atualizar_historico()

def voltar():
    global musica_atual

    if not historico.empty():
        anterior = historico.get()
        if musica_atual:
            historico.put(musica_atual)
        musica_atual = anterior

    sincronizar_indice()
    atualizar_status()
    atualizar_fila()
    atualizar_historico()

def tocar_pausar():
    global estado
    estado = "Tocando" if estado == "Pausado" else "Pausado"
    atualizar_status()

def adicionar_fila(event=None):
    selecionado = tree_biblioteca.focus()
    if not selecionado:
        return
    valores = tree_biblioteca.item(selecionado)["values"]
    fila.put(valores[0])
    atualizar_fila()

frame_botoes = ttk.Frame(app)
frame_botoes.pack(pady=10)

ttk.Button(frame_botoes, text="Tocar/Pausar", command=tocar_pausar).grid(row=0, column=0, padx=5)
ttk.Button(frame_botoes, text="Próximo", command=proximo).grid(row=0, column=1, padx=5)
ttk.Button(frame_botoes, text="Voltar", command=voltar).grid(row=0, column=2, padx=5)

carregar_musicas()

for titulo, (artista, duracao) in biblioteca.items():
    tree_biblioteca.insert("", "end", values=(titulo, artista, duracao))

tree_biblioteca.bind("<Double-1>", adicionar_fila)

app.mainloop()
