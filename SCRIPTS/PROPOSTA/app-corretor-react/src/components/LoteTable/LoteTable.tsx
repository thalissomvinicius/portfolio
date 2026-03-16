import React, { useState } from 'react';
import type { Lote, Empreendimento } from '../../types';
import { getStatusClass, getStatusLabel } from '../../services/api';
import { FaMapMarkerAlt, FaRulerCombined, FaMoneyBillWave, FaEye, FaSortUp, FaSortDown, FaSort, FaCalculator } from 'react-icons/fa';
import OrcamentoModal from '../OrcamentoModal/OrcamentoModal';
import './LoteTable.css';

interface LoteTableProps {
    lotes: Lote[];
    empreendimento: Empreendimento | null;
    onLoteClick: (lote: Lote) => void;
}

type SortField = 'QD' | 'LT' | 'M2' | 'Valor_Terreno' | 'Status_Terreno';
type SortDirection = 'asc' | 'desc' | null;

const LoteTable: React.FC<LoteTableProps> = ({ lotes, empreendimento, onLoteClick }) => {
    const [sortField, setSortField] = useState<SortField | null>(null);
    const [sortDirection, setSortDirection] = useState<SortDirection>(null);
    const [orcamentoModalOpen, setOrcamentoModalOpen] = useState(false);
    const [loteOrcamento, setLoteOrcamento] = useState<Lote | null>(null);

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            // Ciclo: asc -> desc -> null
            if (sortDirection === 'asc') {
                setSortDirection('desc');
            } else if (sortDirection === 'desc') {
                setSortDirection(null);
                setSortField(null);
            }
        } else {
            setSortField(field);
            setSortDirection('asc');
        }
    };

    const getSortedLotes = () => {
        if (!sortField || !sortDirection) return lotes;

        return [...lotes].sort((a, b) => {
            let aVal = a[sortField];
            let bVal = b[sortField];

            // Converter valores para comparação
            if (sortField === 'M2' || sortField === 'Valor_Terreno') {
                aVal = parseFloat(String(aVal).replace(/[^\d,]/g, '').replace(',', '.')) || 0;
                bVal = parseFloat(String(bVal).replace(/[^\d,]/g, '').replace(',', '.')) || 0;
            }

            if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
            if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
            return 0;
        });
    };

    const renderSortIcon = (field: SortField) => {
        if (sortField !== field) return <FaSort className="sort-icon" />;
        return sortDirection === 'asc' ?
            <FaSortUp className="sort-icon active" /> :
            <FaSortDown className="sort-icon active" />;
    };

    const sortedLotes = getSortedLotes();

    return (
        <div className="table-container">
            <table className="lote-table">
                <thead>
                    <tr>
                        <th onClick={() => handleSort('QD')}>
                            Quadra {renderSortIcon('QD')}
                        </th>
                        <th onClick={() => handleSort('LT')}>
                            Lote {renderSortIcon('LT')}
                        </th>
                        <th onClick={() => handleSort('M2')}>
                            <FaRulerCombined /> Área (m²) {renderSortIcon('M2')}
                        </th>
                        <th>
                            <FaMapMarkerAlt /> Logradouro
                        </th>
                        <th onClick={() => handleSort('Valor_Terreno')}>
                            <FaMoneyBillWave /> Valor {renderSortIcon('Valor_Terreno')}
                        </th>
                        <th onClick={() => handleSort('Status_Terreno')}>
                            Status {renderSortIcon('Status_Terreno')}
                        </th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody>
                    {sortedLotes.map((lote) => {
                        const statusClass = getStatusClass(lote.Status_Terreno);
                        const statusLabel = getStatusLabel(lote.Status_Terreno);

                        return (
                            <tr key={`${lote.QD}-${lote.LT}`} onClick={() => onLoteClick(lote)}>
                                <td className="td-quadra">{lote.QD}</td>
                                <td className="td-lote">{lote.LT}</td>
                                <td className="td-area">{lote.M2} m²</td>
                                <td className="td-logradouro">{lote.Logradouro}</td>
                                <td className="td-valor">{lote.Valor_Terreno}</td>
                                <td>
                                    <span className={`table-status ${statusClass}`}>
                                        {statusLabel}
                                    </span>
                                </td>
                                <td className="td-actions">
                                    <button
                                        className="btn-table-view"
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onLoteClick(lote);
                                        }}
                                    >
                                        <FaEye /> Ver
                                    </button>
                                    {lote.Status_Terreno.includes('Disponível') && (
                                        <button
                                            className="btn-table-orcamento"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                setLoteOrcamento(lote);
                                                setOrcamentoModalOpen(true);
                                            }}
                                        >
                                            <FaCalculator /> Orçamento
                                        </button>
                                    )}
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>

            <OrcamentoModal
                lote={loteOrcamento}
                empreendimento={empreendimento}
                isOpen={orcamentoModalOpen}
                onClose={() => {
                    setOrcamentoModalOpen(false);
                    setLoteOrcamento(null);
                }}
            />
        </div>
    );
};

export default LoteTable;
