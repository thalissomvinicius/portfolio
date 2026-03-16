import os
import cairosvg
from io import BytesIO

def test_svg_conversion():
    print("=== Testando Conversão SVG com CairoSVG ===")
    logo_path = os.path.join(os.getcwd(), 'assets', 'logoazulvalle.svg')
    output_path = os.path.join(os.getcwd(), 'test_logo_render.png')
    
    if not os.path.exists(logo_path):
        print(f"Erro: Arquivo não encontrado: {logo_path}")
        return

    try:
        cairosvg.svg2png(url=logo_path, write_to=output_path)
        print(f"Sucesso! Imagem salva em: {output_path}")
        
        # Verificar o tamanho do arquivo gerado
        size = os.path.getsize(output_path)
        print(f"Tamanho do arquivo PNG: {size} bytes")
        
        if size < 1000:
            print("AVISO: Arquivo muito pequeno, pode estar vazio ou errado.")
    except Exception as e:
        print(f"ERRO CRÍTICO ao converter SVG: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_svg_conversion()
