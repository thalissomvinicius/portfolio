using System;

namespace TermosEContratosDesktop.Utils
{
    public static class Formatador
    {
        public static string FormatarMoeda(decimal valor)
        {
            return $"R$ {valor:N2}"; // formatação nativa que pega a cultura
        }

        public static string NormalizeCityName(string name, string cep)
        {
            if (string.IsNullOrWhiteSpace(name)) return "-";
            
            var nameUpper = name.Trim().ToUpper();
            var cepLimpo = cep != null ? new string(System.Linq.Enumerable.ToArray(System.Linq.Enumerable.Where(cep, char.IsDigit))) : "";
            
            if (cepLimpo == "68680000" || cepLimpo == "68682000")
                return "TOMÉ-AÇU";
                
            if (nameUpper.Contains("QUATRO BOCAS") || (nameUpper.Contains("TOME") && nameUpper.Contains("ACU")))
                return "TOMÉ-AÇU";
                
            return nameUpper;
        }
    }
}
