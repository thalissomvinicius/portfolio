import React from 'react';

interface ErrorMessageProps {
    message: string;
    onRetry?: () => void;
}

/**
 * Reusable error message component
 */
export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry }) => {
    return (
        <div className="card" style={{
            background: '#FEE2E2',
            borderColor: '#EF4444',
            borderWidth: '1px',
            borderStyle: 'solid'
        }}>
            <p style={{ color: '#991B1B', marginBottom: onRetry ? '12px' : 0 }}>
                ❌ {message}
            </p>
            {onRetry && (
                <button
                    onClick={onRetry}
                    className="btn btn-primary"
                    style={{ marginTop: '8px' }}
                >
                    Tentar Novamente
                </button>
            )}
        </div>
    );
};
