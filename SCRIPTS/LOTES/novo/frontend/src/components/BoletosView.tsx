import React, { useState, useEffect } from 'react';
import { MetricCard } from './MetricCard';
import { api } from '../api/client';
import type { Boleto } from '../types';

interface BoletosViewProps {
    empresa: number;
    refreshKey: number;
}

export const BoletosView: React.FC<BoletosViewProps> = ({ empresa, refreshKey }) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<Boleto[]>([]);
    const [filteredData, setFilteredData] = useState<Boleto[]>([]);
    const [vendaFilter, setVendaFilter] = useState<string>('');
    const [vendas, setVendas] = useState<number[]>([]);

    useEffect(() => {
        loadData();
    }, [empresa, refreshKey]);

    useEffect(() => {
        if (vendaFilter === '') {
            setFilteredData(data);
        } else {
            const vendaNum = parseInt(vendaFilter);
            setFilteredData(data.filter(b => b.venda === vendaNum));
        }
    }, [vendaFilter, data]);

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.getBoletos(empresa);
            setData(response.data);
            setFilteredData(response.data);

            const uniqueVendas = [...new Set(response.data.map(b => b.venda))].sort((a, b) => a - b);
            setVendas(uniqueVendas);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadCsv = () => {
        const headers = ['Venda', 'Parcela', 'Cliente', 'Nosso Número', 'Emissão', 'Vencimento', 'Valor', 'Enviado'];
        const rows = filteredData.map(b => [
            b.venda,
            b.parcela,
            b.cliente,
            b.nossoNumero,
            b.dataEmissao,
            b.dataVencimento,
            b.valorDocumento,
            b.enviadoEmail ? 'Sim' : 'Não'
        ]);

        const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
        const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `boletos_${new Date().toISOString().slice(0, 10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const currentMetrics = {
        totalBoletos: filteredData.length,
        enviadosEmail: filteredData.filter(b => b.enviadoEmail).length,
        valorTotal: filteredData.reduce((sum, b) => sum + (b.valorDocumento || 0), 0)
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
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
                <MetricCard
                    icon="📊"
                    label="Total de Boletos"
                    value={currentMetrics.totalBoletos}
                    color="primary"
                />
                <MetricCard
                    icon="📧"
                    label="Enviados por Email"
                    value={currentMetrics.enviadosEmail}
                    color="success"
                />
                <MetricCard
                    icon="💰"
                    label="Valor Total"
                    value={`R$ ${currentMetrics.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`}
                    color="warning"
                />
            </div>

            {/* Table */}
            <div className="table-container">
                <div className="table-header-row">
                    <span className="table-title">Boletos Gerados</span>
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                        <select
                            value={vendaFilter}
                            onChange={(e) => setVendaFilter(e.target.value)}
                            className="form-select"
                            style={{ width: 'auto', minWidth: '150px' }}
                        >
                            <option value="">Todas as Vendas</option>
                            {vendas.map(v => (
                                <option key={v} value={v}>Venda {v}</option>
                            ))}
                        </select>
                        <button onClick={handleDownloadCsv} className="btn btn-outline" style={{ padding: '8px 16px' }}>
                            📄 CSV
                        </button>
                    </div>
                </div>

                {filteredData.length > 0 ? (
                    <table>
                        <thead>
                            <tr>
                                <th style={{ textAlign: 'center' }}>Venda</th>
                                <th style={{ textAlign: 'center' }}>Parcela</th>
                                <th>Cliente</th>
                                <th>Nosso Número</th>
                                <th style={{ textAlign: 'center' }}>Emissão</th>
                                <th style={{ textAlign: 'center' }}>Vencimento</th>
                                <th style={{ textAlign: 'right' }}>Valor</th>
                                <th style={{ textAlign: 'center' }}>Email</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredData.map((boleto, index) => (
                                <tr key={`${boleto.venda}-${boleto.parcela}-${index}`}>
                                    <td style={{ textAlign: 'center', fontWeight: 600 }}>{boleto.venda}</td>
                                    <td style={{ textAlign: 'center' }}>
                                        <span className="badge badge-primary">{boleto.parcela}</span>
                                    </td>
                                    <td>{boleto.cliente}</td>
                                    <td style={{ fontFamily: 'monospace', color: '#6B7280', fontSize: '13px' }}>{boleto.nossoNumero}</td>
                                    <td style={{ textAlign: 'center', color: '#6B7280' }}>{boleto.dataEmissao}</td>
                                    <td style={{ textAlign: 'center', color: '#6B7280' }}>{boleto.dataVencimento}</td>
                                    <td style={{ textAlign: 'right', fontWeight: 500, color: '#10B981' }}>
                                        R$ {boleto.valorDocumento?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </td>
                                    <td style={{ textAlign: 'center' }}>
                                        {boleto.enviadoEmail ? (
                                            <span className="badge badge-success">Sim</span>
                                        ) : (
                                            <span className="badge badge-danger">Não</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <div className="empty-state">
                        <div className="empty-state-icon">📭</div>
                        <p>Nenhum boleto encontrado.</p>
                    </div>
                )}
            </div>
        </div>
    );
};
