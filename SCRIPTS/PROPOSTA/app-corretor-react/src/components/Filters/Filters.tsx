import React from 'react';
import type { Filtros, Empreendimento } from '../../types';
import { empreendimentos } from '../../services/api';
import './Filters.css';

interface FiltersProps {
    filtros: Filtros;
    quadras: string[];
    onFiltrosChange: (filtros: Filtros) => void;
    onBuscar: () => void;
    onEmpreendimentoChange: (id: number) => void;
}

const Filters: React.FC<FiltersProps> = ({
    filtros,
    quadras,
    onFiltrosChange,
    onBuscar,
    onEmpreendimentoChange
}) => {
    return (
        <section className="filters-section">
            <h1 className="page-title">Consulta de Lotes</h1>

            <div className="filters-grid">
                <div className="filter-group">
                    <label className="filter-label">Empreendimento</label>
                    <select
                        className="filter-select"
                        onChange={(e) => onEmpreendimentoChange(Number(e.target.value))}
                        defaultValue="600"
                    >
                        {empreendimentos.map((emp: Empreendimento) => (
                            <option key={emp.id} value={emp.id}>
                                {emp.nome} - {emp.cidade}/{emp.estado}
                            </option>
                        ))}
                    </select>
                </div>

                <div className="filter-group">
                    <label className="filter-label">Status</label>
                    <select
                        className="filter-select"
                        value={filtros.status}
                        onChange={(e) => onFiltrosChange({ ...filtros, status: e.target.value })}
                    >
                        <option value="">Todos</option>
                        <option value="disponivel">Disponível</option>
                        <option value="reservado">Reservado</option>
                        <option value="vendido">Vendido</option>
                        <option value="quitado">Quitado</option>
                    </select>
                </div>

                <div className="filter-group">
                    <label className="filter-label">Quadra</label>
                    <select
                        className="filter-select"
                        value={filtros.quadra}
                        onChange={(e) => onFiltrosChange({ ...filtros, quadra: e.target.value })}
                    >
                        <option value="">Todas</option>
                        {quadras.map((qd) => (
                            <option key={qd} value={qd}>Quadra {qd}</option>
                        ))}
                    </select>
                </div>

                <div className="filter-group">
                    <label className="filter-label">Buscar</label>
                    <input
                        type="text"
                        className="filter-input"
                        placeholder="Lote, logradouro..."
                        value={filtros.busca}
                        onChange={(e) => onFiltrosChange({ ...filtros, busca: e.target.value })}
                        onKeyPress={(e) => e.key === 'Enter' && onBuscar()}
                    />
                </div>

                <button onClick={onBuscar} className="btn-primary">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="11" cy="11" r="8"></circle>
                        <path d="m21 21-4.35-4.35"></path>
                    </svg>
                    Buscar
                </button>
            </div>
        </section>
    );
};

export default Filters;
