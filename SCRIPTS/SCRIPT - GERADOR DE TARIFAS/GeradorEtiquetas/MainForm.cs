using GeradorEtiquetas.Models;

namespace GeradorEtiquetas;

public partial class MainForm : Form
{
    private DatabaseService? _dbService;
    private readonly PdfGenerator _pdfGenerator;

    // Cores do tema
    private static readonly Color PrimaryBlue = Color.FromArgb(37, 99, 235);     // #2563EB
    private static readonly Color LightBlue = Color.FromArgb(59, 130, 246);      // #3B82F6
    private static readonly Color DarkBlue = Color.FromArgb(30, 64, 175);        // #1E40AF
    private static readonly Color BackgroundWhite = Color.FromArgb(249, 250, 251);
    private static readonly Color CardWhite = Color.White;
    private static readonly Color TextDark = Color.FromArgb(31, 41, 55);
    private static readonly Color TextGray = Color.FromArgb(107, 114, 128);
    private static readonly Color SuccessGreen = Color.FromArgb(34, 197, 94);
    private static readonly Color ErrorRed = Color.FromArgb(239, 68, 68);

    // Controles do Formulário
    private ComboBox cmbEmpresa = null!;
    private TextBox txtVendas = null!;
    private TextBox txtResultado = null!;
    private Button btnVerificar = null!;
    private Button btnGerarPdf = null!;
    private Button btnLimpar = null!;
    private Button btnSair = null!;
    private ProgressBar progressBar = null!;
    private Label lblStatus = null!;

    public MainForm()
    {
        _pdfGenerator = new PdfGenerator();
        InitializeComponents();
    }

    private void InitializeComponents()
    {
        // Configuração do Form
        Text = "Gerador de Etiquetas para Carnês";
        Size = new Size(920, 800);
        StartPosition = FormStartPosition.CenterScreen;
        BackColor = BackgroundWhite;
        Font = new Font("Segoe UI", 9F);
        FormBorderStyle = FormBorderStyle.FixedSingle;
        MaximizeBox = false;

        // Carregar ícone se existir
        try {
            if (File.Exists("app_new.ico")) {
                this.Icon = new Icon("app_new.ico");
            }
        } catch { /* Ignorar se falhar */ }

        // === HEADER PANEL ===
        var headerPanel = new Panel
        {
            Dock = DockStyle.Top,
            Height = 85,
            BackColor = PrimaryBlue
        };
        Controls.Add(headerPanel);

        // Ícone
        var lblIcon = new Label
        {
            Text = "🏷️",
            Font = new Font("Segoe UI Emoji", 28),
            ForeColor = Color.White,
            AutoSize = true,
            Location = new Point(25, 18)
        };
        headerPanel.Controls.Add(lblIcon);

        // Título
        var lblTitulo = new Label
        {
            Text = "Gerador de Etiquetas para Carnês",
            Font = new Font("Segoe UI", 18, FontStyle.Bold),
            ForeColor = Color.White,
            AutoSize = true,
            Location = new Point(100, 18)
        };
        headerPanel.Controls.Add(lblTitulo);

        // Subtítulo
        var lblSubtitulo = new Label
        {
            Text = "Sistema de impressão de etiquetas TB4263",
            Font = new Font("Segoe UI", 9),
            ForeColor = Color.FromArgb(200, 220, 255),
            AutoSize = true,
            Location = new Point(100, 50)
        };
        headerPanel.Controls.Add(lblSubtitulo);

        // Container principal (Card)
        var mainCard = new Panel
        {
            Location = new Point(25, 100),
            Size = new Size(855, 645),
            BackColor = CardWhite,
            Padding = new Padding(25)
        };
        // Borda arredondada simulada
        mainCard.Paint += (s, e) =>
        {
            using var pen = new Pen(Color.FromArgb(229, 231, 235), 1);
            e.Graphics.DrawRectangle(pen, 0, 0, mainCard.Width - 1, mainCard.Height - 1);
        };
        Controls.Add(mainCard);

        int currentY = 15;

        // === SELEÇÃO DE EMPRESA ===
        var lblEmpresa = new Label
        {
            Text = "Selecione a Empresa",
            Location = new Point(15, currentY),
            AutoSize = true,
            ForeColor = TextDark,
            Font = new Font("Segoe UI", 10, FontStyle.Bold)
        };
        mainCard.Controls.Add(lblEmpresa);
        currentY += 28;

        cmbEmpresa = new ComboBox
        {
            Location = new Point(15, currentY),
            Size = new Size(400, 32),
            DropDownStyle = ComboBoxStyle.DropDownList,
            Font = new Font("Segoe UI", 11),
            BackColor = Color.White,
            ForeColor = TextDark,
            FlatStyle = FlatStyle.Flat
        };
        cmbEmpresa.Items.AddRange(DatabaseService.Empresas.Keys.ToArray());
        cmbEmpresa.SelectedIndex = 2;
        mainCard.Controls.Add(cmbEmpresa);
        currentY += 50;

        // === ENTRADA DE VENDAS ===
        var lblVendas = new Label
        {
            Text = "Números de Venda (um por linha)",
            Location = new Point(15, currentY),
            AutoSize = true,
            ForeColor = TextDark,
            Font = new Font("Segoe UI", 10, FontStyle.Bold)
        };
        mainCard.Controls.Add(lblVendas);
        currentY += 28;

        txtVendas = new TextBox
        {
            Location = new Point(15, currentY),
            Size = new Size(810, 100),
            Multiline = true,
            ScrollBars = ScrollBars.Vertical,
            Font = new Font("Consolas", 11),
            BackColor = Color.White,
            ForeColor = TextDark,
            BorderStyle = BorderStyle.FixedSingle
        };
        mainCard.Controls.Add(txtVendas);
        currentY += 110;

        // === BOTÕES DE AÇÃO ===
        btnVerificar = CreateStyledButton("🔍 Verificar Dados", PrimaryBlue, 15, currentY, true);
        btnVerificar.Click += BtnVerificar_Click;
        mainCard.Controls.Add(btnVerificar);

        btnGerarPdf = CreateStyledButton("📄 Gerar PDF", SuccessGreen, 210, currentY, true);
        btnGerarPdf.Click += BtnGerarPdf_Click;
        mainCard.Controls.Add(btnGerarPdf);

        currentY += 55;

        // === BARRA DE PROGRESSO ===
        progressBar = new ProgressBar
        {
            Location = new Point(15, currentY),
            Size = new Size(810, 8),
            Style = ProgressBarStyle.Continuous,
            Visible = false
        };
        mainCard.Controls.Add(progressBar);

        lblStatus = new Label
        {
            Location = new Point(15, currentY + 12),
            Size = new Size(810, 22),
            ForeColor = TextGray,
            Font = new Font("Segoe UI", 9),
            Text = ""
        };
        mainCard.Controls.Add(lblStatus);
        currentY += 38;

        // === RESULTADO ===
        var lblResultado = new Label
        {
            Text = "Resultado",
            Location = new Point(15, currentY),
            AutoSize = true,
            ForeColor = TextDark,
            Font = new Font("Segoe UI", 10, FontStyle.Bold)
        };
        mainCard.Controls.Add(lblResultado);
        currentY += 28;

        txtResultado = new TextBox
        {
            Location = new Point(15, currentY),
            Size = new Size(810, 220),
            Multiline = true,
            ScrollBars = ScrollBars.Vertical,
            ReadOnly = true,
            BackColor = Color.FromArgb(248, 250, 252),
            ForeColor = TextDark,
            Font = new Font("Consolas", 9),
            BorderStyle = BorderStyle.FixedSingle
        };
        mainCard.Controls.Add(txtResultado);
        currentY += 230;

        // === BARRA INFERIOR ===
        btnLimpar = CreateStyledButton("Limpar", Color.FromArgb(156, 163, 175), 590, currentY, false);
        btnLimpar.Size = new Size(110, 38);
        btnLimpar.Click += (s, e) => LimparCampos();
        mainCard.Controls.Add(btnLimpar);

        btnSair = CreateStyledButton("Sair", ErrorRed, 710, currentY, false);
        btnSair.Size = new Size(110, 38);
        btnSair.Click += (s, e) => Close();
        mainCard.Controls.Add(btnSair);
    }

    private Button CreateStyledButton(string text, Color backColor, int x, int y, bool isPrimary)
    {
        var btn = new Button
        {
            Text = text,
            Size = new Size(180, 45),
            Location = new Point(x, y),
            BackColor = backColor,
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat,
            Cursor = Cursors.Hand,
            Font = new Font("Segoe UI", 10, isPrimary ? FontStyle.Bold : FontStyle.Regular)
        };
        btn.FlatAppearance.BorderSize = 0;
        btn.FlatAppearance.MouseOverBackColor = ControlPaint.Dark(backColor, 0.1f);
        return btn;
    }

    private void AtualizarStatus(string texto, bool mostrarProgresso = false)
    {
        lblStatus.Text = texto;
        progressBar.Visible = mostrarProgresso;
        Application.DoEvents();
    }

    private void AtualizarProgresso(int valor, int maximo)
    {
        progressBar.Maximum = maximo;
        progressBar.Value = Math.Min(valor, maximo);
        Application.DoEvents();
    }

    private List<int> ObterVendasValidas()
    {
        var vendas = new List<int>();
        var linhas = txtVendas.Text.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);

        foreach (var linha in linhas)
        {
            if (int.TryParse(linha.Trim(), out int venda))
            {
                vendas.Add(venda);
            }
        }

        return vendas;
    }

    private EmpresaConfig ObterEmpresaSelecionada()
    {
        var empresaNome = cmbEmpresa.SelectedItem?.ToString() ?? "VALLE DO IPITINGA II";
        return DatabaseService.Empresas[empresaNome];
    }

    private void BtnVerificar_Click(object? sender, EventArgs e)
    {
        var vendas = ObterVendasValidas();
        if (vendas.Count == 0)
        {
            MessageBox.Show("Insira ao menos um número de venda válido.", "Aviso", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        AtualizarStatus("Conectando ao banco de dados...", true);

        _dbService ??= new DatabaseService();
        if (!_dbService.Conectar())
        {
            AtualizarStatus("");
            return;
        }

        var config = ObterEmpresaSelecionada();
        txtResultado.Clear();

        int total = vendas.Count;
        int atual = 0;

        foreach (var venda in vendas)
        {
            atual++;
            AtualizarProgresso(atual, total);
            AtualizarStatus($"Buscando venda {venda}... ({atual}/{total})");

            try
            {
                var cliente = _dbService.ObterInformacoesCliente(venda, config.Empresa, config.Obra);
                if (cliente == null)
                {
                    txtResultado.AppendText($"⚠ CONTRATO {venda}: NÃO ENCONTRADO\r\n");
                    txtResultado.AppendText(new string('─', 60) + "\r\n");
                    continue;
                }

                var telefones = _dbService.ObterTelefonesCliente(cliente.CodigoCliente);
                var endereco = _dbService.ObterEnderecoCliente(cliente.CodigoCliente);

                var texto = $"✓ CLIENTE: {cliente.NomeCliente}\r\n" +
                           $"  CONTRATO: {cliente.NumeroVenda} | QUADRA: {cliente.Quadra} | LOTE: {cliente.Lote}\r\n" +
                           $"  ENDEREÇO: {endereco.Endereco}, {endereco.Numero}\r\n" +
                           $"  BAIRRO: {endereco.Bairro} | CIDADE: {endereco.Cidade}\r\n" +
                           $"  TELS: {string.Join(", ", telefones)}\r\n" +
                           new string('─', 60) + "\r\n";

                txtResultado.AppendText(texto);
            }
            catch (Exception ex)
            {
                txtResultado.AppendText($"✗ ERRO NA VENDA {venda}: {ex.Message}\r\n");
            }
        }

        progressBar.Visible = false;
        AtualizarStatus($"Concluído! {atual} vendas processadas.");
    }

    private void BtnGerarPdf_Click(object? sender, EventArgs e)
    {
        var vendas = ObterVendasValidas();
        if (vendas.Count == 0)
        {
            MessageBox.Show("Insira as vendas para gerar o PDF.", "Aviso", MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        AtualizarStatus("Conectando ao banco de dados...", true);

        _dbService ??= new DatabaseService();
        if (!_dbService.Conectar())
        {
            AtualizarStatus("");
            return;
        }

        var config = ObterEmpresaSelecionada();
        var empresaNome = cmbEmpresa.SelectedItem?.ToString() ?? "VALLE";
        var dados = new List<(ClienteInfo, EnderecoInfo, List<string>)>();

        int total = vendas.Count;
        int atual = 0;

        foreach (var venda in vendas)
        {
            atual++;
            AtualizarProgresso(atual, total);
            AtualizarStatus($"Coletando dados da venda {venda}... ({atual}/{total})");

            try
            {
                var cliente = _dbService.ObterInformacoesCliente(venda, config.Empresa, config.Obra);
                if (cliente == null) continue;

                var endereco = _dbService.ObterEnderecoCliente(cliente.CodigoCliente);
                var telefones = _dbService.ObterTelefonesCliente(cliente.CodigoCliente);
                dados.Add((cliente, endereco, telefones));
            }
            catch
            {
                // Ignorar erros individuais
            }
        }

        if (dados.Count == 0)
        {
            progressBar.Visible = false;
            AtualizarStatus("");
            MessageBox.Show("Nenhum dado válido encontrado para gerar o PDF.", "Aviso", MessageBoxButtons.OK, MessageBoxIcon.Information);
            return;
        }

        AtualizarStatus("Gerando PDF...");

        try
        {
            var filename = _pdfGenerator.GerarPdf(dados, empresaNome);
            
            progressBar.Visible = false;
            AtualizarStatus($"PDF gerado com {dados.Count} etiquetas!");

            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
            {
                FileName = filename,
                UseShellExecute = true
            });

            var msg = $"PDF gerado com sucesso!\n\n" +
                     $"Arquivo: {Path.GetFileName(filename)}\n" +
                     $"Etiquetas: {dados.Count}\n\n" +
                     "IMPORTANTE:\n" +
                     "Ao imprimir, use 'TAMANHO REAL' (100%).";

            MessageBox.Show(msg, "Sucesso", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (Exception ex)
        {
            progressBar.Visible = false;
            AtualizarStatus("");
            MessageBox.Show($"Erro ao gerar PDF: {ex.Message}", "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
    }

    private void LimparCampos()
    {
        txtVendas.Clear();
        txtResultado.Clear();
        AtualizarStatus("");
    }

    protected override void OnFormClosing(FormClosingEventArgs e)
    {
        _dbService?.Dispose();
        base.OnFormClosing(e);
    }
}
