using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Dapper;
using TermosEContratosDesktop.Models;

namespace TermosEContratosDesktop.Repositories
{
    public class ClienteRepository
    {
        public async Task<List<Cliente>> GetClientesVendaAsync(int empresa, string obra, int numVenda)
        {
            var query = @"
            SELECT 
                VC.codCliente,
                VC.tipo,
                VC.participacao,
                P.nome_pes as Nome,
                P.cpf_pes as CPF,
                P.dtnasc_pes as DataNascimento,
                PE.Endereco_pend as Endereco,
                PE.NumEnd_pend as Numero,
                PE.Bairro_pend as Bairro,
                PE.Cidade_pend as Cidade,
                PE.UF_pend as UF,
                PE.CEP_pend as CEP,
                PD.Registro_Doc as RG,
                PD.OrgaoEmissor_Doc as OrgaoExpedidor,
                PD.UF_Doc as UfRg,
                PF.estciv_pf as EstadoCivil,
                PF.RegCasamento_pf as RegimeCasamento
            FROM (
               SELECT 
                   Empresa_cven as empresa, Num_CVen as numVenda, Obra_CVen as obra, 
                   Cliente_CVen as codCliente, Tipo_CVen as tipo, PorcTitular_Cven as participacao 
               FROM VendaClientes WITH(NOLOCK) 
               UNION ALL
               SELECT 
                   Empresa_vrc as empresa, Num_Vrc as numVenda, Obra_Vrc as obra, 
                   Cliente_vrc as codCliente, Tipo_vrc as tipo, PorcTitular_Vrc as participacao 
               FROM VendaRecClientes WITH(NOLOCK) 
            ) AS VC
            INNER JOIN Pessoas P WITH(NOLOCK) ON VC.codCliente = P.cod_pes 
            LEFT JOIN PesFis PF WITH(NOLOCK) ON P.cod_pes = PF.cod_pf
            LEFT JOIN PessoasDoc PD WITH(NOLOCK) ON P.cod_pes = PD.CodPes_Doc AND PD.Tipo_Doc = 1
            LEFT JOIN PesEndereco PE WITH(NOLOCK) ON P.cod_pes = PE.CodPes_pend AND PE.Tipo_pend = 0
            WHERE VC.empresa = @Empresa
               AND VC.numVenda = @NumVenda
               AND RTRIM(VC.obra) = @Obra
            ORDER BY VC.tipo";

            using var connection = DatabaseConfig.GetConnection();
            var result = await connection.QueryAsync<Cliente>(query, new { Empresa = empresa, NumVenda = numVenda, Obra = obra.Trim() });
            
            var clientes = new List<Cliente>();
            var seen = new HashSet<int>();
            
            foreach(var c in result)
            {
                if(!seen.Contains(c.CodCliente))
                {
                    c.Nome = (c.Nome ?? "NÃO INFORMADO").ToUpper();
                    c.Endereco = (c.Endereco ?? "").ToUpper();
                    c.Numero = (c.Numero ?? "").ToUpper();
                    c.Bairro = (c.Bairro ?? "").ToUpper();
                    c.Cidade = (c.Cidade ?? "").ToUpper();
                    c.UF = (c.UF ?? "").ToUpper();
                    c.EstadoCivil = GetEstadoCivilLabel(c.EstadoCivil);
                    c.RegimeCasamento = GetRegimeCasamentoLabel(c.RegimeCasamento);
                    
                    // Naturalidade logic could be simplified here or added later via another query
                    // For now leaving blank as typically it's retrieved individually 
                    // or we ignore it if it wasn't strictly used in the document output
                    
                    clientes.Add(c);
                    seen.Add(c.CodCliente);
                }
            }

            return clientes;
        }

        private string GetEstadoCivilLabel(string codigo)
        {
            if (string.IsNullOrWhiteSpace(codigo)) return "";
            if (codigo.Contains("-")) return codigo.Split('-').Last().Trim().ToUpper();
            
            return codigo.Trim() switch
            {
                "0" => "SOLTEIRO(A)",
                "1" => "CASADO(A)",
                "2" => "DESQUITADO(A)",
                "3" => "DIVORCIADO(A)",
                "4" => "VIÚVO(A)",
                "5" => "SEPARADO(A)",
                "6" => "AMASIADO(A)",
                "7" => "OUTROS",
                "8" => "UNIÃO ESTÁVEL",
                _ => codigo.ToUpper()
            };
        }

        private string GetRegimeCasamentoLabel(string codigo)
        {
            if (string.IsNullOrWhiteSpace(codigo)) return "";
            if (codigo.Contains("-")) return codigo.Split('-').Last().Trim().ToUpper();
            
            return codigo.Trim() switch
            {
                "0" => "COMUNHÃO PARCIAL DE BENS",
                "1" => "COMUNHÃO UNIVERSAL DE BENS",
                "2" => "SEPARAÇÃO TOTAL DE BENS",
                "3" => "PARTICIPAÇÃO FINAL NOS AQUESTOS",
                "4" => "SEPARAÇÃO OBRIGATÓRIA DE BENS",
                "5" => "OUTROS",
                "6" => "UNIÃO ESTÁVEL",
                _ => codigo.ToUpper()
            };
        }
    }
}
