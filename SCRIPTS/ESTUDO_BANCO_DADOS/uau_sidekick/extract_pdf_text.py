import pypdf
import os

files = [
    "CONTRATO VALLE DOS IPÊS QUADRA 003 LOTE 022 - LAURICE ALVES RIBEIRO.pdf",
    "TERMO DE QUITAÇÃO.pdf",
    "TRANSFERENCIA.pdf"
]

for file_name in files:
    path = os.path.join(r"c:\Users\thalissom.cruz\Desktop\PORTIFOLIO\SCRIPTS\ESTUDO_BANCO_DADOS\uau_sidekick", file_name)
    print(f"\n--- FILE: {file_name} ---")
    try:
        reader = pypdf.PdfReader(path)
        # Just extract first 2 pages for analysis
        text = ""
        for i in range(min(2, len(reader.pages))):
            text += reader.pages[i].extract_text()
        print(text[:2000]) # Print first 2000 chars
    except Exception as e:
        print(f"Error reading {file_name}: {e}")
