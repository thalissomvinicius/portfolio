import React, { useState, useEffect, useMemo } from 'react';
import { MetricCard } from './MetricCard';
import { api } from '../api/client';
import type { ResumoVenda, Metrics, Filters } from '../types';

interface DashboardProps {
    filters: Filters;
    refreshKey: number;
}

type BoletoFilter = 'todos' | 'gerado' | 'naoGerado';
type SinaisFilter = 'todos' | 'comSinais' | 'semSinais' | 'vencidos';

export const Dashboard: React.FC<DashboardProps> = ({ filters, refreshKey }) => {
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<ResumoVenda[]>([]);
    const [, setMetrics] = useState<Metrics | null>(null);
    const [downloadingPdf, setDownloadingPdf] = useState(false);

    // Local filters
    const [boletoFilter, setBoletoFilter] = useState<BoletoFilter>('todos');
    const [sinaisFilter, setSinaisFilter] = useState<SinaisFilter>('todos');
    const [corretorFilter, setCorretorFilter] = useState<string>('todos');
    const [startDate, setStartDate] = useState<string>('');
    const [endDate, setEndDate] = useState<string>('');

    // Get unique corretores list
    const corretoresList = useMemo(() => {
        const unique = [...new Set(data.map(v => v.corretor).filter(Boolean))];
        return unique.sort();
    }, [data]);

    useEffect(() => {
        loadData();
    }, [filters.empresa, filters.obra, refreshKey]);

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await api.getResumo(filters.empresa, filters.obra);
            setData(response.data);
            setMetrics(response.metrics);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
        } finally {
            setLoading(false);
        }
    };

    // Filtered data based on local filters
    const filteredData = useMemo(() => {
        let result = data;

        // Filter by boleto status
        if (boletoFilter === 'gerado') {
            result = result.filter(v => v.boletoGerado);
        } else if (boletoFilter === 'naoGerado') {
            result = result.filter(v => !v.boletoGerado);
        }

        // Filter by sinais status
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (sinaisFilter === 'comSinais') {
            result = result.filter(v => v.sinaisAberto > 0);
        } else if (sinaisFilter === 'semSinais') {
            result = result.filter(v => v.sinaisAberto === 0);
        } else if (sinaisFilter === 'vencidos') {
            result = result.filter(v => {
                if (v.sinaisAberto === 0 || !v.primeiroVencimentoISO) return false;
                const dueDate = new Date(v.primeiroVencimentoISO);
                return dueDate < today;
            });
        }

        // Filter by date range (using dataCadastro - registration date)
        if (startDate || endDate) {
            result = result.filter(v => {
                // Use dataCadastro for filtering (same as Power BI)
                const dateStr = (v as any).dataCadastro || v.dataVenda;
                if (!dateStr) return false;
                // date format: DD/MM/YYYY
                const parts = dateStr.split('/');
                if (parts.length !== 3) return false;
                const vendaDate = new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
                vendaDate.setHours(0, 0, 0, 0);

                if (startDate) {
                    // startDate format from input is YYYY-MM-DD
                    const startParts = startDate.split('-');
                    const start = new Date(parseInt(startParts[0]), parseInt(startParts[1]) - 1, parseInt(startParts[2]));
                    start.setHours(0, 0, 0, 0);
                    if (vendaDate < start) return false;
                }
                if (endDate) {
                    const endParts = endDate.split('-');
                    const end = new Date(parseInt(endParts[0]), parseInt(endParts[1]) - 1, parseInt(endParts[2]));
                    end.setHours(23, 59, 59, 999);
                    if (vendaDate > end) return false;
                }
                return true;
            });
        }

        // Filter by corretor
        if (corretorFilter !== 'todos') {
            result = result.filter(v => v.corretor === corretorFilter);
        }

        return result;
    }, [data, boletoFilter, sinaisFilter, corretorFilter, startDate, endDate]);

    const handleDownloadPdf = async () => {
        setDownloadingPdf(true);
        try {
            const { jsPDF } = await import('jspdf');
            const autoTable = (await import('jspdf-autotable')).default;

            const doc = new jsPDF({ orientation: 'landscape', unit: 'mm', format: 'a4' });

            // Header
            doc.setFillColor(30, 64, 175); // Blue
            doc.rect(0, 0, 297, 25, 'F');
            doc.setTextColor(255, 255, 255);
            doc.setFontSize(18);
            doc.setFont('helvetica', 'bold');
            doc.text('VallePrime - Relatório de Vendas', 14, 15);
            doc.setFontSize(10);
            doc.setFont('helvetica', 'normal');
            doc.text(`Obra: ${filters.obra} | Empresa: ${filters.empresa}`, 200, 10);
            doc.text(`Gerado em: ${new Date().toLocaleDateString('pt-BR')} às ${new Date().toLocaleTimeString('pt-BR')}`, 200, 16);

            // Filters applied
            let filterText = 'Filtros: ';
            if (boletoFilter !== 'todos') filterText += `Boleto: ${boletoFilter === 'gerado' ? 'Gerados' : 'Não Gerados'} | `;
            if (sinaisFilter !== 'todos') filterText += `Sinais: ${sinaisFilter} | `;
            if (filterText === 'Filtros: ') filterText += 'Nenhum';
            doc.text(filterText, 14, 22);

            // Summary metrics
            doc.setTextColor(0, 0, 0);
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text('Resumo:', 14, 35);
            doc.setFont('helvetica', 'normal');
            doc.setFontSize(10);

            const valorTotal = filteredData.reduce((sum, v) => sum + (v.valorTotal || 0), 0);
            const comBoleto = filteredData.filter(v => v.boletoGerado).length;
            const semBoleto = filteredData.filter(v => !v.boletoGerado).length;
            const sinaisAberto = filteredData.reduce((sum, v) => sum + v.sinaisAberto, 0);

            doc.text(`Total de Vendas: ${filteredData.length}`, 14, 42);
            doc.text(`Com Boleto: ${comBoleto}`, 60, 42);
            doc.text(`Sem Boleto: ${semBoleto}`, 100, 42);
            doc.text(`Sinais em Aberto: ${sinaisAberto}`, 140, 42);
            doc.text(`Valor Total: R$ ${valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`, 200, 42);

            // Table data
            const tableData = filteredData.map(v => {
                const { quadra, lote } = parseQuadraLote(v.identificador);
                return [
                    v.venda.toString(),
                    v.cliente || '',
                    quadra,
                    lote,
                    v.corretor || '',
                    v.dataVenda || '',
                    `R$ ${(v.valorTotal || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`,
                    v.boletoGerado ? 'Sim' : 'Não',
                    v.sinaisAberto > 0 ? `${v.sinaisAberto} (${v.primeiroVencimento || ''})` : '0'
                ];
            });

            autoTable(doc, {
                startY: 50,
                head: [['Venda', 'Cliente', 'Quadra', 'Lote', 'Corretor', 'Data', 'Valor', 'Boleto', 'Sinais']],
                body: tableData,
                theme: 'grid',
                headStyles: {
                    fillColor: [37, 99, 235],
                    textColor: 255,
                    fontStyle: 'bold',
                    fontSize: 9,
                    halign: 'center'
                },
                bodyStyles: {
                    fontSize: 8,
                    cellPadding: 2
                },
                columnStyles: {
                    0: { halign: 'center', cellWidth: 15 },
                    1: { cellWidth: 55 },
                    2: { halign: 'center', cellWidth: 15 },
                    3: { halign: 'center', cellWidth: 15 },
                    4: { cellWidth: 40 },
                    5: { halign: 'center', cellWidth: 22 },
                    6: { halign: 'right', cellWidth: 30 },
                    7: { halign: 'center', cellWidth: 18 },
                    8: { halign: 'center', cellWidth: 30 }
                },
                alternateRowStyles: {
                    fillColor: [248, 250, 252]
                },
                didParseCell: (data: any) => {
                    // Color Boleto column
                    if (data.column.index === 7 && data.section === 'body') {
                        if (data.cell.text[0] === 'Sim') {
                            data.cell.styles.textColor = [5, 150, 105];
                        } else {
                            data.cell.styles.textColor = [220, 38, 38];
                        }
                    }
                    // Color Sinais column if overdue
                    if (data.column.index === 8 && data.section === 'body') {
                        const row = filteredData[data.row.index];
                        if (row && row.sinaisAberto > 0 && row.primeiroVencimentoISO) {
                            const today = new Date();
                            today.setHours(0, 0, 0, 0);
                            const dueDate = new Date(row.primeiroVencimentoISO);
                            if (dueDate < today) {
                                data.cell.styles.textColor = [220, 38, 38]; // Red
                            } else {
                                data.cell.styles.textColor = [22, 163, 74]; // Green
                            }
                        }
                    }
                }
            });

            // Footer
            const pageCount = doc.getNumberOfPages();
            for (let i = 1; i <= pageCount; i++) {
                doc.setPage(i);
                doc.setFontSize(8);
                doc.setTextColor(150);
                doc.text(`Página ${i} de ${pageCount}`, 280, 200, { align: 'right' });
                doc.text('VallePrime - Sistema de Controle de Vendas', 14, 200);
            }

            doc.save(`relatorio_vendas_${new Date().toISOString().slice(0, 10)}.pdf`);
        } catch (err) {
            console.error(err);
            alert('Erro ao gerar PDF');
        } finally {
            setDownloadingPdf(false);
        }
    };

    const handleDownloadCsv = () => {
        const headers = ['Venda', 'Cliente', 'Quadra', 'Lote', 'Corretor', 'Data Venda', 'Valor Total', 'Boleto', 'Sinais', 'Vencimento'];
        const rows = filteredData.map(v => {
            const { quadra, lote } = parseQuadraLote(v.identificador);
            return [
                v.venda,
                v.cliente,
                quadra,
                lote,
                v.corretor,
                v.dataVenda,
                v.valorTotal,
                v.boletoGerado ? 'Sim' : 'Não',
                v.sinaisAberto,
                v.primeiroVencimento || ''
            ];
        });

        const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
        const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `relatorio_vendas_${new Date().toISOString().slice(0, 10)}.csv`;
        a.click();
        URL.revokeObjectURL(url);
    };

    const parseQuadraLote = (identificador: string) => {
        if (!identificador) return { quadra: '-', lote: '-' };
        const parts = identificador.split(' - ');
        const quadraLote = parts[1] || '';
        const quadraMatch = quadraLote.match(/Q(\d+)/);
        const loteMatch = quadraLote.match(/L(\d+)/);
        return {
            quadra: quadraMatch ? quadraMatch[1].padStart(3, '0') : '-',
            lote: loteMatch ? loteMatch[1].padStart(3, '0') : '-'
        };
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
            {/* Page Header */}
            <div className="page-header">
                <div>
                    <h1 className="page-title">Dashboard de Vendas</h1>
                    <p className="page-subtitle">Acompanhamento de vendas e boletos</p>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button onClick={handleDownloadCsv} className="btn btn-outline">
                        📄 CSV
                    </button>
                    <button
                        onClick={handleDownloadPdf}
                        disabled={downloadingPdf}
                        className="btn btn-primary"
                    >
                        {downloadingPdf ? '⏳...' : '📑 PDF'}
                    </button>
                </div>
            </div>

            {/* Filter Bar */}
            <div className="filter-bar" style={{ flexWrap: 'wrap' }}>
                <div className="filter-group">
                    <label className="filter-label">Data Início</label>
                    <input
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        className="filter-input"
                        style={{ width: '150px' }}
                    />
                </div>
                <div className="filter-group">
                    <label className="filter-label">Data Fim</label>
                    <input
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        className="filter-input"
                        style={{ width: '150px' }}
                    />
                </div>
                <div className="filter-group">
                    <label className="filter-label">Boleto</label>
                    <select
                        value={boletoFilter}
                        onChange={(e) => setBoletoFilter(e.target.value as BoletoFilter)}
                        className="filter-input"
                        style={{ width: '120px' }}
                    >
                        <option value="todos">Todos</option>
                        <option value="gerado">✅ Gerados</option>
                        <option value="naoGerado">❌ Não Gerados</option>
                    </select>
                </div>
                <div className="filter-group">
                    <label className="filter-label">Sinais</label>
                    <select
                        value={sinaisFilter}
                        onChange={(e) => setSinaisFilter(e.target.value as SinaisFilter)}
                        className="filter-input"
                        style={{ width: '120px' }}
                    >
                        <option value="todos">Todos</option>
                        <option value="comSinais">⚠️ Com Sinais</option>
                        <option value="semSinais">✅ Sem Sinais</option>
                        <option value="vencidos">🔴 Vencidos</option>
                    </select>
                </div>
                <div className="filter-group">
                    <label className="filter-label">Corretor</label>
                    <select
                        value={corretorFilter}
                        onChange={(e) => setCorretorFilter(e.target.value)}
                        className="filter-input"
                        style={{ width: '180px' }}
                    >
                        <option value="todos">Todos</option>
                        {corretoresList.map(corretor => (
                            <option key={corretor} value={corretor}>{corretor}</option>
                        ))}
                    </select>
                </div>
                <button onClick={() => loadData()} className="btn btn-primary" style={{ padding: '8px 12px' }}>
                    🔍
                </button>
                <button
                    onClick={() => {
                        setStartDate('');
                        setEndDate('');
                        setBoletoFilter('todos');
                        setSinaisFilter('todos');
                        setCorretorFilter('todos');
                    }}
                    className="btn btn-outline"
                    style={{ padding: '8px 12px' }}
                    title="Limpar filtros"
                >
                    ✕
                </button>
            </div>

            {/* Metrics - based on filtered data */}
            <div className="metric-grid" style={{ gridTemplateColumns: 'repeat(6, 1fr)' }}>
                <MetricCard
                    icon="📊"
                    label="Total de Vendas"
                    value={filteredData.length}
                    color="primary"
                />
                <MetricCard
                    icon="✅"
                    label="Com Boleto"
                    value={filteredData.filter(v => v.boletoGerado).length}
                    color="success"
                />
                <MetricCard
                    icon="❌"
                    label="Sem Boleto (c/ Sinais)"
                    value={filteredData.filter(v => !v.boletoGerado && v.sinaisAberto > 0).length}
                    color="danger"
                />
                <MetricCard
                    icon="⚠️"
                    label="Com Sinais Abertos"
                    value={filteredData.filter(v => v.sinaisAberto > 0).length}
                    color="warning"
                />
                <MetricCard
                    icon="📭"
                    label="Sem Sinais"
                    value={filteredData.filter(v => v.sinaisTotal === 0).length}
                    color="primary"
                />
                <MetricCard
                    icon="✓"
                    label="Quitados"
                    value={filteredData.filter(v => v.sinaisTotal > 0 && v.sinaisAberto === 0).length}
                    color="success"
                />
            </div>

            {/* Valor Total Card */}
            <div className="card" style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <div className="metric-label">Valor Total das Vendas (Filtradas)</div>
                        <div className="metric-value primary" style={{ fontSize: '28px' }}>
                            R$ {filteredData.reduce((sum, v) => sum + (v.valorTotal || 0), 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                        </div>
                    </div>
                    <div className="badge badge-primary">
                        {filteredData.length} de {data.length} vendas
                    </div>
                </div>
            </div>

            {/* Table */}
            <div className="table-container">
                <div className="table-header-row">
                    <span className="table-title">Lista de Vendas</span>
                </div>
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ minWidth: '900px' }}>
                        <thead>
                            <tr>
                                <th style={{ width: '50px' }}>Venda</th>
                                <th style={{ width: '160px' }}>Cliente</th>
                                <th style={{ width: '50px', textAlign: 'center' }}>Quadra</th>
                                <th style={{ width: '50px', textAlign: 'center' }}>Lote</th>
                                <th style={{ width: '130px' }}>Corretor</th>
                                <th style={{ width: '85px' }}>Data</th>
                                <th style={{ width: '115px', textAlign: 'right' }}>Valor</th>
                                <th style={{ width: '55px', textAlign: 'center' }}>Boleto</th>
                                <th style={{ width: '80px' }}>Usuário Bol.</th>
                                <th style={{ width: '85px' }}>Data Geração</th>
                                <th style={{ width: '90px', textAlign: 'center' }}>Sinais</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredData.map((venda) => {
                                const { quadra, lote } = parseQuadraLote(venda.identificador);
                                const today = new Date();
                                today.setHours(0, 0, 0, 0);
                                const dueDate = venda.primeiroVencimentoISO ? new Date(venda.primeiroVencimentoISO) : null;
                                const isOverdue = dueDate && dueDate < today;

                                return (
                                    <tr key={venda.venda}>
                                        <td style={{ fontWeight: 600, fontSize: '12px', textAlign: 'center' }}>{venda.venda}</td>
                                        <td style={{ fontSize: '12px', maxWidth: '180px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={venda.cliente}>
                                            {venda.cliente}
                                        </td>
                                        <td style={{ textAlign: 'center', fontWeight: 600, color: '#2563EB', fontSize: '12px' }}>
                                            {quadra}
                                        </td>
                                        <td style={{ textAlign: 'center', fontWeight: 600, color: '#2563EB', fontSize: '12px' }}>
                                            {lote}
                                        </td>
                                        <td style={{ fontSize: '11px', maxWidth: '140px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={venda.corretor}>
                                            {venda.corretor}
                                        </td>
                                        <td style={{ color: '#64748B', fontSize: '11px' }}>{(venda as any).dataCadastro || venda.dataVenda}</td>
                                        <td style={{ textAlign: 'right', fontWeight: 500, color: '#10B981', fontSize: '11px', whiteSpace: 'nowrap' }}>
                                            R$ {venda.valorTotal?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                        </td>
                                        <td style={{ textAlign: 'center' }}>
                                            {venda.boletoGerado ? (
                                                <span className="badge badge-success">Sim</span>
                                            ) : venda.sinaisTotal > 0 && venda.sinaisAberto === 0 ? (
                                                <span className="badge badge-warning" title="Pago manualmente sem boleto">Baixado</span>
                                            ) : (
                                                <span className="badge badge-danger">Não</span>
                                            )}
                                        </td>
                                        <td style={{ fontSize: '10px', maxWidth: '90px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={(venda as any).boletoUsuario || '-'}>
                                            {(venda as any).boletoUsuario || '-'}
                                        </td>
                                        <td style={{ fontSize: '10px', color: '#64748B' }}>
                                            {(venda as any).boletoDataHora || '-'}
                                        </td>
                                        <td style={{ textAlign: 'center' }}>
                                            {venda.sinaisAberto > 0 ? (
                                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px' }}>
                                                    <span className="badge badge-warning" style={{ fontSize: '11px', padding: '2px 8px' }}>
                                                        {venda.sinaisAberto} aberto{venda.sinaisAberto > 1 ? 's' : ''}
                                                    </span>
                                                    {venda.primeiroVencimento && (
                                                        <span style={{
                                                            fontSize: '10px',
                                                            fontWeight: 500,
                                                            color: isOverdue ? '#DC2626' : '#16A34A'
                                                        }}>
                                                            {venda.primeiroVencimento}
                                                        </span>
                                                    )}
                                                </div>
                                            ) : venda.sinaisTotal > 0 ? (
                                                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px' }}>
                                                    <span className="badge badge-success" style={{ fontSize: '11px', padding: '2px 8px' }}>
                                                        ✓ Quitado
                                                    </span>
                                                    <span style={{ fontSize: '9px', color: '#64748B' }}>
                                                        {venda.sinaisPagos}/{venda.sinaisTotal} pagos
                                                    </span>
                                                </div>
                                            ) : (
                                                <span style={{ color: '#94A3B8', fontSize: '11px' }}>Sem sinais</span>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};
