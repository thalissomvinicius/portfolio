from docxtpl import DocxTemplate

def generate_docx(template_path, data, output_path):
    """
    Carrega um template .docx, preenche com os dados e salva no output_path.
    """
    try:
        doc = DocxTemplate(template_path)
        doc.render(data)
        doc.save(output_path)
        return True
    except Exception as e:
        print(f"Erro ao gerar documento: {e}")
        raise e
