import React from 'react';
import type { Estatisticas } from '../../types';
import { FaChartBar, FaCheckCircle, FaClock, FaHandshake } from 'react-icons/fa';
import './Stats.css';

interface StatsProps {
    stats: Estatisticas;
}

const Stats: React.FC<StatsProps> = ({ stats }) => {
    return (
        <section className="stats-section">
            <div className="stat-card stat-total">
                <div className="stat-icon">
                    <FaChartBar />
                </div>
                <div className="stat-info">
                    <div className="stat-value">{stats.total}</div>
                    <div className="stat-label">Total de Lotes</div>
                </div>
            </div>

            <div className="stat-card stat-disponivel">
                <div className="stat-icon">
                    <FaCheckCircle />
                </div>
                <div className="stat-info">
                    <div className="stat-value">{stats.disponiveis}</div>
                    <div className="stat-label">Disponíveis</div>
                </div>
            </div>

            <div className="stat-card stat-reservado">
                <div className="stat-icon">
                    <FaClock />
                </div>
                <div className="stat-info">
                    <div className="stat-value">{stats.reservados}</div>
                    <div className="stat-label">Reservados</div>
                </div>
            </div>

            <div className="stat-card stat-vendido">
                <div className="stat-icon">
                    <FaHandshake />
                </div>
                <div className="stat-info">
                    <div className="stat-value">{stats.vendidos}</div>
                    <div className="stat-label">Vendidos</div>
                </div>
            </div>
        </section>
    );
};

export default Stats;
