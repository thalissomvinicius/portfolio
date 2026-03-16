import pandas as pd
import logging
from datetime import date
from typing import Dict, List, Optional, Tuple, Any, Union
from database import get_db_connection

logger = logging.getLogger(__name__)

# Configuração das empresas (Ported from main.py)
EMPRESAS_CONFIG = {
    'ML': {
        'codigo': 999,
        'obra': '70100',
        'nome_curto': 'ML CONSTRUTORA',
        'conta': None,
        'cor': '#4CAF50'
    },
    'VALLE': {
        'codigo': 6,
        'obra': '70400', 
        'nome_curto': 'VALLE EMPREENDIMENTOS',
        'conta': '577570402-5',
        'cor': '#2196F3'
    },
    'VALLE_II': {
        'codigo': 28,
        'obra': '70100',
        'nome_curto': 'VALLE IPTITINGA II',
        'conta': ['13005587-5', '529-0', '27083-6'],
        'cor': '#FF9800'
    },
    'VALLE_IPES': {
        'codigo': 29,
        'obra': '70100',
        'nome_curto': 'VALLE DOS IPÊS',
        'conta': ['13005588-2', '549-5', '31714-8'],
        'cor': '#E91E63'
    }
}

def fetch_receipt_data(data_inicial: Union[str, date], data_final: Union[str, date], empresa_id: str) -> Optional[pd.DataFrame]:
    """
    Fetches receipt data from the database for a specific company or CONSOLIDADO (all).
    """
    if empresa_id == 'CONSOLIDADO':
        all_dfs = []
        for eid in EMPRESAS_CONFIG.keys():
            df = _fetch_single_company_data(data_inicial, data_final, eid)
            if df is not None:
                all_dfs.append(df)
        
        if not all_dfs:
            return pd.DataFrame()
            
        return pd.concat(all_dfs, ignore_index=True)
    
    return _fetch_single_company_data(data_inicial, data_final, empresa_id)

def _fetch_single_company_data(data_inicial: Union[str, date], data_final: Union[str, date], empresa_id: str) -> Optional[pd.DataFrame]:
    """
    Helper function to fetch data for a single company.
    """
    config = EMPRESAS_CONFIG[empresa_id]
    conn = get_db_connection()
    if not conn:
        return None
        
    try:
        query = """
        SELECT 
            PrdSrv.Descricao_psc AS Empreendimento,
            Recebidas.Empresa_rec AS Empresa, 
            Recebidas.Obra_Rec AS Obra, 
            Recebidas.NumVend_Rec AS Venda, 
            ISNULL(UnidadePer.Identificador_unid, 'N/A') AS [Quadra_Lote], 
            Recebidas.Tipo_Rec + ' - ' + Parcelas.Descricao_par AS Tipo, 
            CAST(Recebidas.NumParc_Rec AS VARCHAR) + '-' + 
            CAST(GrupoParc_rec AS VARCHAR) + '/' + 
            CAST(TotParc_Rec AS VARCHAR) AS Parcela, 
            Recebidas.Data_doc AS DtConciliacao, 
            Recebidas.Data_Dep AS DtDeposito, 
            Recebidas.Data_Rec AS DtReceb, 
            Recebidas.DataVenci_Rec AS DtVenc,
            ISNULL(ValorPago, 0) AS ValorPago,
            Recebidas.conta_doc AS Conta
        FROM (
            SELECT 
                Depositos.Data_Dep, 
                Extrato.Data_doc, 
                Extrato.conta_doc,
                Recebidas.Empresa_rec, 
                Recebidas.Obra_Rec, 
                Recebidas.NumVend_Rec, 
                Recebidas.NumParc_Rec, 
                Recebidas.Tipo_Rec, 
                Recebidas.DataVenci_Rec, 
                Recebidas.Data_Rec, 
                GrupoParc_rec, 
                TotParc_Rec,
                ISNULL(Valor_Rec, 0) + ISNULL(ValorConf_Rec, 0)
                + ISNULL(VlCorrecao_Rec, 0) + ISNULL(VlCorrecaoConf_Rec, 0)
                + ISNULL(VlCorrecaoAtr_Rec, 0) + ISNULL(VlCorrecaoAtrConf_Rec, 0)
                + ISNULL(VlTaxaBol_Rec, 0) + ISNULL(VlTaxaBolConf_Rec, 0)
                + ISNULL(VlMulta_Rec, 0) + ISNULL(VlMultaConf_Rec, 0)
                + ISNULL(VlJurosParc_Rec, 0) + ISNULL(VlJurosParcConf_Rec, 0)
                + ISNULL(VlJuros_Rec, 0) + ISNULL(VlJurosConf_Rec, 0)
                + ISNULL(VlAcresConf_Rec, 0) + ISNULL(VlAcres_Rec, 0)
                - (ISNULL(VlDesconto_Rec, 0) + ISNULL(VlDescontoConf_Rec, 0)
                + ISNULL(ValDescontoCusta_Rec, 0) + ISNULL(ValDescontoCustaConf_Rec, 0)
                + ISNULL(ValDescontoImposto_Rec, 0) + ISNULL(ValDescontoImpostoConf_Rec, 0)) AS ValorPago
            FROM Depositos WITH(NOLOCK)
            INNER JOIN RecebePgto WITH(NOLOCK)
                ON Depositos.Empresa_dep = RecebePgto.Empresa_rpg 
                AND Depositos.Numero_Dep = RecebePgto.NumDep_Rpg 
                AND Depositos.Banco_Dep = RecebePgto.BancoDep_Rpg 
                AND Depositos.Conta_Dep = RecebePgto.ContaDep_Rpg 
            INNER JOIN RecebePgtoDiv WITH(NOLOCK)
                ON RecebePgtoDiv.Empresa_Rpd = RecebePgto.Empresa_rpg 
                AND RecebePgtoDiv.NumReceb_Rpd = RecebePgto.NumReceb_Rpg 
                AND RecebePgtoDiv.TipoRpg_Rpd = RecebePgto.Tipo_Rpg 
                AND RecebePgtoDiv.NumCont_Rpd = RecebePgto.NumCont_Rpg 
            INNER JOIN Recebidas WITH(NOLOCK)
                ON RecebePgtoDiv.Empresa_Rpd = Recebidas.Empresa_rec 
                AND RecebePgtoDiv.NumVend_Rpd = Recebidas.NumVend_Rec 
                AND RecebePgtoDiv.Obra_Rpd = Recebidas.Obra_Rec 
                AND RecebePgtoDiv.NumParc_Rpd = Recebidas.NumParc_Rec 
                AND RecebePgtoDiv.ParcType_Rpd = Recebidas.ParcType_Rec 
                AND RecebePgtoDiv.Tipo_Rpd = Recebidas.Tipo_Rec 
                AND RecebePgtoDiv.NumParcGer_Rpd = Recebidas.NumParcGer_Rec 
            INNER JOIN Extrato WITH(NOLOCK)
                ON Depositos.Empresa_dep = Extrato.Empresa_doc 
                AND Depositos.Banco_Dep = Extrato.Banco_doc 
                AND Depositos.Conta_Dep = Extrato.Conta_doc 
                AND CAST(Depositos.Numero_Dep AS VARCHAR) = Extrato.Numero_doc	
            WHERE (Extrato.Tipo_doc = 1 OR Extrato.Tipo_doc IS NULL)  
            AND RecebePgto.Status_Rpg <> 2
        ) AS Recebidas 
        INNER JOIN VendasRecebidas WITH(NOLOCK)
            ON Recebidas.Empresa_rec = VendasRecebidas.Empresa_vrec 
            AND Recebidas.NumVend_Rec = VendasRecebidas.Num_VRec 
            AND Recebidas.Obra_Rec = VendasRecebidas.Obra_VRec
        INNER JOIN Parcelas WITH(NOLOCK)
            ON Recebidas.Tipo_Rec = Parcelas.Tipo_par
        INNER JOIN ItensRecebidas WITH(NOLOCK)
            ON VendasRecebidas.Empresa_vrec = ItensRecebidas.Empresa_itr 
            AND VendasRecebidas.Num_VRec = ItensRecebidas.NumVend_Itr 
            AND VendasRecebidas.Obra_VRec = ItensRecebidas.Obra_Itr
        INNER JOIN PrdSrv WITH(NOLOCK)
            ON ItensRecebidas.Produto_Itr = PrdSrv.NumProd_psc
        LEFT JOIN UnidadePer WITH(NOLOCK)
            ON ItensRecebidas.Empresa_itr = UnidadePer.Empresa_unid 
            AND ItensRecebidas.Produto_itr = UnidadePer.Prod_unid 
            AND ItensRecebidas.CodPerson_itr = UnidadePer.NumPer_unid
        WHERE Recebidas.Empresa_rec = ?
            AND CAST(Recebidas.Data_doc AS DATE) BETWEEN ? AND ?
        """
        
        params = [config['codigo'], data_inicial.strftime('%Y%m%d'), data_final.strftime('%Y%m%d')]
        
        if config['conta']:
            if isinstance(config['conta'], list):
                placeholders = ', '.join(['?'] * len(config['conta']))
                query += f" AND Recebidas.conta_doc IN ({placeholders})"
                params.extend(config['conta'])
            else:
                query += " AND Recebidas.conta_doc = ?"
                params.append(config['conta'])
                
        query += " ORDER BY CAST(Recebidas.Data_doc AS DATE)"
        
        df = pd.read_sql(query, conn, params=params)
        return df
        
    except Exception as e:
        logger.error(f"❌ Error in _fetch_single_company_data: {e}")
        return None
    finally:
        conn.close()

def process_receipts(df: pd.DataFrame) -> Tuple[List[Dict], Dict]:
    """
    Processes receipt data for visualization.
    """
    if df.empty:
        return [], {}
        
    # Standardize column types
    df['DtConciliacao'] = pd.to_datetime(df['DtConciliacao'])
    
    # Aggregation for chart
    daily_totals = df.groupby('DtConciliacao').agg({
        'ValorPago': 'sum'
    }).reset_index()
    
    chart_data = daily_totals.rename(columns={'DtConciliacao': 'date', 'ValorPago': 'value'}).to_dict('records')
    
    # KPIs (Average is now calculated per active day)
    stats = {
        'total': float(df['ValorPago'].sum()),
        'average': float(daily_totals['ValorPago'].mean()) if not daily_totals.empty else 0,
        'count': int(len(df)),
        'max': float(df['ValorPago'].max())
    }
    
    # Detailed records for table
    records = df.to_dict('records')
    
    return chart_data, stats, records
