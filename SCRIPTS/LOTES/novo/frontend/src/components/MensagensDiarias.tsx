import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import { formatCurrency } from '../utils/format';
import { PageHeader, LoadingSpinner, ErrorMessage } from './shared';

interface MensagensDiariasProps {
    empresa: number;
    obra: string;
    refreshKey: number;
}

interface ResumoDiario {
    nomeObra: string;
    data: string;
    vendas: {
        qtdDia: number;
        valorDia: number;
        qtdMes: number;
        valorMes: number;
        qtdTotal: number;
        valorTotal: number;
        valorTotalProdutos: number;
    };
    distratos: {
        qtdDia: number;
        qtdMes: number;
    };
    estoque: {
        disponivel: number;
        reservado: number;
        suspenso: number;
        foraVenda: number;
        vendido: number;
        quitado: number;
        total: number;
    };
}

export const MensagensDiarias: React.FC<MensagensDiariasProps> = ({ empresa, obra, refreshKey }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [resumo, setResumo] = useState<ResumoDiario | null>(null);
    const [copied, setCopied] = useState(false);

    // Local filter state
    const [empresaFilter, setEmpresaFilter] = useState(empresa);
    const [obraFilter, setObraFilter] = useState(obra);
    const [dataFilter, setDataFilter] = useState(new Date().toISOString().split('T')[0]);

    const fetchResumo = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await api.getResumoDiario(empresaFilter, obraFilter);
            // Ensure valorTotalProdutos has a default value
            setResumo({
                ...data,
                vendas: {
                    ...data.vendas,
                    valorTotalProdutos: data.vendas.valorTotalProdutos || data.vendas.valorTotal || 0
                }
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao buscar dados');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchResumo();
    }, [refreshKey]);

    const generateMessage = () => {
        if (!resumo) return '';

        // Format date from filter
        const dataParts = dataFilter.split('-');
        const dataFormatada = `${dataParts[2]}/${dataParts[1]}/${dataParts[0]}`;

        return `*${resumo.nomeObra}*
Data: *${dataFormatada}*

*VENDAS: (QTD/R$)*
do dia: ${resumo.vendas.qtdDia} / R$ ${formatCurrency(resumo.vendas.valorDia)}
do mês: ${resumo.vendas.qtdMes} / R$ ${formatCurrency(resumo.vendas.valorMes)}
Total: R$ ${formatCurrency(resumo.vendas.valorTotalProdutos)}

*DISTRATOS: (QTD)*
do dia: ${resumo.distratos.qtdDia}
do mês: ${resumo.distratos.qtdMes}

*ESTOQUE: (QTD)*
Disponível: ${resumo.estoque.disponivel}
Reservado: ${resumo.estoque.reservado}
Suspenso: ${resumo.estoque.suspenso}
Fora Venda: ${resumo.estoque.foraVenda}
Vendido: ${resumo.estoque.vendido}
Quitado: ${resumo.estoque.quitado}
*Total ${resumo.estoque.total.toLocaleString('pt-BR')}*`;
    };

    const copyToClipboard = async () => {
        const message = generateMessage();
        try {
            // Tenta usar a API moderna de clipboard
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(message);
            } else {
                // Fallback para contextos não-seguros (HTTP)
                const textArea = document.createElement('textarea');
                textArea.value = message;
                textArea.style.position = 'fixed';
                textArea.style.left = '-9999px';
                textArea.style.top = '-9999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
            }
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Erro ao copiar:', err);
            // Fallback final usando execCommand
            try {
                const textArea = document.createElement('textarea');
                textArea.value = message;
                textArea.style.position = 'fixed';
                textArea.style.left = '-9999px';
                document.body.appendChild(textArea);
                textArea.focus();
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
            } catch (fallbackErr) {
                console.error('Erro no fallback:', fallbackErr);
                alert('Não foi possível copiar. Por favor, selecione o texto manualmente.');
            }
        }
    };

    return (
        <div className="animate-fade-in">
            <PageHeader
                title="Mensagens Diárias"
                subtitle="Gere o resumo diário para enviar no WhatsApp"
            />

            {/* Filters Card */}
            <div className="card" style={{ marginBottom: '24px' }}>
                <div className="card-title" style={{ marginBottom: '20px' }}>🔍 Filtros do Relatório</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr auto', gap: '20px', alignItems: 'end' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <label style={{ fontSize: '13px', fontWeight: 600, color: '#374151' }}>Empresa</label>
                        <input
                            type="number"
                            style={{
                                padding: '12px 16px',
                                border: '2px solid #E5E7EB',
                                borderRadius: '8px',
                                fontSize: '14px',
                                fontWeight: 500,
                                transition: 'border-color 0.2s',
                                outline: 'none'
                            }}
                            value={empresaFilter}
                            onChange={(e) => setEmpresaFilter(parseInt(e.target.value) || 28)}
                            onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                            onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                        />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <label style={{ fontSize: '13px', fontWeight: 600, color: '#374151' }}>Obra</label>
                        <input
                            type="text"
                            style={{
                                padding: '12px 16px',
                                border: '2px solid #E5E7EB',
                                borderRadius: '8px',
                                fontSize: '14px',
                                fontWeight: 500,
                                transition: 'border-color 0.2s',
                                outline: 'none'
                            }}
                            value={obraFilter}
                            onChange={(e) => setObraFilter(e.target.value)}
                            onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                            onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                        />
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <label style={{ fontSize: '13px', fontWeight: 600, color: '#374151' }}>Data do Relatório</label>
                        <input
                            type="date"
                            style={{
                                padding: '12px 16px',
                                border: '2px solid #E5E7EB',
                                borderRadius: '8px',
                                fontSize: '14px',
                                fontWeight: 500,
                                transition: 'border-color 0.2s',
                                outline: 'none'
                            }}
                            value={dataFilter}
                            onChange={(e) => setDataFilter(e.target.value)}
                            onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                            onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                        />
                    </div>
                    <button
                        onClick={fetchResumo}
                        className="btn btn-primary"
                        disabled={loading}
                        style={{
                            height: '48px',
                            padding: '0 24px',
                            fontSize: '14px',
                            fontWeight: 600,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            whiteSpace: 'nowrap'
                        }}
                    >
                        {loading ? '⏳ Carregando...' : '🔄 Gerar Resumo'}
                    </button>
                </div>
            </div>

            {error && <ErrorMessage message={error} />}

            {loading && <LoadingSpinner />}

            {resumo && !loading && (
                <>
                    {/* Summary Cards */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
                        {/* Vendas do Dia */}
                        <div className="card" style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)', color: 'white' }}>
                            <div style={{ fontSize: '12px', opacity: 0.9 }}>📈 VENDAS DO DIA</div>
                            <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '8px' }}>{resumo.vendas.qtdDia}</div>
                            <div style={{ fontSize: '14px', marginTop: '4px' }}>R$ {formatCurrency(resumo.vendas.valorDia)}</div>
                        </div>

                        {/* Vendas do Mês */}
                        <div className="card" style={{ background: 'linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%)', color: 'white' }}>
                            <div style={{ fontSize: '12px', opacity: 0.9 }}>📊 VENDAS DO MÊS</div>
                            <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '8px' }}>{resumo.vendas.qtdMes}</div>
                            <div style={{ fontSize: '14px', marginTop: '4px' }}>R$ {formatCurrency(resumo.vendas.valorMes)}</div>
                        </div>

                        {/* Total Geral */}
                        <div className="card" style={{ background: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)', color: 'white' }}>
                            <div style={{ fontSize: '12px', opacity: 0.9 }}>💰 TOTAL GERAL</div>
                            <div style={{ fontSize: '28px', fontWeight: 700, marginTop: '8px' }}>{resumo.vendas.qtdTotal}</div>
                            <div style={{ fontSize: '14px', marginTop: '4px' }}>R$ {formatCurrency(resumo.vendas.valorTotalProdutos)}</div>
                        </div>
                    </div>

                    {/* Distratos e Estoque */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px', marginBottom: '24px' }}>
                        {/* Distratos */}
                        <div className="card">
                            <div className="card-title">
                                <span>⚠️ Distratos</span>
                            </div>
                            <div style={{ display: 'grid', gap: '12px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', background: '#FEF3C7', borderRadius: '8px' }}>
                                    <span>Hoje</span>
                                    <span style={{ fontWeight: 700, color: '#D97706' }}>{resumo.distratos.qtdDia}</span>
                                </div>
                                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', background: '#FEE2E2', borderRadius: '8px' }}>
                                    <span>Este mês</span>
                                    <span style={{ fontWeight: 700, color: '#DC2626' }}>{resumo.distratos.qtdMes}</span>
                                </div>
                            </div>
                        </div>

                        {/* Estoque */}
                        <div className="card">
                            <div className="card-title">
                                <span>🏠 Estoque</span>
                                <span className="badge badge-primary">{resumo.estoque.total}</span>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
                                <div style={{ padding: '12px', background: '#D1FAE5', borderRadius: '8px', textAlign: 'center' }}>
                                    <div style={{ fontSize: '11px', color: '#065F46' }}>Disponível</div>
                                    <div style={{ fontSize: '20px', fontWeight: 700, color: '#10B981' }}>{resumo.estoque.disponivel}</div>
                                </div>
                                <div style={{ padding: '12px', background: '#DBEAFE', borderRadius: '8px', textAlign: 'center' }}>
                                    <div style={{ fontSize: '11px', color: '#1E40AF' }}>Reservado</div>
                                    <div style={{ fontSize: '20px', fontWeight: 700, color: '#3B82F6' }}>{resumo.estoque.reservado}</div>
                                </div>
                                <div style={{ padding: '12px', background: '#FEF3C7', borderRadius: '8px', textAlign: 'center' }}>
                                    <div style={{ fontSize: '11px', color: '#92400E' }}>Suspenso</div>
                                    <div style={{ fontSize: '20px', fontWeight: 700, color: '#F59E0B' }}>{resumo.estoque.suspenso}</div>
                                </div>
                                <div style={{ padding: '12px', background: '#FEE2E2', borderRadius: '8px', textAlign: 'center' }}>
                                    <div style={{ fontSize: '11px', color: '#991B1B' }}>Fora Venda</div>
                                    <div style={{ fontSize: '20px', fontWeight: 700, color: '#DC2626' }}>{resumo.estoque.foraVenda}</div>
                                </div>
                                <div style={{ padding: '12px', background: '#EDE9FE', borderRadius: '8px', textAlign: 'center' }}>
                                    <div style={{ fontSize: '11px', color: '#5B21B6' }}>Vendido</div>
                                    <div style={{ fontSize: '20px', fontWeight: 700, color: '#8B5CF6' }}>{resumo.estoque.vendido}</div>
                                </div>
                                <div style={{ padding: '12px', background: '#ECFDF5', borderRadius: '8px', textAlign: 'center' }}>
                                    <div style={{ fontSize: '11px', color: '#065F46' }}>Quitado</div>
                                    <div style={{ fontSize: '20px', fontWeight: 700, color: '#059669' }}>{resumo.estoque.quitado}</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Message Preview */}
                    <div className="card">
                        <div className="card-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span>📨 Mensagem para WhatsApp</span>
                            <button
                                onClick={copyToClipboard}
                                className={`btn ${copied ? 'btn-success' : 'btn-primary'}`}
                                style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
                            >
                                {copied ? '✅ Copiado!' : '📋 Copiar Mensagem'}
                            </button>
                        </div>
                        <div style={{
                            background: '#075E54',
                            color: 'white',
                            padding: '20px',
                            borderRadius: '12px',
                            fontFamily: 'monospace',
                            fontSize: '13px',
                            lineHeight: '1.6',
                            whiteSpace: 'pre-wrap'
                        }}>
                            {generateMessage()}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
};
