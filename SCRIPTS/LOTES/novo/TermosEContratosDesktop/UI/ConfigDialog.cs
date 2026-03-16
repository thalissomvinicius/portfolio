using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Windows.Forms;
using TermosEContratosDesktop.Models;
using TermosEContratosDesktop.Services;

namespace TermosEContratosDesktop.UI
{
    public partial class ConfigDialog : Form
    {
        private readonly LoteQuitado _lote;
        private readonly Empresa _empresa;
        private readonly string _tipoDoc;
        private readonly CalculoQuitacaoService _calcService = new();
        private readonly PdfGenerator _pdfGen = new();
        private readonly DocxGenerator _docxGen = new();

        public ConfigDialog(LoteQuitado lote, Empresa empresa, string tipoDoc)
        {
            InitializeComponent();
            _lote = lote;
            _empresa = empresa;
            _tipoDoc = tipoDoc;

            lblLoteInfo.Text = $"Lote: Q{_lote.Quadra} L{_lote.Lote} - {_lote.Cliente}";
            dtpDataDoc.Value = DateTime.Now;

            if (_tipoDoc == "carta")
            {
                this.Text = "Configurar Carta de Quitação";
                pnlTermoOptions.Visible = false;
                btnGerarWord.Visible = false;
                btnGerarExtrato.Visible = false;
                btnGerarPdf.Text = "📄 Gerar Carta";
            }
            else
            {
                this.Text = "Configurar Termo de Quitação";
                pnlTermoOptions.Visible = true;
                btnGerarWord.Visible = true;
                btnGerarExtrato.Visible = true;
                btnGerarPdf.Text = "📄 Gerar Termo (PDF)";
            }
        }

        private async void btnGerarPdf_Click(object sender, EventArgs e)
        {
            await ProcessarDocumentos("pdf");
        }

        private async void btnGerarWord_Click(object sender, EventArgs e)
        {
            await ProcessarDocumentos("docx");
        }

        private async void btnGerarExtrato_Click(object sender, EventArgs e)
        {
            // Opcional: Gerar extrato em PDF (pode usar o questPDF ou exportar txt/csv)
            MessageBox.Show("Função de Extrato ainda não implementada na versão Desktop.", "Aviso", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }

        private async System.Threading.Tasks.Task ProcessarDocumentos(string formato)
        {
            if (_lote == null || _empresa == null) return;
            
            try
            {
                btnGerarPdf.Enabled = false;
                btnGerarWord.Enabled = false;
                Cursor = Cursors.WaitCursor;

                var tiposSelecionados = ObterTiposParcela();
                var dataDoc = dtpDataDoc.Value;

                // 1. Obter Cliente Mestre
                var clienteRepo = new Repositories.ClienteRepository();
                var numVenda = _lote.NumVenda ?? 0;
                var clientes = await clienteRepo.GetClientesVendaAsync(_empresa.Codigo_Emp, _lote.NomeObra, numVenda);
                var clienteMestre = clientes.FirstOrDefault(c => c.Tipo == 0) ?? clientes.FirstOrDefault() ?? new Cliente();

                // 2. Realizar Cálculo
                var dadosCalc = await _calcService.CalcularValorQuitacaoAsync(_empresa.Codigo_Emp, _lote.NomeObra, _lote.Quadra, _lote.Lote, tiposSelecionados);

                _lote.ValorCalculado = dadosCalc.TotalQuitacao; // Atualiza com o valor exato no momento da geração

                string dataUltimoPg = dadosCalc.UltimoRecebimento?.ToString("dd/MM/yyyy") ?? "-";

                // 3. Gerar Documento
                byte[] bytes = null;
                string ext = formato == "pdf" ? ".pdf" : ".docx";
                string nomeArquivo = $"{_tipoDoc}-Q{_lote.Quadra}-L{_lote.Lote}-{DateTime.Now:yyyyMMddHHmmss}{ext}";
                string path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), nomeArquivo);

                if (_tipoDoc == "carta")
                {
                    bytes = _pdfGen.GerarCartaQuitacao(_lote, _empresa, clienteMestre, dataDoc, dataUltimoPg);
                }
                else if (_tipoDoc == "termo")
                {
                    if (formato == "docx")
                        bytes = _docxGen.GerarTermoQuitacao(_lote, _empresa, clienteMestre, dataDoc, dataUltimoPg);
                    else
                        MessageBox.Show("Termo em PDF ainda não suportado, use Word.", "Aviso");
                }

                if (bytes != null)
                {
                    File.WriteAllBytes(path, bytes);
                    MessageBox.Show($"Documento gerado com sucesso em:\n{path}", "Sucesso", MessageBoxButtons.OK, MessageBoxIcon.Information);
                    System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo() { FileName = path, UseShellExecute = true });
                    this.Close();
                }
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Erro ao gerar documento: {ex.Message}", "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
            finally
            {
                btnGerarPdf.Enabled = true;
                btnGerarWord.Enabled = true;
                Cursor = Cursors.Default;
            }
        }

        private List<string> ObterTiposParcela()
        {
            var selecionados = new List<string>();
            foreach (Control c in pnlTiposParam.Controls)
            {
                if (c is CheckBox chk && chk.Checked && chk.Tag != null)
                {
                    selecionados.Add(chk.Tag.ToString());
                }
            }
            if (!selecionados.Any()) selecionados.AddRange(new[] { "E", "P", "S" });
            return selecionados;
        }

        private void btnCancelar_Click(object sender, EventArgs e)
        {
            this.Close();
        }
    }
}
