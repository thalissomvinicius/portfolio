import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Venda, SinalPago, Boleto } from '../types';

interface VendaDetailsViewProps {
    empresa: number;
    obra: string;
    refreshKey: number;
}

export const VendaDetailsView: React.FC<VendaDetailsViewProps> = ({
    empresa,
    obra,
    refreshKey,
}) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [vendas, setVendas] = useState<Venda[]>([]);
    const [selectedVenda, setSelectedVenda] = useState<number | null>(null);
    const [selectedVendaData, setSelectedVendaData] = useState<Venda | null>(null);
    const [sinaisPagos, setSinaisPagos] = useState<SinalPago[]>([]);
    const [boletos, setBoletos] = useState<Boleto[]>([]);
    const [loadingDetails, setLoadingDetails] = useState(false);

    useEffect(() => {
        loadVendas();
    }, [empresa, obra, refreshKey]);

    useEffect(() => {
        if (selectedVenda) {
            loadDetails(selectedVenda);
        }
    }, [selectedVenda]);

    const loadVendas = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.getVendas(empresa, obra);
            setVendas(response.data);
            if (response.data.length > 0) {
                setSelectedVenda(response.data[0].venda);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao carregar vendas');
        } finally {
            setLoading(false);
        }
    };

    const loadDetails = async (vendaNum: number) => {
        setLoadingDetails(true);
        try {
            const vendaData = vendas.find(v => v.venda === vendaNum);
            setSelectedVendaData(vendaData || null);

            const [sinaisResponse, boletosResponse] = await Promise.all([
                api.getSinaisPagos(vendaNum, empresa, obra).catch(() => ({ data: [] })),
                api.getBoletos(empresa, vendaNum).catch(() => ({ data: [] }))
            ]);

            setSinaisPagos(sinaisResponse.data);
            setBoletos(boletosResponse.data);
        } catch (err) {
            console.error('Error loading details:', err);
        } finally {
            setLoadingDetails(false);
        }
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
            {/* Venda Selector */}
            <div className="card" style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <div className="metric-label">Selecione uma Venda</div>
                        <select
                            value={selectedVenda || ''}
                            onChange={(e) => setSelectedVenda(parseInt(e.target.value))}
                            className="form-select"
                            style={{ minWidth: '300px', marginTop: '8px' }}
                        >
                            {vendas.map(v => (
                                <option key={v.venda} value={v.venda}>
                                    Venda {v.venda} - {v.cliente?.substring(0, 30)}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>

            {loadingDetails ? (
                <div className="loading">
                    <div className="spinner"></div>
                </div>
            ) : selectedVendaData ? (
                <>
                    {/* Venda Info */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
                        <div className="card">
                            <div className="card-title">📋 Informações da Venda</div>
                            <div style={{ display: 'grid', gap: '12px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span style={{ color: '#6B7280' }}>Venda:</span>
                                    <span style={{ fontWeight: 600 }}>{selectedVendaData.venda}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span style={{ color: '#6B7280' }}>Cliente:</span>
                                    <span>{selectedVendaData.cliente}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span style={{ color: '#6B7280' }}>Corretor:</span>
                                    <span>{selectedVendaData.corretor}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span style={{ color: '#6B7280' }}>Identificador:</span>
                                    <span>{selectedVendaData.identificador}</span>
                                </div>
                            </div>
                        </div>

                        <div className="card">
                            <div className="card-title">💰 Valores</div>
                            <div style={{ display: 'grid', gap: '12px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                    <span style={{ color: '#6B7280' }}>Data da Venda:</span>
                                    <span>{selectedVendaData.dataVenda}</span>
                                </div>
                                <div style={{ marginTop: '20px' }}>
                                    <div className="metric-label">Valor Total</div>
                                    <div className="metric-value success" style={{ fontSize: '28px' }}>
                                        R$ {selectedVendaData.valorTotal?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Sinais Pagos */}
                    <div className="table-container" style={{ marginBottom: '24px' }}>
                        <div className="table-header-row">
                            <span className="table-title">✅ Sinais Pagos</span>
                            <span className="badge badge-success">{sinaisPagos.length} registros</span>
                        </div>
                        {sinaisPagos.length > 0 ? (
                            <table>
                                <thead>
                                    <tr>
                                        <th>Parcela</th>
                                        <th>Data Recebimento</th>
                                        <th>Data Vencimento</th>
                                        <th style={{ textAlign: 'right' }}>Valor Pago</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {sinaisPagos.map((sinal, index) => (
                                        <tr key={index}>
                                            <td><span className="badge badge-success">{sinal.parcela}</span></td>
                                            <td>{sinal.dataRecebimento}</td>
                                            <td style={{ color: '#6B7280' }}>{sinal.dataVencimento}</td>
                                            <td style={{ textAlign: 'right', fontWeight: 500, color: '#10B981' }}>
                                                R$ {sinal.valorPago?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <div className="empty-state" style={{ padding: '30px' }}>
                                <p style={{ color: '#6B7280' }}>Nenhum sinal pago encontrado.</p>
                            </div>
                        )}
                    </div>

                    {/* Boletos */}
                    <div className="table-container">
                        <div className="table-header-row">
                            <span className="table-title">📄 Boletos da Venda</span>
                            <span className="badge badge-primary">{boletos.length} registros</span>
                        </div>
                        {boletos.length > 0 ? (
                            <table>
                                <thead>
                                    <tr>
                                        <th>Parcela</th>
                                        <th>Nosso Número</th>
                                        <th>Vencimento</th>
                                        <th style={{ textAlign: 'right' }}>Valor</th>
                                        <th style={{ textAlign: 'center' }}>Email</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {boletos.map((boleto, index) => (
                                        <tr key={index}>
                                            <td><span className="badge badge-primary">{boleto.parcela}</span></td>
                                            <td style={{ fontFamily: 'monospace', color: '#6B7280' }}>{boleto.nossoNumero}</td>
                                            <td>{boleto.dataVencimento}</td>
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
                            <div className="empty-state" style={{ padding: '30px' }}>
                                <p style={{ color: '#6B7280' }}>Nenhum boleto gerado para esta venda.</p>
                            </div>
                        )}
                    </div>
                </>
            ) : (
                <div className="card empty-state">
                    <div className="empty-state-icon">🔍</div>
                    <p>Selecione uma venda para ver os detalhes.</p>
                </div>
            )}
        </div>
    );
};
