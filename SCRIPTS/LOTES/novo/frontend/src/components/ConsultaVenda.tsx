import React, { useState, useEffect } from 'react';
import { api } from '../api/client';
import type { Venda, SinalPago, Boleto } from '../types';

interface ConsultaVendaProps {
    empresa: number;
    obra: string;
    refreshKey: number;
}

interface SinalAberto {
    parcela: number;
    qtdParcelas: number;
    vencimento: string;
    valorParcela: number;
}

interface EmpresaOption {
    codigo: number;
    nome: string;
}

interface ObraOption {
    codigo: string;
    nome: string;
}

type SearchType = 'venda' | 'quadraLote' | 'cliente' | 'cpfCnpj';

export const ConsultaVenda: React.FC<ConsultaVendaProps> = ({ empresa: empresaProp, obra: obraProp }) => {
    // Estados para empresas e obras carregadas do banco
    const [empresas, setEmpresas] = useState<EmpresaOption[]>([]);
    const [obras, setObras] = useState<ObraOption[]>([]);
    const [loadingEmpresas, setLoadingEmpresas] = useState(true);
    const [loadingObras, setLoadingObras] = useState(false);

    // Estado local para empresa e obra selecionadas
    const [empresa, setEmpresa] = useState<number>(empresaProp);
    const [obra, setObra] = useState<string>(obraProp);

    const [searchType, setSearchType] = useState<SearchType>('venda');
    const [vendaInput, setVendaInput] = useState<string>('');
    const [quadraInput, setQuadraInput] = useState<string>('');
    const [loteInput, setLoteInput] = useState<string>('');
    const [clienteInput, setClienteInput] = useState<string>('');
    const [cpfCnpjInput, setCpfCnpjInput] = useState<string>('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [vendaData, setVendaData] = useState<Venda | null>(null);
    const [multipleResults, setMultipleResults] = useState<Venda[]>([]);
    const [savedMultipleResults, setSavedMultipleResults] = useState<Venda[]>([]);
    const [sinaisAbertos, setSinaisAbertos] = useState<SinalAberto[]>([]);
    const [sinaisPagos, setSinaisPagos] = useState<SinalPago[]>([]);
    const [boletos, setBoletos] = useState<Boleto[]>([]);

    // Carregar empresas do banco
    useEffect(() => {
        const loadEmpresas = async () => {
            setLoadingEmpresas(true);
            try {
                const response = await fetch('/api/empresas');
                const data = await response.json();
                setEmpresas(data.empresas || []);
                // Se a empresa prop não estiver na lista, usar a primeira
                if (data.empresas && data.empresas.length > 0) {
                    const empresaExists = data.empresas.some((e: EmpresaOption) => e.codigo === empresaProp);
                    if (!empresaExists) {
                        setEmpresa(data.empresas[0].codigo);
                    }
                }
            } catch (err) {
                console.error('Erro ao carregar empresas:', err);
            } finally {
                setLoadingEmpresas(false);
            }
        };
        loadEmpresas();
    }, []);

    // Carregar obras quando empresa mudar
    useEffect(() => {
        const loadObras = async () => {
            if (!empresa) return;
            setLoadingObras(true);
            try {
                const response = await fetch(`/api/obras?empresa=${empresa}`);
                const data = await response.json();
                setObras(data.obras || []);
                // Se a obra atual não estiver na lista, usar a primeira
                if (data.obras && data.obras.length > 0) {
                    const obraExists = data.obras.some((o: ObraOption) => o.codigo === obra);
                    if (!obraExists) {
                        setObra(data.obras[0].codigo);
                    }
                }
            } catch (err) {
                console.error('Erro ao carregar obras:', err);
            } finally {
                setLoadingObras(false);
            }
        };
        loadObras();
    }, [empresa]);

    // Limpar resultados ao trocar de empresa/obra
    useEffect(() => {
        setVendaData(null);
        setMultipleResults([]);
        setSavedMultipleResults([]);
        setSinaisAbertos([]);
        setSinaisPagos([]);
        setBoletos([]);
        setError(null);
    }, [empresa, obra]);

    // Scroll to top on mount
    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    const parseQuadraLote = (identificador: string) => {
        if (!identificador) return { quadra: '', lote: '' };
        const parts = identificador.split(' - ');
        const quadraLote = parts[1] || '';
        const quadraMatch = quadraLote.match(/Q(\d+)/);
        const loteMatch = quadraLote.match(/L(\d+)/);
        return {
            quadra: quadraMatch ? quadraMatch[1] : '',
            lote: loteMatch ? loteMatch[1] : ''
        };
    };

    const formatCpfCnpj = (value: string) => {
        const numbers = value.replace(/\D/g, '');
        if (numbers.length <= 11) {
            // CPF: 000.000.000-00
            return numbers
                .replace(/(\d{3})(\d)/, '$1.$2')
                .replace(/(\d{3})(\d)/, '$1.$2')
                .replace(/(\d{3})(\d{1,2})$/, '$1-$2');
        } else {
            // CNPJ: 00.000.000/0000-00
            return numbers
                .replace(/(\d{2})(\d)/, '$1.$2')
                .replace(/(\d{3})(\d)/, '$1.$2')
                .replace(/(\d{3})(\d)/, '$1/$2')
                .replace(/(\d{4})(\d{1,2})$/, '$1-$2');
        }
    };

    const handleSearch = async () => {
        setLoading(true);
        setError(null);
        setVendaData(null);
        setMultipleResults([]);
        setSinaisAbertos([]);
        setSinaisPagos([]);
        setBoletos([]);

        try {
            let venda: Venda | undefined;

            if (searchType === 'venda') {
                const vendaNum = parseInt(vendaInput);
                if (!vendaNum) {
                    setError('Digite um número de venda válido');
                    setLoading(false);
                    return;
                }
                try {
                    const response = await fetch(`/api/venda/${vendaNum}?empresa=${empresa}&obra=${obra}`);
                    if (response.status === 404) {
                        setError(`Venda ${vendaNum} não encontrada`);
                        setLoading(false);
                        return;
                    }
                    if (!response.ok) throw new Error('Erro ao buscar venda');
                    const data = await response.json();
                    venda = data.data;
                } catch (err) {
                    setError(`Venda ${vendaNum} não encontrada`);
                    setLoading(false);
                    return;
                }
            } else if (searchType === 'cpfCnpj') {
                // Search by CPF/CNPJ
                const cpfLimpo = cpfCnpjInput.replace(/\D/g, '');
                if (!cpfLimpo || cpfLimpo.length < 5) {
                    setError('Digite um CPF ou CNPJ válido (mínimo 5 dígitos)');
                    setLoading(false);
                    return;
                }

                try {
                    const response = await fetch(`/api/venda/cpf/${cpfLimpo}?empresa=${empresa}&obra=${obra}`);
                    if (response.status === 404) {
                        setError(`Nenhuma venda encontrada para o CPF/CNPJ informado`);
                        setLoading(false);
                        return;
                    }
                    if (!response.ok) throw new Error('Erro ao buscar venda');
                    const data = await response.json();

                    if (data.data.length === 1) {
                        venda = data.data[0];
                    } else {
                        setMultipleResults(data.data);
                        setLoading(false);
                        return;
                    }
                } catch (err) {
                    setError(`Nenhuma venda encontrada para o CPF/CNPJ informado`);
                    setLoading(false);
                    return;
                }
            } else if (searchType === 'cliente') {
                if (!clienteInput.trim()) {
                    setError('Digite o nome do cliente');
                    setLoading(false);
                    return;
                }

                try {
                    const response = await fetch(`/api/vendas/buscar-cliente/${encodeURIComponent(clienteInput.trim())}?empresa=${empresa}&obra=${obra}`);
                    if (response.status === 404) {
                        setError(`Nenhuma venda encontrada para cliente "${clienteInput}"`);
                        setLoading(false);
                        return;
                    }
                    if (!response.ok) throw new Error('Erro ao buscar venda');
                    const data = await response.json();

                    if (data.data.length === 1) {
                        venda = data.data[0];
                    } else {
                        setMultipleResults(data.data);
                        setLoading(false);
                        return;
                    }
                } catch (err) {
                    setError(`Nenhuma venda encontrada para cliente "${clienteInput}"`);
                    setLoading(false);
                    return;
                }
            } else {
                if (!quadraInput || !loteInput) {
                    setError('Digite a quadra e o lote');
                    setLoading(false);
                    return;
                }

                try {
                    const response = await fetch(`/api/vendas/buscar-lote?empresa=${empresa}&obra=${obra}&quadra=${encodeURIComponent(quadraInput.trim())}&lote=${encodeURIComponent(loteInput.trim())}`);
                    if (response.status === 404) {
                        setError(`Nenhuma venda encontrada para Quadra ${quadraInput}, Lote ${loteInput}`);
                        setLoading(false);
                        return;
                    }
                    if (!response.ok) throw new Error('Erro ao buscar venda');
                    const data = await response.json();

                    if (data.data.length === 1) {
                        venda = data.data[0];
                    } else {
                        setMultipleResults(data.data);
                        setLoading(false);
                        return;
                    }
                } catch (err) {
                    setError(`Nenhuma venda encontrada para Quadra ${quadraInput}, Lote ${loteInput}`);
                    setLoading(false);
                    return;
                }
            }

            if (!venda) {
                setError('Venda não encontrada');
                setLoading(false);
                return;
            }

            setVendaData(venda);

            try {
                const sinaisResponse = await api.getSinais(empresa, obra, '2099-12-31');
                const sinaisVenda = sinaisResponse.data.filter(s => s.venda === venda.venda);
                setSinaisAbertos(sinaisVenda.map(s => ({
                    parcela: s.parcela,
                    qtdParcelas: s.qtdParcelas,
                    vencimento: s.vencimento,
                    valorParcela: s.valorParcela
                })));
            } catch (e) {
                console.log('No open sinais');
            }

            try {
                const sinaisPagosResponse = await api.getSinaisPagos(venda.venda, empresa, obra);
                setSinaisPagos(sinaisPagosResponse.data);
            } catch (e) {
                console.log('No paid sinais');
            }

            try {
                const boletosResponse = await api.getBoletos(empresa, venda.venda);
                setBoletos(boletosResponse.data);
            } catch (e) {
                console.log('No boletos');
            }

        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao buscar dados');
        } finally {
            setLoading(false);
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    const parseQuadraLoteDisplay = (identificador: string) => {
        const { quadra, lote } = parseQuadraLote(identificador);
        return {
            quadra: quadra.padStart(3, '0'),
            lote: lote.padStart(3, '0')
        };
    };

    const searchOptions: { type: SearchType; icon: React.ReactNode; label: string; shortLabel: string; gradient: string }[] = [
        {
            type: 'venda',
            icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="2" /><path d="M7 8h4M7 12h6M7 16h8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /><path d="M15 8h2v2h-2zM15 12h2v2h-2z" fill="currentColor" /></svg>,
            label: 'Número da Venda',
            shortLabel: 'Número',
            gradient: 'linear-gradient(135deg, #0089D6 0%, #00528F 100%)'
        },
        {
            type: 'quadraLote',
            icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2L2 7l10 5 10-5-10-5z" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" /><path d="M2 17l10 5 10-5M2 12l10 5 10-5" stroke="currentColor" strokeWidth="2" strokeLinejoin="round" /></svg>,
            label: 'Quadra/Lote',
            shortLabel: 'Q/L',
            gradient: 'linear-gradient(135deg, #8CC63E 0%, #6B9F2E 100%)'
        },
        {
            type: 'cliente',
            icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke="currentColor" strokeWidth="2" /><path d="M4 20c0-4 4-6 8-6s8 2 8 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>,
            label: 'Nome do Cliente',
            shortLabel: 'Cliente',
            gradient: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)'
        },
        {
            type: 'cpfCnpj',
            icon: <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><rect x="3" y="4" width="18" height="16" rx="2" stroke="currentColor" strokeWidth="2" /><path d="M7 9h3M7 13h5M14 9h3v3h-3z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" /><circle cx="15.5" cy="14.5" r="1.5" fill="currentColor" /></svg>,
            label: 'CPF/CNPJ',
            shortLabel: 'CPF/CNPJ',
            gradient: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)'
        }
    ];

    return (
        <div className="animate-fade-in">
            {/* Header Moderno */}
            <div style={{
                background: 'linear-gradient(135deg, #00528F 0%, #0089D6 50%, #00A5FF 100%)',
                borderRadius: '20px',
                padding: '32px',
                marginBottom: '24px',
                position: 'relative',
                overflow: 'hidden'
            }}>
                {/* Background Decoration */}
                <div style={{
                    position: 'absolute',
                    top: '-50px',
                    right: '-50px',
                    width: '200px',
                    height: '200px',
                    borderRadius: '50%',
                    background: 'radial-gradient(circle, rgba(140, 198, 62, 0.2) 0%, transparent 70%)',
                    filter: 'blur(40px)'
                }} />
                <div style={{
                    position: 'absolute',
                    bottom: '-30px',
                    left: '-30px',
                    width: '150px',
                    height: '150px',
                    borderRadius: '50%',
                    background: 'radial-gradient(circle, rgba(16, 185, 129, 0.2) 0%, transparent 70%)',
                    filter: 'blur(30px)'
                }} />

                <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '8px' }}>
                        <div style={{
                            width: '56px',
                            height: '56px',
                            borderRadius: '16px',
                            background: 'rgba(255,255,255,0.15)',
                            backdropFilter: 'blur(10px)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            border: '1px solid rgba(255,255,255,0.2)',
                            boxShadow: '0 8px 32px rgba(0,0,0,0.1)'
                        }}>
                            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" style={{ color: 'white' }}>
                                <circle cx="11" cy="11" r="7" stroke="currentColor" strokeWidth="2.5" />
                                <path d="M16 16l4 4" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" />
                            </svg>
                        </div>
                        <div>
                            <h1 style={{
                                fontSize: '32px',
                                fontWeight: 800,
                                color: 'white',
                                margin: 0,
                                letterSpacing: '-0.5px',
                                textShadow: '0 2px 20px rgba(0,0,0,0.1)'
                            }}>Consultar Venda</h1>
                            <p style={{
                                fontSize: '15px',
                                color: 'rgba(255,255,255,0.8)',
                                margin: 0
                            }}>Busque por número, localização, cliente ou documento</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Seletor de Empresa/Obra */}
            <div style={{
                background: 'white',
                borderRadius: '16px',
                padding: '20px 24px',
                marginBottom: '24px',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                border: '1px solid #E2E8F0'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '14px',
                        fontWeight: 600,
                        color: '#475569'
                    }}>
                        🏢 Empresa:
                    </div>
                    <select
                        value={empresa}
                        onChange={(e) => setEmpresa(parseInt(e.target.value))}
                        disabled={loadingEmpresas}
                        style={{
                            minWidth: '200px',
                            padding: '12px 16px',
                            borderRadius: '10px',
                            border: '2px solid #E2E8F0',
                            fontSize: '14px',
                            fontWeight: 500,
                            color: '#1E293B',
                            background: 'white',
                            cursor: loadingEmpresas ? 'wait' : 'pointer',
                            transition: 'all 0.2s',
                            outline: 'none'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                        onBlur={(e) => e.target.style.borderColor = '#E2E8F0'}
                    >
                        {loadingEmpresas ? (
                            <option>Carregando...</option>
                        ) : (
                            empresas.map((emp) => (
                                <option key={emp.codigo} value={emp.codigo}>
                                    {emp.codigo} - {emp.nome}
                                </option>
                            ))
                        )}
                    </select>

                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        fontSize: '14px',
                        fontWeight: 600,
                        color: '#475569'
                    }}>
                        🏗️ Obra:
                    </div>
                    <select
                        value={obra}
                        onChange={(e) => setObra(e.target.value)}
                        disabled={loadingObras || obras.length === 0}
                        style={{
                            flex: 1,
                            minWidth: '250px',
                            padding: '12px 16px',
                            borderRadius: '10px',
                            border: '2px solid #E2E8F0',
                            fontSize: '14px',
                            fontWeight: 500,
                            color: '#1E293B',
                            background: 'white',
                            cursor: loadingObras ? 'wait' : 'pointer',
                            transition: 'all 0.2s',
                            outline: 'none'
                        }}
                        onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                        onBlur={(e) => e.target.style.borderColor = '#E2E8F0'}
                    >
                        {loadingObras ? (
                            <option>Carregando...</option>
                        ) : obras.length === 0 ? (
                            <option>Nenhuma obra disponível</option>
                        ) : (
                            obras.map((ob) => (
                                <option key={ob.codigo} value={ob.codigo}>
                                    {ob.codigo} - {ob.nome}
                                </option>
                            ))
                        )}
                    </select>

                    <div style={{
                        padding: '8px 16px',
                        background: 'linear-gradient(135deg, #0089D6 0%, #00528F 100%)',
                        color: 'white',
                        borderRadius: '8px',
                        fontSize: '12px',
                        fontWeight: 600,
                        whiteSpace: 'nowrap'
                    }}>
                        Emp: {empresa} | Obra: {obra}
                    </div>
                </div>
            </div>

            {/* Search Card Premium */}
            <div style={{
                background: 'white',
                borderRadius: '16px',
                padding: '24px',
                marginBottom: '24px',
                boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                border: '1px solid #E2E8F0'
            }}>
                {/* Search Type Tabs - Premium */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(4, 1fr)',
                    gap: '12px',
                    marginBottom: '24px'
                }}>
                    {searchOptions.map(opt => (
                        <button
                            key={opt.type}
                            onClick={() => setSearchType(opt.type)}
                            style={{
                                padding: '20px 16px',
                                borderRadius: '16px',
                                border: searchType === opt.type ? '2px solid #0089D6' : '2px solid #E2E8F0',
                                background: searchType === opt.type
                                    ? 'linear-gradient(135deg, #EBF8FF 0%, #DBEAFE 100%)'
                                    : 'white',
                                cursor: 'pointer',
                                transition: 'all 0.25s ease',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                gap: '12px',
                                boxShadow: searchType === opt.type
                                    ? '0 8px 25px rgba(0, 137, 214, 0.2)'
                                    : '0 2px 8px rgba(0, 0, 0, 0.04)'
                            }}
                        >
                            <div style={{
                                width: '48px',
                                height: '48px',
                                borderRadius: '12px',
                                background: searchType === opt.type ? opt.gradient : '#F1F5F9',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: searchType === opt.type ? 'white' : '#64748B',
                                transition: 'all 0.25s ease',
                                boxShadow: searchType === opt.type
                                    ? '0 4px 12px rgba(0, 0, 0, 0.15)'
                                    : 'none'
                            }}>
                                {opt.icon}
                            </div>
                            <span style={{
                                fontSize: '13px',
                                fontWeight: 600,
                                color: searchType === opt.type ? '#00528F' : '#64748B'
                            }}>{opt.shortLabel}</span>
                        </button>
                    ))}
                </div>

                {/* Search Inputs - Premium */}
                <div style={{
                    display: 'flex',
                    gap: '16px',
                    alignItems: 'flex-end',
                    flexWrap: 'wrap'
                }}>
                    {searchType === 'venda' && (
                        <div style={{ flex: 1, minWidth: '200px' }}>
                            <label style={{
                                display: 'block',
                                fontSize: '13px',
                                fontWeight: 600,
                                color: '#475569',
                                marginBottom: '8px'
                            }}>
                                🔢 Número da Venda
                            </label>
                            <input
                                type="number"
                                value={vendaInput}
                                onChange={(e) => setVendaInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Ex: 725"
                                style={{
                                    width: '100%',
                                    padding: '14px 16px',
                                    borderRadius: '10px',
                                    border: '2px solid #E2E8F0',
                                    fontSize: '15px',
                                    transition: 'all 0.2s',
                                    outline: 'none'
                                }}
                                onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                                onBlur={(e) => e.target.style.borderColor = '#E2E8F0'}
                            />
                        </div>
                    )}

                    {searchType === 'quadraLote' && (
                        <>
                            <div style={{ minWidth: '120px' }}>
                                <label style={{
                                    display: 'block',
                                    fontSize: '13px',
                                    fontWeight: 600,
                                    color: '#475569',
                                    marginBottom: '8px'
                                }}>
                                    📍 Quadra
                                </label>
                                <input
                                    type="number"
                                    value={quadraInput}
                                    onChange={(e) => setQuadraInput(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Ex: 4"
                                    style={{
                                        width: '100%',
                                        padding: '14px 16px',
                                        borderRadius: '10px',
                                        border: '2px solid #E2E8F0',
                                        fontSize: '15px',
                                        transition: 'all 0.2s',
                                        outline: 'none'
                                    }}
                                    onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                                    onBlur={(e) => e.target.style.borderColor = '#E2E8F0'}
                                />
                            </div>
                            <div style={{ minWidth: '120px' }}>
                                <label style={{
                                    display: 'block',
                                    fontSize: '13px',
                                    fontWeight: 600,
                                    color: '#475569',
                                    marginBottom: '8px'
                                }}>
                                    📍 Lote
                                </label>
                                <input
                                    type="number"
                                    value={loteInput}
                                    onChange={(e) => setLoteInput(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder="Ex: 21"
                                    style={{
                                        width: '100%',
                                        padding: '14px 16px',
                                        borderRadius: '10px',
                                        border: '2px solid #E2E8F0',
                                        fontSize: '15px',
                                        transition: 'all 0.2s',
                                        outline: 'none'
                                    }}
                                    onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                                    onBlur={(e) => e.target.style.borderColor = '#E2E8F0'}
                                />
                            </div>
                        </>
                    )}

                    {searchType === 'cliente' && (
                        <div style={{ flex: 1, minWidth: '250px' }}>
                            <label style={{
                                display: 'block',
                                fontSize: '13px',
                                fontWeight: 600,
                                color: '#475569',
                                marginBottom: '8px'
                            }}>
                                👤 Nome do Cliente
                            </label>
                            <input
                                type="text"
                                value={clienteInput}
                                onChange={(e) => setClienteInput(e.target.value)}
                                onKeyPress={handleKeyPress}
                                placeholder="Digite o nome..."
                                style={{
                                    width: '100%',
                                    padding: '14px 16px',
                                    borderRadius: '10px',
                                    border: '2px solid #E2E8F0',
                                    fontSize: '15px',
                                    transition: 'all 0.2s',
                                    outline: 'none'
                                }}
                                onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                                onBlur={(e) => e.target.style.borderColor = '#E2E8F0'}
                            />
                        </div>
                    )}

                    {searchType === 'cpfCnpj' && (
                        <div style={{ flex: 1, minWidth: '250px' }}>
                            <label style={{
                                display: 'block',
                                fontSize: '13px',
                                fontWeight: 600,
                                color: '#475569',
                                marginBottom: '8px'
                            }}>
                                🆔 CPF ou CNPJ
                            </label>
                            <input
                                type="text"
                                value={cpfCnpjInput}
                                onChange={(e) => setCpfCnpjInput(formatCpfCnpj(e.target.value))}
                                onKeyPress={handleKeyPress}
                                placeholder="000.000.000-00 ou 00.000.000/0000-00"
                                maxLength={18}
                                style={{
                                    width: '100%',
                                    padding: '14px 16px',
                                    borderRadius: '10px',
                                    border: '2px solid #E2E8F0',
                                    fontSize: '15px',
                                    transition: 'all 0.2s',
                                    outline: 'none',
                                    fontFamily: 'monospace'
                                }}
                                onFocus={(e) => e.target.style.borderColor = '#3B82F6'}
                                onBlur={(e) => e.target.style.borderColor = '#E2E8F0'}
                            />
                        </div>
                    )}

                    <button
                        onClick={handleSearch}
                        disabled={loading}
                        style={{
                            padding: '14px 32px',
                            borderRadius: '10px',
                            border: 'none',
                            background: loading
                                ? '#94A3B8'
                                : 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
                            color: 'white',
                            fontSize: '15px',
                            fontWeight: 600,
                            cursor: loading ? 'not-allowed' : 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)',
                            transition: 'all 0.2s'
                        }}
                    >
                        {loading ? (
                            <>
                                <span style={{ animation: 'spin 1s linear infinite' }}>⏳</span>
                                Buscando...
                            </>
                        ) : (
                            <>
                                🔍 Buscar
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Error Message */}
            {error && (
                <div style={{
                    background: 'linear-gradient(135deg, #FEE2E2 0%, #FECACA 100%)',
                    borderRadius: '12px',
                    padding: '16px 20px',
                    marginBottom: '24px',
                    border: '1px solid #F87171',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                }}>
                    <span style={{ fontSize: '24px' }}>❌</span>
                    <span style={{ color: '#991B1B', fontWeight: 500 }}>{error}</span>
                </div>
            )}

            {/* Loading */}
            {loading && (
                <div style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    padding: '60px',
                    background: 'white',
                    borderRadius: '16px',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)'
                }}>
                    <div className="spinner" style={{ marginRight: '12px' }}></div>
                    <span style={{ color: '#64748B', fontSize: '15px' }}>Buscando informações...</span>
                </div>
            )}

            {/* Multiple results list */}
            {multipleResults.length > 0 && !vendaData && !loading && (
                <div style={{
                    background: 'white',
                    borderRadius: '16px',
                    padding: '24px',
                    marginBottom: '24px',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                    border: '1px solid #E2E8F0'
                }}>
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        marginBottom: '16px'
                    }}>
                        <span style={{
                            background: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
                            color: 'white',
                            padding: '6px 12px',
                            borderRadius: '8px',
                            fontSize: '14px',
                            fontWeight: 600
                        }}>
                            {multipleResults.length} vendas encontradas
                        </span>
                        <span style={{ color: '#64748B', fontSize: '14px' }}>
                            Clique para ver detalhes
                        </span>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {multipleResults.map(v => {
                            const { quadra, lote } = parseQuadraLote(v.identificador);
                            return (
                                <div
                                    key={v.venda}
                                    onClick={async () => {
                                        setSavedMultipleResults(multipleResults);
                                        setMultipleResults([]);
                                        setVendaData(v);
                                        try {
                                            const sinaisResponse = await api.getSinais(empresa, obra, '2099-12-31');
                                            const sinaisVenda = sinaisResponse.data.filter(s => s.venda === v.venda);
                                            setSinaisAbertos(sinaisVenda.map(s => ({
                                                parcela: s.parcela,
                                                qtdParcelas: s.qtdParcelas,
                                                vencimento: s.vencimento,
                                                valorParcela: s.valorParcela
                                            })));
                                        } catch { }
                                        try {
                                            const sinaisPagosResponse = await api.getSinaisPagos(v.venda, empresa, obra);
                                            const sinaisPagosVenda = sinaisPagosResponse.data.filter(s => s.venda === v.venda);
                                            setSinaisPagos(sinaisPagosVenda);
                                        } catch { }
                                        try {
                                            const boletosResponse = await api.getBoletos(empresa, v.venda);
                                            const boletosVenda = boletosResponse.data.filter(b => b.venda === v.venda);
                                            setBoletos(boletosVenda);
                                        } catch { }
                                    }}
                                    style={{
                                        padding: '16px 20px',
                                        background: 'linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)',
                                        borderRadius: '12px',
                                        cursor: 'pointer',
                                        border: '2px solid #E2E8F0',
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        transition: 'all 0.2s'
                                    }}
                                    onMouseEnter={(e) => {
                                        e.currentTarget.style.background = 'linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%)';
                                        e.currentTarget.style.borderColor = '#3B82F6';
                                        e.currentTarget.style.transform = 'translateX(4px)';
                                    }}
                                    onMouseLeave={(e) => {
                                        e.currentTarget.style.background = 'linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)';
                                        e.currentTarget.style.borderColor = '#E2E8F0';
                                        e.currentTarget.style.transform = 'translateX(0)';
                                    }}
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                        <span style={{
                                            background: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
                                            color: 'white',
                                            padding: '8px 12px',
                                            borderRadius: '8px',
                                            fontWeight: 700,
                                            fontSize: '14px'
                                        }}>#{v.venda}</span>
                                        <div>
                                            <div style={{ fontWeight: 600, color: '#1E293B', fontSize: '15px' }}>{v.cliente}</div>
                                            <div style={{ fontSize: '12px', color: '#64748B' }}>
                                                Q{quadra} L{lote} • {v.dataVenda}
                                            </div>
                                        </div>
                                    </div>
                                    <div style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '8px',
                                        color: '#3B82F6',
                                        fontWeight: 600
                                    }}>
                                        Ver detalhes →
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {/* Venda Details */}
            {vendaData && !loading && (
                <>
                    {savedMultipleResults.length > 0 && (
                        <button
                            onClick={() => {
                                setVendaData(null);
                                setMultipleResults(savedMultipleResults);
                                setSinaisAbertos([]);
                                setSinaisPagos([]);
                                setBoletos([]);
                            }}
                            style={{
                                padding: '12px 20px',
                                borderRadius: '10px',
                                border: '2px solid #E2E8F0',
                                background: 'white',
                                color: '#475569',
                                fontSize: '14px',
                                fontWeight: 600,
                                cursor: 'pointer',
                                marginBottom: '16px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px'
                            }}
                        >
                            ← Voltar para lista ({savedMultipleResults.length} vendas)
                        </button>
                    )}

                    {/* Info Cards Grid */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
                        {/* Informações da Venda */}
                        <div style={{
                            background: 'white',
                            borderRadius: '16px',
                            padding: '24px',
                            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                            border: '1px solid #E2E8F0'
                        }}>
                            <div style={{
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                marginBottom: '20px'
                            }}>
                                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#1E293B' }}>
                                    📋 Informações da Venda
                                </h3>
                                <span style={{
                                    background: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
                                    color: 'white',
                                    padding: '6px 12px',
                                    borderRadius: '8px',
                                    fontWeight: 700,
                                    fontSize: '14px'
                                }}>#{vendaData.venda}</span>
                            </div>
                            <div style={{ display: 'grid', gap: '12px' }}>
                                {[
                                    { label: 'Cliente', value: vendaData.cliente, icon: '👤' },
                                    { label: 'Corretor', value: vendaData.corretor, icon: '🏢' },
                                    { label: 'Quadra', value: parseQuadraLoteDisplay(vendaData.identificador).quadra, icon: '📍', highlight: true },
                                    { label: 'Lote', value: parseQuadraLoteDisplay(vendaData.identificador).lote, icon: '📍', highlight: true },
                                    { label: 'Data da Venda', value: vendaData.dataVenda, icon: '📅' }
                                ].map((item, idx) => (
                                    <div key={idx} style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        padding: '12px 16px',
                                        background: '#F8FAFC',
                                        borderRadius: '10px'
                                    }}>
                                        <span style={{ color: '#64748B', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            {item.icon} {item.label}
                                        </span>
                                        <span style={{
                                            fontWeight: 600,
                                            fontSize: '14px',
                                            color: item.highlight ? '#2563EB' : '#1E293B'
                                        }}>{item.value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Valores e Resumo */}
                        <div style={{
                            background: 'white',
                            borderRadius: '16px',
                            padding: '24px',
                            boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                            border: '1px solid #E2E8F0'
                        }}>
                            <h3 style={{ margin: '0 0 20px 0', fontSize: '16px', fontWeight: 600, color: '#1E293B' }}>
                                💰 Valores e Resumo
                            </h3>
                            <div style={{
                                background: 'linear-gradient(135deg, #00528F 0%, #0089D6 100%)',
                                borderRadius: '12px',
                                padding: '24px',
                                marginBottom: '20px',
                                textAlign: 'center'
                            }}>
                                <div style={{ fontSize: '12px', color: '#94A3B8', marginBottom: '4px' }}>VALOR TOTAL</div>
                                <div style={{
                                    fontSize: '32px',
                                    fontWeight: 700,
                                    background: 'linear-gradient(135deg, #3B82F6 0%, #60A5FA 100%)',
                                    WebkitBackgroundClip: 'text',
                                    WebkitTextFillColor: 'transparent'
                                }}>
                                    R$ {vendaData.valorTotal?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                </div>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                                {[
                                    { label: 'Sinais Abertos', value: sinaisAbertos.length, color: '#F59E0B', bg: '#FEF3C7' },
                                    { label: 'Sinais Pagos', value: sinaisPagos.length, color: '#10B981', bg: '#D1FAE5' },
                                    { label: 'Boletos', value: boletos.length, color: '#3B82F6', bg: '#DBEAFE' }
                                ].map((item, idx) => (
                                    <div key={idx} style={{
                                        textAlign: 'center',
                                        padding: '16px 12px',
                                        background: item.bg,
                                        borderRadius: '12px'
                                    }}>
                                        <div style={{ fontSize: '24px', fontWeight: 700, color: item.color }}>{item.value}</div>
                                        <div style={{ fontSize: '11px', color: '#64748B', fontWeight: 500 }}>{item.label}</div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Sinais em Aberto */}
                    <div style={{
                        background: 'white',
                        borderRadius: '16px',
                        marginBottom: '24px',
                        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                        border: '1px solid #E2E8F0',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '20px 24px',
                            borderBottom: '1px solid #E2E8F0',
                            background: '#FFFBEB'
                        }}>
                            <span style={{ fontWeight: 600, color: '#1E293B', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                ⚠️ Sinais em Aberto
                            </span>
                            <span style={{
                                background: '#F59E0B',
                                color: 'white',
                                padding: '4px 12px',
                                borderRadius: '20px',
                                fontSize: '13px',
                                fontWeight: 600
                            }}>{sinaisAbertos.length}</span>
                        </div>
                        {sinaisAbertos.length > 0 ? (
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <thead>
                                    <tr style={{ background: '#F8FAFC' }}>
                                        <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '13px', color: '#64748B' }}>Parcela</th>
                                        <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '13px', color: '#64748B' }}>Vencimento</th>
                                        <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '13px', color: '#64748B' }}>Valor</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {sinaisAbertos.map((sinal, index) => {
                                        const today = new Date();
                                        today.setHours(0, 0, 0, 0);
                                        const [day, month, year] = sinal.vencimento.split('/').map(Number);
                                        const vencDate = new Date(year, month - 1, day);
                                        const isOverdue = vencDate < today;
                                        return (
                                            <tr key={index} style={{ borderBottom: '1px solid #E2E8F0' }}>
                                                <td style={{ padding: '14px 16px', textAlign: 'center' }}>
                                                    <span style={{
                                                        background: '#3B82F6',
                                                        color: 'white',
                                                        padding: '4px 10px',
                                                        borderRadius: '6px',
                                                        fontSize: '12px',
                                                        fontWeight: 600
                                                    }}>{sinal.parcela}/{sinal.qtdParcelas}</span>
                                                </td>
                                                <td style={{
                                                    padding: '14px 16px',
                                                    textAlign: 'center',
                                                    color: isOverdue ? '#DC2626' : '#16A34A',
                                                    fontWeight: 600
                                                }}>
                                                    {isOverdue && '⚠️ '}{sinal.vencimento}
                                                </td>
                                                <td style={{
                                                    padding: '14px 16px',
                                                    textAlign: 'right',
                                                    fontWeight: 600,
                                                    color: '#F59E0B'
                                                }}>
                                                    R$ {sinal.valorParcela?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        ) : (
                            <div style={{ padding: '40px', textAlign: 'center' }}>
                                <span style={{ fontSize: '24px' }}>✅</span>
                                <p style={{ color: '#10B981', fontWeight: 500, margin: '8px 0 0 0' }}>Nenhum sinal em aberto</p>
                            </div>
                        )}
                    </div>

                    {/* Sinais Pagos */}
                    <div style={{
                        background: 'white',
                        borderRadius: '16px',
                        marginBottom: '24px',
                        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                        border: '1px solid #E2E8F0',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '20px 24px',
                            borderBottom: '1px solid #E2E8F0',
                            background: '#ECFDF5'
                        }}>
                            <span style={{ fontWeight: 600, color: '#1E293B', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                ✅ Sinais Pagos
                            </span>
                            <span style={{
                                background: '#10B981',
                                color: 'white',
                                padding: '4px 12px',
                                borderRadius: '20px',
                                fontSize: '13px',
                                fontWeight: 600
                            }}>{sinaisPagos.length}</span>
                        </div>
                        {sinaisPagos.length > 0 ? (
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <thead>
                                    <tr style={{ background: '#F8FAFC' }}>
                                        <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '13px', color: '#64748B' }}>Parcela</th>
                                        <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '13px', color: '#64748B' }}>Recebimento</th>
                                        <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '13px', color: '#64748B' }}>Vencimento</th>
                                        <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '13px', color: '#64748B' }}>Valor Pago</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {sinaisPagos.map((sinal, index) => (
                                        <tr key={index} style={{ borderBottom: '1px solid #E2E8F0' }}>
                                            <td style={{ padding: '14px 16px', textAlign: 'center' }}>
                                                <span style={{
                                                    background: '#10B981',
                                                    color: 'white',
                                                    padding: '4px 10px',
                                                    borderRadius: '6px',
                                                    fontSize: '12px',
                                                    fontWeight: 600
                                                }}>{sinal.parcela}</span>
                                            </td>
                                            <td style={{ padding: '14px 16px', textAlign: 'center', fontWeight: 600, color: '#10B981' }}>{sinal.dataRecebimento}</td>
                                            <td style={{ padding: '14px 16px', textAlign: 'center', color: '#64748B' }}>{sinal.dataVencimento}</td>
                                            <td style={{ padding: '14px 16px', textAlign: 'right', fontWeight: 600, color: '#10B981' }}>
                                                R$ {sinal.valorPago?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        ) : (
                            <div style={{ padding: '40px', textAlign: 'center' }}>
                                <p style={{ color: '#64748B', margin: 0 }}>Nenhum sinal pago encontrado</p>
                            </div>
                        )}
                    </div>

                    {/* Boletos */}
                    <div style={{
                        background: 'white',
                        borderRadius: '16px',
                        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                        border: '1px solid #E2E8F0',
                        overflow: 'hidden'
                    }}>
                        <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            padding: '20px 24px',
                            borderBottom: '1px solid #E2E8F0',
                            background: '#EFF6FF'
                        }}>
                            <span style={{ fontWeight: 600, color: '#1E293B', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                📄 Boletos Gerados
                            </span>
                            <span style={{
                                background: '#3B82F6',
                                color: 'white',
                                padding: '4px 12px',
                                borderRadius: '20px',
                                fontSize: '13px',
                                fontWeight: 600
                            }}>{boletos.length}</span>
                        </div>
                        {boletos.length > 0 ? (
                            <div style={{ overflowX: 'auto' }}>
                                <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: '700px' }}>
                                    <thead>
                                        <tr style={{ background: '#F8FAFC' }}>
                                            <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '13px', color: '#64748B' }}>Parcela</th>
                                            <th style={{ padding: '12px 16px', textAlign: 'left', fontSize: '13px', color: '#64748B' }}>Nosso Número</th>
                                            <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '13px', color: '#64748B' }}>Emissão</th>
                                            <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '13px', color: '#64748B' }}>Vencimento</th>
                                            <th style={{ padding: '12px 16px', textAlign: 'right', fontSize: '13px', color: '#64748B' }}>Valor</th>
                                            <th style={{ padding: '12px 16px', textAlign: 'center', fontSize: '13px', color: '#64748B' }}>Gerado Por</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {boletos.map((boleto, index) => (
                                            <tr key={index} style={{
                                                borderBottom: '1px solid #E2E8F0',
                                                backgroundColor: (boleto as any).foiAlterado === 1 ? '#FEF3C7' : 'inherit'
                                            }}>
                                                <td style={{ padding: '14px 16px', textAlign: 'center' }}>
                                                    <span style={{
                                                        background: '#3B82F6',
                                                        color: 'white',
                                                        padding: '4px 10px',
                                                        borderRadius: '6px',
                                                        fontSize: '12px',
                                                        fontWeight: 600
                                                    }}>{boleto.parcela}</span>
                                                    {(boleto as any).foiAlterado === 1 && (
                                                        <span style={{ marginLeft: '4px', fontSize: '10px', color: '#D97706' }} title="Boleto alterado">📝</span>
                                                    )}
                                                </td>
                                                <td style={{ padding: '14px 16px', fontFamily: 'monospace', color: '#64748B', fontSize: '12px' }}>{boleto.nossoNumero}</td>
                                                <td style={{ padding: '14px 16px', textAlign: 'center', color: '#64748B' }}>{boleto.dataEmissao}</td>
                                                <td style={{ padding: '14px 16px', textAlign: 'center', color: '#64748B' }}>{boleto.dataVencimento}</td>
                                                <td style={{ padding: '14px 16px', textAlign: 'right', fontWeight: 600, color: '#2563EB' }}>
                                                    R$ {boleto.valorDocumento?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                                </td>
                                                <td style={{ padding: '14px 16px', textAlign: 'center', fontSize: '11px', maxWidth: '100px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={(boleto as any).usuarioGerou || '-'}>
                                                    {(boleto as any).usuarioGerou || '-'}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <div style={{ padding: '40px', textAlign: 'center' }}>
                                <span style={{ fontSize: '24px' }}>❌</span>
                                <p style={{ color: '#DC2626', fontWeight: 500, margin: '8px 0 0 0' }}>Nenhum boleto gerado</p>
                            </div>
                        )}
                    </div>
                </>
            )}

            {/* Empty State */}
            {!vendaData && !loading && !error && multipleResults.length === 0 && (
                <div style={{
                    background: 'white',
                    borderRadius: '16px',
                    padding: '60px',
                    textAlign: 'center',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
                    border: '1px solid #E2E8F0'
                }}>
                    <div style={{
                        width: '80px',
                        height: '80px',
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, #F1F5F9 0%, #E2E8F0 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 16px',
                        fontSize: '32px'
                    }}>
                        🔍
                    </div>
                    <h3 style={{ color: '#1E293B', fontSize: '18px', fontWeight: 600, margin: '0 0 8px 0' }}>
                        Faça uma busca
                    </h3>
                    <p style={{ color: '#64748B', fontSize: '14px', margin: 0 }}>
                        Escolha o tipo de busca acima e preencha os campos
                    </p>
                </div>
            )}
        </div>
    );
};
