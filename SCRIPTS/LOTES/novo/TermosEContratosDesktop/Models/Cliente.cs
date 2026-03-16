using System;

namespace TermosEContratosDesktop.Models
{
    public class Cliente
    {
        public int CodCliente { get; set; }
        public int Tipo { get; set; }
        public decimal Participacao { get; set; }
        public string Nome { get; set; } = string.Empty;
        public string CPF { get; set; } = string.Empty;
        public DateTime? DataNascimento { get; set; }
        public string Endereco { get; set; } = string.Empty;
        public string Numero { get; set; } = string.Empty;
        public string Bairro { get; set; } = string.Empty;
        public string Cidade { get; set; } = string.Empty;
        public string UF { get; set; } = string.Empty;
        public string CEP { get; set; } = string.Empty;
        public string RG { get; set; } = string.Empty;
        public string OrgaoExpedidor { get; set; } = string.Empty;
        public string UfRg { get; set; } = string.Empty;
        public string EstadoCivil { get; set; } = string.Empty; // Texto formatado (Ex: CASADO(A))
        public string RegimeCasamento { get; set; } = string.Empty;
        public string CidadeNascimento { get; set; } = string.Empty;
        public string UfNascimento { get; set; } = string.Empty;

        public string CpfCnpjFormatado
        {
            get
            {
                if (string.IsNullOrWhiteSpace(CPF)) return "";
                var d = new string(System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Where(CPF, char.IsDigit)));
                if (d.Length == 11) return $"{d.Substring(0, 3)}.{d.Substring(3, 3)}.{d.Substring(6, 3)}-{d.Substring(9)}";
                if (d.Length == 14) return $"{d.Substring(0, 2)}.{d.Substring(2, 3)}.{d.Substring(5, 3)}/{d.Substring(8, 4)}-{d.Substring(12)}";
                return CPF;
            }
        }
    }
}
