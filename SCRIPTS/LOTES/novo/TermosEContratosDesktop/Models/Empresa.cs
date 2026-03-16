using System;

namespace TermosEContratosDesktop.Models
{
    public class Empresa
    {
        public int Codigo_Emp { get; set; }
        public string Desc_Emp { get; set; } = string.Empty;
        public string CGC_Emp { get; set; } = string.Empty;
        public string Endereco_Emp { get; set; } = string.Empty;
        public string NumEnd_Emp { get; set; } = string.Empty;
        public string Setor_Emp { get; set; } = string.Empty;
        public string Cidade_Emp { get; set; } = string.Empty;
        public string UF_Emp { get; set; } = string.Empty;
        public string CEP_Emp { get; set; } = string.Empty;

        // Propriedades formatadas usadas no doc
        public string RazaoSocial => string.IsNullOrWhiteSpace(Desc_Emp) ? "NÃO INFORMADA" : Desc_Emp;
        public string CnpjFormatado => FormatarCpfCnpj(CGC_Emp);
        public string EnderecoCompleto => $"{Endereco_Emp}{(string.IsNullOrWhiteSpace(NumEnd_Emp) ? "" : $", {NumEnd_Emp}")}";
        public string Bairro => Setor_Emp ?? "";
        public string Cidade => string.IsNullOrWhiteSpace(Cidade_Emp) ? "Tomé-Açu" : Cidade_Emp;
        public string UF => string.IsNullOrWhiteSpace(UF_Emp) ? "PA" : UF_Emp;
        public string CEP => CEP_Emp ?? "";

        private string FormatarCpfCnpj(string doc)
        {
            if (string.IsNullOrWhiteSpace(doc)) return "";
            var d = new string(System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Where(doc, char.IsDigit)));
            if (d.Length == 11) return $"{d.Substring(0, 3)}.{d.Substring(3, 3)}.{d.Substring(6, 3)}-{d.Substring(9)}";
            if (d.Length == 14) return $"{d.Substring(0, 2)}.{d.Substring(2, 3)}.{d.Substring(5, 3)}/{d.Substring(8, 4)}-{d.Substring(12)}";
            return doc;
        }

        public string DisplayString => $"{Codigo_Emp} - {Desc_Emp}";

        public override string ToString()
        {
            return DisplayString;
        }
    }
}
