using System.Data.SqlClient;
using GeradorEtiquetas.Models;

namespace GeradorEtiquetas;

public class DatabaseService : IDisposable
{
    private readonly string _connectionString;
    private SqlConnection? _connection;

    // Configuração do Banco (mesma do Python)
    private const string Server = "DCWBD11\\VALLEPRIME_PRD";
    private const string Database = "UAU-VALLEPRIME";
    private const string UserId = "consultasBD";
    private const string Password = "V@lle#2021";

    public static readonly Dictionary<string, EmpresaConfig> Empresas = new()
    {
        { "VALLE DO IPITINGA", new EmpresaConfig { Empresa = 6, Obra = "70400" } },
        { "ML CONSTRUTORA", new EmpresaConfig { Empresa = 999, Obra = "70100" } },
        { "VALLE DO IPITINGA II", new EmpresaConfig { Empresa = 28, Obra = "70100" } },
        { "VALLE DOS IPÊS", new EmpresaConfig { Empresa = 29, Obra = "70100" } }
    };

    public DatabaseService()
    {
        _connectionString = $"Server={Server};Database={Database};User Id={UserId};Password={Password};Connection Timeout=5;";
    }

    public bool Conectar()
    {
        try
        {
            _connection = new SqlConnection(_connectionString);
            _connection.Open();
            return true;
        }
        catch (SqlException ex)
        {
            MessageBox.Show($"Erro de Conexão:\n{ex.Message}", "Erro", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return false;
        }
    }

    public ClienteInfo? ObterInformacoesCliente(int numeroVenda, int empresa, string obra)
    {
        if (_connection == null) return null;

        // Query corrigida: usa ItensVenda.CodPerson_Itv para fazer o JOIN com UnidadePer
        const string sql = @"
            SELECT 
                p.nome_pes AS NomeCliente,
                v.Num_Ven AS NumeroVenda,
                v.Cliente_Ven AS CodigoCliente,
                u.Identificador_unid AS Identificador
            FROM Vendas v WITH(NOLOCK)
            INNER JOIN Pessoas p WITH(NOLOCK) ON p.cod_pes = v.Cliente_Ven
            INNER JOIN ItensVenda i WITH(NOLOCK) ON
                i.Empresa_itv = v.Empresa_Ven
                AND i.Obra_Itv = v.Obra_Ven
                AND i.NumVend_Itv = v.Num_Ven
            LEFT JOIN UnidadePer u WITH(NOLOCK) ON
                u.Empresa_unid = i.Empresa_itv
                AND u.Prod_unid = i.Produto_Itv
                AND u.NumPer_unid = i.CodPerson_Itv
            WHERE v.Num_Ven = @NumeroVenda AND v.Empresa_Ven = @Empresa AND v.Obra_Ven = @Obra";

        using var cmd = new SqlCommand(sql, _connection);
        cmd.Parameters.AddWithValue("@NumeroVenda", numeroVenda);
        cmd.Parameters.AddWithValue("@Empresa", empresa);
        cmd.Parameters.AddWithValue("@Obra", obra);

        using var reader = cmd.ExecuteReader();
        if (reader.Read())
        {
            var info = new ClienteInfo
            {
                NomeCliente = reader["NomeCliente"]?.ToString() ?? string.Empty,
                NumeroVenda = Convert.ToInt32(reader["NumeroVenda"]),
                CodigoCliente = Convert.ToInt32(reader["CodigoCliente"]),
                Identificador = reader["Identificador"]?.ToString() ?? string.Empty
            };

            // Separar Quadra e Lote
            SepararQuadraLote(info, empresa);
            return info;
        }

        return null;
    }

    private static void SepararQuadraLote(ClienteInfo info, int empresa)
    {
        if (string.IsNullOrEmpty(info.Identificador)) return;

        try
        {
            // Usar regex para extrair quadra e lote de forma mais robusta
            // Padrão: QUADRA XXX LOTE YYY (case insensitive, com ou sem espaços extras)
            var identificador = info.Identificador.ToUpper().Trim();
            
            // Tentar extrair usando regex
            var regex = new System.Text.RegularExpressions.Regex(
                @"QUADRA\s+(\S+)\s+LOTE\s+(\S+)", 
                System.Text.RegularExpressions.RegexOptions.IgnoreCase);
            
            var match = regex.Match(identificador);
            
            if (match.Success)
            {
                info.Quadra = match.Groups[1].Value.Trim();
                info.Lote = match.Groups[2].Value.Trim();
            }
            else
            {
                // Fallback: tentar split tradicional
                if (identificador.Contains(" LOTE "))
                {
                    var partes = identificador.Split(new[] { " LOTE " }, StringSplitOptions.None);
                    info.Quadra = partes[0].Replace("QUADRA", "").Trim();
                    info.Lote = partes.Length > 1 ? partes[1].Trim() : "N/A";
                }
                else if (identificador.Contains("LOTE"))
                {
                    var partes = identificador.Split(new[] { "LOTE" }, StringSplitOptions.None);
                    info.Quadra = partes[0].Replace("QUADRA", "").Trim();
                    info.Lote = partes.Length > 1 ? partes[1].Trim() : "N/A";
                }
                else
                {
                    info.Quadra = identificador;
                    info.Lote = "N/A";
                }
            }
        }
        catch
        {
            info.Quadra = info.Identificador;
            info.Lote = "N/A";
        }
    }

    public List<string> ObterTelefonesCliente(int codigoCliente)
    {
        var telefones = new List<string>();
        if (_connection == null) return new List<string> { "TELEFONE NÃO DISPONÍVEL" };

        const string sql = "SELECT ddd_tel, fone_tel FROM PESTEL WHERE pes_tel = @CodigoCliente";
        using var cmd = new SqlCommand(sql, _connection);
        cmd.Parameters.AddWithValue("@CodigoCliente", codigoCliente);

        using var reader = cmd.ExecuteReader();
        while (reader.Read())
        {
            var ddd = reader["ddd_tel"]?.ToString() ?? "";
            var fone = reader["fone_tel"]?.ToString();
            if (!string.IsNullOrEmpty(fone))
            {
                telefones.Add($"({ddd}) {fone}");
            }
        }

        return telefones.Count > 0 ? telefones : new List<string> { "TELEFONE NÃO DISPONÍVEL" };
    }

    public EnderecoInfo ObterEnderecoCliente(int codigoCliente)
    {
        if (_connection == null) return new EnderecoInfo();

        const string sql = @"
            SELECT TOP 1
                ISNULL(p.Endereco_pend, 'ENDEREÇO NÃO DISPONÍVEL') AS Endereco,
                ISNULL(p.Bairro_pend, '') AS Bairro,
                ISNULL(p.Cidade_pend, '') AS Cidade,
                ISNULL(p.UF_pend, '') AS UF,
                ISNULL(p.CEP_pend, '') AS CEP,
                ISNULL(p.NumEnd_pend, '') AS Numero,
                ISNULL(p.ComplEndereco_pend, '') AS Complemento
            FROM PesEndereco p
            WHERE p.CodPes_pend = @CodigoCliente";

        using var cmd = new SqlCommand(sql, _connection);
        cmd.Parameters.AddWithValue("@CodigoCliente", codigoCliente);

        using var reader = cmd.ExecuteReader();
        if (reader.Read())
        {
            return new EnderecoInfo
            {
                Endereco = reader["Endereco"]?.ToString() ?? "ENDEREÇO NÃO DISPONÍVEL",
                Bairro = reader["Bairro"]?.ToString() ?? "",
                Cidade = reader["Cidade"]?.ToString() ?? "",
                UF = reader["UF"]?.ToString() ?? "",
                CEP = reader["CEP"]?.ToString() ?? "",
                Numero = reader["Numero"]?.ToString() ?? "",
                Complemento = reader["Complemento"]?.ToString() ?? ""
            };
        }

        return new EnderecoInfo();
    }

    public void Dispose()
    {
        _connection?.Close();
        _connection?.Dispose();
    }
}
