using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Dapper;
using TermosEContratosDesktop.Models;
using TermosEContratosDesktop.Repositories;

namespace TermosEContratosDesktop.Services
{
    public class CalculoQuitacaoResult
    {
        public decimal TotalQuitacao { get; set; }
        public decimal TotalPago { get; set; }
        public decimal TotalConfirmado { get; set; }
        public DateTime? UltimoRecebimento { get; set; }
        public List<TransferenciaHistorico> HistoricoTransferencias { get; set; } = new();
        public List<ParcelaDetalhada> ParcelasDetalhadas { get; set; } = new();
    }

    public class CalculoQuitacaoService
    {
        private readonly ClienteRepository _clienteRepo = new ClienteRepository();

        private readonly Dictionary<string, string> _tipoParcelaMap = new()
        {
            { "0", "Seguro" },
            { "1", "Custas" },
            { "2", "Acerto final" },
            { "A", "Resíduo Agrupado" },
            { "B", "Balão" },
            { "C", "Chave" },
            { "E", "Entrada" },
            { "ER", "Entrada Renegociada" },
            { "I", "Intermediação" },
            { "IN", "Intermediárias" },
            { "P", "Parcela" },
            { "R", "Resíduo" },
            { "S", "Comissão Corretagem" },
            { "T", "Taxa" },
            { "M", "Multa" },
            { "J", "Juros" }
        };

        public async Task<CalculoQuitacaoResult> CalcularValorQuitacaoAsync(int empresa, string obra, string quadra, string lote, List<string> tiposParcela = null)
        {
            if (tiposParcela == null || !tiposParcela.Any())
                tiposParcela = new List<string> { "E", "P", "S" };

            var result = new CalculoQuitacaoResult();
            var quadraSafe = quadra.Replace("'", "''").Trim();
            var loteSafe = lote.Replace("'", "''").Trim();

            var queryVendas = $@"
            WITH VendaAtual AS (
                SELECT DISTINCT V.Num_Ven as NumVenda, V.Empresa_Ven, V.Obra_Ven, V.Data_Ven, 
                       V.ValorTot_Ven, V.Status_Ven, P.Nome_pes as Cliente, P.cpf_pes as CPF, P.cod_pes as CodCliente,
                       V.DataCessao_Ven as DataCessao, CAST('Vendas' as varchar(20)) as Origem
                FROM ItensVenda IV WITH(NOLOCK)
                INNER JOIN Vendas V WITH(NOLOCK) ON IV.Empresa_Itv = V.Empresa_Ven AND IV.NumVend_Itv = V.Num_Ven AND IV.Obra_Itv = V.Obra_Ven
                INNER JOIN UnidadePer U WITH(NOLOCK) ON IV.Empresa_Itv = U.Empresa_unid AND IV.Obra_Itv = U.Obra_unid 
                    AND IV.Produto_Itv = U.Prod_unid AND IV.CodPerson_Itv = U.NumPer_unid
                LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
                WHERE U.Empresa_unid = @Empresa AND U.Obra_unid = @Obra 
                  AND RTRIM(LTRIM(U.C1_unid)) = @Quadra AND RTRIM(LTRIM(U.C2_unid)) = @Lote
                  AND V.Status_Ven IN (0, 3)
                  
                UNION
                
                SELECT DISTINCT VR.Num_VRec as NumVenda, VR.Empresa_VRec, VR.Obra_VRec, VR.Data_VRec, 
                       VR.ValorTot_VRec, VR.Status_VRec, P.Nome_pes as Cliente, P.cpf_pes as CPF, P.cod_pes as CodCliente,
                       VR.DataCessao_VRec as DataCessao, CAST('VendasRecebidas' as varchar(20)) as Origem
                FROM ItensRecebidas IR WITH(NOLOCK)
                INNER JOIN VendasRecebidas VR WITH(NOLOCK) ON IR.Empresa_Itr = VR.Empresa_VRec AND IR.NumVend_Itr = VR.Num_VRec AND IR.Obra_Itr = VR.Obra_VRec
                INNER JOIN UnidadePer U WITH(NOLOCK) ON IR.Empresa_Itr = U.Empresa_unid AND IR.Obra_Itr = U.Obra_unid 
                    AND IR.Produto_Itr = U.Prod_unid AND IR.CodPerson_Itr = U.NumPer_unid
                LEFT JOIN Pessoas P WITH(NOLOCK) ON VR.Cliente_VRec = P.cod_pes
                WHERE U.Empresa_unid = @Empresa AND U.Obra_unid = @Obra 
                  AND RTRIM(LTRIM(U.C1_unid)) = @Quadra AND RTRIM(LTRIM(U.C2_unid)) = @Lote
                  AND VR.Status_VRec IN (0, 3)
            ),
            CadeiaCessoesID AS (
                SELECT NumVenda, Empresa_Ven, Obra_Ven
                FROM VendaAtual
                
                UNION ALL
                
                SELECT VH.NumVend_vhist as NumVenda, C.Empresa_Ven, C.Obra_Ven
                FROM CadeiaCessoesID C
                INNER JOIN VendaHist VH WITH(NOLOCK) 
                    ON VH.Empresa_vhist = C.Empresa_Ven 
                    AND VH.Obra_vhist = C.Obra_Ven 
                    AND VH.NumNovaVend_vhist = C.NumVenda
                    AND VH.TipoMnt_vhist IN (2, 8)
            )
            SELECT DISTINCT
                C.NumVenda, C.Empresa_Ven, C.Obra_Ven, V.Data_Ven as DataVenda, V.ValorTot_Ven as ValorVenda, P.Nome_pes as Cliente, 
                P.cpf_pes as CPF, P.cod_pes as CodCliente, VH_Origem.DataAssinaturaCessao_vhist as DataCessao,
                CASE WHEN VA.NumVenda IS NOT NULL THEN VA.Origem ELSE CAST('CessaoAnterior' as varchar(20)) END as Origem
            FROM CadeiaCessoesID C
            LEFT JOIN VendaAtual VA ON C.NumVenda = VA.NumVenda AND C.Empresa_Ven = VA.Empresa_Ven AND C.Obra_Ven = VA.Obra_Ven
            LEFT JOIN (
                SELECT Empresa_Ven, Obra_Ven, Num_Ven, Data_Ven, ValorTot_Ven, Cliente_Ven, Status_Ven FROM Vendas WITH(NOLOCK)
                UNION ALL
                SELECT Empresa_VRec, Obra_VRec, Num_VRec, Data_VRec, ValorTot_VRec, Cliente_VRec, Status_VRec FROM VendasRecebidas WITH(NOLOCK)
            ) V ON V.Empresa_Ven = C.Empresa_Ven AND V.Obra_Ven = C.Obra_Ven AND V.Num_Ven = C.NumVenda
            LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
            LEFT JOIN VendaHist VH_Origem WITH(NOLOCK) ON VH_Origem.Empresa_vhist = C.Empresa_Ven AND VH_Origem.Obra_vhist = C.Obra_Ven AND VH_Origem.NumNovaVend_vhist = C.NumVenda AND VH_Origem.TipoMnt_vhist IN (2, 8)
            WHERE C.NumVenda IS NOT NULL
            ORDER BY V.Data_Ven
            OPTION (MAXRECURSION 100)";

            using var connection = DatabaseConfig.GetConnection();
            
            var vendas = (await connection.QueryAsync<TransferenciaHistorico>(queryVendas, new { Empresa = empresa, Obra = obra, Quadra = quadraSafe, Lote = loteSafe })).ToList();

            if (!vendas.Any())
                return result;

            var vendasNums = vendas.Select(v => v.NumVenda.ToString()).ToList();
            var vendasIn = string.Join(",", vendasNums);
            var tiposIn = string.Join(",", tiposParcela.Select(t => $"'{t}'"));

            var queryPagamentos = $@"
            SELECT 
                R.NumVend_Rec AS NumVenda,
                SUM(
                    CASE 
                        WHEN (R.Valor_Rec + ISNULL(R.VlJurosParc_Rec, 0) + ISNULL(R.VlCorrecao_Rec, 0) + 
                              ISNULL(R.VlAcres_Rec, 0) + ISNULL(R.VlTaxaBol_Rec, 0) + ISNULL(R.VlMulta_Rec, 0) + 
                              ISNULL(R.VlJuros_Rec, 0) + ISNULL(R.VlCorrecaoAtr_Rec, 0)
                              - (ISNULL(R.VlDesconto_Rec, 0) + ISNULL(R.ValDescontoCusta_Rec, 0) + 
                                 ISNULL(R.ValDescontoImposto_Rec, 0) + ISNULL(R.ValDescontoCondicional_rec, 0))
                              + ISNULL(R.ValorConf_Rec, 0) + ISNULL(R.VlJurosParcConf_Rec, 0) + 
                              ISNULL(R.VlCorrecaoConf_Rec, 0) + ISNULL(R.VlAcresConf_Rec, 0) + 
                              ISNULL(R.VlTaxaBolConf_Rec, 0) + ISNULL(R.VlMultaConf_Rec, 0) + 
                              ISNULL(R.VlJurosConf_Rec, 0) + ISNULL(R.VlCorrecaoAtrConf_Rec, 0)
                              - (ISNULL(R.VlDescontoConf_Rec, 0) + ISNULL(R.ValDescontoCustaConf_Rec, 0) + 
                                 ISNULL(R.ValDescontoImpostoConf_Rec, 0) + ISNULL(R.ValDescontoCondicionalConf_rec, 0)))
                        < (ISNULL(R.VlCorrecao_Rec, 0) + ISNULL(R.VlCorrecaoConf_Rec, 0) 
                           + CASE 
                               WHEN R.Tipo_Rec IN ('R', 'A') THEN 0 
                               ELSE CASE ISNULL(VR.AniversarioContr_VRec, 0)
                                   WHEN 0 THEN (ISNULL(R.Valor_Rec, 0) + ISNULL(R.ValorConf_Rec, 0))  
                                   ELSE (ISNULL(R.Valor_Rec, 0) + ISNULL(R.ValorConf_Rec, 0) + 
                                         ISNULL(R.VlJurosParcEmb_Rec, 0) + ISNULL(R.VlJurosParcEmbConf_Rec, 0) + 
                                         ISNULL(R.VlCorrecaoEmb_Rec, 0) + ISNULL(R.VlCorrecaoEmbConf_Rec, 0))
                                   END
                            END)
                        THEN (R.Valor_Rec + ISNULL(R.VlJurosParc_Rec, 0) + ISNULL(R.VlCorrecao_Rec, 0) + 
                              ISNULL(R.VlAcres_Rec, 0) + ISNULL(R.VlTaxaBol_Rec, 0) + ISNULL(R.VlMulta_Rec, 0) + 
                              ISNULL(R.VlJuros_Rec, 0) + ISNULL(R.VlCorrecaoAtr_Rec, 0)
                              - (ISNULL(R.VlDesconto_Rec, 0) + ISNULL(R.ValDescontoCusta_Rec, 0) + 
                                 ISNULL(R.ValDescontoImposto_Rec, 0) + ISNULL(R.ValDescontoCondicional_rec, 0))
                              + ISNULL(R.ValorConf_Rec, 0) + ISNULL(R.VlJurosParcConf_Rec, 0) + 
                              ISNULL(R.VlCorrecaoConf_Rec, 0) + ISNULL(R.VlAcresConf_Rec, 0) + 
                              ISNULL(R.VlTaxaBolConf_Rec, 0) + ISNULL(R.VlMultaConf_Rec, 0) + 
                              ISNULL(R.VlJurosConf_Rec, 0) + ISNULL(R.VlCorrecaoAtrConf_Rec, 0)
                              - (ISNULL(R.VlDescontoConf_Rec, 0) + ISNULL(R.ValDescontoCustaConf_Rec, 0) + 
                                 ISNULL(R.ValDescontoImpostoConf_Rec, 0) + ISNULL(R.ValDescontoCondicionalConf_rec, 0)))
                        ELSE (ISNULL(R.VlCorrecao_Rec, 0) + ISNULL(R.VlCorrecaoConf_Rec, 0) 
                           + CASE 
                               WHEN R.Tipo_Rec IN ('R', 'A') THEN 0 
                               ELSE CASE ISNULL(VR.AniversarioContr_VRec, 0)
                                   WHEN 0 THEN (ISNULL(R.Valor_Rec, 0) + ISNULL(R.ValorConf_Rec, 0))  
                                   ELSE (ISNULL(R.Valor_Rec, 0) + ISNULL(R.ValorConf_Rec, 0) + 
                                         ISNULL(R.VlJurosParcEmb_Rec, 0) + ISNULL(R.VlJurosParcEmbConf_Rec, 0) + 
                                         ISNULL(R.VlCorrecaoEmb_Rec, 0) + ISNULL(R.VlCorrecaoEmbConf_Rec, 0))
                                   END
                            END)
                    END
                ) AS ValorPago
            FROM Recebidas R WITH(NOLOCK)
            LEFT JOIN VendasRecebidas VR WITH(NOLOCK) ON R.Empresa_Rec = VR.Empresa_VRec 
                AND R.Obra_Rec = VR.Obra_VRec AND R.NumVend_Rec = VR.Num_VRec
            WHERE R.Empresa_Rec = @Empresa
              AND R.Obra_Rec = @Obra
              AND R.NumVend_Rec IN ({vendasIn})
              AND R.Data_Rec IS NOT NULL
              AND R.Tipo_Rec IN ({tiposIn})
            GROUP BY R.NumVend_Rec";

            var pagamentosRaw = await connection.QueryAsync(queryPagamentos, new { Empresa = empresa, Obra = obra });
            var pagamentosMap = pagamentosRaw.ToDictionary(p => (int)p.NumVenda, p => (decimal)(p.ValorPago ?? 0m));

            foreach (var v in vendas)
            {
                v.ValorPago = pagamentosMap.ContainsKey(v.NumVenda) ? pagamentosMap[v.NumVenda] : 0m;
                
                var clientesVenda = await _clienteRepo.GetClientesVendaAsync(empresa, obra, v.NumVenda);
                var titulares = clientesVenda.Where(c => c.Tipo == 0).ToList();
                
                if (titulares.Any())
                {
                    v.Cliente = string.Join(", ", titulares.Select(t => t.Nome));
                    v.Owners = titulares.Select(t => new ClienteParticipacao { Nome = t.Nome, Participacao = t.Participacao }).ToList();
                }
                
                result.HistoricoTransferencias.Add(v);
            }

            var queryParcelas = $@"
            SELECT 
                R.NumParc_Rec AS Parcela,
                R.Tipo_Rec AS Tipo,
                R.NumVend_Rec AS NumVenda,
                R.Data_Rec AS DataRecebimento,
                (R.Valor_Rec + ISNULL(R.VlJurosParc_Rec, 0) + ISNULL(R.VlCorrecao_Rec, 0) + 
                 ISNULL(R.VlAcres_Rec, 0) + ISNULL(R.VlTaxaBol_Rec, 0) + ISNULL(R.VlMulta_Rec, 0) + 
                 ISNULL(R.VlJuros_Rec, 0) + ISNULL(R.VlCorrecaoAtr_Rec, 0)
                 - (ISNULL(R.VlDesconto_Rec, 0) + ISNULL(R.ValDescontoCusta_Rec, 0) + 
                    ISNULL(R.ValDescontoImposto_Rec, 0) + ISNULL(R.ValDescontoCondicional_rec, 0))
                 + ISNULL(R.ValorConf_Rec, 0) + ISNULL(R.VlJurosParcConf_Rec, 0) + 
                 ISNULL(R.VlCorrecaoConf_Rec, 0) + ISNULL(R.VlAcresConf_Rec, 0) + 
                 ISNULL(R.VlTaxaBolConf_Rec, 0) + ISNULL(R.VlMultaConf_Rec, 0) + 
                 ISNULL(R.VlJurosConf_Rec, 0) + ISNULL(R.VlCorrecaoAtrConf_Rec, 0)
                 - (ISNULL(R.VlDescontoConf_Rec, 0) + ISNULL(R.ValDescontoCustaConf_Rec, 0) + 
                    ISNULL(R.ValDescontoImpostoConf_Rec, 0) + ISNULL(R.ValDescontoCondicionalConf_rec, 0))
                ) AS ValorPago,
                (ISNULL(R.VlCorrecao_Rec, 0) + ISNULL(R.VlCorrecaoConf_Rec, 0) 
                + CASE 
                    WHEN R.Tipo_Rec IN ('R', 'A') 
                    THEN 0 
                    ELSE  
                        CASE ISNULL(VR.AniversarioContr_VRec, 0)
                            WHEN 0  
                            THEN (ISNULL(R.Valor_Rec, 0) + ISNULL(R.ValorConf_Rec, 0))  
                            ELSE (ISNULL(R.Valor_Rec, 0) + ISNULL(R.ValorConf_Rec, 0) + 
                                  ISNULL(R.VlJurosParcEmb_Rec, 0) + ISNULL(R.VlJurosParcEmbConf_Rec, 0) + 
                                  ISNULL(R.VlCorrecaoEmb_Rec, 0) + ISNULL(R.VlCorrecaoEmbConf_Rec, 0))
                        END
                END) AS ValorConfirmado
            FROM Recebidas R WITH(NOLOCK)
            LEFT JOIN VendasRecebidas VR WITH(NOLOCK) ON R.Empresa_Rec = VR.Empresa_VRec 
                AND R.Obra_Rec = VR.Obra_VRec AND R.NumVend_Rec = VR.Num_VRec
            WHERE R.Empresa_Rec = @Empresa
              AND R.Obra_Rec = @Obra
              AND R.NumVend_Rec IN ({vendasIn})
              AND R.Data_Rec IS NOT NULL
              AND R.Tipo_Rec IN ({tiposIn})
            ORDER BY R.Data_Rec, R.NumParc_Rec";

            var parcelas = await connection.QueryAsync<ParcelaDetalhada>(queryParcelas, new { Empresa = empresa, Obra = obra });

            foreach (var p in parcelas)
            {
                p.TipoDescricao = _tipoParcelaMap.ContainsKey(p.Tipo.ToUpper()) ? _tipoParcelaMap[p.Tipo.ToUpper()] : p.Tipo;
                p.ValorMenor = p.ValorConfirmado > 0 ? Math.Min(p.ValorPago, p.ValorConfirmado) : p.ValorPago;
                
                result.TotalPago += p.ValorPago;
                result.TotalConfirmado += p.ValorConfirmado;
                result.TotalQuitacao += p.ValorMenor;

                if (p.DataRecebimento.HasValue && (result.UltimoRecebimento == null || p.DataRecebimento.Value > result.UltimoRecebimento.Value))
                {
                    result.UltimoRecebimento = p.DataRecebimento.Value;
                }

                result.ParcelasDetalhadas.Add(p);
            }

            return result;
        }
    }
}
