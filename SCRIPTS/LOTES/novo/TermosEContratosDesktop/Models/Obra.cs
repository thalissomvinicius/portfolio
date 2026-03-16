using System;

namespace TermosEContratosDesktop.Models
{
    public class Obra
    {
        public string Cod_Obr { get; set; } = string.Empty;
        public string Descr_Obr { get; set; } = string.Empty;

        public string DisplayString => $"{Cod_Obr} - {Descr_Obr}";

        public override string ToString()
        {
            return DisplayString;
        }
    }
}
