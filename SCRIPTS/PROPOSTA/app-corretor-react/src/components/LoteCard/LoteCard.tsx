import React from 'react';
import type { Lote } from '../../types';
import { getStatusClass, getStatusLabel } from '../../services/api';
import './LoteCard.css';

interface LoteCardProps {
    lote: Lote;
    onClick: () => void;
}

const LoteCard: React.FC<LoteCardProps> = ({ lote, onClick }) => {
    const statusClass = getStatusClass(lote.Status_Terreno);
    const statusLabel = getStatusLabel(lote.Status_Terreno);

    return (
        <div className="lote-card" onClick={onClick}>
            <div className="lote-header">
                <div className="lote-id">
                    <span className="lote-quadra">Quadra {lote.QD}</span>
                    <span className="lote-numero">Lote {lote.LT}</span>
                </div>
                <span className={`lote-status ${statusClass}`}>{statusLabel}</span>
            </div>
            <div className="lote-body">
                <div className="lote-info">
                    <div className="lote-info-item">
                        <span className="lote-info-label">Área</span>
                        <span className="lote-info-value">{lote.M2} m²</span>
                    </div>
                    <div className="lote-info-item">
                        <span className="lote-info-label">Frente</span>
                        <span className="lote-info-value">{lote.M_Frente} m</span>
                    </div>
                    <div className="lote-info-item">
                        <span className="lote-info-label">Fundo</span>
                        <span className="lote-info-value">{lote.M_Fundo} m</span>
                    </div>
                    <div className="lote-info-item">
                        <span className="lote-info-label">Lado Dir.</span>
                        <span className="lote-info-value">{lote.M_Lado_Direito} m</span>
                    </div>
                </div>
                <div className="lote-logradouro">📍 {lote.Logradouro}</div>
            </div>
            <div className="lote-footer">
                <span className="lote-preco">R$ {lote.Valor_Terreno}</span>
                <button className="btn-detalhes" onClick={(e) => { e.stopPropagation(); onClick(); }}>
                    Ver Detalhes
                </button>
            </div>
        </div>
    );
};

export default LoteCard;
