namespace TermosEContratosDesktop.UI
{
    partial class ConfigDialog
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
            this.lblLoteInfo = new System.Windows.Forms.Label();
            this.dtpDataDoc = new System.Windows.Forms.DateTimePicker();
            this.label1 = new System.Windows.Forms.Label();
            this.pnlTermoOptions = new System.Windows.Forms.Panel();
            this.label2 = new System.Windows.Forms.Label();
            this.txtMatricula = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.txtFolha = new System.Windows.Forms.TextBox();
            this.label4 = new System.Windows.Forms.Label();
            this.txtLivro = new System.Windows.Forms.TextBox();
            this.label5 = new System.Windows.Forms.Label();
            this.pnlTiposParam = new System.Windows.Forms.FlowLayoutPanel();
            this.chkE = new System.Windows.Forms.CheckBox();
            this.chkP = new System.Windows.Forms.CheckBox();
            this.chkS = new System.Windows.Forms.CheckBox();
            this.chkB = new System.Windows.Forms.CheckBox();
            this.btnCancelar = new System.Windows.Forms.Button();
            this.btnGerarPdf = new System.Windows.Forms.Button();
            this.btnGerarWord = new System.Windows.Forms.Button();
            this.btnGerarExtrato = new System.Windows.Forms.Button();
            this.pnlHeader = new System.Windows.Forms.Panel();
            this.pnlActions = new System.Windows.Forms.Panel();
            this.pnlTermoOptions.SuspendLayout();
            this.pnlTiposParam.SuspendLayout();
            this.pnlHeader.SuspendLayout();
            this.pnlActions.SuspendLayout();
            this.SuspendLayout();

            // ===== HEADER PANEL =====
            this.pnlHeader.BackColor = System.Drawing.Color.FromArgb(30, 41, 59);
            this.pnlHeader.Dock = System.Windows.Forms.DockStyle.Top;
            this.pnlHeader.Height = 64;
            this.pnlHeader.Name = "pnlHeader";
            this.pnlHeader.Controls.Add(this.lblLoteInfo);

            this.lblLoteInfo.ForeColor = System.Drawing.Color.White;
            this.lblLoteInfo.Font = new System.Drawing.Font("Segoe UI", 11F, System.Drawing.FontStyle.Bold);
            this.lblLoteInfo.AutoSize = true;
            this.lblLoteInfo.Location = new System.Drawing.Point(18, 20);
            this.lblLoteInfo.Name = "lblLoteInfo";
            this.lblLoteInfo.Text = "Lote: Q000 L000 - Cliente";

            // ===== LABEL DATA =====
            this.label1.Text = "DATA DO DOCUMENTO";
            this.label1.Font = new System.Drawing.Font("Segoe UI", 7.5F, System.Drawing.FontStyle.Bold);
            this.label1.ForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(18, 80);
            this.label1.Name = "label1";

            // ===== DATE PICKER =====
            this.dtpDataDoc.Format = System.Windows.Forms.DateTimePickerFormat.Short;
            this.dtpDataDoc.Location = new System.Drawing.Point(18, 98);
            this.dtpDataDoc.Name = "dtpDataDoc";
            this.dtpDataDoc.Size = new System.Drawing.Size(180, 25);
            this.dtpDataDoc.Font = new System.Drawing.Font("Segoe UI", 10F);
            this.dtpDataDoc.CalendarForeColor = System.Drawing.Color.White;
            this.dtpDataDoc.CalendarMonthBackground = System.Drawing.Color.FromArgb(30, 41, 59);
            this.dtpDataDoc.TabIndex = 1;

            // ===== TERMO OPTIONS PANEL =====
            this.pnlTermoOptions.BorderStyle = System.Windows.Forms.BorderStyle.None;
            this.pnlTermoOptions.BackColor = System.Drawing.Color.FromArgb(24, 34, 52);
            this.pnlTermoOptions.Controls.Add(this.pnlTiposParam);
            this.pnlTermoOptions.Controls.Add(this.label5);
            this.pnlTermoOptions.Controls.Add(this.txtLivro);
            this.pnlTermoOptions.Controls.Add(this.label4);
            this.pnlTermoOptions.Controls.Add(this.txtFolha);
            this.pnlTermoOptions.Controls.Add(this.label3);
            this.pnlTermoOptions.Controls.Add(this.txtMatricula);
            this.pnlTermoOptions.Controls.Add(this.label2);
            this.pnlTermoOptions.Location = new System.Drawing.Point(18, 140);
            this.pnlTermoOptions.Name = "pnlTermoOptions";
            this.pnlTermoOptions.Size = new System.Drawing.Size(444, 165);
            this.pnlTermoOptions.TabIndex = 3;
            this.pnlTermoOptions.Padding = new System.Windows.Forms.Padding(8);

            // Matrícula label
            this.label2.Text = "MATRÍCULA";
            this.label2.Font = new System.Drawing.Font("Segoe UI", 7.5F, System.Drawing.FontStyle.Bold);
            this.label2.ForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(10, 10);
            this.label2.Name = "label2";

            // txtMatricula
            this.txtMatricula.BackColor = System.Drawing.Color.FromArgb(51, 65, 85);
            this.txtMatricula.ForeColor = System.Drawing.Color.White;
            this.txtMatricula.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.txtMatricula.Font = new System.Drawing.Font("Segoe UI", 9.5F);
            this.txtMatricula.Location = new System.Drawing.Point(10, 28);
            this.txtMatricula.Name = "txtMatricula";
            this.txtMatricula.Size = new System.Drawing.Size(130, 24);
            this.txtMatricula.TabIndex = 1;

            // Folha label
            this.label3.Text = "FOLHA";
            this.label3.Font = new System.Drawing.Font("Segoe UI", 7.5F, System.Drawing.FontStyle.Bold);
            this.label3.ForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(155, 10);
            this.label3.Name = "label3";

            // txtFolha
            this.txtFolha.BackColor = System.Drawing.Color.FromArgb(51, 65, 85);
            this.txtFolha.ForeColor = System.Drawing.Color.White;
            this.txtFolha.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.txtFolha.Font = new System.Drawing.Font("Segoe UI", 9.5F);
            this.txtFolha.Location = new System.Drawing.Point(155, 28);
            this.txtFolha.Name = "txtFolha";
            this.txtFolha.Size = new System.Drawing.Size(130, 24);
            this.txtFolha.TabIndex = 2;

            // Livro label
            this.label4.Text = "LIVRO";
            this.label4.Font = new System.Drawing.Font("Segoe UI", 7.5F, System.Drawing.FontStyle.Bold);
            this.label4.ForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(300, 10);
            this.label4.Name = "label4";

            // txtLivro
            this.txtLivro.BackColor = System.Drawing.Color.FromArgb(51, 65, 85);
            this.txtLivro.ForeColor = System.Drawing.Color.White;
            this.txtLivro.BorderStyle = System.Windows.Forms.BorderStyle.FixedSingle;
            this.txtLivro.Font = new System.Drawing.Font("Segoe UI", 9.5F);
            this.txtLivro.Location = new System.Drawing.Point(300, 28);
            this.txtLivro.Name = "txtLivro";
            this.txtLivro.Size = new System.Drawing.Size(130, 24);
            this.txtLivro.TabIndex = 3;

            // label5 - tipos
            this.label5.Text = "TIPOS DE PARCELA";
            this.label5.Font = new System.Drawing.Font("Segoe UI", 7.5F, System.Drawing.FontStyle.Bold);
            this.label5.ForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(10, 68);
            this.label5.Name = "label5";

            // ===== CHECKBOXES =====
            this.pnlTiposParam.Location = new System.Drawing.Point(7, 86);
            this.pnlTiposParam.Name = "pnlTiposParam";
            this.pnlTiposParam.Size = new System.Drawing.Size(430, 68);
            this.pnlTiposParam.BackColor = System.Drawing.Color.FromArgb(24, 34, 52);
            this.pnlTiposParam.Controls.Add(this.chkE);
            this.pnlTiposParam.Controls.Add(this.chkP);
            this.pnlTiposParam.Controls.Add(this.chkS);
            this.pnlTiposParam.Controls.Add(this.chkB);
            this.pnlTiposParam.TabIndex = 4;

            this.chkE.Text = "E - Entrada";
            this.chkE.Tag = "E";
            this.chkE.Checked = true;
            this.chkE.CheckState = System.Windows.Forms.CheckState.Checked;
            this.chkE.ForeColor = System.Drawing.Color.FromArgb(226, 232, 240);
            this.chkE.Font = new System.Drawing.Font("Segoe UI", 9.5F);
            this.chkE.AutoSize = true;
            this.chkE.Location = new System.Drawing.Point(3, 3);

            this.chkP.Text = "P - Parcela";
            this.chkP.Tag = "P";
            this.chkP.Checked = true;
            this.chkP.CheckState = System.Windows.Forms.CheckState.Checked;
            this.chkP.ForeColor = System.Drawing.Color.FromArgb(226, 232, 240);
            this.chkP.Font = new System.Drawing.Font("Segoe UI", 9.5F);
            this.chkP.AutoSize = true;
            this.chkP.Location = new System.Drawing.Point(108, 3);

            this.chkS.Text = "S - Corretagem";
            this.chkS.Tag = "S";
            this.chkS.Checked = true;
            this.chkS.CheckState = System.Windows.Forms.CheckState.Checked;
            this.chkS.ForeColor = System.Drawing.Color.FromArgb(226, 232, 240);
            this.chkS.Font = new System.Drawing.Font("Segoe UI", 9.5F);
            this.chkS.AutoSize = true;
            this.chkS.Location = new System.Drawing.Point(213, 3);

            this.chkB.Text = "B - Balão";
            this.chkB.Tag = "B";
            this.chkB.ForeColor = System.Drawing.Color.FromArgb(226, 232, 240);
            this.chkB.Font = new System.Drawing.Font("Segoe UI", 9.5F);
            this.chkB.AutoSize = true;
            this.chkB.Location = new System.Drawing.Point(335, 3);

            // ===== ACTIONS PANEL =====
            this.pnlActions.BackColor = System.Drawing.Color.FromArgb(15, 23, 42);
            this.pnlActions.Dock = System.Windows.Forms.DockStyle.Bottom;
            this.pnlActions.Height = 56;
            this.pnlActions.Name = "pnlActions";
            this.pnlActions.Controls.Add(this.btnCancelar);
            this.pnlActions.Controls.Add(this.btnGerarPdf);
            this.pnlActions.Controls.Add(this.btnGerarWord);
            this.pnlActions.Controls.Add(this.btnGerarExtrato);

            this.btnCancelar.Text = "Cancelar";
            this.btnCancelar.Font = new System.Drawing.Font("Segoe UI", 9F);
            this.btnCancelar.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnCancelar.FlatAppearance.BorderColor = System.Drawing.Color.FromArgb(71, 85, 105);
            this.btnCancelar.BackColor = System.Drawing.Color.FromArgb(30, 41, 59);
            this.btnCancelar.ForeColor = System.Drawing.Color.FromArgb(148, 163, 184);
            this.btnCancelar.Cursor = System.Windows.Forms.Cursors.Hand;
            this.btnCancelar.Location = new System.Drawing.Point(14, 12);
            this.btnCancelar.Name = "btnCancelar";
            this.btnCancelar.Size = new System.Drawing.Size(90, 32);
            this.btnCancelar.TabIndex = 4;
            this.btnCancelar.Click += new System.EventHandler(this.btnCancelar_Click);

            this.btnGerarPdf.Text = "📄  Carta (PDF)";
            this.btnGerarPdf.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold);
            this.btnGerarPdf.BackColor = System.Drawing.Color.FromArgb(37, 99, 235);
            this.btnGerarPdf.ForeColor = System.Drawing.Color.White;
            this.btnGerarPdf.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnGerarPdf.FlatAppearance.BorderSize = 0;
            this.btnGerarPdf.Cursor = System.Windows.Forms.Cursors.Hand;
            this.btnGerarPdf.Location = new System.Drawing.Point(116, 12);
            this.btnGerarPdf.Name = "btnGerarPdf";
            this.btnGerarPdf.Size = new System.Drawing.Size(120, 32);
            this.btnGerarPdf.TabIndex = 5;
            this.btnGerarPdf.Click += new System.EventHandler(this.btnGerarPdf_Click);

            this.btnGerarWord.Text = "📝  Termo (Word)";
            this.btnGerarWord.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold);
            this.btnGerarWord.BackColor = System.Drawing.Color.FromArgb(5, 150, 105);
            this.btnGerarWord.ForeColor = System.Drawing.Color.White;
            this.btnGerarWord.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnGerarWord.FlatAppearance.BorderSize = 0;
            this.btnGerarWord.Cursor = System.Windows.Forms.Cursors.Hand;
            this.btnGerarWord.Location = new System.Drawing.Point(248, 12);
            this.btnGerarWord.Name = "btnGerarWord";
            this.btnGerarWord.Size = new System.Drawing.Size(130, 32);
            this.btnGerarWord.TabIndex = 6;
            this.btnGerarWord.Click += new System.EventHandler(this.btnGerarWord_Click);

            this.btnGerarExtrato.Text = "📊  Extrato";
            this.btnGerarExtrato.Font = new System.Drawing.Font("Segoe UI", 9F, System.Drawing.FontStyle.Bold);
            this.btnGerarExtrato.BackColor = System.Drawing.Color.FromArgb(109, 40, 217);
            this.btnGerarExtrato.ForeColor = System.Drawing.Color.White;
            this.btnGerarExtrato.FlatStyle = System.Windows.Forms.FlatStyle.Flat;
            this.btnGerarExtrato.FlatAppearance.BorderSize = 0;
            this.btnGerarExtrato.Cursor = System.Windows.Forms.Cursors.Hand;
            this.btnGerarExtrato.Location = new System.Drawing.Point(390, 12);
            this.btnGerarExtrato.Name = "btnGerarExtrato";
            this.btnGerarExtrato.Size = new System.Drawing.Size(100, 32);
            this.btnGerarExtrato.TabIndex = 7;
            this.btnGerarExtrato.Click += new System.EventHandler(this.btnGerarExtrato_Click);

            // ===== DIALOG FORM =====
            this.AutoScaleDimensions = new System.Drawing.SizeF(7F, 15F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.BackColor = System.Drawing.Color.FromArgb(15, 23, 42);
            this.ClientSize = new System.Drawing.Size(480, 380);
            this.Controls.Add(this.pnlTermoOptions);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.dtpDataDoc);
            this.Controls.Add(this.pnlActions);
            this.Controls.Add(this.pnlHeader);
            this.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedDialog;
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "ConfigDialog";
            this.StartPosition = System.Windows.Forms.FormStartPosition.CenterParent;
            this.Text = "Gerar Documento";

            this.pnlTermoOptions.ResumeLayout(false);
            this.pnlTermoOptions.PerformLayout();
            this.pnlTiposParam.ResumeLayout(false);
            this.pnlTiposParam.PerformLayout();
            this.pnlHeader.ResumeLayout(false);
            this.pnlHeader.PerformLayout();
            this.pnlActions.ResumeLayout(false);
            this.ResumeLayout(false);
            this.PerformLayout();
        }

        private System.Windows.Forms.Label lblLoteInfo;
        private System.Windows.Forms.DateTimePicker dtpDataDoc;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Panel pnlTermoOptions;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.TextBox txtFolha;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.TextBox txtMatricula;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.FlowLayoutPanel pnlTiposParam;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.TextBox txtLivro;
        private System.Windows.Forms.CheckBox chkE;
        private System.Windows.Forms.CheckBox chkP;
        private System.Windows.Forms.CheckBox chkS;
        private System.Windows.Forms.CheckBox chkB;
        private System.Windows.Forms.Button btnCancelar;
        private System.Windows.Forms.Button btnGerarPdf;
        private System.Windows.Forms.Button btnGerarWord;
        private System.Windows.Forms.Button btnGerarExtrato;
        private System.Windows.Forms.Panel pnlHeader;
        private System.Windows.Forms.Panel pnlActions;
    }
}
