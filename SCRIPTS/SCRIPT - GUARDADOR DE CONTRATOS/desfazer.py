import os
import shutil

def desfazer_organizacao(diretorio_origem, diretorio_destino_ml, diretorio_destino_valle):
    print(f"Iniciando a reversão da organização dos arquivos das pastas: {diretorio_destino_ml} e {diretorio_destino_valle}")
    
    # Função para mover arquivos de volta para o diretório de origem e remover diretórios vazios
    def mover_arquivos_e_remover_diretorios(diretorio_destino):
        for quadra in os.listdir(diretorio_destino):
            caminho_quadra = os.path.join(diretorio_destino, quadra)
            
            if os.path.isdir(caminho_quadra):
                # Percorre todos os diretórios de lote dentro da quadra
                for lote in os.listdir(caminho_quadra):
                    caminho_lote = os.path.join(caminho_quadra, lote)
                    
                    if os.path.isdir(caminho_lote):
                        # Move todos os arquivos de volta para o diretório de origem
                        for arquivo in os.listdir(caminho_lote):
                            caminho_arquivo = os.path.join(caminho_lote, arquivo)
                            if os.path.isfile(caminho_arquivo):
                                destino_arquivo = os.path.join(diretorio_origem, arquivo)
                                print(f"Movendo o arquivo de volta para: {destino_arquivo}")
                                shutil.move(caminho_arquivo, destino_arquivo)
                        
                        # Remove o diretório de lote se estiver vazio
                        if not os.listdir(caminho_lote):
                            print(f"Removendo o diretório vazio: {caminho_lote}")
                            os.rmdir(caminho_lote)
                
                # Remove o diretório de quadra se estiver vazio
                if not os.listdir(caminho_quadra):
                    print(f"Removendo o diretório vazio: {caminho_quadra}")
                    os.rmdir(caminho_quadra)
    
    # Desfazer a organização na pasta ML
    mover_arquivos_e_remover_diretorios(diretorio_destino_ml)
    
    # Desfazer a organização na pasta VALLE
    mover_arquivos_e_remover_diretorios(diretorio_destino_valle)
    
    print("Reversão da organização concluída.")

# Diretórios de exemplo
diretorio_origem = r'C:\Users\thalissom.cruz\Desktop\CONTRATOS'
diretorio_destino_ml = r'C:\Users\thalissom.cruz\Desktop\CONTRATO ARQUIVADOS\ARQUIVO\ML'
diretorio_destino_valle = r'C:\Users\thalissom.cruz\Desktop\CONTRATO ARQUIVADOS\ARQUIVO\VALLE'

desfazer_organizacao(diretorio_origem, diretorio_destino_ml, diretorio_destino_valle)