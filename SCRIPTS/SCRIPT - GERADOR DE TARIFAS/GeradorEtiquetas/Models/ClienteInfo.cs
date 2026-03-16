namespace GeradorEtiquetas.Models;

public class ClienteInfo
{
    public string NomeCliente { get; set; } = string.Empty;
    public int NumeroVenda { get; set; }
    public int CodigoCliente { get; set; }
    public string Identificador { get; set; } = string.Empty;
    public string Quadra { get; set; } = "N/A";
    public string Lote { get; set; } = "N/A";
}

public class EnderecoInfo
{
    public string Endereco { get; set; } = "ENDEREÇO NÃO DISPONÍVEL";
    public string Bairro { get; set; } = string.Empty;
    public string Cidade { get; set; } = string.Empty;
    public string UF { get; set; } = string.Empty;
    public string CEP { get; set; } = string.Empty;
    public string Numero { get; set; } = string.Empty;
    public string Complemento { get; set; } = string.Empty;
}

public class EmpresaConfig
{
    public int Empresa { get; set; }
    public string Obra { get; set; } = string.Empty;
}
