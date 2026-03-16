import pyodbc
import os
import pandas as pd
from datetime import datetime

def conectar_banco_dados():
    """Conecta ao banco de dados com configuração de ambiente"""
    try:
        connection_string = (
            "Driver={SQL Server};"
            "Server=" + os.getenv('DB_SERVER', 'DCWBD11\\VALLEPRIME_PRD') + ";"
            "Database=" + os.getenv('DB_DATABASE', 'UAU-VALLEPRIME') + ";"
            "UID=" + os.getenv('DB_UID', 'consultasBD') + ";"
            "PWD=" + os.getenv('DB_PWD', 'V@lle#2021') + ";"
            "Timeout=30;"
        )
        conn = pyodbc.connect(connection_string)
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar com o banco de dados: {e}")
        return None

def buscar_boletos_sem_status_recebida(empresa_id=29):
    """
    Busca todos os boletos especificados e retorna aqueles que NÃO têm Status_Rea = 2 (Recebida)
    
    Args:
        empresa_id: ID da empresa (padrão: 29)
    
    Returns:
        DataFrame com os boletos que não têm status 2
    """
    
    # NOVA LISTA de números de boleto para verificar
    nosso_numeros = [
        981, 294, 874, 879, 982, 1120, 675, 299, 592, 181, 345, 1588, 942, 806, 
        705, 796, 5201, 5200, 1082, 5094, 1075, 1514, 1405, 773, 922, 1582, 339, 
        962, 184, 5230, 521, 1399, 1785, 1782, 511, 103, 121, 1464, 1779, 1444, 
        637, 4948, 5190, 948, 936, 909, 4806, 1092, 4792, 387, 136, 133, 5172, 
        43, 55, 62, 236, 163, 1014, 5222, 1139, 658, 649, 595, 487, 357, 414, 
        598, 652, 330, 381, 1585, 831, 272, 464, 306, 822, 1347, 1323, 517, 977, 
        1052, 5187, 1511, 1090, 1356, 1298, 1225, 1146, 1231, 1500, 1289, 1359, 
        1201, 342, 348, 1600, 782, 604, 761, 728, 481, 351, 166, 5143, 130, 1151, 
        127, 1762, 1760, 508, 914, 690, 1765, 1438, 1439, 655, 919, 5145, 5061, 
        467, 478, 444, 573, 1144, 1103, 834, 903, 678, 857, 877, 441, 447, 65, 
        1002, 646, 1084, 1077, 124
    ]
    
    # Converte a lista em string para usar no SQL (IN clause)
    nosso_num_str = ','.join(map(str, nosso_numeros))
    
    # Query SQL baseada na query original
    query = f"""
    SELECT TOP 40000 
        SeuNum_Bol, 
        Banco_Bol, 
        Num_Bol, 
        NumDoc_Bol, 
        StatusBanco_Bol,
        DataVenc_Bol,
        ValDoc_Bol,
        Nome_Pes,
        RecebAutoConfirmado.Status_Rea,
        CASE 
            WHEN RecebAutoConfirmado.Status_Rea = 2 THEN 'Recebida'
            WHEN RecebAutoConfirmado.Status_Rea = 1 THEN 'Pendente'
            WHEN RecebAutoConfirmado.Status_Rea = 3 THEN 'Cancelada'
            ELSE 'Outro (' + CAST(RecebAutoConfirmado.Status_Rea AS VARCHAR) + ')'
        END AS Status_Descricao,
        RecebAutoConfirmado.ValorPar_Rea,
        RecebAutoConfirmado.DataGera_REa,
        Empresas.Desc_emp,
        CASE WHEN DataEnvioPorEmail_bol IS NOT NULL THEN 1 ELSE 0 END AS BoletoEnviado_bol,
        ParametroCobranca.Descr_pcb
    FROM BoletoConfirmado
    INNER JOIN Empresas
        ON BoletoConfirmado.Empresa_Bol = Empresas.Codigo_emp
    LEFT JOIN Pessoas
        ON Cod_Pes = ClienteVen_Bol
    INNER JOIN ( 
        SELECT SeuNum_Rea, Banco_Rea, NumParcPrc_Rea, TipoPrc_Rea, NumParcGerPrc_Rea, 
               Empresa_Rea, ObraPrc_Rea, NumVendPrc_Rea, Agrupado_Rea, ValorPar_Rea, 
               Status_Rea, ComRes_Rea, ValRes_Rea, DataGera_REa, NumArq_Rea, Antecipado_Rea, 
               StatusCarteira_Rea, UsrCad_Rea, UsrAlt_Rea, OcorrenciaExclusao_Rea, DataExclusao_Rea, 
               DataEmis_Rea, ValDesc_Rea, StatusConstrugiro_Rea, NumBol_Rea, 
               ValDescontoCondicional_Rea, DataLimiteDescCond_Rea 
        FROM RecebAutoConfirmado 
        UNION 
        SELECT SeuNum_rea, Banco_rea, NumParcPpar_rea, TipoPpar_rea, NumParcGerPpar_rea, 
               Empresa_pven, Obra_pven, NumProp_rea, Agrupado_rea, ValorPar_rea, 
               Status_rea, ComRea_rea, ValRes_rea, DataGera_rea, NumArq_rea, Antecipado_rea, 
               StatusCarteira_rea, UsrCad_rea, UsrAlt_rea, OcorrenciaExclusao_rea, DataExclusao_rea, 
               DataEmis_rea, ValDesc_rea, StatusConstrugiro_rea, NumBol_rea, 
               ValDescontoCondicional_rea, DataLimiteDescCond_rea 
        FROM ( 
            SELECT PropostaRecebAutoConfirmado.*, PropostaVenda.Empresa_pven, PropostaVenda.Obra_pven 
            FROM PropostaVenda 
            INNER JOIN PropostaParcela ON NumProp_ppar = PropostaVenda.NumProp_pven 
            INNER JOIN PropostaRecebAutoConfirmado ON NumProp_ppar = NumProp_rea 
                AND NumParc_ppar = NumParcPpar_rea AND Tipo_pPar = TipoPpar_rea 
                AND NumParcGer_ppar = NumParcGerPpar_rea 
        ) AS PropostaRecebAutoConfirmado 
    ) AS RecebAutoConfirmado 
        ON RecebAutoConfirmado.NumBol_Rea = Num_Bol
        AND RecebAutoConfirmado.SeuNum_Rea = SeuNum_Bol
        AND RecebAutoConfirmado.Banco_Rea = Banco_Bol
    LEFT JOIN ParametroCobranca 
        ON ParametroCobranca.Empresa_pcb = BoletoConfirmado.Empresa_bol 
        AND ParametroCobranca.Num_pcb = BoletoConfirmado.NumPcb_bol 
    WHERE Empresa_Bol = {empresa_id} 
        AND SeuNum_Bol IN ({nosso_num_str})
        AND RecebAutoConfirmado.Status_Rea != 2  -- Filtra apenas os que NÃO são status 2 (Recebida)
    ORDER BY SeuNum_Bol, Num_Bol
    """
    
    conn = conectar_banco_dados()
    if conn is None:
        return None
    
    try:
        print(f"🔍 Buscando boletos da empresa {empresa_id}...")
        print(f"📋 Total de números a verificar: {len(nosso_numeros)}")
        
        df = pd.read_sql(query, conn)
        
        print(f"\n✅ Consulta executada com sucesso!")
        print(f"📊 Total de boletos encontrados SEM status 2 (Recebida): {len(df)}")
        
        if len(df) > 0:
            print(f"\n📈 Resumo dos status encontrados:")
            print(df['Status_Descricao'].value_counts())
        
        return df
        
    except Exception as e:
        print(f"❌ Erro ao executar consulta: {e}")
        return None
    finally:
        conn.close()

def exportar_resultados(df, nome_arquivo=None):
    """
    Exporta os resultados para um arquivo Excel
    
    Args:
        df: DataFrame com os resultados
        nome_arquivo: Nome do arquivo (opcional)
    """
    if df is None or len(df) == 0:
        print("⚠️ Nenhum dado para exportar")
        return
    
    if nome_arquivo is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"boletos_sem_status_recebida_{timestamp}.xlsx"
    
    try:
        df.to_excel(nome_arquivo, index=False, engine='openpyxl')
        print(f"\n💾 Arquivo exportado com sucesso: {nome_arquivo}")
    except Exception as e:
        print(f"❌ Erro ao exportar arquivo: {e}")

def main():
    """Função principal"""
    print("=" * 70)
    print("VERIFICADOR DE STATUS DE BOLETOS - Valle Prime")
    print("=" * 70)
    print("\nBuscando boletos que NÃO têm status 2 (Recebida)...\n")
    
    # Busca os boletos
    df_resultado = buscar_boletos_sem_status_recebida(empresa_id=29)
    
    if df_resultado is not None and len(df_resultado) > 0:
        print("\n" + "=" * 70)
        print("BOLETOS ENCONTRADOS (Sem Status Recebida):")
        print("=" * 70)
        
        # Exibe as primeiras linhas
        print("\nPrimeiros registros:")
        print(df_resultado[['SeuNum_Bol', 'Num_Bol', 'Nome_Pes', 'Status_Descricao', 
                            'ValDoc_Bol', 'DataVenc_Bol']].head(10))
        
        # Pergunta se deseja exportar
        exportar = input("\n📁 Deseja exportar os resultados para Excel? (s/n): ").lower()
        if exportar == 's':
            exportar_resultados(df_resultado)
    else:
        print("\n✅ Todos os boletos verificados têm status 2 (Recebida) ou não foram encontrados!")
    
    print("\n" + "=" * 70)
    print("Processo concluído!")
    print("=" * 70)

if __name__ == "__main__":
    main()