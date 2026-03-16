import React, { useState, useEffect } from 'react';
import { formatCurrency } from '../utils/format';
import { PageHeader, LoadingSpinner, ErrorMessage } from './shared';

interface EvolucaoViewProps {
    empresa: number;
    obra: string;
    refreshKey: number;
}

interface EvolucaoData {
    vendas: {
        total: number;
        valorTotal: number;
        mes: number;
        valorMes: number;
        ano: number;
        valorAno: number;
        hoje: number;
        valorHoje: number;
    };
    recebimentos: {
        hoje: number;
        mes: number;
        ano: number;
        total: number;
    };
    inadimplencia: {
        parcelas: number;
        valor: number;
    };
    estoque: {
        disponivel: number;
        reservado: number;
        vendido: number;
        quitado: number;
        suspenso: number;
        foraVenda: number;
        total: number;
    };
    sinais: {
        pagos: number;
        valorPago: number;
    };
    recebimentosDiarios: Array<{
        data: string;
        dataFormatada: string;
        valor: number;
    }>;
    dataAtualizacao: string;
}

export const EvolucaoView: React.FC<EvolucaoViewProps> = ({ empresa, obra, refreshKey }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<EvolucaoData | null>(null);

    // Local filter state - only date filter
    const [filterData, setFilterData] = useState(new Date().toISOString().split('T')[0]); // YYYY-MM-DD

    // Auto-load when empresa/obra or refreshKey changes
    useEffect(() => {
        loadData();
    }, [empresa, obra, refreshKey]);

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`/api/evolucao?empresa=${empresa}&obra=${obra}&data=${filterData}`);
            if (!response.ok) throw new Error('Erro ao carregar dados');
            const result = await response.json();
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
        } finally {
            setLoading(false);
        }
    };

    const formatFullCurrency = (value: number) => {
        return value.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
    };

    // Find max value for chart scaling
    const maxChartValue = data?.recebimentosDiarios?.length
        ? Math.max(...data.recebimentosDiarios.map(d => d.valor))
        : 0;

    // Format selected date for display
    const formatSelectedDate = () => {
        const [_year, month, day] = filterData.split('-');
        return `${day}/${month}`;
    };

    return (
        <div className="animate-fade-in">
            {/* Header */}
            <PageHeader
                title="📊 Evolução do Empreendimento"
                subtitle={`Visão executiva de vendas, recebimentos e estoque ${data ? `• Atualizado em ${data.dataAtualizacao}` : ''}`}
                style={{ marginBottom: '16px' }}
            />

            {/* Filter Controls */}
            <div className="card" style={{ padding: '16px', marginBottom: '24px' }}>
                <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-end', flexWrap: 'wrap' }}>
                    <div style={{ flex: '1', minWidth: '140px' }}>
                        <label style={{ fontSize: '11px', color: '#6B7280', display: 'block', marginBottom: '4px' }}>
                            DATA REFERÊNCIA
                        </label>
                        <input
                            type="date"
                            value={filterData}
                            onChange={(e) => setFilterData(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '8px 12px',
                                borderRadius: '8px',
                                border: '1px solid #E5E7EB',
                                fontSize: '14px'
                            }}
                        />
                    </div>
                    <button
                        onClick={loadData}
                        className="btn btn-primary"
                        disabled={loading}
                        style={{ height: '40px', minWidth: '120px' }}
                    >
                        {loading ? '⏳ Carregando...' : '🔍 Buscar'}
                    </button>
                </div>
            </div>

            {/* Loading State */}
            {loading && <LoadingSpinner />}

            {/* Error State */}
            {error && !loading && <ErrorMessage message={error} />}

            {/* Data Display */}
            {data && !loading && (
                <>

                    {/* Main Metrics Row */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(4, 1fr)',
                        gap: '16px',
                        marginBottom: '24px'
                    }}>
                        {/* Vendas Hoje */}
                        <div className="card" style={{
                            background: 'linear-gradient(135deg, #3B82F6 0%, #1E40AF 100%)',
                            color: 'white',
                            padding: '20px',
                            borderRadius: '16px'
                        }}>
                            <div style={{ fontSize: '12px', opacity: 0.9, marginBottom: '4px' }}>VENDAS {formatSelectedDate()}</div>
                            <div style={{ fontSize: '32px', fontWeight: 700 }}>{data.vendas.hoje}</div>
                            <div style={{ fontSize: '14px', opacity: 0.8, marginTop: '8px' }}>
                                R$ {formatCurrency(data.vendas.valorHoje)}
                            </div>
                        </div>

                        {/* Recebimentos Hoje */}
                        <div className="card" style={{
                            background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                            color: 'white',
                            padding: '20px',
                            borderRadius: '16px'
                        }}>
                            <div style={{ fontSize: '12px', opacity: 0.9, marginBottom: '4px' }}>RECEBIDO {formatSelectedDate()}</div>
                            <div style={{ fontSize: '28px', fontWeight: 700 }}>R$ {formatCurrency(data.recebimentos.hoje)}</div>
                            <div style={{ fontSize: '11px', opacity: 0.8, marginTop: '8px' }}>
                                📅 Mês: R$ {formatCurrency(data.recebimentos.mes)}
                            </div>
                        </div>

                        {/* Inadimplência */}
                        <div className="card" style={{
                            background: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
                            color: 'white',
                            padding: '20px',
                            borderRadius: '16px'
                        }}>
                            <div style={{ fontSize: '12px', opacity: 0.9, marginBottom: '4px' }}>INADIMPLÊNCIA</div>
                            <div style={{ fontSize: '28px', fontWeight: 700 }}>R$ {formatCurrency(data.inadimplencia.valor)}</div>
                            <div style={{ fontSize: '11px', opacity: 0.8, marginTop: '8px' }}>
                                ⚠️ {data.inadimplencia.parcelas} parcelas em atraso
                            </div>
                        </div>

                        {/* Sinais Pagos */}
                        <div className="card" style={{
                            background: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)',
                            color: 'white',
                            padding: '20px',
                            borderRadius: '16px'
                        }}>
                            <div style={{ fontSize: '12px', opacity: 0.9, marginBottom: '4px' }}>SINAIS QUITADOS</div>
                            <div style={{ fontSize: '28px', fontWeight: 700 }}>R$ {formatCurrency(data.sinais.valorPago)}</div>
                            <div style={{ fontSize: '11px', opacity: 0.8, marginTop: '8px' }}>
                                ✅ {data.sinais.pagos} sinais pagos
                            </div>
                        </div>
                    </div>

                    {/* Second Row - Vendas & Recebimentos Período */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(3, 1fr)',
                        gap: '16px',
                        marginBottom: '24px'
                    }}>
                        {/* Vendas Mês */}
                        <div className="card" style={{ padding: '20px', borderLeft: '4px solid #3B82F6' }}>
                            <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>VENDAS DO MÊS</div>
                            <div style={{ fontSize: '28px', fontWeight: 700, color: '#1E40AF' }}>{data.vendas.mes}</div>
                            <div style={{ fontSize: '14px', color: '#3B82F6', marginTop: '4px' }}>
                                R$ {formatFullCurrency(data.vendas.valorMes)}
                            </div>
                        </div>

                        {/* Vendas Ano */}
                        <div className="card" style={{ padding: '20px', borderLeft: '4px solid #10B981' }}>
                            <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>VENDAS DO ANO</div>
                            <div style={{ fontSize: '28px', fontWeight: 700, color: '#059669' }}>{data.vendas.ano}</div>
                            <div style={{ fontSize: '14px', color: '#10B981', marginTop: '4px' }}>
                                R$ {formatFullCurrency(data.vendas.valorAno)}
                            </div>
                        </div>

                        {/* Total Vendas */}
                        <div className="card" style={{ padding: '20px', borderLeft: '4px solid #8B5CF6' }}>
                            <div style={{ fontSize: '11px', color: '#6B7280', marginBottom: '4px' }}>TOTAL GERAL</div>
                            <div style={{ fontSize: '28px', fontWeight: 700, color: '#6D28D9' }}>{data.vendas.total}</div>
                            <div style={{ fontSize: '14px', color: '#8B5CF6', marginTop: '4px' }}>
                                R$ {formatFullCurrency(data.vendas.valorTotal)}
                            </div>
                        </div>
                    </div>

                    {/* Chart and Estoque Row */}
                    <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '16px', marginBottom: '24px' }}>
                        {/* Gráfico de Recebimentos Diários */}
                        <div className="card" style={{ padding: '20px' }}>
                            <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '16px', color: '#374151' }}>
                                📈 Recebimentos Diários (Últimos 30 dias)
                            </h3>
                            <div style={{
                                display: 'flex',
                                alignItems: 'flex-end',
                                gap: '4px',
                                height: '200px',
                                padding: '10px 0',
                                borderBottom: '2px solid #E5E7EB'
                            }}>
                                {data.recebimentosDiarios.map((dia, index) => {
                                    const height = maxChartValue > 0
                                        ? (dia.valor / maxChartValue) * 180
                                        : 0;
                                    return (
                                        <div
                                            key={index}
                                            style={{
                                                flex: 1,
                                                display: 'flex',
                                                flexDirection: 'column',
                                                alignItems: 'center',
                                                gap: '4px'
                                            }}
                                        >
                                            <div
                                                style={{
                                                    width: '100%',
                                                    height: `${Math.max(height, 4)}px`,
                                                    background: 'linear-gradient(180deg, #10B981 0%, #059669 100%)',
                                                    borderRadius: '4px 4px 0 0',
                                                    transition: 'height 0.3s ease',
                                                    cursor: 'pointer'
                                                }}
                                                title={`${dia.dataFormatada}: R$ ${formatFullCurrency(dia.valor)}`}
                                            />
                                        </div>
                                    );
                                })}
                            </div>
                            <div style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                marginTop: '8px',
                                fontSize: '10px',
                                color: '#9CA3AF'
                            }}>
                                <span>{data.recebimentosDiarios[0]?.dataFormatada || '-'}</span>
                                <span>{data.recebimentosDiarios[data.recebimentosDiarios.length - 1]?.dataFormatada || '-'}</span>
                            </div>
                        </div>

                        {/* Estoque */}
                        <div className="card" style={{ padding: '20px' }}>
                            <h3 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '16px', color: '#374151' }}>
                                🏠 Estoque de Lotes
                            </h3>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontSize: '13px', color: '#374151' }}>🟢 Disponível</span>
                                    <span className="badge badge-success" style={{ fontSize: '14px', fontWeight: 600 }}>
                                        {data.estoque.disponivel}
                                    </span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontSize: '13px', color: '#374151' }}>🟡 Reservado</span>
                                    <span className="badge badge-warning" style={{ fontSize: '14px', fontWeight: 600 }}>
                                        {data.estoque.reservado}
                                    </span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontSize: '13px', color: '#374151' }}>🔵 Vendido</span>
                                    <span className="badge badge-primary" style={{ fontSize: '14px', fontWeight: 600 }}>
                                        {data.estoque.vendido}
                                    </span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontSize: '13px', color: '#374151' }}>✅ Quitado</span>
                                    <span style={{
                                        background: '#8B5CF6',
                                        color: 'white',
                                        padding: '2px 10px',
                                        borderRadius: '10px',
                                        fontSize: '14px',
                                        fontWeight: 600
                                    }}>
                                        {data.estoque.quitado}
                                    </span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontSize: '13px', color: '#374151' }}>⚪ Suspenso</span>
                                    <span style={{
                                        background: '#9CA3AF',
                                        color: 'white',
                                        padding: '2px 10px',
                                        borderRadius: '10px',
                                        fontSize: '14px',
                                        fontWeight: 600
                                    }}>
                                        {data.estoque.suspenso}
                                    </span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontSize: '13px', color: '#374151' }}>⛔ Fora de Venda</span>
                                    <span className="badge badge-danger" style={{ fontSize: '14px', fontWeight: 600 }}>
                                        {data.estoque.foraVenda}
                                    </span>
                                </div>
                                <div style={{
                                    borderTop: '1px solid #E5E7EB',
                                    paddingTop: '12px',
                                    marginTop: '8px',
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center'
                                }}>
                                    <span style={{ fontSize: '14px', fontWeight: 600, color: '#374151' }}>TOTAL</span>
                                    <span style={{
                                        background: '#1E40AF',
                                        color: 'white',
                                        padding: '4px 12px',
                                        borderRadius: '10px',
                                        fontSize: '16px',
                                        fontWeight: 700
                                    }}>
                                        {data.estoque.total}
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div style={{
                        textAlign: 'center',
                        padding: '16px',
                        color: '#9CA3AF',
                        fontSize: '11px'
                    }}>
                        © 2025 VallePrime - Desenvolvido por Vinicius Dev
                    </div>
                </>
            )}
        </div>
    );
};
