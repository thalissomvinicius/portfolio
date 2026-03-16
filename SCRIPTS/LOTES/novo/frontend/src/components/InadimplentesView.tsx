import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { formatCurrency } from '../utils/format';
import { PageHeader, LoadingSpinner, ErrorMessage, DataTable } from './shared';

interface InadimplentesViewProps {
    empresa: number;
    obra: string;
    refreshKey: number;
}

interface Inadimplente {
    venda: number;
    cliente: string;
    corretor: string;
    identificador: string;
    quadra: string;
    lote: string;
    tipoParcela: string;
    parcelaNumero: string;
    dataVencimento: string;
    diasAtraso: number;
    valor: number;
    email: string;
    telefone: string;
    dataProrrogacao: string | null;
    foiProrrogado: number;
    prorrogacaoVencida: number;
}

interface Metrics {
    totalBoletos: number;
    valorTotal: number;
    ate30Dias: number;
    de31a60Dias: number;
    de61a90Dias: number;
    mais90Dias: number;
}

export const InadimplentesView: React.FC<InadimplentesViewProps> = ({ empresa, obra, refreshKey }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<Inadimplente[]>([]);
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [diasMinimo, setDiasMinimo] = useState(1);
    const [corretorFilter, setCorretorFilter] = useState<string>('');
    const [estruturas, setEstruturas] = useState<{ codigo: number, nome: string }[]>([]);
    const [selectedEstrutura, setSelectedEstrutura] = useState<string>('');

    // Fetch structures
    useEffect(() => {
        const fetchEstruturas = async () => {
            try {
                const response = await fetch(`/api/corretores/estruturas?empresa=${empresa}&obra=${obra}`);
                if (response.ok) {
                    const data = await response.json();
                    setEstruturas(data);
                }
            } catch (err) {
                console.error('Erro ao buscar estruturas:', err);
            }
        };
        fetchEstruturas();
    }, [empresa, obra]);

    // Get unique corretores for filter dropdown
    const corretores = React.useMemo(() => {
        const unique = [...new Set(data.map(d => d.corretor).filter(Boolean))];
        return unique.sort();
    }, [data]);

    // Filter data by corretor
    const filteredData = React.useMemo(() => {
        if (!corretorFilter) return data;
        return data.filter(d => d.corretor === corretorFilter);
    }, [data, corretorFilter]);

    // Calculate metrics based on filtered data (for when corretor is selected)
    const filteredMetrics = React.useMemo(() => {
        const sourceData = corretorFilter ? filteredData : data;
        const totalBoletos = sourceData.length;
        const valorTotal = sourceData.reduce((sum, d) => sum + (d.valor || 0), 0);
        const ate30Dias = sourceData.filter(d => d.diasAtraso <= 30).length;
        const de31a60Dias = sourceData.filter(d => d.diasAtraso > 30 && d.diasAtraso <= 60).length;
        const de61a90Dias = sourceData.filter(d => d.diasAtraso > 60 && d.diasAtraso <= 90).length;
        const mais90Dias = sourceData.filter(d => d.diasAtraso > 90).length;
        return { totalBoletos, valorTotal, ate30Dias, de31a60Dias, de61a90Dias, mais90Dias };
    }, [data, filteredData, corretorFilter]);

    const fetchData = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.getInadimplentes(empresa, obra, diasMinimo, selectedEstrutura);
            setData(response.data);
            setMetrics(response.metrics);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao buscar dados');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [empresa, obra, refreshKey, selectedEstrutura]);

    const getDiasAtrasoColor = (dias: number) => {
        if (dias > 90) return '#991B1B';
        if (dias > 60) return '#DC2626';
        if (dias > 30) return '#D97706';
        return '#059669';
    };

    const getDiasAtrasoBg = (dias: number) => {
        if (dias > 90) return '#FEE2E2';
        if (dias > 60) return '#FEF3C7';
        if (dias > 30) return '#FEF9C3';
        return '#D1FAE5';
    };

    const downloadPdf = async () => {
        try {
            let url = `/api/inadimplentes/pdf?empresa=${empresa}&obra=${obra}&dias_minimo=${diasMinimo}`;
            if (selectedEstrutura) {
                url += `&estrutura=${selectedEstrutura}`;
            }
            if (corretorFilter) {
                url += `&corretor=${encodeURIComponent(corretorFilter)}`;
            }
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error('Erro ao gerar PDF');
            }
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = `cobranca_inadimplentes_${new Date().toISOString().slice(0, 10)}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(downloadUrl);
            a.remove();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao gerar PDF');
        }
    };

    return (
        <div className="animate-fade-in">
            <PageHeader
                title="Controle de Inadimplência"
                subtitle="Boletos vencidos e não pagos para acompanhamento de cobrança"
            />

            {/* Filters */}
            <div className="card" style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', gap: '16px', alignItems: 'end', flexWrap: 'wrap' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <label style={{ fontSize: '13px', fontWeight: 600, color: '#374151' }}>Dias mínimos de atraso</label>
                        <input
                            type="number"
                            min="1"
                            style={{
                                padding: '10px 16px',
                                border: '2px solid #E5E7EB',
                                borderRadius: '8px',
                                fontSize: '14px',
                                width: '150px'
                            }}
                            value={diasMinimo}
                            onChange={(e) => setDiasMinimo(parseInt(e.target.value) || 1)}
                        />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <label style={{ fontSize: '13px', fontWeight: 600, color: '#374151' }}>Equipe / Estrutura</label>
                        <select
                            style={{
                                padding: '10px 16px',
                                border: '2px solid #E5E7EB',
                                borderRadius: '8px',
                                fontSize: '14px',
                                minWidth: '200px',
                                background: 'white'
                            }}
                            value={selectedEstrutura}
                            onChange={(e) => setSelectedEstrutura(e.target.value)}
                        >
                            <option value="">Todas as Estruturas</option>
                            {estruturas.map((e) => (
                                <option key={e.codigo} value={e.codigo}>{e.nome}</option>
                            ))}
                        </select>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <label style={{ fontSize: '13px', fontWeight: 600, color: '#374151' }}>Filtrar por Corretor</label>
                        <select
                            style={{
                                padding: '10px 16px',
                                border: '2px solid #E5E7EB',
                                borderRadius: '8px',
                                fontSize: '14px',
                                minWidth: '200px',
                                background: 'white'
                            }}
                            value={corretorFilter}
                            onChange={(e) => setCorretorFilter(e.target.value)}
                        >
                            <option value="">Todos os Corretores</option>
                            {corretores.map((c, i) => (
                                <option key={i} value={c}>{c}</option>
                            ))}
                        </select>
                    </div>
                    <button
                        onClick={fetchData}
                        className="btn btn-primary"
                        disabled={loading}
                        style={{ height: '44px' }}
                    >
                        {loading ? '⏳ Carregando...' : '🔍 Filtrar'}
                    </button>
                    <button
                        onClick={downloadPdf}
                        className="btn"
                        disabled={loading || filteredData.length === 0}
                        style={{
                            height: '44px',
                            background: 'linear-gradient(135deg, #DC2626 0%, #991B1B 100%)',
                            color: 'white',
                            border: 'none',
                            borderRadius: '8px',
                            padding: '0 20px',
                            fontWeight: 600,
                            cursor: filteredData.length === 0 ? 'not-allowed' : 'pointer',
                            opacity: filteredData.length === 0 ? 0.5 : 1
                        }}
                    >
                        📄 Gerar PDF Cobrança
                    </button>
                </div>
            </div>

            {error && <ErrorMessage message={error} />}

            {loading && <LoadingSpinner />}

            {metrics && !loading && (
                <>
                    {/* Metrics Cards */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px', marginBottom: '24px' }}>
                        <div className="card" style={{ background: 'linear-gradient(135deg, #DC2626 0%, #991B1B 100%)', color: 'white', padding: '16px' }}>
                            <div style={{ fontSize: '11px', opacity: 0.9 }}>TOTAL EM ATRASO</div>
                            <div style={{ fontSize: '24px', fontWeight: 700, marginTop: '4px' }}>{filteredMetrics.totalBoletos}</div>
                        </div>
                        <div className="card" style={{ background: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)', color: 'white', padding: '16px' }}>
                            <div style={{ fontSize: '11px', opacity: 0.9 }}>VALOR TOTAL</div>
                            <div style={{ fontSize: '16px', fontWeight: 700, marginTop: '4px' }}>R$ {formatCurrency(filteredMetrics.valorTotal)}</div>
                        </div>
                        <div className="card" style={{ background: '#D1FAE5', padding: '16px' }}>
                            <div style={{ fontSize: '11px', color: '#065F46' }}>ATÉ 30 DIAS</div>
                            <div style={{ fontSize: '24px', fontWeight: 700, color: '#059669', marginTop: '4px' }}>{filteredMetrics.ate30Dias}</div>
                        </div>
                        <div className="card" style={{ background: '#FEF9C3', padding: '16px' }}>
                            <div style={{ fontSize: '11px', color: '#92400E' }}>31-60 DIAS</div>
                            <div style={{ fontSize: '24px', fontWeight: 700, color: '#D97706', marginTop: '4px' }}>{filteredMetrics.de31a60Dias}</div>
                        </div>
                        <div className="card" style={{ background: '#FEF3C7', padding: '16px' }}>
                            <div style={{ fontSize: '11px', color: '#92400E' }}>61-90 DIAS</div>
                            <div style={{ fontSize: '24px', fontWeight: 700, color: '#DC2626', marginTop: '4px' }}>{filteredMetrics.de61a90Dias}</div>
                        </div>
                        <div className="card" style={{ background: '#FEE2E2', padding: '16px' }}>
                            <div style={{ fontSize: '11px', color: '#991B1B' }}>+90 DIAS</div>
                            <div style={{ fontSize: '24px', fontWeight: 700, color: '#991B1B', marginTop: '4px' }}>{filteredMetrics.mais90Dias}</div>
                        </div>
                    </div>

                    {/* Table */}
                    <DataTable title="⚠️ Boletos em Atraso" badgeText={String(filteredData.length)} badgeVariant="danger">
                        {filteredData.length > 0 ? (
                            <table>
                                <thead>
                                    <tr>
                                        <th style={{ width: '60px', textAlign: 'center' }}>Venda</th>
                                        <th style={{ width: '180px' }}>Cliente</th>
                                        <th style={{ width: '130px' }}>Corretor</th>
                                        <th style={{ width: '35px', textAlign: 'center' }}>Q</th>
                                        <th style={{ width: '35px', textAlign: 'center' }}>L</th>
                                        <th style={{ width: '90px' }}>Tipo</th>
                                        <th style={{ width: '90px', textAlign: 'center' }}>Vencimento</th>
                                        <th style={{ width: '60px', textAlign: 'center' }}>Dias</th>
                                        <th style={{ width: '100px', textAlign: 'right' }}>Valor</th>
                                        <th style={{ width: '120px', textAlign: 'center' }}>Prorrogado</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredData.map((item, index) => (
                                        <tr key={index} style={{ backgroundColor: getDiasAtrasoBg(item.diasAtraso) }}>
                                            <td style={{ textAlign: 'center', fontWeight: 600 }}>{item.venda}</td>
                                            <td style={{ fontSize: '12px', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={item.cliente}>
                                                {item.cliente}
                                            </td>
                                            <td style={{ fontSize: '12px', maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={item.corretor || '-'}>
                                                {item.corretor || '-'}
                                            </td>
                                            <td style={{ textAlign: 'center', fontWeight: 600, color: '#2563EB' }}>{item.quadra || '-'}</td>
                                            <td style={{ textAlign: 'center', fontWeight: 600, color: '#2563EB' }}>{item.lote || '-'}</td>
                                            <td style={{ fontSize: '11px', maxWidth: '100px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={item.tipoParcela}>
                                                {item.tipoParcela || '-'}
                                            </td>
                                            <td style={{ textAlign: 'center', color: '#DC2626', fontWeight: 500 }}>{item.dataVencimento}</td>
                                            <td style={{ textAlign: 'center' }}>
                                                <span style={{
                                                    background: getDiasAtrasoColor(item.diasAtraso),
                                                    color: 'white',
                                                    padding: '4px 8px',
                                                    borderRadius: '12px',
                                                    fontSize: '12px',
                                                    fontWeight: 600
                                                }}>
                                                    {item.diasAtraso}
                                                </span>
                                            </td>
                                            <td style={{ textAlign: 'right', fontWeight: 600, color: '#DC2626' }}>
                                                R$ {formatCurrency(item.valor)}
                                            </td>
                                            <td style={{ textAlign: 'center' }}>
                                                {item.foiProrrogado === 1 ? (
                                                    item.prorrogacaoVencida === 1 ? (
                                                        <span style={{
                                                            background: '#F59E0B',
                                                            color: 'white',
                                                            padding: '2px 6px',
                                                            borderRadius: '10px',
                                                            fontSize: '9px',
                                                            fontWeight: 600
                                                        }} title="Prorrogado mas ainda vencido!">
                                                            ⚠️ {item.dataProrrogacao}
                                                        </span>
                                                    ) : (
                                                        <span style={{
                                                            background: '#10B981',
                                                            color: 'white',
                                                            padding: '2px 6px',
                                                            borderRadius: '10px',
                                                            fontSize: '9px',
                                                            fontWeight: 600
                                                        }} title="Prorrogado - nova data válida">
                                                            ✅ {item.dataProrrogacao}
                                                        </span>
                                                    )
                                                ) : (
                                                    <span style={{ color: '#9CA3AF', fontSize: '11px' }}>-</span>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <div className="empty-state" style={{ padding: '40px', textAlign: 'center' }}>
                                <p style={{ color: '#10B981', fontSize: '16px' }}>✅ Nenhum boleto em atraso encontrado!</p>
                            </div>
                        )}
                    </DataTable>
                </>
            )}
        </div>
    );
};
