using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Dapper;
using TermosEContratosDesktop.Models;

namespace TermosEContratosDesktop.Repositories
{
    public class ObraRepository
    {
        public async Task<List<Obra>> GetObrasByEmpresaAsync(int codigoEmpresa)
        {
            const string query = @"
                SELECT 
                    Cod_Obr,
                    Descr_Obr
                FROM Obras WITH(NOLOCK)
                WHERE Empresa_Obr = @Empresa
                ORDER BY Descr_Obr";

            using var connection = DatabaseConfig.GetConnection();
            var obras = await connection.QueryAsync<Obra>(query, new { Empresa = codigoEmpresa });
            return obras.ToList();
        }
    }
}
