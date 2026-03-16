using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Dapper;
using TermosEContratosDesktop.Models;

namespace TermosEContratosDesktop.Repositories
{
    public class EmpresaRepository
    {
        public async Task<List<Empresa>> GetAllEmpresasAsync()
        {
            const string query = @"
                SELECT 
                    Codigo_emp,
                    Desc_emp,
                    CGC_emp
                FROM Empresas WITH(NOLOCK)
                ORDER BY Codigo_emp";

            using var connection = DatabaseConfig.GetConnection();
            var empresas = await connection.QueryAsync<Empresa>(query);
            return empresas.ToList();
        }

        public async Task<Empresa?> GetEmpresaDadosAsync(int codigoEmpresa)
        {
            const string query = @"
                SELECT 
                    Codigo_emp,
                    Desc_emp,
                    CGC_emp,
                    Endereco_emp,
                    NumEnd_emp,
                    Setor_emp,
                    Cidade_emp,
                    UF_emp,
                    CEP_emp
                FROM Empresas WITH(NOLOCK)
                WHERE Codigo_emp = @Codigo";

            using var connection = DatabaseConfig.GetConnection();
            return await connection.QueryFirstOrDefaultAsync<Empresa>(query, new { Codigo = codigoEmpresa });
        }
    }
}
