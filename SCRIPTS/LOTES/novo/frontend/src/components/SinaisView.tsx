import React, { useState, useEffect } from 'react';
import { MetricCard } from './MetricCard';
import { api } from '../api/client';
import type { Sinal } from '../types';

interface SinaisViewProps {
    empresa: number;
    obra: string;
    dataVencimento: string;
    refreshKey: number;
}

export const SinaisView: React.FC<SinaisViewProps> = ({
    empresa,
    obra,
    dataVencimento,
    refreshKey,
}) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<Sinal[]>([]);
    const [metrics, setMetrics] = useState<{
        totalParcelas: number;
        valorTotal: number;
        vendasDistintas: number;
    } | null>(null);

    useEffect(() => {
        loadData();
    }, [empresa, obra, dataVencimento, refreshKey]);

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.getSinais(empresa, obra, dataVencimento);
            setData(response.data);
            setMetrics(response.metrics);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadCsv = () => {
        const headers = ['Corretor', 'Cliente', 'Venda', 'Quadra', 'Lote', 'Parcela', 'Vencimento', 'Valor'];
        const rows = data.map(s => [
            s.corretor,
            s.cliente,
            s.venda,
            s.quadra,
            s.lote,
            `${s.parcela}/${s.qtdParcelas}`,
            s.vencimento,
            s.valorParcela
        ]);

        const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
        const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `sinais_corretagem_${new Date().toISOString().slice(0, 10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    if (loading) {
        return (
            <div className="loading">
                <div className="spinner"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ background: '#FEE2E2', borderColor: '#EF4444' }}>
                <p style={{ color: '#991B1B' }}>❌ {error}</p>
            </div>
        );
    }

    return (
        <div className="animate-fade-in">
            {/* Metrics */}
            {metrics && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
                    <MetricCard
                        icon="📊"
                        label="Total de Parcelas"
                        value={metrics.totalParcelas}
                        color="primary"
                    />
                    <MetricCard
                        icon="💰"
                        label="Valor Total"
                        value={`R$ ${metrics.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`}
                        color="success"
                    />
                    <MetricCard
                        icon="🏠"
                        label="Vendas Distintas"
                        value={metrics.vendasDistintas}
                        color="warning"
                    />
                </div>
            )}

            {/* Table */}
            {data.length > 0 ? (
                <div className="table-container">
                    <div className="table-header-row">
                        <span className="table-title">Sinais de Corretagem</span>
                        <button onClick={handleDownloadCsv} className="btn btn-outline" style={{ padding: '8px 16px' }}>
                            📄 CSV
                        </button>
                    </div>
                    <table>
                        <thead>
                            <tr>
                                <th>Corretor</th>
                                <th>Cliente</th>
                                <th style={{ textAlign: 'center' }}>Venda</th>
                                <th style={{ textAlign: 'center' }}>Quadra</th>
                                <th style={{ textAlign: 'center' }}>Lote</th>
                                <th style={{ textAlign: 'center' }}>Parcela</th>
                                <th style={{ textAlign: 'center' }}>Vencimento</th>
                                <th style={{ textAlign: 'right' }}>Valor</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((sinal, index) => (
                                <tr key={`${sinal.venda}-${sinal.parcela}-${index}`}>
                                    <td>{sinal.corretor}</td>
                                    <td>{sinal.cliente}</td>
                                    <td style={{ textAlign: 'center', fontWeight: 600 }}>{sinal.venda}</td>
                                    <td style={{ textAlign: 'center', color: '#6B7280' }}>{sinal.quadra}</td>
                                    <td style={{ textAlign: 'center', color: '#6B7280' }}>{sinal.lote}</td>
                                    <td style={{ textAlign: 'center' }}>
                                        <span className="badge badge-primary">{sinal.parcela}/{sinal.qtdParcelas}</span>
                                    </td>
                                    <td style={{ textAlign: 'center', color: '#6B7280' }}>{sinal.vencimento}</td>
                                    <td style={{ textAlign: 'right', fontWeight: 500, color: '#10B981' }}>
                                        R$ {sinal.valorParcela?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            ) : (
                <div className="card empty-state">
                    <div className="empty-state-icon">📭</div>
                    <p>Nenhum sinal de corretagem encontrado para o período selecionado.</p>
                </div>
            )}
        </div>
    );
};
