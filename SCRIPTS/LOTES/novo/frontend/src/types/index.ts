// API Types for VallePrime Dashboard

export interface Venda {
    venda: number;
    cliente: string;
    clienteId?: number;
    corretor: string;
    vendedorId?: number;
    identificador: string;
    dataVenda: string;
    dataCadastro?: string;
    valorTotal: number;
    empresa?: number;
    obra?: string;
    status?: number;
}

export interface ResumoVenda extends Venda {
    boletoGerado: boolean;
    sinaisAberto: number;
    sinaisPagos: number;
    sinaisTotal: number;
    primeiroVencimento: string | null;
    primeiroVencimentoISO: string | null;
}

export interface Metrics {
    totalVendas: number;
    vendasComBoleto: number;
    vendasSemBoleto: number;
    totalSinaisAberto: number;
    valorTotal: number;
}

export interface ResumoResponse {
    data: ResumoVenda[];
    metrics: Metrics;
}

export interface Sinal {
    corretor: string;
    cliente: string;
    empresa: number;
    venda: number;
    obra: string;
    quadra: string;
    lote: string;
    dataVenda: string;
    dataCadastro?: string;
    valorVenda: number;
    parcela: number;
    qtdParcelas: number;
    vencimento: string;
    prorrogacao?: string;
    valorParcela: number;
}

export interface SinaisResponse {
    data: Sinal[];
    total: number;
    metrics: {
        totalParcelas: number;
        valorTotal: number;
        vendasDistintas: number;
    };
}

export interface SinalPago {
    empresa: number;
    obra: string;
    venda: number;
    parcela: number;
    tipo: string;
    dataRecebimento: string;
    dataVencimento: string;
    valorPago: number;
    cliente: string;
}

export interface Boleto {
    empresa: number;
    obra: string;
    venda: number;
    parcela: number;
    tipo: string;
    cliente: string;
    nossoNumero: string;
    numeroBoleto: string;
    dataEmissao: string;
    dataVencimento: string;
    valorDocumento: number;
    enviadoEmail: boolean;
}

export interface BoletosResponse {
    data: Boleto[];
    total: number;
    metrics: {
        totalBoletos: number;
        enviadosEmail: number;
        valorTotal: number;
    };
}

export interface ApiError {
    error: string;
    type: string;
}

export type ViewType = 'dashboard' | 'sinais' | 'boletos' | 'detalhes';

export interface Filters {
    empresa: number;
    obra: string;
    dataVencimento: string;
}
