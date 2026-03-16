import React from 'react';

export type MetricVariant = 'primary' | 'success' | 'warning' | 'danger' | 'default';

interface StatCardProps {
    icon?: string;
    label: string;
    value: string | number;
    variant?: MetricVariant;
    subtext?: string;
    onClick?: () => void;
}

const variantColors: Record<MetricVariant, string> = {
    primary: '#2563EB',
    success: '#10B981',
    warning: '#F59E0B',
    danger: '#EF4444',
    default: '#1E293B'
};

/**
 * Reusable statistic card component
 */
export const StatCard: React.FC<StatCardProps> = ({
    icon,
    label,
    value,
    variant = 'default',
    subtext,
    onClick
}) => {
    return (
        <div
            className="metric-card"
            onClick={onClick}
            style={{ cursor: onClick ? 'pointer' : 'default' }}
        >
            {icon && <div className="metric-card-icon">{icon}</div>}
            <div className="metric-card-content">
                <div className="metric-label">{label}</div>
                <div
                    className={`metric-value ${variant !== 'default' ? variant : ''}`}
                    style={{ color: variantColors[variant] }}
                >
                    {value}
                </div>
                {subtext && (
                    <div style={{ fontSize: '12px', color: '#64748B', marginTop: '4px' }}>
                        {subtext}
                    </div>
                )}
            </div>
        </div>
    );
};
