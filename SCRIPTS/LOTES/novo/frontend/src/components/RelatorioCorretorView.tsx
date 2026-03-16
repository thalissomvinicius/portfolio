import React, { useState, useEffect } from 'react';
import { formatCurrency } from '../utils/format';

interface RelatorioCorretorViewProps {
    empresa: number;
    obra: string;
    refreshKey: number;
}

interface CorretorStats {
    corretor: string;
    totalVendas: number;
    valorTotal: number;
    sinaisAbertos: number;
    valorSinaisAberto: number;
    sinaisPagos: number;
    valorSinaisPagos: number;
    sinaisVencidos: number;
    valorSinaisVencidos: number;
}

export const RelatorioCorretorView: React.FC<RelatorioCorretorViewProps> = ({ empresa, obra, refreshKey }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [corretores, setCorretores] = useState<string[]>([]);
    const [corretorSelecionado, setCorretorSelecionado] = useState<string>('');
    const [corretoresStats, setCorretoresStats] = useState<CorretorStats[]>([]);
    const [totaisAPI, setTotaisAPI] = useState<any>({});
    const [gerando, setGerando] = useState(false);
    const [dataInicio, setDataInicio] = useState('');
    const [dataFim, setDataFim] = useState('');

    // Carregar lista de corretores
    const loadCorretores = async () => {
        try {
            const response = await fetch(`/api/corretores/lista?empresa=${empresa}&obra=${obra}`);
            if (response.ok) {
                const result = await response.json();
                setCorretores(result.corretores || []);
            }
        } catch (err) {
            console.error('Erro ao carregar corretores:', err);
        }
    };

    // Carregar estatísticas dos corretores
    const loadCorretoresStats = async () => {
        setLoading(true);
        setError(null);
        try {
            const params = new URLSearchParams({
                empresa: empresa.toString(),
                obra: obra
            });
            if (corretorSelecionado) {
                params.append('corretor', corretorSelecionado);
            }
            // Passar filtro de datas se definidos
            if (dataInicio) {
                params.append('data_inicio', dataInicio);
            }
            if (dataFim) {
                params.append('data_fim', dataFim);
            }
            const response = await fetch(`/api/corretores/stats?${params}`);
            if (response.ok) {
                const result = await response.json();
                setCorretoresStats(result.corretores || []);
                setTotaisAPI(result.totais || {});
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadCorretores();
        loadCorretoresStats();
    }, [empresa, obra, refreshKey]);

    // Gerar PDF individual para corretor
    const generatePDF = async (corretor: string) => {
        setGerando(true);
        try {
            const params = new URLSearchParams({
                empresa: empresa.toString(),
                obra: obra,
                corretor: corretor,
                data_inicio: dataInicio,
                data_fim: dataFim
            });

            const response = await fetch(`/api/relatorio-corretor-pdf?${params}`);
            if (!response.ok) throw new Error('Erro ao gerar PDF');

            const blob = await response.blob();
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `relatorio_${corretor.replace(/\s+/g, '_')}.pdf`;
            link.click();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao gerar PDF');
        } finally {
            setGerando(false);
        }
    };

    // Gerar PDF para todos os corretores
    const generatePDFAll = async () => {
        setGerando(true);
        try {
            const params = new URLSearchParams({
                empresa: empresa.toString(),
                obra: obra,
                data_inicio: dataInicio,
                data_fim: dataFim
            });

            const response = await fetch(`/api/relatorio-corretor-pdf?${params}`);
            if (!response.ok) throw new Error('Erro ao gerar PDF');

            const blob = await response.blob();
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `relatorio_todos_corretores.pdf`;
            link.click();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao gerar PDF');
        } finally {
            setGerando(false);
        }
    };

    // Usar totais da API (query direta) para os cards
    const totais = {
        vendas: corretoresStats.reduce((acc, c) => acc + (c.totalVendas || 0), 0),
        sinaisTotais: (totaisAPI.sinaisAbertos || 0) + (totaisAPI.sinaisPagos || 0),
        valorTotais: (totaisAPI.valorSinaisAbertos || 0) + (totaisAPI.valorSinaisPagos || 0),
        sinaisAbertos: totaisAPI.sinaisAbertos || 0,
        valorAberto: totaisAPI.valorSinaisAbertos || 0,
        sinaisVencidos: totaisAPI.sinaisVencidos || 0,
        valorVencidos: totaisAPI.valorSinaisVencidos || 0,
        sinaisPagos: totaisAPI.sinaisPagos || 0,
        valorPago: totaisAPI.valorSinaisPagos || 0
    };

    return (
        <div className="animate-fade-in">
            {/* Header */}
            <div className="page-header" style={{ marginBottom: '16px' }}>
                <div>
                    <h1 className="page-title">📄 Relatório por Corretor</h1>
                    <p className="page-subtitle">Gere relatórios PDF individuais ou consolidados por corretor</p>
                </div>
            </div>

            {/* Filtros */}
            <div className="card" style={{ marginBottom: '24px', padding: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: '16px', flexWrap: 'wrap' }}>
                    <div className="filter-group">
                        <label className="filter-label">Data Início (opcional)</label>
                        <input
                            type="date"
                            value={dataInicio}
                            onChange={(e) => setDataInicio(e.target.value)}
                            className="filter-input"
                            style={{ width: '150px' }}
                        />
                    </div>
                    <div className="filter-group">
                        <label className="filter-label">Data Fim (opcional)</label>
                        <input
                            type="date"
                            value={dataFim}
                            onChange={(e) => setDataFim(e.target.value)}
                            className="filter-input"
                            style={{ width: '150px' }}
                        />
                    </div>
                    <div className="filter-group">
                        <label className="filter-label">Corretor</label>
                        <select
                            value={corretorSelecionado}
                            onChange={(e) => setCorretorSelecionado(e.target.value)}
                            className="filter-input"
                            style={{ width: '220px', height: '42px' }}
                        >
                            <option value="">Todos os Corretores</option>
                            {corretores.map((c, i) => (
                                <option key={i} value={c}>{c}</option>
                            ))}
                        </select>
                    </div>
                    <button
                        onClick={() => loadCorretoresStats()}
                        className="btn btn-primary"
                        disabled={loading}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            height: '42px'
                        }}
                    >
                        {loading ? '⏳ Carregando...' : '🔍 Buscar'}
                    </button>
                    <button
                        onClick={() => corretorSelecionado ? generatePDF(corretorSelecionado) : generatePDFAll()}
                        className="btn"
                        disabled={gerando}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            height: '42px',
                            background: 'linear-gradient(135deg, #059669, #047857)',
                            color: 'white',
                            border: 'none',
                            fontWeight: 600
                        }}
                    >
                        {gerando ? '⏳ Gerando...' : '📄 Gerar PDF'}
                    </button>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className="card" style={{ background: '#FEE2E2', borderColor: '#EF4444', marginBottom: '24px' }}>
                    <p style={{ color: '#991B1B' }}>❌ {error}</p>
                </div>
            )}

            {/* Loading */}
            {loading && (
                <div className="loading">
                    <div className="spinner"></div>
                </div>
            )}

            {/* Cards de Resumo */}
            {!loading && (
                <>
                    <div className="metric-grid" style={{ gridTemplateColumns: 'repeat(5, 1fr)', marginBottom: '24px' }}>
                        <div className="metric-card">
                            <div className="metric-card-icon">👥</div>
                            <div className="metric-card-content">
                                <div className="metric-label">CORRETORES</div>
                                <div className="metric-value primary" style={{ fontSize: '24px' }}>{corretoresStats.length}</div>
                            </div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-card-icon">📋</div>
                            <div className="metric-card-content">
                                <div className="metric-label">SINAIS TOTAIS</div>
                                <div className="metric-value" style={{ fontSize: '24px', color: '#2563EB' }}>{totais.sinaisTotais}</div>
                                <div style={{ fontSize: '12px', color: '#2563EB' }}>R$ {formatCurrency(totais.valorTotais)}</div>
                            </div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-card-icon">⏳</div>
                            <div className="metric-card-content">
                                <div className="metric-label">EM ABERTO</div>
                                <div className="metric-value" style={{ fontSize: '24px', color: '#F59E0B' }}>{totais.sinaisAbertos}</div>
                                <div style={{ fontSize: '12px', color: '#F59E0B' }}>R$ {formatCurrency(totais.valorAberto)}</div>
                            </div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-card-icon">⚠️</div>
                            <div className="metric-card-content">
                                <div className="metric-label">VENCIDOS</div>
                                <div className="metric-value danger" style={{ fontSize: '24px' }}>{totais.sinaisVencidos}</div>
                                <div style={{ fontSize: '12px', color: '#DC2626' }}>R$ {formatCurrency(totais.valorVencidos)}</div>
                            </div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-card-icon">✅</div>
                            <div className="metric-card-content">
                                <div className="metric-label">PAGOS</div>
                                <div className="metric-value success" style={{ fontSize: '24px' }}>{totais.sinaisPagos}</div>
                                <div style={{ fontSize: '12px', color: '#10B981' }}>R$ {formatCurrency(totais.valorPago)}</div>
                            </div>
                        </div>
                    </div>

                    {/* Tabela de Corretores */}
                    <div className="table-container">
                        <div className="table-header-row">
                            <span className="table-title">👤 Corretores</span>
                            <span className="badge badge-primary">{corretoresStats.length} corretores</span>
                        </div>
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ minWidth: '900px' }}>
                                <thead>
                                    <tr>
                                        <th style={{ width: '180px' }}>Corretor</th>
                                        <th style={{ width: '70px', textAlign: 'center' }}>Vendas</th>
                                        <th style={{ width: '70px', textAlign: 'center' }}>Totais</th>
                                        <th style={{ width: '70px', textAlign: 'center' }}>Aberto</th>
                                        <th style={{ width: '110px', textAlign: 'right' }}>Valor Aberto</th>
                                        <th style={{ width: '70px', textAlign: 'center' }}>Vencidos</th>
                                        <th style={{ width: '70px', textAlign: 'center' }}>Pagos</th>
                                        <th style={{ width: '110px', textAlign: 'right' }}>Valor Pago</th>
                                        <th style={{ width: '80px', textAlign: 'center' }}>Ação</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {corretoresStats.map((c, index) => (
                                        <tr key={index}>
                                            <td style={{ fontWeight: 600, fontSize: '13px' }}>{c.corretor}</td>
                                            <td style={{ textAlign: 'center', fontWeight: 600, color: '#2563EB' }}>{c.totalVendas}</td>
                                            <td style={{ textAlign: 'center', fontWeight: 600 }}>{(c.sinaisAbertos || 0) + (c.sinaisPagos || 0)}</td>
                                            <td style={{ textAlign: 'center' }}>
                                                <span style={{
                                                    display: 'inline-block',
                                                    padding: '4px 8px',
                                                    borderRadius: '4px',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    background: c.sinaisAbertos > 0 ? '#FEF3C7' : '#F3F4F6',
                                                    color: c.sinaisAbertos > 0 ? '#D97706' : '#6B7280'
                                                }}>
                                                    {c.sinaisAbertos}
                                                </span>
                                            </td>
                                            <td style={{ textAlign: 'right', color: '#D97706', fontWeight: 500 }}>
                                                R$ {formatCurrency(c.valorSinaisAberto)}
                                            </td>
                                            <td style={{ textAlign: 'center' }}>
                                                <span style={{
                                                    display: 'inline-block',
                                                    padding: '4px 8px',
                                                    borderRadius: '4px',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    background: c.sinaisVencidos > 0 ? '#FEE2E2' : '#F3F4F6',
                                                    color: c.sinaisVencidos > 0 ? '#DC2626' : '#6B7280'
                                                }}>
                                                    {c.sinaisVencidos || 0}
                                                </span>
                                            </td>
                                            <td style={{ textAlign: 'center' }}>
                                                <span style={{
                                                    display: 'inline-block',
                                                    padding: '4px 8px',
                                                    borderRadius: '4px',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    background: '#D1FAE5',
                                                    color: '#059669'
                                                }}>
                                                    {c.sinaisPagos}
                                                </span>
                                            </td>
                                            <td style={{ textAlign: 'right', color: '#10B981', fontWeight: 500 }}>
                                                R$ {formatCurrency(c.valorSinaisPagos)}
                                            </td>
                                            <td style={{ textAlign: 'center' }}>
                                                <button
                                                    onClick={() => generatePDF(c.corretor)}
                                                    disabled={gerando}
                                                    style={{
                                                        padding: '6px 12px',
                                                        borderRadius: '6px',
                                                        border: 'none',
                                                        background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                                                        color: 'white',
                                                        fontSize: '11px',
                                                        fontWeight: 600,
                                                        cursor: 'pointer',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '4px',
                                                        justifyContent: 'center'
                                                    }}
                                                >
                                                    📄 PDF
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}

            {/* Empty state */}
            {!loading && corretoresStats.length === 0 && (
                <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
                    <h3 style={{ color: '#374151', marginBottom: '8px' }}>Nenhum corretor encontrado</h3>
                    <p style={{ color: '#6B7280' }}>Não há dados de corretores para esta obra</p>
                </div>
            )}
        </div>
    );
};
