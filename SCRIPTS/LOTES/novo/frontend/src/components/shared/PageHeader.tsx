import React from 'react';

interface PageHeaderProps {
    title: string;
    subtitle?: string;
    actions?: React.ReactNode;
    style?: React.CSSProperties;
}

/**
 * Reusable page header component with title, subtitle and optional actions
 */
export const PageHeader: React.FC<PageHeaderProps> = ({
    title,
    subtitle,
    actions,
    style
}) => {
    return (
        <div className="page-header" style={{ marginBottom: '24px', ...style }}>
            <div>
                <h1 className="page-title">{title}</h1>
                {subtitle && <p className="page-subtitle">{subtitle}</p>}
            </div>
            {actions && <div className="page-header-actions">{actions}</div>}
        </div>
    );
};
