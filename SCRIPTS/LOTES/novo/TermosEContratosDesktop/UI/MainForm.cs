using System;
using System.Collections.Generic;
using System.Drawing;
using System.Linq;
using System.Threading.Tasks;
using System.Windows.Forms;
using TermosEContratosDesktop.Models;
using TermosEContratosDesktop.Repositories;

namespace TermosEContratosDesktop.UI
{
    public partial class MainForm : Form
    {
        private readonly EmpresaRepository _empresaRepo = new();
        private readonly ObraRepository _obraRepo = new();
        private readonly LoteRepository _loteRepo = new();

        private List<LoteQuitado> _todosLotes = new();

        public MainForm()
        {
            InitializeComponent();
            SetupDataGridView();
        }

        private void SetupDataGridView()
        {
            dgvLotes.AutoGenerateColumns = false;
            dgvLotes.AllowUserToAddRows = false;
            dgvLotes.ReadOnly = true;
            dgvLotes.SelectionMode = DataGridViewSelectionMode.FullRowSelect;
            dgvLotes.MultiSelect = false;

            dgvLotes.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Quadra", HeaderText = "Quadra", Width = 60, DefaultCellStyle = new DataGridViewCellStyle { Alignment = DataGridViewContentAlignment.MiddleCenter } });
            dgvLotes.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Lote", HeaderText = "Lote", Width = 60, DefaultCellStyle = new DataGridViewCellStyle { Alignment = DataGridViewContentAlignment.MiddleCenter } });
            dgvLotes.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Cliente", HeaderText = "Cliente", Width = 200 });
            dgvLotes.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "CpfCnpjFormatado", HeaderText = "CPF/CNPJ", Width = 130 });
            dgvLotes.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "Area", HeaderText = "Área (m²)", Width = 80, DefaultCellStyle = new DataGridViewCellStyle { Alignment = DataGridViewContentAlignment.MiddleRight, Format = "N2" } });
            dgvLotes.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "ValorFinal", HeaderText = "Valor", Width = 100, DefaultCellStyle = new DataGridViewCellStyle { Alignment = DataGridViewContentAlignment.MiddleRight, Format = "C2", ForeColor = Color.SeaGreen } });
            dgvLotes.Columns.Add(new DataGridViewTextBoxColumn { DataPropertyName = "NumVenda", HeaderText = "Venda", Width = 80, DefaultCellStyle = new DataGridViewCellStyle { Alignment = DataGridViewContentAlignment.MiddleCenter } });

            // Button Columns
            var btnCarta = new DataGridViewButtonColumn
            {
                HeaderText = "Ações",
                Text = "📄 Carta",
                UseColumnTextForButtonValue = true,
                Width = 80,
                FlatStyle = FlatStyle.Flat
            };
            btnCarta.DefaultCellStyle.BackColor = Color.CornflowerBlue;
            btnCarta.DefaultCellStyle.ForeColor = Color.White;
            dgvLotes.Columns.Add(btnCarta);

            var btnTermo = new DataGridViewButtonColumn
            {
                HeaderText = "",
                Text = "📋 Termo",
                UseColumnTextForButtonValue = true,
                Width = 80,
                FlatStyle = FlatStyle.Flat
            };
            btnTermo.DefaultCellStyle.BackColor = Color.MediumSeaGreen;
            btnTermo.DefaultCellStyle.ForeColor = Color.White;
            dgvLotes.Columns.Add(btnTermo);
        }

        private async void MainForm_Load(object sender, EventArgs e)
        {
            try
            {
                var empresas = await _empresaRepo.GetAllEmpresasAsync();
                cmbEmpresas.DataSource = empresas;
                cmbEmpresas.DisplayMember = "DisplayString"; // Fix formatting
            }
            catch (Exception ex)
            {
                MessageBox.Show($"Erro ao carregar empresas: {ex.Message}", "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private async void cmbEmpresas_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (cmbEmpresas.SelectedItem is Empresa emp)
            {
                try
                {
                    var obras = await _obraRepo.GetObrasByEmpresaAsync(emp.Codigo_Emp);
                    cmbObras.DataSource = obras;
                    cmbObras.DisplayMember = "DisplayString"; // Fix formatting
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Erro ao carregar obras: {ex.Message}", "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }

        private async void btnBuscar_Click(object sender, EventArgs e)
        {
            if (cmbEmpresas.SelectedItem is Empresa emp && cmbObras.SelectedItem is Obra obra)
            {
                lblStatus.Text = "Carregando lotes...";
                try
                {
                    _todosLotes = await _loteRepo.GetLotesQuitadosAsync(emp.Codigo_Emp, obra.Cod_Obr);
                    FiltrarLotes();
                    lblStatus.Text = "Concluído.";
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Erro ao buscar lotes: {ex.Message}", "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    lblStatus.Text = "Erro.";
                }
            }
        }

        private void txtBusca_TextChanged(object sender, EventArgs e)
        {
            FiltrarLotes();
        }

        private void FiltrarLotes()
        {
            var termo = txtBusca.Text.Trim().ToLower();
            var filtrados = _todosLotes.Where(l => 
                l.Quadra.ToLower().Contains(termo) ||
                l.Lote.ToLower().Contains(termo) ||
                l.Cliente.ToLower().Contains(termo) ||
                l.CPF.Contains(termo) ||
                (l.NumVenda?.ToString().Contains(termo) ?? false)
            ).ToList();

            dgvLotes.DataSource = filtrados;
            lblTotalLotes.Text = $"Total de lotes quitados: {filtrados.Count}";
        }

        private void dgvLotes_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            if (e.RowIndex < 0) return;

            var grid = (DataGridView)sender;
            var lote = (LoteQuitado)grid.Rows[e.RowIndex].DataBoundItem;
            var emp = (Empresa)cmbEmpresas.SelectedItem;

            // Carta (Index 7)
            if (e.ColumnIndex == 7)
            {
                using var dialog = new ConfigDialog(lote, emp, "carta");
                dialog.ShowDialog();
            }
            // Termo (Index 8)
            else if (e.ColumnIndex == 8)
            {
                using var dialog = new ConfigDialog(lote, emp, "termo");
                dialog.ShowDialog();
            }
        }
    }
}
