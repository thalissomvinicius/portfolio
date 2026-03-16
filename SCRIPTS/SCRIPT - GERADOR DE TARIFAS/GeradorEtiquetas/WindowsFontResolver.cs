using PdfSharp.Fonts;
using System.Reflection;

namespace GeradorEtiquetas;

/// <summary>
/// Resolver de fontes do sistema Windows para PdfSharp 6.0
/// </summary>
public class WindowsFontResolver : IFontResolver
{
    public FontResolverInfo? ResolveTypeface(string familyName, bool isBold, bool isItalic)
    {
        // Mapear para fontes do Windows
        var fontName = familyName.ToLower() switch
        {
            "arial" => isBold ? "arialbd" : "arial",
            "consolas" => isBold ? "consolasb" : "consolas",
            "segoe ui" => isBold ? "segoeuib" : "segoeui",
            "helvetica" => isBold ? "arialbd" : "arial", // Helvetica -> Arial no Windows
            _ => isBold ? "arialbd" : "arial"
        };

        return new FontResolverInfo(fontName);
    }

    public byte[]? GetFont(string faceName)
    {
        // Caminho das fontes do Windows
        var fontsPath = Environment.GetFolderPath(Environment.SpecialFolder.Fonts);
        
        var fontFile = faceName.ToLower() switch
        {
            "arial" => "arial.ttf",
            "arialbd" => "arialbd.ttf",
            "consolas" => "consola.ttf",
            "consolasb" => "consolab.ttf",
            "segoeui" => "segoeui.ttf",
            "segoeuib" => "segoeuib.ttf",
            _ => "arial.ttf"
        };

        var fullPath = Path.Combine(fontsPath, fontFile);
        
        if (File.Exists(fullPath))
        {
            return File.ReadAllBytes(fullPath);
        }

        return null;
    }
}
