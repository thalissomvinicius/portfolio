import React, { useState, useEffect } from 'react';
import type { Filters } from '../types';

interface DashboardExecutivoProps {
    filters: Filters;
    refreshKey: number;
}

interface StatusResumo {
    status: string;
    qtde: number;
    percent: number;
    valor: number;
}

interface VendaDiaria {
    data: string;
    qtdVendas: number;
    valorVendas: number;
    qtdCancelamentos: number;
    valorMedio: number;
}

interface TotaisPeriodo {
    totalVendas: number;
    valorTotalVendas: number;
    totalCancelamentos: number;
    valorMedio: number;
}

interface DashboardData {
    resumoStatus: StatusResumo[];
    totalUnidades: number;
    valorTotalUnidades: number;
    vendasDiarias: VendaDiaria[];
    totaisPeriodo: TotaisPeriodo;
    periodo: {
        inicio: string;
        fim: string;
    };
}

const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
};

const formatNumber = (value: number): string => {
    return new Intl.NumberFormat('pt-BR').format(value);
};

// Status colors
const statusColors: Record<string, string> = {
    'Vendido': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    'Quitado': 'linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)',
    'Reservado': 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    'Disponível': 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%)',
    'Suspenso': 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
    'Fora de Venda': 'linear-gradient(135deg, #6b7280 0%, #4b5563 100%)',
    'Permuta/Dação': 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)'
};

export const DashboardExecutivo: React.FC<DashboardExecutivoProps> = ({ filters, refreshKey }) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<DashboardData | null>(null);
    const [dataInicio, setDataInicio] = useState<string>('');
    const [dataFim, setDataFim] = useState<string>('');

    useEffect(() => {
        loadData();
    }, [filters.empresa, filters.obra, refreshKey]);

    const loadData = async (inicio?: string, fim?: string) => {
        setLoading(true);
        setError(null);
        try {
            let url = `/api/dashboard-resumo?empresa=${filters.empresa}&obra=${filters.obra}`;
            if (inicio) url += `&data_inicio=${inicio}`;
            if (fim) url += `&data_fim=${fim}`;

            const response = await fetch(url);
            if (!response.ok) throw new Error('Erro ao carregar dados');
            const result = await response.json();
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
        } finally {
            setLoading(false);
        }
    };

    const handleFilterSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        loadData(dataInicio, dataFim);
    };

    if (loading) {
        return (
            <div className="dashboard-loading">
                <div className="loading-spinner"></div>
                <p>Carregando Dashboard Executivo...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="dashboard-error">
                <div className="error-icon">⚠️</div>
                <p>{error}</p>
                <button onClick={() => loadData()}>Tentar novamente</button>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="dashboard-executivo">
            {/* Header with period filter */}
            <div className="dashboard-header">
                <div className="header-title">
                    <h2>📊 Dashboard Executivo</h2>
                    <span className="periodo-badge">
                        Período: {data.periodo.inicio} a {data.periodo.fim}
                    </span>
                </div>
                <form className="date-filter-form" onSubmit={handleFilterSubmit}>
                    <div className="date-inputs">
                        <input
                            type="text"
                            placeholder="dd/mm/yyyy"
                            value={dataInicio}
                            onChange={(e) => setDataInicio(e.target.value)}
                            className="date-input"
                        />
                        <span>até</span>
                        <input
                            type="text"
                            placeholder="dd/mm/yyyy"
                            value={dataFim}
                            onChange={(e) => setDataFim(e.target.value)}
                            className="date-input"
                        />
                    </div>
                    <button type="submit" className="filter-btn">
                        🔍 Filtrar
                    </button>
                </form>
            </div>

            {/* Status Summary Cards */}
            <section className="status-section">
                <h3>📋 Resumo por Status de Unidades</h3>
                <div className="status-cards">
                    {data.resumoStatus.map((s) => (
                        <div
                            key={s.status}
                            className="status-card"
                            style={{ background: statusColors[s.status] || statusColors['Disponível'] }}
                        >
                            <div className="status-name">{s.status}</div>
                            <div className="status-qtde">{formatNumber(s.qtde)}</div>
                            <div className="status-percent">{s.percent.toFixed(2)}%</div>
                            {s.valor > 0 && (
                                <div className="status-valor">{formatCurrency(s.valor)}</div>
                            )}
                        </div>
                    ))}
                    <div className="status-card total-card">
                        <div className="status-name">TOTAL</div>
                        <div className="status-qtde">{formatNumber(data.totalUnidades)}</div>
                        <div className="status-percent">100%</div>
                        <div className="status-valor">{formatCurrency(data.valorTotalUnidades)}</div>
                    </div>
                </div>
            </section>

            {/* Period Totals */}
            <section className="totals-section">
                <h3>📈 Totais do Período</h3>
                <div className="totals-cards">
                    <div className="total-card vendas">
                        <div className="total-icon">🏠</div>
                        <div className="total-info">
                            <div className="total-label">Vendas</div>
                            <div className="total-value">{formatNumber(data.totaisPeriodo.totalVendas)}</div>
                        </div>
                    </div>
                    <div className="total-card valor">
                        <div className="total-icon">💰</div>
                        <div className="total-info">
                            <div className="total-label">Valor Total</div>
                            <div className="total-value">{formatCurrency(data.totaisPeriodo.valorTotalVendas)}</div>
                        </div>
                    </div>
                    <div className="total-card medio">
                        <div className="total-icon">📊</div>
                        <div className="total-info">
                            <div className="total-label">Valor Médio</div>
                            <div className="total-value">{formatCurrency(data.totaisPeriodo.valorMedio)}</div>
                        </div>
                    </div>
                    <div className="total-card cancelamentos">
                        <div className="total-icon">❌</div>
                        <div className="total-info">
                            <div className="total-label">Cancelamentos</div>
                            <div className="total-value">{formatNumber(data.totaisPeriodo.totalCancelamentos)}</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Daily Sales Table */}
            <section className="daily-section">
                <h3>📅 Resumo Diário (por data de cadastro)</h3>
                <div className="table-container">
                    <table className="daily-table">
                        <thead>
                            <tr>
                                <th>Data</th>
                                <th>Vendas</th>
                                <th>Valor Total</th>
                                <th>Valor Médio</th>
                                <th>Cancelamentos</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.vendasDiarias.map((d) => (
                                <tr key={d.data}>
                                    <td className="data-cell">{d.data}</td>
                                    <td className="qtd-cell">{formatNumber(d.qtdVendas)}</td>
                                    <td className="valor-cell">{formatCurrency(d.valorVendas)}</td>
                                    <td className="valor-cell">{formatCurrency(d.valorMedio)}</td>
                                    <td className={`cancel-cell ${d.qtdCancelamentos > 0 ? 'has-cancel' : ''}`}>
                                        {d.qtdCancelamentos > 0 ? d.qtdCancelamentos : '-'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                        <tfoot>
                            <tr className="total-row">
                                <td>TOTAL</td>
                                <td>{formatNumber(data.totaisPeriodo.totalVendas)}</td>
                                <td>{formatCurrency(data.totaisPeriodo.valorTotalVendas)}</td>
                                <td>{formatCurrency(data.totaisPeriodo.valorMedio)}</td>
                                <td className="has-cancel">{data.totaisPeriodo.totalCancelamentos}</td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </section>

            <style>{`
                .dashboard-executivo {
                    padding: 1.5rem;
                    max-width: 1400px;
                    margin: 0 auto;
                }

                .dashboard-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 2rem;
                    flex-wrap: wrap;
                    gap: 1rem;
                }

                .header-title h2 {
                    margin: 0;
                    font-size: 1.75rem;
                    color: var(--text-primary);
                }

                .periodo-badge {
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 0.25rem 0.75rem;
                    border-radius: 20px;
                    font-size: 0.875rem;
                    margin-top: 0.5rem;
                }

                .date-filter-form {
                    display: flex;
                    align-items: center;
                    gap: 0.75rem;
                }

                .date-inputs {
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }

                .date-input {
                    padding: 0.5rem 0.75rem;
                    border: 1px solid var(--border-color);
                    border-radius: 8px;
                    background: var(--bg-secondary);
                    color: var(--text-primary);
                    width: 120px;
                }

                .filter-btn {
                    padding: 0.5rem 1rem;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: 500;
                    transition: transform 0.2s;
                }

                .filter-btn:hover {
                    transform: scale(1.02);
                }

                section {
                    margin-bottom: 2rem;
                }

                section h3 {
                    font-size: 1.25rem;
                    color: var(--text-secondary);
                    margin-bottom: 1rem;
                    border-bottom: 2px solid var(--border-color);
                    padding-bottom: 0.5rem;
                }

                /* Status Cards */
                .status-cards {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                    gap: 1rem;
                }

                .status-card {
                    padding: 1rem;
                    border-radius: 12px;
                    color: white;
                    text-align: center;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                    transition: transform 0.2s;
                }

                .status-card:hover {
                    transform: translateY(-3px);
                }

                .status-card.total-card {
                    background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
                    border: 2px solid #3b82f6;
                }

                .status-name {
                    font-size: 0.875rem;
                    font-weight: 600;
                    opacity: 0.9;
                    margin-bottom: 0.5rem;
                }

                .status-qtde {
                    font-size: 1.75rem;
                    font-weight: 700;
                }

                .status-percent {
                    font-size: 0.875rem;
                    opacity: 0.8;
                }

                .status-valor {
                    font-size: 0.75rem;
                    margin-top: 0.5rem;
                    opacity: 0.9;
                }

                /* Totals Section */
                .totals-cards {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                }

                .totals-cards .total-card {
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    padding: 1.25rem;
                    border-radius: 12px;
                    background: var(--bg-secondary);
                    border: 1px solid var(--border-color);
                    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                }

                .totals-cards .total-card.vendas {
                    border-left: 4px solid #10b981;
                }

                .totals-cards .total-card.valor {
                    border-left: 4px solid #3b82f6;
                }

                .totals-cards .total-card.medio {
                    border-left: 4px solid #f59e0b;
                }

                .totals-cards .total-card.cancelamentos {
                    border-left: 4px solid #ef4444;
                }

                .total-icon {
                    font-size: 2rem;
                }

                .total-label {
                    font-size: 0.875rem;
                    color: var(--text-secondary);
                }

                .total-value {
                    font-size: 1.25rem;
                    font-weight: 700;
                    color: var(--text-primary);
                }

                /* Daily Table */
                .table-container {
                    overflow-x: auto;
                    border-radius: 12px;
                    border: 1px solid var(--border-color);
                }

                .daily-table {
                    width: 100%;
                    border-collapse: collapse;
                    background: var(--bg-secondary);
                }

                .daily-table th,
                .daily-table td {
                    padding: 0.75rem 1rem;
                    text-align: left;
                    border-bottom: 1px solid var(--border-color);
                }

                .daily-table th {
                    background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
                    color: white;
                    font-weight: 600;
                    font-size: 0.875rem;
                }

                .daily-table tbody tr:hover {
                    background: var(--bg-tertiary);
                }

                .data-cell {
                    font-weight: 500;
                }

                .qtd-cell {
                    font-weight: 600;
                    color: var(--text-primary);
                }

                .valor-cell {
                    color: #10b981;
                    font-weight: 500;
                }

                .cancel-cell {
                    color: var(--text-secondary);
                }

                .cancel-cell.has-cancel {
                    color: #ef4444;
                    font-weight: 600;
                }

                .total-row {
                    background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%) !important;
                    color: white;
                    font-weight: 700;
                }

                .total-row td {
                    border-bottom: none;
                }

                .total-row .valor-cell {
                    color: #4ade80;
                }

                .total-row .has-cancel {
                    color: #f87171;
                }

                /* Loading & Error States */
                .dashboard-loading,
                .dashboard-error {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    padding: 4rem;
                    text-align: center;
                }

                .loading-spinner {
                    width: 50px;
                    height: 50px;
                    border: 4px solid var(--border-color);
                    border-top-color: #667eea;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin-bottom: 1rem;
                }

                @keyframes spin {
                    to { transform: rotate(360deg); }
                }

                .error-icon {
                    font-size: 3rem;
                    margin-bottom: 1rem;
                }

                .dashboard-error button {
                    margin-top: 1rem;
                    padding: 0.75rem 1.5rem;
                    background: #667eea;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    cursor: pointer;
                }

                @media (max-width: 768px) {
                    .dashboard-header {
                        flex-direction: column;
                        align-items: flex-start;
                    }

                    .date-filter-form {
                        flex-direction: column;
                        align-items: stretch;
                        width: 100%;
                    }

                    .date-inputs {
                        flex-wrap: wrap;
                    }

                    .status-cards {
                        grid-template-columns: repeat(2, 1fr);
                    }
                }
            `}</style>
        </div>
    );
};
