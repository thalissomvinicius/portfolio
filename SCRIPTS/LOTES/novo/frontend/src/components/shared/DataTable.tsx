import React from 'react';

interface DataTableProps {
    title: string;
    badgeText?: string;
    badgeVariant?: 'primary' | 'success' | 'warning' | 'danger';
    children: React.ReactNode;
    headerActions?: React.ReactNode;
}

/**
 * Reusable data table container with header
 */
export const DataTable: React.FC<DataTableProps> = ({
    title,
    badgeText,
    badgeVariant = 'primary',
    children,
    headerActions
}) => {
    return (
        <div className="table-container">
            <div className="table-header-row">
                <span className="table-title">{title}</span>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    {badgeText && (
                        <span className={`badge badge-${badgeVariant}`}>{badgeText}</span>
                    )}
                    {headerActions}
                </div>
            </div>
            {children}
        </div>
    );
};
