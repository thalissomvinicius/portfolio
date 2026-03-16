using System;

namespace TermosEContratosDesktop.Models
{
    public class ParcelaDetalhada
    {
        public int Parcela { get; set; }
        public string Tipo { get; set; } = string.Empty;
        public string TipoDescricao { get; set; } = string.Empty;
        public DateTime? DataRecebimento { get; set; }
        public decimal ValorPago { get; set; }
        public decimal ValorConfirmado { get; set; }
        public decimal ValorMenor { get; set; }
        public int NumVenda { get; set; }
    }
}
