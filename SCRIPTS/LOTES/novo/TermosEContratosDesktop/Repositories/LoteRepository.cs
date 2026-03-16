using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Dapper;
using TermosEContratosDesktop.Models;

namespace TermosEContratosDesktop.Repositories
{
    public class LoteRepository
    {
        public async Task<List<LoteQuitado>> GetLotesQuitadosAsync(int empresa, string obra)
        {
            var query = @"
            SELECT 
                U.Identificador_Unid as Identificador,
                U.C1_unid as Quadra,
                U.C2_unid as Lote,
                U.Qtde_Unid as Area,
                U.C4_unid as Logradouro,
                U.ValPreco_Unid * ISNULL(U.Qtde_Unid, 1) as ValorCalculado,
                COALESCE(VendasAtivas.Num_Ven, VendasRec.Num_VRec) as NumVenda,
                COALESCE(VendasAtivas.ValorTot_Ven, VendasRec.ValorTot_VRec) as Valor,
                COALESCE(VendasAtivas.Nome_pes, VendasRec.Nome_pes) as Cliente,
                COALESCE(VendasAtivas.cpf_pes, VendasRec.cpf_pes) as CPF,
                COALESCE(VendasAtivas.cod_pes, VendasRec.cod_pes) as CodCliente,
                O.Descr_Obr as NomeObra,
                ISNULL(O.cid_obr, '') as CidadeObra,
                ISNULL(O.uf_obr, 'PA') as UfObra,
                CASE 
                    WHEN VendasAtivas.Num_Ven IS NOT NULL THEN 'V'
                    WHEN VendasRec.Num_VRec IS NOT NULL THEN 'VR'
                    ELSE NULL
                END as TipoVenda
            FROM UnidadePer U WITH(NOLOCK)
            INNER JOIN Obras O WITH(NOLOCK) ON U.Empresa_unid = O.Empresa_Obr AND U.Obra_unid = O.Cod_Obr
            OUTER APPLY (
                SELECT TOP 1 V.Num_Ven, V.ValorTot_Ven, P.Nome_pes, P.cpf_pes, P.cod_pes
                FROM ItensVenda IV WITH(NOLOCK)
                INNER JOIN Vendas V WITH(NOLOCK) 
                    ON IV.Empresa_itv = V.Empresa_Ven 
                    AND IV.Obra_Itv = V.Obra_Ven
                    AND IV.NumVend_Itv = V.Num_Ven
                LEFT JOIN Pessoas P WITH(NOLOCK) ON V.Cliente_Ven = P.cod_pes
                WHERE IV.Empresa_itv = U.Empresa_unid 
                  AND IV.Obra_Itv = U.Obra_unid
                  AND IV.Produto_Itv = U.Prod_unid 
                  AND IV.CodPerson_Itv = U.NumPer_unid
                  AND V.Status_Ven IN (0, 3)
            ) VendasAtivas
            OUTER APPLY (
                SELECT TOP 1 VR.Num_VRec, VR.ValorTot_VRec, P.Nome_pes, P.cpf_pes, P.cod_pes
                FROM ItensRecebidas IR WITH(NOLOCK)
                INNER JOIN VendasRecebidas VR WITH(NOLOCK)
                    ON IR.Empresa_Itr = VR.Empresa_VRec
                    AND IR.Obra_Itr = VR.Obra_VRec
                    AND IR.NumVend_Itr = VR.Num_VRec
                LEFT JOIN Pessoas P WITH(NOLOCK) ON VR.Cliente_VRec = P.cod_pes
                WHERE IR.Empresa_Itr = U.Empresa_unid 
                  AND IR.Obra_Itr = U.Obra_unid
                  AND IR.Produto_Itr = U.Prod_unid 
                  AND IR.CodPerson_Itr = U.NumPer_unid
                  AND VR.Status_VRec IN (0, 3)
                  AND VendasAtivas.Num_Ven IS NULL
            ) VendasRec
            WHERE U.Empresa_unid = @Empresa
              AND U.Obra_unid = @Obra
              AND U.Vendido_unid = 4
            ORDER BY U.C1_unid, U.C2_unid";

            using var connection = DatabaseConfig.GetConnection();
            var lotes = await connection.QueryAsync<LoteQuitado>(query, new { Empresa = empresa, Obra = obra });
            
            // Clean up quadra and lote names from spaces
            foreach (var l in lotes)
            {
                l.Quadra = l.Quadra?.Trim() ?? "";
                l.Lote = l.Lote?.Trim() ?? "";
            }

            return lotes.ToList();
        }
    }
}
