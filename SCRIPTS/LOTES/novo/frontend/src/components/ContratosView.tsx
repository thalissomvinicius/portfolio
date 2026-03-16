import React, { useState, useEffect, useCallback } from 'react';
import { PageHeader, LoadingSpinner, ErrorMessage, DataTable } from './shared';

interface ContratosViewProps {
    empresa: number;
    obra: string;
    refreshKey?: number;
}

interface Contrato {
    venda: number;
    cliente: string;
    cpf: string;
    quadra: string;
    lote: string;
    corretor: string;
    dataVenda: string;
    valorLote: number;
    status: string;
    tipoAssinatura: string;
    dataEnvio: string | null;
    dataAssinatura: string | null;
    responsavelEnvio: string | null;
    observacoes: string;
    propostaStatus: string;
    propostaData: string | null;
    pendencias: string;
    atualizadoEm: string | null;
}

interface Metrics {
    totalVendas: number;
    naoEnviado: number;
    enviado: number;
    pendenteAssinatura: number;
    assinado: number;
    assinaturaDigital: number;
    assinaturaBalcao: number;
}

const STATUS_LABELS: Record<string, string> = {
    nao_enviado: 'Não Enviado',
    enviado: 'Enviado',
    pendente_assinatura: 'Pend. Assinatura',
    assinado: 'Assinado',
    cancelado: 'Cancelado'
};

const TIPO_LABELS: Record<string, string> = {
    pendente_escolha: 'Pendente',
    digital: 'Digital',
    balcao: 'Balcão'
};

const STATUS_COLORS: Record<string, { bg: string; color: string }> = {
    nao_enviado: { bg: '#FEE2E2', color: '#991B1B' },
    enviado: { bg: '#DBEAFE', color: '#1D4ED8' },
    pendente_assinatura: { bg: '#FEF3C7', color: '#92400E' },
    assinado: { bg: '#D1FAE5', color: '#065F46' },
    cancelado: { bg: '#E5E7EB', color: '#374151' }
};

const PROPOSTA_LABELS: Record<string, string> = {
    nao_gerada: 'Não Gerada',
    gerada: 'Gerada',
    enviada: 'Enviada',
    assinada_digital: 'Assin. Digital',
    assinada_presencial: 'Assin. Presencial',
    cancelada: 'Cancelada'
};

const PROPOSTA_COLORS: Record<string, { bg: string; color: string }> = {
    nao_gerada: { bg: '#F3F4F6', color: '#6B7280' },
    gerada: { bg: '#E0E7FF', color: '#4338CA' },
    enviada: { bg: '#DBEAFE', color: '#1D4ED8' },
    assinada_digital: { bg: '#D1FAE5', color: '#065F46' },
    assinada_presencial: { bg: '#FEF3C7', color: '#92400E' },
    cancelada: { bg: '#FEE2E2', color: '#991B1B' }
};

export const ContratosView: React.FC<ContratosViewProps> = ({ empresa, obra, refreshKey }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<Contrato[]>([]);
    const [metrics, setMetrics] = useState<Metrics | null>(null);
    const [saving, setSaving] = useState<number | null>(null);

    // Filters
    const [statusFilter, setStatusFilter] = useState<string>('');
    const [tipoFilter, setTipoFilter] = useState<string>('');
    const [corretorFilter, setCorretorFilter] = useState<string>('');
    const [searchTerm, setSearchTerm] = useState<string>('');

    // Editing
    const [editingObs, setEditingObs] = useState<number | null>(null);
    const [tempObs, setTempObs] = useState<string>('');
    const [editingDate, setEditingDate] = useState<{ venda: number; field: 'dataEnvio' | 'dataAssinatura' } | null>(null);
    const [tempDate, setTempDate] = useState<string>('');

    // Modal for date prompt when changing status
    const [dateModal, setDateModal] = useState<{
        show: boolean;
        venda: number;
        status: string;
        field: 'dataEnvio' | 'dataAssinatura';
        label: string;
    } | null>(null);
    const [modalDate, setModalDate] = useState<string>(new Date().toISOString().slice(0, 10));

    // Get unique corretores
    const corretores = React.useMemo(() => {
        const unique = [...new Set(data.map(d => d.corretor).filter(Boolean))];
        return unique.sort();
    }, [data]);

    const fetchData = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const params = new URLSearchParams({ empresa: String(empresa), obra });
            if (statusFilter) params.append('status', statusFilter);
            if (tipoFilter) params.append('tipo_assinatura', tipoFilter);

            const [contratosRes, metricsRes] = await Promise.all([
                fetch(`/api/contratos?${params}`),
                fetch(`/api/contratos/metrics?empresa=${empresa}&obra=${obra}`)
            ]);

            if (!contratosRes.ok || !metricsRes.ok) {
                throw new Error('Erro ao buscar dados');
            }

            const contratosData = await contratosRes.json();
            const metricsData = await metricsRes.json();

            setData(contratosData.data);
            setMetrics(metricsData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao buscar dados');
        } finally {
            setLoading(false);
        }
    }, [empresa, obra, statusFilter, tipoFilter]);

    useEffect(() => {
        fetchData();
    }, [fetchData, refreshKey]);

    // Filter data locally for search and corretor
    const filteredData = React.useMemo(() => {
        let result = data;

        if (corretorFilter) {
            result = result.filter(d => d.corretor === corretorFilter);
        }

        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            result = result.filter(d =>
                d.cliente?.toLowerCase().includes(term) ||
                String(d.venda).includes(term) ||
                d.quadra?.toLowerCase().includes(term) ||
                d.lote?.toLowerCase().includes(term)
            );
        }

        return result;
    }, [data, corretorFilter, searchTerm]);

    const updateContrato = async (venda: number, updates: Partial<Contrato>) => {
        setSaving(venda);
        try {
            const response = await fetch(`/api/contratos?empresa=${empresa}&obra=${obra}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ venda, ...updates })
            });

            if (!response.ok) {
                throw new Error('Erro ao atualizar contrato');
            }

            // Refresh data
            await fetchData();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao atualizar');
        } finally {
            setSaving(null);
        }
    };

    const handleStatusChange = (venda: number, status: string) => {
        // Show modal to ask for date based on status
        if (status === 'enviado' || status === 'pendente_assinatura') {
            setDateModal({
                show: true,
                venda,
                status,
                field: 'dataEnvio',
                label: 'Data de Envio do Contrato'
            });
            setModalDate(new Date().toISOString().slice(0, 10));
            return;
        }
        if (status === 'assinado') {
            setDateModal({
                show: true,
                venda,
                status,
                field: 'dataAssinatura',
                label: 'Data de Assinatura do Contrato'
            });
            setModalDate(new Date().toISOString().slice(0, 10));
            return;
        }

        // For other statuses, just update without asking date
        updateContrato(venda, { status });
    };

    const handleModalConfirm = () => {
        if (!dateModal) return;

        const updates: any = { status: dateModal.status };
        if (dateModal.field === 'dataEnvio') {
            updates.data_envio = modalDate;
        } else {
            updates.data_assinatura = modalDate;
        }

        updateContrato(dateModal.venda, updates);
        setDateModal(null);
    };

    const handleModalCancel = () => {
        setDateModal(null);
    };

    const handleTipoChange = (venda: number, tipoAssinatura: string) => {
        updateContrato(venda, { tipoAssinatura } as any);
    };

    const handlePropostaChange = (venda: number, propostaStatus: string) => {
        updateContrato(venda, { proposta_status: propostaStatus } as any);
    };

    const [editingPendencias, setEditingPendencias] = useState<number | null>(null);
    const [tempPendencias, setTempPendencias] = useState<string>('');

    const handleSavePendencias = (venda: number) => {
        updateContrato(venda, { pendencias: tempPendencias } as any);
        setEditingPendencias(null);
        setTempPendencias('');
    };

    const handleSaveObs = (venda: number) => {
        updateContrato(venda, { observacoes: tempObs } as any);
        setEditingObs(null);
        setTempObs('');
    };

    const handleDateChange = (venda: number, field: 'dataEnvio' | 'dataAssinatura', value: string) => {
        // Convert from YYYY-MM-DD to DD/MM/YYYY for display, but save as YYYY-MM-DD
        updateContrato(venda, { [field === 'dataEnvio' ? 'data_envio' : 'data_assinatura']: value } as any);
        setEditingDate(null);
        setTempDate('');
    };

    const formatDateForInput = (dateStr: string | null): string => {
        if (!dateStr) return '';
        // If already in YYYY-MM-DD format
        if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) return dateStr;
        // If in DD/MM/YYYY format, convert to YYYY-MM-DD
        const parts = dateStr.split('/');
        if (parts.length === 3) {
            return `${parts[2]}-${parts[1]}-${parts[0]}`;
        }
        return dateStr;
    };

    const formatDateForDisplay = (dateStr: string | null): string => {
        if (!dateStr) return '-';
        // If in YYYY-MM-DD format, convert to DD/MM/YYYY
        if (dateStr.match(/^\d{4}-\d{2}-\d{2}$/)) {
            const parts = dateStr.split('-');
            return `${parts[2]}/${parts[1]}/${parts[0]}`;
        }
        return dateStr;
    };

    const exportToExcel = async () => {
        try {
            const response = await fetch(`/api/contratos/export?empresa=${empresa}&obra=${obra}`);
            if (!response.ok) throw new Error('Erro ao exportar');

            const { data } = await response.json();

            // Convert to CSV
            const headers = Object.keys(data[0] || {});
            const csv = [
                headers.join(';'),
                ...data.map((row: any) => headers.map(h => `"${row[h] || ''}"`).join(';'))
            ].join('\n');

            // Download
            const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `contratos_${new Date().toISOString().slice(0, 10)}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            setError('Erro ao exportar para Excel');
        }
    };

    return (
        <div className="animate-fade-in">
            <PageHeader
                title="📝 Gerenciador de Contratos"
                subtitle="Acompanhe o envio e assinatura dos contratos de venda"
            />

            {error && <ErrorMessage message={error} />}

            {/* Date Prompt Modal */}
            {dateModal && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0,0,0,0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 9999
                }}>
                    <div style={{
                        background: 'white',
                        borderRadius: '16px',
                        padding: '24px',
                        minWidth: '360px',
                        boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
                    }}>
                        <h3 style={{
                            margin: '0 0 8px 0',
                            fontSize: '18px',
                            color: '#1F2937',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}>
                            📅 {dateModal.label}
                        </h3>
                        <p style={{
                            margin: '0 0 20px 0',
                            fontSize: '14px',
                            color: '#6B7280'
                        }}>
                            Informe a data para o contrato da venda <strong>#{dateModal.venda}</strong>
                        </p>

                        <input
                            type="date"
                            value={modalDate}
                            onChange={(e) => setModalDate(e.target.value)}
                            style={{
                                width: '100%',
                                padding: '12px 16px',
                                fontSize: '16px',
                                border: '2px solid #3B82F6',
                                borderRadius: '8px',
                                marginBottom: '20px',
                                boxSizing: 'border-box'
                            }}
                            autoFocus
                        />

                        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                            <button
                                onClick={handleModalCancel}
                                style={{
                                    padding: '10px 20px',
                                    background: '#F3F4F6',
                                    border: 'none',
                                    borderRadius: '8px',
                                    fontSize: '14px',
                                    fontWeight: 600,
                                    color: '#374151',
                                    cursor: 'pointer'
                                }}
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={handleModalConfirm}
                                style={{
                                    padding: '10px 24px',
                                    background: dateModal.field === 'dataAssinatura'
                                        ? 'linear-gradient(135deg, #10B981 0%, #059669 100%)'
                                        : 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)',
                                    border: 'none',
                                    borderRadius: '8px',
                                    fontSize: '14px',
                                    fontWeight: 600,
                                    color: 'white',
                                    cursor: 'pointer'
                                }}
                            >
                                ✓ Confirmar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Metrics Cards */}
            {metrics && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '12px', marginBottom: '24px' }}>
                    <div className="card" style={{ background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)', color: 'white', padding: '16px' }}>
                        <div style={{ fontSize: '11px', opacity: 0.9 }}>TOTAL VENDAS</div>
                        <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '4px' }}>{metrics.totalVendas}</div>
                    </div>
                    <div className="card" style={{ background: '#FEE2E2', padding: '16px' }}>
                        <div style={{ fontSize: '11px', color: '#991B1B' }}>NÃO ENVIADO</div>
                        <div style={{ fontSize: '28px', fontWeight: 700, color: '#991B1B', marginTop: '4px' }}>{metrics.naoEnviado}</div>
                    </div>
                    <div className="card" style={{ background: '#DBEAFE', padding: '16px' }}>
                        <div style={{ fontSize: '11px', color: '#1D4ED8' }}>ENVIADO</div>
                        <div style={{ fontSize: '28px', fontWeight: 700, color: '#1D4ED8', marginTop: '4px' }}>{metrics.enviado}</div>
                    </div>
                    <div className="card" style={{ background: '#FEF3C7', padding: '16px' }}>
                        <div style={{ fontSize: '11px', color: '#92400E' }}>PEND. ASSINATURA</div>
                        <div style={{ fontSize: '28px', fontWeight: 700, color: '#92400E', marginTop: '4px' }}>{metrics.pendenteAssinatura}</div>
                    </div>
                    <div className="card" style={{ background: '#D1FAE5', padding: '16px' }}>
                        <div style={{ fontSize: '11px', color: '#065F46' }}>ASSINADOS</div>
                        <div style={{ fontSize: '28px', fontWeight: 700, color: '#065F46', marginTop: '4px' }}>{metrics.assinado}</div>
                    </div>
                    <div className="card" style={{ background: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)', color: 'white', padding: '16px' }}>
                        <div style={{ fontSize: '11px', opacity: 0.9 }}>DIGITAL / BALCÃO</div>
                        <div style={{ fontSize: '20px', fontWeight: 700, marginTop: '4px' }}>
                            {metrics.assinaturaDigital} / {metrics.assinaturaBalcao}
                        </div>
                    </div>
                </div>
            )}

            {/* Filters */}
            <div className="card" style={{ marginBottom: '24px' }}>
                <div style={{ display: 'flex', gap: '16px', alignItems: 'end', flexWrap: 'wrap' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        <label style={{ fontSize: '12px', fontWeight: 600, color: '#374151' }}>Status</label>
                        <select
                            style={{
                                padding: '10px 14px',
                                border: '2px solid #E5E7EB',
                                borderRadius: '8px',
                                fontSize: '13px',
                                minWidth: '160px',
                                background: 'white'
                            }}
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                        >
                            <option value="">Todos</option>
                            {Object.entries(STATUS_LABELS).map(([value, label]) => (
                                <option key={value} value={value}>{label}</option>
                            ))}
                        </select>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        <label style={{ fontSize: '12px', fontWeight: 600, color: '#374151' }}>Tipo Assinatura</label>
                        <select
                            style={{
                                padding: '10px 14px',
                                border: '2px solid #E5E7EB',
                                borderRadius: '8px',
                                fontSize: '13px',
                                minWidth: '140px',
                                background: 'white'
                            }}
                            value={tipoFilter}
                            onChange={(e) => setTipoFilter(e.target.value)}
                        >
                            <option value="">Todos</option>
                            {Object.entries(TIPO_LABELS).map(([value, label]) => (
                                <option key={value} value={value}>{label}</option>
                            ))}
                        </select>
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                        <label style={{ fontSize: '12px', fontWeight: 600, color: '#374151' }}>Corretor</label>
                        <select
                            style={{
                                padding: '10px 14px',
                                border: '2px solid #E5E7EB',
                                borderRadius: '8px',
                                fontSize: '13px',
                                minWidth: '180px',
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

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1, minWidth: '200px' }}>
                        <label style={{ fontSize: '12px', fontWeight: 600, color: '#374151' }}>Buscar</label>
                        <input
                            type="text"
                            placeholder="Cliente, venda, quadra, lote..."
                            style={{
                                padding: '10px 14px',
                                border: '2px solid #E5E7EB',
                                borderRadius: '8px',
                                fontSize: '13px'
                            }}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>

                    <button
                        onClick={fetchData}
                        className="btn btn-primary"
                        disabled={loading}
                        style={{ height: '44px' }}
                    >
                        {loading ? '⏳' : '🔄'} Atualizar
                    </button>

                    <button
                        onClick={exportToExcel}
                        className="btn"
                        style={{
                            height: '44px',
                            background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                            color: 'white',
                            border: 'none',
                            borderRadius: '8px',
                            padding: '0 20px',
                            fontWeight: 600,
                            cursor: 'pointer'
                        }}
                    >
                        📊 Exportar Excel
                    </button>
                </div>
            </div>

            {loading && <LoadingSpinner />}

            {!loading && (
                <DataTable title="📋 Contratos" badgeText={String(filteredData.length)} badgeVariant="primary">
                    {filteredData.length > 0 ? (
                        <table>
                            <thead>
                                <tr>
                                    <th style={{ width: '55px', textAlign: 'center' }}>Venda</th>
                                    <th style={{ width: '200px' }}>Cliente</th>
                                    <th style={{ width: '35px', textAlign: 'center' }}>Q</th>
                                    <th style={{ width: '35px', textAlign: 'center' }}>L</th>
                                    <th style={{ width: '130px' }}>Corretor</th>
                                    <th style={{ width: '115px' }}>Proposta</th>
                                    <th style={{ width: '115px' }}>Contrato</th>
                                    <th style={{ width: '85px' }}>Tipo</th>
                                    <th style={{ width: '90px', textAlign: 'center' }}>Dt Envio</th>
                                    <th style={{ width: '90px', textAlign: 'center' }}>Dt Assin.</th>
                                    <th style={{ width: '150px' }}>Pendências</th>
                                    <th style={{ width: '150px' }}>Observações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredData.map((item) => (
                                    <tr key={item.venda} style={{
                                        backgroundColor: item.status === 'assinado' ? '#F0FDF4' :
                                            item.status === 'nao_enviado' ? '#FEF2F2' : 'white'
                                    }}>
                                        <td style={{ textAlign: 'center', fontWeight: 600, fontSize: '10px' }}>{item.venda}</td>
                                        <td style={{
                                            fontSize: '10px',
                                            maxWidth: '200px',
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                            whiteSpace: 'nowrap'
                                        }} title={item.cliente}>
                                            {item.cliente}
                                        </td>
                                        <td style={{ textAlign: 'center', fontWeight: 600, color: '#2563EB', fontSize: '10px' }}>{item.quadra || '-'}</td>
                                        <td style={{ textAlign: 'center', fontWeight: 600, color: '#2563EB', fontSize: '10px' }}>{item.lote || '-'}</td>
                                        <td style={{ fontSize: '10px', maxWidth: '130px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                            {item.corretor || '-'}
                                        </td>
                                        <td>
                                            <select
                                                value={item.propostaStatus || 'nao_gerada'}
                                                onChange={(e) => handlePropostaChange(item.venda, e.target.value)}
                                                disabled={saving === item.venda}
                                                style={{
                                                    padding: '3px 5px',
                                                    borderRadius: '4px',
                                                    border: '1px solid #E5E7EB',
                                                    fontSize: '9px',
                                                    fontWeight: 600,
                                                    background: PROPOSTA_COLORS[item.propostaStatus || 'nao_gerada']?.bg || '#F3F4F6',
                                                    color: PROPOSTA_COLORS[item.propostaStatus || 'nao_gerada']?.color || '#374151',
                                                    cursor: 'pointer',
                                                    width: '100%'
                                                }}
                                            >
                                                {Object.entries(PROPOSTA_LABELS).map(([value, label]) => (
                                                    <option key={value} value={value}>{label}</option>
                                                ))}
                                            </select>
                                        </td>
                                        <td>
                                            <select
                                                value={item.status}
                                                onChange={(e) => handleStatusChange(item.venda, e.target.value)}
                                                disabled={saving === item.venda}
                                                style={{
                                                    padding: '3px 5px',
                                                    borderRadius: '4px',
                                                    border: '1px solid #E5E7EB',
                                                    fontSize: '9px',
                                                    fontWeight: 600,
                                                    background: STATUS_COLORS[item.status]?.bg || '#F3F4F6',
                                                    color: STATUS_COLORS[item.status]?.color || '#374151',
                                                    cursor: 'pointer',
                                                    width: '100%'
                                                }}
                                            >
                                                {Object.entries(STATUS_LABELS).map(([value, label]) => (
                                                    <option key={value} value={value}>{label}</option>
                                                ))}
                                            </select>
                                        </td>
                                        <td>
                                            <select
                                                value={item.tipoAssinatura}
                                                onChange={(e) => handleTipoChange(item.venda, e.target.value)}
                                                disabled={saving === item.venda}
                                                style={{
                                                    padding: '3px 5px',
                                                    borderRadius: '4px',
                                                    border: '1px solid #E5E7EB',
                                                    fontSize: '9px',
                                                    fontWeight: 500,
                                                    background: item.tipoAssinatura === 'digital' ? '#DBEAFE' :
                                                        item.tipoAssinatura === 'balcao' ? '#FEF3C7' : '#F3F4F6',
                                                    cursor: 'pointer',
                                                    width: '100%'
                                                }}
                                            >
                                                {Object.entries(TIPO_LABELS).map(([value, label]) => (
                                                    <option key={value} value={value}>{label}</option>
                                                ))}
                                            </select>
                                        </td>
                                        <td style={{ textAlign: 'center' }}>
                                            {editingDate?.venda === item.venda && editingDate?.field === 'dataEnvio' ? (
                                                <input
                                                    type="date"
                                                    value={tempDate}
                                                    onChange={(e) => setTempDate(e.target.value)}
                                                    onBlur={() => {
                                                        if (tempDate) handleDateChange(item.venda, 'dataEnvio', tempDate);
                                                        else { setEditingDate(null); setTempDate(''); }
                                                    }}
                                                    onKeyDown={(e) => {
                                                        if (e.key === 'Enter' && tempDate) handleDateChange(item.venda, 'dataEnvio', tempDate);
                                                        if (e.key === 'Escape') { setEditingDate(null); setTempDate(''); }
                                                    }}
                                                    style={{
                                                        padding: '4px 6px',
                                                        fontSize: '11px',
                                                        border: '2px solid #3B82F6',
                                                        borderRadius: '4px',
                                                        width: '100%'
                                                    }}
                                                    autoFocus
                                                />
                                            ) : (
                                                <div
                                                    onClick={() => {
                                                        setEditingDate({ venda: item.venda, field: 'dataEnvio' });
                                                        setTempDate(formatDateForInput(item.dataEnvio));
                                                    }}
                                                    style={{
                                                        fontSize: '9px',
                                                        color: item.dataEnvio ? '#1D4ED8' : '#9CA3AF',
                                                        cursor: 'pointer',
                                                        padding: '2px 4px',
                                                        borderRadius: '4px',
                                                        background: item.dataEnvio ? '#EFF6FF' : 'transparent',
                                                        fontWeight: item.dataEnvio ? 500 : 400
                                                    }}
                                                    title="Clique para editar data de envio"
                                                >
                                                    {formatDateForDisplay(item.dataEnvio) || '+ Data'}
                                                </div>
                                            )}
                                        </td>
                                        <td style={{ textAlign: 'center' }}>
                                            {editingDate?.venda === item.venda && editingDate?.field === 'dataAssinatura' ? (
                                                <input
                                                    type="date"
                                                    value={tempDate}
                                                    onChange={(e) => setTempDate(e.target.value)}
                                                    onBlur={() => {
                                                        if (tempDate) handleDateChange(item.venda, 'dataAssinatura', tempDate);
                                                        else { setEditingDate(null); setTempDate(''); }
                                                    }}
                                                    onKeyDown={(e) => {
                                                        if (e.key === 'Enter' && tempDate) handleDateChange(item.venda, 'dataAssinatura', tempDate);
                                                        if (e.key === 'Escape') { setEditingDate(null); setTempDate(''); }
                                                    }}
                                                    style={{
                                                        padding: '4px 6px',
                                                        fontSize: '11px',
                                                        border: '2px solid #10B981',
                                                        borderRadius: '4px',
                                                        width: '100%'
                                                    }}
                                                    autoFocus
                                                />
                                            ) : (
                                                <div
                                                    onClick={() => {
                                                        setEditingDate({ venda: item.venda, field: 'dataAssinatura' });
                                                        setTempDate(formatDateForInput(item.dataAssinatura));
                                                    }}
                                                    style={{
                                                        fontSize: '9px',
                                                        color: item.dataAssinatura ? '#059669' : '#9CA3AF',
                                                        cursor: 'pointer',
                                                        padding: '2px 4px',
                                                        borderRadius: '4px',
                                                        background: item.dataAssinatura ? '#ECFDF5' : 'transparent',
                                                        fontWeight: item.dataAssinatura ? 600 : 400
                                                    }}
                                                    title="Clique para editar data de assinatura"
                                                >
                                                    {formatDateForDisplay(item.dataAssinatura) || '+ Data'}
                                                </div>
                                            )}
                                        </td>
                                        <td>
                                            {editingPendencias === item.venda ? (
                                                <div style={{ display: 'flex', gap: '4px' }}>
                                                    <input
                                                        type="text"
                                                        value={tempPendencias}
                                                        onChange={(e) => setTempPendencias(e.target.value)}
                                                        style={{
                                                            flex: 1,
                                                            padding: '4px 8px',
                                                            fontSize: '11px',
                                                            border: '2px solid #EF4444',
                                                            borderRadius: '4px'
                                                        }}
                                                        onKeyDown={(e) => {
                                                            if (e.key === 'Enter') handleSavePendencias(item.venda);
                                                            if (e.key === 'Escape') { setEditingPendencias(null); setTempPendencias(''); }
                                                        }}
                                                        autoFocus
                                                        placeholder="Pendências..."
                                                    />
                                                    <button
                                                        onClick={() => handleSavePendencias(item.venda)}
                                                        style={{
                                                            background: '#EF4444',
                                                            color: 'white',
                                                            border: 'none',
                                                            borderRadius: '4px',
                                                            padding: '4px 8px',
                                                            cursor: 'pointer',
                                                            fontSize: '11px'
                                                        }}
                                                    >
                                                        ✓
                                                    </button>
                                                </div>
                                            ) : (
                                                <div
                                                    onClick={() => { setEditingPendencias(item.venda); setTempPendencias(item.pendencias || ''); }}
                                                    style={{
                                                        fontSize: '9px',
                                                        color: item.pendencias ? '#DC2626' : '#9CA3AF',
                                                        cursor: 'pointer',
                                                        padding: '2px',
                                                        borderRadius: '4px',
                                                        maxWidth: '150px',
                                                        overflow: 'hidden',
                                                        textOverflow: 'ellipsis',
                                                        whiteSpace: 'nowrap',
                                                        background: item.pendencias ? '#FEF2F2' : 'transparent',
                                                        fontWeight: item.pendencias ? 500 : 400
                                                    }}
                                                    title={item.pendencias || 'Clique para adicionar pendência'}
                                                >
                                                    {item.pendencias || '+ Pendência'}
                                                </div>
                                            )}
                                        </td>
                                        <td>
                                            {editingObs === item.venda ? (
                                                <div style={{ display: 'flex', gap: '4px' }}>
                                                    <input
                                                        type="text"
                                                        value={tempObs}
                                                        onChange={(e) => setTempObs(e.target.value)}
                                                        style={{
                                                            flex: 1,
                                                            padding: '4px 8px',
                                                            fontSize: '12px',
                                                            border: '1px solid #3B82F6',
                                                            borderRadius: '4px'
                                                        }}
                                                        onKeyDown={(e) => {
                                                            if (e.key === 'Enter') handleSaveObs(item.venda);
                                                            if (e.key === 'Escape') { setEditingObs(null); setTempObs(''); }
                                                        }}
                                                        autoFocus
                                                    />
                                                    <button
                                                        onClick={() => handleSaveObs(item.venda)}
                                                        style={{
                                                            background: '#10B981',
                                                            color: 'white',
                                                            border: 'none',
                                                            borderRadius: '4px',
                                                            padding: '4px 8px',
                                                            cursor: 'pointer',
                                                            fontSize: '12px'
                                                        }}
                                                    >
                                                        ✓
                                                    </button>
                                                </div>
                                            ) : (
                                                <div
                                                    onClick={() => { setEditingObs(item.venda); setTempObs(item.observacoes || ''); }}
                                                    style={{
                                                        fontSize: '9px',
                                                        color: item.observacoes ? '#374151' : '#9CA3AF',
                                                        cursor: 'pointer',
                                                        padding: '2px',
                                                        borderRadius: '4px',
                                                        maxWidth: '150px',
                                                        overflow: 'hidden',
                                                        textOverflow: 'ellipsis',
                                                        whiteSpace: 'nowrap'
                                                    }}
                                                    title={item.observacoes || 'Clique para adicionar'}
                                                >
                                                    {item.observacoes || '+ Nota'}
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <div className="empty-state" style={{ padding: '40px', textAlign: 'center' }}>
                            <p style={{ color: '#6B7280', fontSize: '16px' }}>
                                {loading ? 'Carregando...' : 'Nenhum contrato encontrado com os filtros selecionados'}
                            </p>
                        </div>
                    )}
                </DataTable>
            )}
        </div>
    );
};
