// ============================================
// Types & Interfaces
// ============================================

export interface Lote {
    QD: string;
    LT: string;
    M2: string;
    Logradouro: string;
    M_Frente: string;
    M_Fundo: string;
    M_Lado_Direito: string;
    M_Lado_Esquerdo: string;
    Chanfro: string;
    Valor_Terreno: string;
    Status_Terreno: string;
    Data_Atualizacao: string;
}

export interface ApiResponse {
    success: boolean;
    count: number;
    numprod_psc: number;
    data: Lote[];
}

export interface Empreendimento {
    id: number;
    nome: string;
    cidade: string;
    estado: string;
}

export type StatusType = 'disponivel' | 'reservado' | 'vendido' | 'quitado' | 'fora' | 'outro';

export interface Filtros {
    status: string;
    quadra: string;
    busca: string;
}

export interface Estatisticas {
    total: number;
    disponiveis: number;
    reservados: number;
    vendidos: number;
}
