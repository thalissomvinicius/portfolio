import React from 'react';
import type { Lote } from '../../types';
import { getStatusClass, getStatusLabel } from '../../services/api';
import './LoteModal.css';

interface LoteModalProps {
    lote: Lote | null;
    isOpen: boolean;
    onClose: () => void;
    onNovaPropostaClick: (lote: Lote) => void;
}

const LoteModal: React.FC<LoteModalProps> = ({ lote, isOpen, onClose, onNovaPropostaClick }) => {
    if (!isOpen || !lote) return null;

    const statusClass = getStatusClass(lote.Status_Terreno);
    const statusLabel = getStatusLabel(lote.Status_Terreno);
    const isDisponivel = lote.Status_Terreno.includes('Disponível');

    return (
        <div className={`modal ${isOpen ? 'active' : ''}`} onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <button className="modal-close" onClick={onClose}>&times;</button>

                <div className="modal-header">
                    <h2 className="modal-title">Quadra {lote.QD} - Lote {lote.LT}</h2>
                    <p className="modal-subtitle">{lote.Logradouro}</p>
                </div>

                <div className="modal-body">
                    <div className="modal-section">
                        <div className="modal-grid">
                            <div className="modal-item">
                                <span className="modal-label">Status</span>
                                <span className={`lote-status ${statusClass}`} style={{ display: 'inline-block', marginTop: '4px' }}>
                                    {statusLabel}
                                </span>
                            </div>
                            <div className="modal-item">
                                <span className="modal-label">Atualizado em</span>
                                <span className="modal-value">{lote.Data_Atualizacao}</span>
                            </div>
                        </div>
                    </div>

                    <div className="modal-section">
                        <h3 className="modal-section-title">Dimensões</h3>
                        <div className="modal-grid">
                            <div className="modal-item">
                                <span className="modal-label">Área Total</span>
                                <span className="modal-value">{lote.M2} m²</span>
                            </div>
                            <div className="modal-item">
                                <span className="modal-label">Frente</span>
                                <span className="modal-value">{lote.M_Frente} m</span>
                            </div>
                            <div className="modal-item">
                                <span className="modal-label">Fundo</span>
                                <span className="modal-value">{lote.M_Fundo} m</span>
                            </div>
                            <div className="modal-item">
                                <span className="modal-label">Lado Direito</span>
                                <span className="modal-value">{lote.M_Lado_Direito} m</span>
                            </div>
                            <div className="modal-item">
                                <span className="modal-label">Lado Esquerdo</span>
                                <span className="modal-value">{lote.M_Lado_Esquerdo} m</span>
                            </div>
                            <div className="modal-item">
                                <span className="modal-label">Chanfro</span>
                                <span className="modal-value">{lote.Chanfro}</span>
                            </div>
                        </div>
                    </div>

                    <div className="modal-section">
                        <h3 className="modal-section-title">Valor</h3>
                        <div className="modal-item">
                            <span className="modal-label">Valor do Terreno</span>
                            <span className="modal-value preco">R$ {lote.Valor_Terreno}</span>
                        </div>
                    </div>
                </div>

                <div className="modal-footer">
                    <button className="btn-secondary" onClick={onClose}>Fechar</button>
                    {isDisponivel && (
                        <button className="btn-success" onClick={() => onNovaPropostaClick(lote)}>
                            📝 Gerar Proposta
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default LoteModal;
