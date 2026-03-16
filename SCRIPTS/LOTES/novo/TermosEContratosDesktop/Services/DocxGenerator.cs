using System;
using System.IO;
using System.Linq;
using Xceed.Document.NET;
using Xceed.Words.NET;
using TermosEContratosDesktop.Models;
using TermosEContratosDesktop.Utils;

namespace TermosEContratosDesktop.Services
{
    public class DocxGenerator
    {
        private static readonly string LOGO_PATH = @"c:\Users\thalissom.cruz\Desktop\PORTIFOLIO\SCRIPTS\LOTES\novo\backend\assets\logoazulvalle.png";

        public byte[] GerarTermoQuitacao(LoteQuitado lote, Empresa empresa, Cliente cliente, DateTime dataDocumento, string ultimoRecebimento)
        {
            using (var stream = new MemoryStream())
            {
                using (var doc = DocX.Create(stream))
                {
                    // === PAGE SETUP: match Python 210x297mm, margins in points ===
                    doc.MarginLeft  = 56.7f;  // ~20mm
                    doc.MarginRight = 42.5f;  // ~15mm
                    doc.MarginTop   = 70.9f;  // ~25mm
                    doc.MarginBottom= 42.5f;  // ~15mm

                    // === HEADER: Logo ===
                    doc.AddHeaders();
                    doc.AddFooters();
                    var header = doc.Headers.Odd;
                    var footer = doc.Footers.Odd;

                    try
                    {
                        if (File.Exists(LOGO_PATH))
                        {
                            var pHeader = header.InsertParagraph();
                            pHeader.Alignment = Alignment.center;
                            var img = doc.AddImage(LOGO_PATH);
                            var pic = img.CreatePicture();
                            // Scale to ~7cm width
                            double scale = 198.425 / pic.Width;
                            pic.Width  = (int)198.425;
                            pic.Height = (int)(pic.Height * scale);
                            pHeader.AppendPicture(pic);
                        }
                    }
                    catch { /* Logo não crítico */ }

                    // === FOOTER: website ===
                    var pFooter = footer.InsertParagraph();
                    pFooter.Alignment = Alignment.center;
                    pFooter.Append("www.valleprime.com.br")
                           .Font("Helvetica").FontSize(9);

                    // === TÍTULO ===
                    var pTitle = doc.InsertParagraph();
                    pTitle.Alignment = Alignment.center;
                    pTitle.Append("TERMO DE QUITAÇÃO")
                          .Bold().Font("Helvetica").FontSize(24);

                    var pSub = doc.InsertParagraph();
                    pSub.Alignment = Alignment.center;
                    pSub.Append("DE LOTE/TERRENO")
                        .Bold().Font("Helvetica").FontSize(20);
                    pSub.SpacingAfter(20d);

                    // === VENDEDORA ===
                    var pVend = doc.InsertParagraph();
                    pVend.Append("VENDEDORA: ").Bold().Font("Helvetica").FontSize(10);
                    pVend.Append($"{empresa.RazaoSocial}, pessoa jurídica de direito privado, CNPJ {empresa.CnpjFormatado}, com sede à {empresa.EnderecoCompleto}, Bairro {empresa.Bairro}, CEP {empresa.CEP} Município de {empresa.Cidade} - {empresa.UF}.")
                         .Font("Helvetica").FontSize(10);
                    pVend.SpacingAfter(8d);

                    // === COMPRADOR ===
                    var pComp = doc.InsertParagraph();
                    pComp.Append("COMPRADOR: ").Bold().Font("Helvetica").FontSize(10);
                    string rgStr = !string.IsNullOrEmpty(cliente.RG)
                        ? $", RG nº {cliente.RG} {cliente.OrgaoExpedidor}".Trim()
                        : "";
                    pComp.Append($"{cliente.Nome}, CPF/CNPJ nº {cliente.CpfCnpjFormatado}{rgStr}, residente e domiciliado à {cliente.Endereco}, Número {cliente.Numero}, Bairro {cliente.Bairro}, CEP {cliente.CEP}, Município de {cliente.Cidade} - {cliente.UF}.")
                         .Font("Helvetica").FontSize(10);
                    pComp.SpacingAfter(20d);

                    // === TABELA LOTE ===
                    var table = doc.InsertTable(2, 4);
                    table.Alignment = Alignment.center;
                    table.Design = TableDesign.TableGrid;
                    table.AutoFit = AutoFit.Contents;

                    string[] headers = { "LOTE/TERRENO", "QUADRA", "ÁREA TOTAL", "SITUAÇÃO" };
                    for (int i = 0; i < 4; i++)
                    {
                        var p = table.Rows[0].Cells[i].Paragraphs[0];
                        p.Alignment = Alignment.center;
                        p.Append(headers[i]).Bold().Font("Helvetica").FontSize(10);
                    }

                    string[] vals = { lote.Lote, lote.Quadra, $"{lote.AreaFormatada} m²", "QUITADO" };
                    for (int i = 0; i < 4; i++)
                    {
                        var p = table.Rows[1].Cells[i].Paragraphs[0];
                        p.Alignment = Alignment.center;
                        p.Append(vals[i]).Font("Helvetica").FontSize(10);
                    }

                    doc.InsertParagraph().SpacingAfter(10d);

                    // === DA AUTORIZAÇÃO PARA ESCRITURA ===
                    doc.InsertParagraph()
                       .Append("DA AUTORIZAÇÃO PARA ESCRITURA")
                       .Bold().Font("Helvetica").FontSize(10);

                    string cidadeDocumento = !string.IsNullOrWhiteSpace(lote.CidadeObra)
                        ? lote.CidadeObra.ToUpper()
                        : Formatador.NormalizeCityName(lote.NomeObra, "");
                    string ufDocumento = !string.IsNullOrWhiteSpace(lote.UfObra)
                        ? lote.UfObra.ToUpper()
                        : empresa.UF.ToUpper();

                    var pAut = doc.InsertParagraph();
                    pAut.Alignment = Alignment.both;
                    pAut.Append($"A VENDEDORA DECLARA QUE TODAS AS OBRIGAÇÕES CONTRATUAIS DO COMPRADOR ESTÃO QUITADAS E, POR ISSO, AUTORIZA O CARTÓRIO DE REGISTRO DE IMÓVEIS DA COMARCA DE {cidadeDocumento} - {ufDocumento}, A LAVRAR ESCRITURA PÚBLICA DE COMPRA E VENDA DO IMÓVEL IDENTIFICADO NO PREÂMBULO EM FAVOR DO COMPRADOR ACIMA QUALIFICADO.")
                       .Font("Helvetica").FontSize(10);

                    // === DO PREÇO ===
                    doc.InsertParagraph()
                       .Append("DO PREÇO")
                       .Bold().Font("Helvetica").FontSize(10);

                    var pPr = doc.InsertParagraph();
                    pPr.Alignment = Alignment.both;
                    pPr.Append("O VALOR DO LOTE/TERRENO É DE ").Font("Helvetica").FontSize(10);
                    pPr.Append(Formatador.FormatarMoeda(lote.ValorFinal)).Bold().Font("Helvetica").FontSize(10);
                    pPr.Append(", QUE JÁ FOI QUITADO PERANTE A VENDEDORA EM ").Font("Helvetica").FontSize(10);
                    pPr.Append($"{ultimoRecebimento}.").Bold().Font("Helvetica").FontSize(10);

                    // === DA VALIDADE ===
                    doc.InsertParagraph()
                       .Append("DA VALIDADE")
                       .Bold().Font("Helvetica").FontSize(10);

                    var pVal = doc.InsertParagraph();
                    pVal.Alignment = Alignment.both;
                    pVal.Append("A PRESENTE AUTORIZAÇÃO TERÁ VALIDADE DE 120 (CENTO E VINTE) DIAS, A CONTAR DA DATA DE SUA EMISSÃO.")
                        .Font("Helvetica").FontSize(10);

                    doc.InsertParagraph().SpacingAfter(8d);

                    var pFirm = doc.InsertParagraph();
                    pFirm.Alignment = Alignment.both;
                    pFirm.Append("POR SER EXPRESSÃO DA VERDADE, FIRMAMOS A PRESENTE EM 03 (TRÊS) VIAS DE IGUAL TEOR E FORMA.")
                         .Font("Helvetica").FontSize(10);

                    doc.InsertParagraph().SpacingAfter(20d);

                    // === LOCAL E DATA ===
                    string[] meses = { "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO",
                                       "JUNHO", "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO" };
                    string cidadeEmissao = !string.IsNullOrWhiteSpace(lote.CidadeObra)
                        ? Formatador.NormalizeCityName(lote.CidadeObra + " " + lote.NomeObra, "")
                        : Formatador.NormalizeCityName(lote.NomeObra, empresa.CEP);
                    string ufEmissao = !string.IsNullOrWhiteSpace(lote.UfObra) ? lote.UfObra.ToUpper() : empresa.UF.ToUpper();

                    string localData = $"{cidadeEmissao} - {ufEmissao}, {dataDocumento.Day} DE {meses[dataDocumento.Month - 1]} DE {dataDocumento.Year}.";
                    var pData = doc.InsertParagraph();
                    pData.Alignment = Alignment.right;
                    pData.Append(localData).Font("Helvetica").FontSize(10);

                    doc.InsertParagraph().SpacingAfter(40d);

                    // === ASSINATURAS ===
                    var pAss1 = doc.InsertParagraph();
                    pAss1.Alignment = Alignment.center;
                    pAss1.Append("__________________________________________________________________").Bold();
                    pAss1.AppendLine(empresa.RazaoSocial.ToUpper()).Bold().Font("Helvetica").FontSize(10);
                    pAss1.SpacingAfter(40d);

                    var pAss2 = doc.InsertParagraph();
                    pAss2.Alignment = Alignment.left;
                    string lineStr = new string('_', Math.Max(43, (int)(cliente.Nome.Length * 1.3)));
                    pAss2.Append(lineStr).Bold();
                    pAss2.AppendLine(cliente.Nome.ToUpper()).Bold().Font("Helvetica").FontSize(10);
                    pAss2.SpacingAfter(40d);

                    // === TESTEMUNHAS ===
                    doc.InsertParagraph()
                       .Append("TESTEMUNHAS:")
                       .Bold().Font("Helvetica").FontSize(10)
                       .SpacingAfter(40d);

                    var ttable = doc.InsertTable(3, 3);
                    ttable.AutoFit = AutoFit.ColumnWidth;
                    ttable.Design = TableDesign.None;

                    // Set column widths
                    foreach (var row in ttable.Rows)
                    {
                        row.Cells[0].Width = 198.425; // ~7cm
                        row.Cells[1].Width = 85;       // spacer
                        row.Cells[2].Width = 198.425;
                    }

                    ttable.Rows[0].Cells[0].Paragraphs[0].Append("_____________________________").Font("Helvetica").FontSize(10);
                    ttable.Rows[0].Cells[2].Paragraphs[0].Append("_____________________________").Font("Helvetica").FontSize(10);
                    ttable.Rows[1].Cells[0].Paragraphs[0].Append("NOME:").Font("Helvetica").FontSize(10);
                    ttable.Rows[1].Cells[2].Paragraphs[0].Append("NOME:").Font("Helvetica").FontSize(10);
                    ttable.Rows[2].Cells[0].Paragraphs[0].Append("CPF:").Font("Helvetica").FontSize(10);
                    ttable.Rows[2].Cells[2].Paragraphs[0].Append("CPF:").Font("Helvetica").FontSize(10);

                    doc.Save();
                }
                return stream.ToArray();
            }
        }
    }
}
