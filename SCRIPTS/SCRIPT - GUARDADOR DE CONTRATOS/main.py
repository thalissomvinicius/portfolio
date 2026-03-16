import os
import shutil
import tkinter as tk
from tkinter import filedialog

def encontrar_arquivos_duplicados(diretorio_origem):
    """Encontra arquivos duplicados no diretório de origem."""
    arquivos_duplicados = {}
    for root, _, files in os.walk(diretorio_origem):
        for filename in files:
            arquivo = os.path.join(root, filename)
            # Ignora diretórios e verifica apenas arquivos
            if os.path.isfile(arquivo):
                # Obtém nome e extensão do arquivo
                nome_arquivo, extensao = os.path.splitext(filename)
                # Verifica se já encontrou um arquivo com o mesmo nome e extensão
                if (nome_arquivo, extensao) in arquivos_duplicados:
                    arquivos_duplicados[(nome_arquivo, extensao)].append(arquivo)
                else:
                    arquivos_duplicados[(nome_arquivo, extensao)] = [arquivo]
    return {chave: arquivos for chave, arquivos in arquivos_duplicados.items() if len(arquivos) > 1}

def verificar_nome_arquivo(nome_arquivo):
    """Verifica se o nome do arquivo está completo."""
    if "QD" not in nome_arquivo or "LT" not in nome_arquivo:
        print(f"AVISO: O arquivo {nome_arquivo} está com o nome incompleto. Verifique se 'QD' e 'LT' estão presentes.")
        return False
    return True

def organizar_arquivos(diretorio_origem, diretorio_base_destino, lbl_status, txt_log):
    """Organiza os arquivos da pasta de origem."""
    print(f"Iniciando a organização dos arquivos da pasta: {diretorio_origem}")
    txt_log.delete(1.0, tk.END)  # Limpa o log de mensagens
    lbl_status.config(text="Organizando arquivos...", fg="blue")

    # Define os caminhos para as subpastas VALLE e ML
    diretorio_valle = os.path.join(diretorio_origem, 'VALLE')
    diretorio_ml = os.path.join(diretorio_origem, 'ML')

    if not os.path.exists(diretorio_valle):
        lbl_status.config(text="Erro: Pasta VALLE não encontrada no diretório de origem.", fg="red")
        return
    if not os.path.exists(diretorio_ml):
        lbl_status.config(text="Erro: Pasta ML não encontrada no diretório de origem.", fg="red")
        return

    # Define os caminhos base de destino para VALLE e ML
    caminho_valle = os.path.join(diretorio_base_destino, 'VALLE')
    caminho_ml = os.path.join(diretorio_base_destino, 'ML')

    # Verifica se os diretórios de destino (ML e VALLE) existem, se não, cria
    if not os.path.exists(caminho_ml):
        print(f"Criando o diretório: {caminho_ml}")
        os.makedirs(caminho_ml)
        
    if not os.path.exists(caminho_valle):
        print(f"Criando o diretório: {caminho_valle}")
        os.makedirs(caminho_valle)

    # Variável para acompanhar se houve algum erro durante a organização
    houve_erro = False

    # Função auxiliar para organizar arquivos em uma pasta específica
    def processar_arquivos(diretorio_origem, prefixo, caminho_destino):
        nonlocal houve_erro
        for arquivo in os.listdir(diretorio_origem):
            caminho_arquivo = os.path.join(diretorio_origem, arquivo)
            # Verifica se é um arquivo
            if os.path.isfile(caminho_arquivo):
                # Verifica se o nome do arquivo está completo
                if not verificar_nome_arquivo(arquivo):
                    houve_erro = True
                    continue
                # Realiza o split para obter as partes necessárias
                partes = arquivo.split('-')
                
                if len(partes) >= 5:
                    # Determina o diretório de destino com base no prefixo
                    if prefixo == '999-70100':
                        quadra = partes[5]  # Assume que a quadra será uma letra
                    elif prefixo == '6-70400':
                        quadra = partes[5].zfill(3)  # Garante três dígitos para a quadra
                    else:
                        print(f"O arquivo {arquivo} possui um prefixo não reconhecido.")
                        houve_erro = True
                        continue
                    
                    # Identifica o lote
                    try:
                        lote = os.path.splitext(partes[7])[0].zfill(3)
                    except IndexError as e:
                        print(f"Erro ao processar lote para o arquivo {arquivo}: {e}")
                        houve_erro = True
                        continue
                    
                    # Formata os nomes dos diretórios
                    nome_quadra = f"QUADRA {quadra}"
                    nome_lote = f"LOTE {lote}"
                    
                    # Cria os diretórios de quadra e lote se não existirem
                    caminho_quadra = os.path.join(caminho_destino, nome_quadra)
                    caminho_lote = os.path.join(caminho_quadra, nome_lote)
                    
                    if not os.path.exists(caminho_lote):
                        print(f"Criando o diretório: {caminho_lote}")
                        os.makedirs(caminho_lote)
                    
                    # Move o arquivo para o destino especificado
                    destino_arquivo = os.path.join(caminho_lote, arquivo)
                    try:
                        shutil.move(caminho_arquivo, destino_arquivo)
                        msg = f"ARQUIVO: {arquivo} ARQUIVADO COM SUCESSO\n"
                        print(msg.strip())
                        txt_log.insert(tk.END, msg)
                    except Exception as e:
                        msg = f"Erro ao arquivar o arquivo {arquivo}: {e}\n"
                        print(msg.strip())
                        txt_log.insert(tk.END, msg)
                        houve_erro = True
                else:
                    msg = f"O arquivo {arquivo} não possui o formato esperado.\n"
                    print(msg.strip())
                    txt_log.insert(tk.END, msg)
                    houve_erro = True
            else:
                msg = f"{arquivo} não é um arquivo e será ignorado.\n"
                print(msg.strip())
                txt_log.insert(tk.END, msg)
                houve_erro = True

    # Processa arquivos em VALLE e ML
    processar_arquivos(diretorio_valle, '6-70400', caminho_valle)
    processar_arquivos(diretorio_ml, '999-70100', caminho_ml)
    
    if not houve_erro:
        lbl_status.config(text="Organização concluída com sucesso.", fg="green")
    else:
        lbl_status.config(text="Organização concluída com erros.", fg="red")

def selecionar_diretorio_origem():
    """Abre um diálogo para selecionar o diretório de origem."""
    diretorio_origem = filedialog.askdirectory()
    entry_origem.delete(0, tk.END)
    entry_origem.insert(0, diretorio_origem)

def selecionar_diretorio_destino():
    """Abre um diálogo para selecionar o diretório de destino."""
    diretorio_destino = filedialog.askdirectory()
    entry_destino.delete(0, tk.END)
    entry_destino.insert(0, diretorio_destino)

# Cria a janela principal
root = tk.Tk()
root.title("Organizador de Arquivos")
root.geometry("500x400")

# Frame para os widgets
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Botão para selecionar o diretório de origem
btn_origem = tk.Button(frame, text="Selecionar Origem", command=selecionar_diretorio_origem)
btn_origem.grid(row=0, column=0, padx=5, pady=5)

# Botão para selecionar o diretório de destino
btn_destino = tk.Button(frame, text="Selecionar Destino", command=selecionar_diretorio_destino)
btn_destino.grid(row=1, column=0, padx=5, pady=5)

# Entrada para exibir o diretório de origem selecionado
entry_origem = tk.Entry(frame, width=50)
entry_origem.grid(row=0, column=1, padx=5, pady=5)

# Entrada para exibir o diretório de destino selecionado
entry_destino = tk.Entry(frame, width=50)
entry_destino.grid(row=1, column=1, padx=5, pady=5)

# Rótulo para exibir o status da organização
lbl_status = tk.Label(frame, text="", fg="black")
lbl_status.grid(row=2, column=0, columnspan=2)

# Área de texto para exibir o log de mensagens
txt_log = tk.Text(frame, width=60, height=10)
txt_log.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

# Barra de rolagem vertical para a área de texto
scrollbar = tk.Scrollbar(frame, command=txt_log.yview)
scrollbar.grid(row=3, column=2, sticky='ns')
txt_log.config(yscrollcommand=scrollbar.set)

# Botão para iniciar a organização dos arquivos
btn_organizar = tk.Button(frame, text="Organizar Arquivos", command=lambda: organizar_arquivos(entry_origem.get(), entry_destino.get(), lbl_status, txt_log))
btn_organizar.grid(row=4, column=0, columnspan=2, pady=10)

# Rótulo para exibir o footer
lbl_footer = tk.Label(root, text="By Vinicius Developer", fg="gray")
lbl_footer.pack(side=tk.BOTTOM, pady=5)

# Configuração dos estilos
root.option_add("*Font", "Arial 10")
frame.config(bg="#f0f0f0", bd=2, relief="groove")
entry_origem.config(bd=2, relief="sunken")
entry_destino.config(bd=2, relief="sunken")
txt_log.config(bd=2, relief="sunken")

# Executa o loop principal da janela
root.mainloop()