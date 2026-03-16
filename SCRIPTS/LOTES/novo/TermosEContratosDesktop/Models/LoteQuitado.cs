using System;

namespace TermosEContratosDesktop.Models
{
    public class LoteQuitado
    {
        public string Identificador { get; set; } = string.Empty;
        public string Quadra { get; set; } = string.Empty;
        public string Lote { get; set; } = string.Empty;
        public decimal Area { get; set; }
        public string Logradouro { get; set; } = string.Empty;
        public int? NumVenda { get; set; }
        public decimal Valor { get; set; }
        public decimal ValorCalculado { get; set; }
        public string Cliente { get; set; } = string.Empty;
        public string CPF { get; set; } = string.Empty;
        public int CodCliente { get; set; }
        public string NomeObra { get; set; } = string.Empty;
        public string CidadeObra { get; set; } = string.Empty;
        public string UfObra { get; set; } = string.Empty;
        public string TipoVenda { get; set; } = string.Empty;
        
        // Propriedade consolidada para usar a correta (tabela vem valor ou valorCalculado)
        public decimal ValorFinal => Valor > 0 ? Valor : ValorCalculado;
        
        // Area formatada sem zeros decimais desnecessários
        public string AreaFormatada
        {
            get
            {
                if (Area == 0) return "0";
                var s = Area.ToString("0.################"); 
                return s.Contains('.') ? s.TrimEnd('0').TrimEnd('.') : s;
            }
        }

        public string CpfCnpjFormatado
        {
            get
            {
                if (string.IsNullOrWhiteSpace(CPF)) return "-";
                var d = new string(System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Where(CPF, char.IsDigit)));
                if (d.Length == 11) return $"{d.Substring(0, 3)}.{d.Substring(3, 3)}.{d.Substring(6, 3)}-{d.Substring(9)}";
                if (d.Length == 14) return $"{d.Substring(0, 2)}.{d.Substring(2, 3)}.{d.Substring(5, 3)}/{d.Substring(8, 4)}-{d.Substring(12)}";
                return CPF;
            }
        }
    }
}
