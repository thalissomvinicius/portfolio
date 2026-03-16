namespace TermosEContratosDesktop.UI
{
    partial class MainForm
    {
        private System.ComponentModel.IContainer components = null;

        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        private void InitializeComponent()
        {
            this.cmbEmpresas = new System.Windows.Forms.ComboBox();
            this.cmbObras = new System.Windows.Forms.ComboBox();
            this.label1 = new System.Windows.Forms.Label();
            this.label2 = new System.Windows.Forms.Label();
            this.btnBuscar = new System.Windows.Forms.Button();
            this.dgvLotes = new System.Windows.Forms.DataGridView();
            this.txtBusca = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.lblTotalLotes = new System.Windows.Forms.Label();
            this.statusStrip1 = new System.Windows.Forms.StatusStrip();
            this.lblStatus = new System.Windows.Forms.ToolStripStatusLabel();
            this.pnlTopBar = new System.Windows.Forms.Panel();
            this.lblTitle = new System.Windows.Forms.Label();
            this.pnlFilters = new System.Windows.Forms.Panel();
            this.pnlSearch = new System.Windows.Forms.Panel();
            this.panel1 = new System.Windows.Forms.Panel();
            ((System.ComponentModel.ISupportInitialize)(this.dgvLotes)).BeginInit();
            this.statusStrip1.SuspendLayout();
            this.pnlTopBar.SuspendLayout();
            this.pnlFilters.SuspendLayout();
            this.pnlSearch.SuspendLayout();
            this.panel1.SuspendLayout();
            this.SuspendLayout();

            // ===== TOP BAR =====
            this.pnlTopBar.BackColor = System.Drawing.Color.FromArgb(15, 23, 42);
            this.pnlTopBar.Dock = System.Windows.Forms.DockStyle.Top;
            this.pnlTopBar.Height = 56;
            this.pnlTopBar.Controls.Add(this.lblTitle);
            this.pnlTopBar.Name = "pnlTopBar";

            this.lblTitle.Text = "📋  Termos e Contratos";
            this.lblTitle.Font = new System.Drawing.Font("Segoe UI", 14F, System.Drawing.FontStyle.Bold);
            this.lblTitle.ForeColor = System.Drawing.Color.White;
            this.lblTitle.AutoSize = true;
            this.lblTitle.Location = new System.Drawing.Point(20, 14);

            // ===== FILTERS PANEL =====
            this.pnlFilters.BackColor = System.Drawing.Color.FromArgb(30, 41, 59);
            this.pnlFilters.Dock = System.Windows.Forms.DockStyle.Top;
            this.pnlFilters.Height = 64;
            this.pnlFilters.Name = "pnlFilters";
            this.pnlFilters.Controls.Add(this.label1);
            this.pnlFilters.Controls.Add(this.cmbEmpresas);
            this.pnlFilters.Controls.Add(this.label2);
            this.pnlFilters.Controls.Add(this.cmbObras);
            this.pnlFilters.Controls.Add(this.btnBuscar);

            // label1 - Empresa
            this.label1.Text = "EMPRESA";
            this.label1.Font = new System.Drawing.Font("Segoe UI", 7.5F, System.Drawing.FontStyle.Bold);
            this.label1.ForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(20, 10);
            this.label1.Name = "label1";

            // cmbEmpresas
            this.cmbEmpresas.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbEmpresas.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.cmbEmpresas.BackColor = System.Drawing.Color.FromArgb(51, 65, 85);
            this.cmbEmpresas.ForeColor = System.Drawing.Color.White;
            this.cmbEmpresas.Font = new System.Drawing.Font("Segoe UI", 9.5F);
            this.cmbEmpresas.FormattingEnabled = true;
            this.cmbEmpresas.Location = new System.Drawing.Point(20, 30);
            this.cmbEmpresas.Name = "cmbEmpresas";
            this.cmbEmpresas.Size = new System.Drawing.Size(280, 24);
            this.cmbEmpresas.TabIndex = 0;
            this.cmbEmpresas.SelectedIndexChanged += new System.EventHandler(this.cmbEmpresas_SelectedIndexChanged);

            // label2 - Obra
            this.label2.Text = "OBRA";
            this.label2.Font = new System.Drawing.Font("Segoe UI", 7.5F, System.Drawing.FontStyle.Bold);
            this.label2.ForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(318, 10);
            this.label2.Name = "label2";

            // cmbObras
            this.cmbObras.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.cmbObras.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.cmbObras.BackColor = System.Drawing.Color.FromArgb(51, 65, 85);
            this.cmbObras.ForeColor = System.Drawing.Color.White;
            this.cmbObras.Font = new System.Drawing.Font("Segoe UI", 9.5F);
            this.cmbObras.FormattingEnabled = true;
            this.cmbObras.Location = new System.Drawing.Point(318, 30);
            this.cmbObras.Name = "cmbObras";
            this.cmbObras.Size = new System.Drawing.Size(320, 24);
            this.cmbObras.TabIndex = 1;

            // btnBuscar
            this.btnBuscar.Text = "⟳  Buscar";
            this.btnBuscar.Font = new System.Drawing.Font("Segoe UI", 9.5F, System.Drawing.FontStyle.Bold);
            this.btnBuscar.BackColor = System.Drawing.Color.FromArgb(37, 99, 235);
            this.btnBuscar.ForeColor = System.Drawing.Color.White;
            this.btnBuscar.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnBuscar.FlatAppearance.BorderSize = 0;
            this.btnBuscar.Cursor = System.Windows.Forms.Cursors.Hand;
            this.btnBuscar.Location = new System.Drawing.Point(656, 26);
            this.btnBuscar.Name = "btnBuscar";
            this.btnBuscar.Size = new System.Drawing.Size(120, 30);
            this.btnBuscar.TabIndex = 2;
            this.btnBuscar.Click += new System.EventHandler(this.btnBuscar_Click);

            // ===== SEARCH PANEL =====
            this.pnlSearch.BackColor = System.Drawing.Color.FromArgb(30, 41, 59);
            this.pnlSearch.Dock = System.Windows.Forms.DockStyle.Top;
            this.pnlSearch.Height = 52;
            this.pnlSearch.Name = "pnlSearch";
            this.pnlSearch.Controls.Add(this.label3);
            this.pnlSearch.Controls.Add(this.txtBusca);
            this.pnlSearch.Controls.Add(this.lblTotalLotes);

            this.label3.Text = "🔍";
            this.label3.Font = new System.Drawing.Font("Segoe UI", 11F);
            this.label3.ForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(20, 16);
            this.label3.Name = "label3";

            this.txtBusca.Font = new System.Drawing.Font("Segoe UI", 10F);
            this.txtBusca.BackColor = System.Drawing.Color.FromArgb(51, 65, 85);
            this.txtBusca.ForeColor = System.Drawing.Color.White;
            this.txtBusca.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.txtBusca.PlaceholderText = "Buscar por cliente, lote, CPF...";
            this.txtBusca.Location = new System.Drawing.Point(48, 13);
            this.txtBusca.Name = "txtBusca";
            this.txtBusca.Size = new System.Drawing.Size(320, 25);
            this.txtBusca.TabIndex = 3;
            this.txtBusca.TextChanged += new System.EventHandler(this.txtBusca_TextChanged);

            this.lblTotalLotes.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold);
            this.lblTotalLotes.ForeColor = System.Drawing.Color.FromArgb(74, 222, 128);
            this.lblTotalLotes.AutoSize = true;
            this.lblTotalLotes.Location = new System.Drawing.Point(390, 17);
            this.lblTotalLotes.Name = "lblTotalLotes";
            this.lblTotalLotes.Text = "Total: 0 lotes quitados";

            // ===== DATA GRID =====
            this.dgvLotes.AllowUserToAddRows = false;
            this.dgvLotes.AllowUserToDeleteRows = false;
            this.dgvLotes.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.dgvLotes.BackgroundColor = System.Drawing.Color.FromArgb(15, 23, 42);
            this.dgvLotes.GridColor = System.Drawing.Color.FromArgb(51, 65, 85);
            this.dgvLotes.ColumnHeadersBorderStyle = System.Windows.Forms.DataGridViewHeaderBorderStyle.None;
            this.dgvLotes.ColumnHeadersDefaultCellStyle.BackColor = System.Drawing.Color.FromArgb(30, 41, 59);
            this.dgvLotes.ColumnHeadersDefaultCellStyle.ForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.dgvLotes.ColumnHeadersDefaultCellStyle.Font = new System.Drawing.Font("Segoe UI", 8.5F, System.Drawing.FontStyle.Bold);
            this.dgvLotes.ColumnHeadersDefaultCellStyle.SelectionBackColor = System.Drawing.Color.FromArgb(30, 41, 59);
            this.dgvLotes.ColumnHeadersDefaultCellStyle.SelectionForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.dgvLotes.ColumnHeadersHeight = 36;
            this.dgvLotes.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.DisableResizing;
            this.dgvLotes.DefaultCellStyle.BackColor = System.Drawing.Color.FromArgb(15, 23, 42);
            this.dgvLotes.DefaultCellStyle.ForeColor = System.Drawing.Color.FromArgb(226, 232, 240);
            this.dgvLotes.DefaultCellStyle.Font = new System.Drawing.Font("Segoe UI", 9.5F);
            this.dgvLotes.DefaultCellStyle.SelectionBackColor = System.Drawing.Color.FromArgb(37, 99, 235);
            this.dgvLotes.DefaultCellStyle.SelectionForeColor = System.Drawing.Color.White;
            this.dgvLotes.DefaultCellStyle.Padding = new System.Windows.Forms.Padding(0, 0, 5, 0);
            this.dgvLotes.AlternatingRowsDefaultCellStyle.BackColor = System.Drawing.Color.FromArgb(22, 32, 52);
            this.dgvLotes.AlternatingRowsDefaultCellStyle.ForeColor = System.Drawing.Color.FromArgb(226, 232, 240);
            this.dgvLotes.AlternatingRowsDefaultCellStyle.SelectionBackColor = System.Drawing.Color.FromArgb(37, 99, 235);
            this.dgvLotes.Dock = System.Windows.Forms.DockStyle.Fill;
            this.dgvLotes.Name = "dgvLotes";
            this.dgvLotes.ReadOnly = true;
            this.dgvLotes.RowHeadersVisible = false;
            this.dgvLotes.RowTemplate.Height = 38;
            this.dgvLotes.CellBorderStyle = System.Windows.Forms.DataGridViewCellBorderStyle.SingleHorizontal;
            this.dgvLotes.TabIndex = 5;
            this.dgvLotes.CellClick += new System.Windows.Forms.DataGridViewCellEventHandler(this.dgvLotes_CellClick);

            // ===== STATUS BAR =====
            this.statusStrip1.BackColor = System.Drawing.Color.FromArgb(15, 23, 42);
            this.statusStrip1.ForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.statusStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] { this.lblStatus });
            this.statusStrip1.Name = "statusStrip1";
            this.statusStrip1.SizingGrip = false;

            this.lblStatus.Name = "lblStatus";
            this.lblStatus.ForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.lblStatus.Font = new System.Drawing.Font("Segoe UI", 8.5F);
            this.lblStatus.Text = "Pronto — Selecione uma empresa e obra para buscar lotes.";

            // ===== WRAP PANEL =====
            this.panel1.Dock = System.Windows.Forms.DockStyle.Fill;
            this.panel1.Name = "panel1";
            this.panel1.Controls.Add(this.dgvLotes);
            this.panel1.Controls.Add(this.pnlSearch);
            this.panel1.Controls.Add(this.pnlFilters);

            // ===== MAIN FORM =====
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.FromArgb(15, 23, 42);
            this.ClientSize = new System.Drawing.Size(1100, 660);
            this.Controls.Add(this.panel1);
            this.Controls.Add(this.pnlTopBar);
            this.Controls.Add(this.statusStrip1);
            this.Name = "MainForm";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen;
            this.Text = "Termos e Contratos";

            this.Load += new System.EventHandler(this.MainForm_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dgvLotes)).EndInit();
            this.statusStrip1.ResumeLayout(false);
            this.statusStrip1.PerformLayout();
            this.pnlTopBar.ResumeLayout(false);
            this.pnlTopBar.PerformLayout();
            this.pnlFilters.ResumeLayout(false);
            this.pnlFilters.PerformLayout();
            this.pnlSearch.ResumeLayout(false);
            this.pnlSearch.PerformLayout();
            this.panel1.ResumeLayout(false);
            this.panel1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();
        }

        private System.Windows.Forms.ComboBox cmbEmpresas;
        private System.Windows.Forms.ComboBox cmbObras;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.Button btnBuscar;
        private System.Windows.Forms.DataGridView dgvLotes;
        private System.Windows.Forms.TextBox txtBusca;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Label lblTotalLotes;
        private System.Windows.Forms.StatusStrip statusStrip1;
        private System.Windows.Forms.ToolStripStatusLabel lblStatus;
        private System.Windows.Forms.Panel pnlTopBar;
        private System.Windows.Forms.Label lblTitle;
        private System.Windows.Forms.Panel pnlFilters;
        private System.Windows.Forms.Panel pnlSearch;
        private System.Windows.Forms.Panel panel1;
    }
}
