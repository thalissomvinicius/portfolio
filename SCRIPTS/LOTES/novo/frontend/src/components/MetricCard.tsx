import React from 'react';

interface MetricCardProps {
    icon: string;
    label: string;
    value: string | number;
    color?: 'primary' | 'success' | 'warning' | 'danger';
}

export const MetricCard: React.FC<MetricCardProps> = ({
    icon,
    label,
    value,
    color = 'primary',
}) => {
    return (
        <div className="metric-card animate-fade-in">
            <div className="metric-icon">{icon}</div>
            <div className="metric-label">{label}</div>
            <div className={`metric-value ${color}`}>{value}</div>
        </div>
    );
};
