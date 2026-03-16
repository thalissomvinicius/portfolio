import React from 'react';

interface LoadingSpinnerProps {
    message?: string;
}

/**
 * Reusable loading spinner component
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ message }) => {
    return (
        <div className="loading">
            <div className="spinner"></div>
            {message && (
                <p style={{ marginTop: '16px', color: '#64748B', fontSize: '14px' }}>
                    {message}
                </p>
            )}
        </div>
    );
};
