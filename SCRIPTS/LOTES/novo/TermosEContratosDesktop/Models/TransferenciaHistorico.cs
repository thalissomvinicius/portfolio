using System;
using System.Collections.Generic;

namespace TermosEContratosDesktop.Models
{
    public class TransferenciaHistorico
    {
        public int NumVenda { get; set; }
        public string Cliente { get; set; } = string.Empty;
        public string CPF { get; set; } = string.Empty;
        public int? CodCliente { get; set; }
        public DateTime? DataVenda { get; set; }
        public DateTime? DataCessao { get; set; }
        public decimal ValorVenda { get; set; }
        public decimal ValorPago { get; set; }
        public string Origem { get; set; } = string.Empty;
        public List<ClienteParticipacao> Owners { get; set; } = new List<ClienteParticipacao>();
    }

    public class ClienteParticipacao
    {
        public string Nome { get; set; } = string.Empty;
        public decimal Participacao { get; set; }
    }
}
