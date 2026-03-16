using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;
using TermosEContratosDesktop.Models;
using TermosEContratosDesktop.Utils;
using System;
using System.Linq;

namespace TermosEContratosDesktop.Services
{
    public class PdfGenerator
    {
        public PdfGenerator()
        {
            QuestPDF.Settings.License = LicenseType.Community;
        }

        public byte[] GerarCartaQuitacao(LoteQuitado lote, Empresa empresa, Cliente cliente, DateTime dataDocumento, string dataUltimoPg)
        {
            var document = Document.Create(container =>
            {
                container.Page(page =>
                {
                    page.Size(PageSizes.A4);
                    page.Margin(25, Unit.Millimetre);
                    page.PageColor(Colors.White);
                    page.DefaultTextStyle(x => x.FontSize(12).FontFamily("Helvetica"));

                    page.Header().Element(ComposeHeader);
                    page.Content().Element(c => ComposeContent(c, lote, empresa, cliente, dataDocumento, dataUltimoPg));
                    page.Footer().Element(ComposeFooter);
                });
            });

            return document.GeneratePdf();
        }

        private void ComposeHeader(IContainer container)
        {
            try 
            {
                string logoPath = @"c:\Users\thalissom.cruz\Desktop\PORTIFOLIO\SCRIPTS\LOTES\novo\backend\assets\logoazulvalle.png";
                if (System.IO.File.Exists(logoPath))
                {
                    container.AlignCenter().Height(60).Image(logoPath);
                }
            }
            catch {}
        }

        private void ComposeContent(IContainer container, LoteQuitado lote, Empresa empresa, Cliente cliente, DateTime dataDocumento, string dataUltimoPg)
        {
            container.PaddingTop(1, Unit.Centimetre).Column(col =>
            {
                col.Spacing(20);
                
                col.Item().Text("DECLARAÇÃO DE QUITAÇÃO").Bold().FontSize(14).AlignCenter();
                
                col.Item().PaddingTop(10).Text(txt =>
                {
                    txt.Justify();
                    txt.Span("A ").FontSize(12);
                    txt.Span(empresa.RazaoSocial).Bold().FontSize(12);
                    txt.Span($", com sede na {empresa.EnderecoCompleto}, {empresa.Bairro}, {empresa.Cidade} - {empresa.UF}, Inscrita no CNPJ/MF sob o Nº {empresa.CnpjFormatado}, neste ato representada por, ").FontSize(12);
                    txt.Span("RAIMUNDA DAS GRAÇAS P. MARQUES").Bold().FontSize(12);
                    txt.Span(", Casada, Gerente Administrativa, portador da cédula de identidade RG Nº 2148954 e inscrito no CPF/MF Nº 352.369.222-91 domiciliado em Tomé-Açu-PA, ").FontSize(12);
                    txt.Span("DECLARA").Bold().FontSize(12);
                    txt.Span(", para os devidos fins de direito, que O Sr(a). ").FontSize(12);
                    txt.Span(cliente.Nome).Bold().FontSize(12);
                    txt.Span(" portador CPF/CNPJ Nº ").FontSize(12);
                    txt.Span(cliente.CpfCnpjFormatado).Bold().FontSize(12);
                    txt.Span(", promitente comprador do imóvel constituído pela unidade designada ").FontSize(12);
                    txt.Span($"QUADRA {lote.Quadra} LOTE {lote.Lote}").Bold().FontSize(12);
                    txt.Span(" do empreendimento denominado em \"").FontSize(12);
                    txt.Span(lote.NomeObra).Bold().FontSize(12);
                    txt.Span("\", pagou integralmente as parcelas do financiamento do preço de venda previstas no Instrumento Particular de Promessa de Venda e Compra quitado em ").FontSize(12);
                    txt.Span(dataUltimoPg).Bold().FontSize(12);
                    txt.Span(".").FontSize(12);
                });
                
                // Data Local
                string[] meses = { "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO" };
                
                // Normalize City properly
                var localData = $"{Formatador.NormalizeCityName(lote.NomeObra, empresa.CEP)} - {empresa.UF}, {dataDocumento.Day} de {meses[dataDocumento.Month - 1].ToLower()} de {dataDocumento.Year}.";
                
                col.Item().PaddingTop(20).Text(localData).AlignRight();

                // Assinatura
                col.Item().PaddingTop(50).Column(assinatura =>
                {
                    assinatura.Item().Text("________________________________________________").AlignCenter();
                    assinatura.Item().PaddingTop(15).Text("RAIMUNDA DAS GRAÇAS P. MARQUES").Bold().AlignCenter();
                    assinatura.Item().Text("Gerente Administrativa").AlignCenter();
                });
            });
        }

        private void ComposeFooter(IContainer container)
        {
            container.AlignCenter().Text(x =>
            {
                x.Span("www.valleprime.com.br").FontSize(9).FontColor(Colors.Grey.Medium);
                x.Span("   |   ");
                x.Span("Página ");
                x.CurrentPageNumber();
            });
        }
    }
}
