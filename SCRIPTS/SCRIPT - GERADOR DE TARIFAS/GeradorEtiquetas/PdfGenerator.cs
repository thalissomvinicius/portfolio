using PdfSharp.Drawing;
using PdfSharp.Pdf;
using PdfSharp.Fonts;
using GeradorEtiquetas.Models;

namespace GeradorEtiquetas;

public class PdfGenerator
{
    // Configurações da Folha TB4263 (14 etiquetas por folha: 2 colunas x 7 linhas)
    private const double LabelWidthMm = 99.1;
    private const double LabelHeightMm = 38.1;
    private const double VerticalStepMm = 38.2;
    private const double MarginLeftMm = 5.9;
    private const double MarginTopMm = 15.1;

    // Compensações progressivas por linha (valores menores = subir)
    private static readonly double[] LineCompensations = { 0, 0, 0, 0, -1.0, -2.0, -3.0 };

    private const int LabelsPerPage = 14;
    private const int Columns = 2;
    private const int Rows = 7;

    // Conversão mm para pontos PDF (1 mm = 2.834645669 pontos)
    private static double MmToPoints(double mm) => mm * 2.834645669;

    static PdfGenerator()
    {
        // Registrar o resolver de fontes do Windows
        if (GlobalFontSettings.FontResolver == null)
        {
            GlobalFontSettings.FontResolver = new WindowsFontResolver();
        }
    }

    public string GerarPdf(List<(ClienteInfo Cliente, EnderecoInfo Endereco, List<string> Telefones)> dados, string empresaNome)
    {
        var tempDir = Path.GetTempPath();
        var timestamp = DateTime.Now.ToString("yyyyMMdd_HHmmss");
        var filename = Path.Combine(tempDir, $"Etiquetas_TB4263_{timestamp}.pdf");

        using var document = new PdfDocument();
        document.Info.Title = "Etiquetas TB4263";

        var pageWidth = MmToPoints(210);  // A4
        var pageHeight = MmToPoints(297); // A4
        var labelWidth = MmToPoints(LabelWidthMm);
        var labelHeight = MmToPoints(LabelHeightMm);
        var marginLeft = MmToPoints(MarginLeftMm);
        var marginTop = MmToPoints(MarginTopMm);
        var verticalStep = MmToPoints(VerticalStepMm);

        // Calcular posições Y (de cima para baixo)
        double[] yPositions = new double[Rows];
        for (int row = 0; row < Rows; row++)
        {
            var offset = row * verticalStep + MmToPoints(LineCompensations[row]);
            yPositions[row] = marginTop + offset;
        }

        // Posições X
        double[] xPositions = { marginLeft, marginLeft + labelWidth };

        PdfPage? page = null;
        XGraphics? gfx = null;

        var fontBold = new XFont("Arial", 10, XFontStyleEx.Bold);
        var fontRegular = new XFont("Arial", 10, XFontStyleEx.Regular);
        var fontSmallBold = new XFont("Arial", 9, XFontStyleEx.Bold);
        var fontSmall = new XFont("Arial", 9, XFontStyleEx.Regular);

        int idx = 0;
        int totalEtiquetas = 0;

        foreach (var (cliente, endereco, telefones) in dados)
        {
            // Nova página a cada 14 etiquetas
            if (idx % LabelsPerPage == 0)
            {
                page = document.AddPage();
                page.Width = XUnit.FromMillimeter(210);
                page.Height = XUnit.FromMillimeter(297);
                gfx = XGraphics.FromPdfPage(page);
                idx = 0;
            }

            if (gfx == null) continue;

            int col = idx % Columns;
            int row = (idx / Columns) % Rows;

            double x = xPositions[col];
            double y = yPositions[row];
            double pad = MmToPoints(4);
            double textX = x + pad;
            double textY = y + pad + 10; // Offset para texto

            // 1. Nome do Empreendimento
            gfx.DrawString(empresaNome, fontBold, XBrushes.Black, textX, textY);

            // 2. Nome do Cliente
            textY += MmToPoints(4.5);
            gfx.DrawString("NOME: ", fontBold, XBrushes.Black, textX, textY);
            var nome = cliente.NomeCliente.Length > 45 ? cliente.NomeCliente[..45] : cliente.NomeCliente;
            gfx.DrawString(nome, fontRegular, XBrushes.Black, textX + MmToPoints(13), textY);

            // 3. Endereço
            textY += MmToPoints(4);
            gfx.DrawString("ENDEREÇO: ", fontSmallBold, XBrushes.Black, textX, textY);
            var end = endereco.Endereco.Length > 50 ? endereco.Endereco[..50] : endereco.Endereco;
            gfx.DrawString(end, fontSmall, XBrushes.Black, textX + MmToPoints(20), textY);

            // 4. Complementos
            textY += MmToPoints(4);
            gfx.DrawString($"Nº: {endereco.Numero} - {endereco.Bairro} - {endereco.Cidade}", fontSmall, XBrushes.Black, textX, textY);

            // 5. Contrato / Quadra / Lote
            textY += MmToPoints(4.5);
            gfx.DrawString("CONTRATO: ", fontSmallBold, XBrushes.Black, textX, textY);
            gfx.DrawString(cliente.NumeroVenda.ToString(), fontSmall, XBrushes.Black, textX + MmToPoints(19), textY);
            gfx.DrawString("QUADRA: ", fontSmallBold, XBrushes.Black, textX + MmToPoints(33), textY);
            gfx.DrawString(cliente.Quadra, fontSmall, XBrushes.Black, textX + MmToPoints(48), textY);
            gfx.DrawString("LOTE: ", fontSmallBold, XBrushes.Black, textX + MmToPoints(63), textY);
            gfx.DrawString(cliente.Lote, fontSmall, XBrushes.Black, textX + MmToPoints(74), textY);

            // 6. Telefones
            textY += MmToPoints(4);
            gfx.DrawString("TEL: ", fontSmallBold, XBrushes.Black, textX, textY);
            var tels = string.Join(", ", telefones);
            if (tels.Length > 55) tels = tels[..55];
            gfx.DrawString(tels, fontSmall, XBrushes.Black, textX + MmToPoints(8), textY);

            idx++;
            totalEtiquetas++;
        }

        document.Save(filename);
        return filename;
    }
}
