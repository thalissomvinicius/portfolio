/**
 * Utility functions for formatting values
 */

/**
 * Format a number as Brazilian Real currency
 */
export const formatCurrency = (value: number): string => {
    return value.toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
};

/**
 * Format currency in millions - now shows full value (deprecated abbreviation)
 */
export const formatCurrencyMi = (value: number): string => {
    return formatCurrency(value);
};

/**
 * Format a date string from ISO to Brazilian format
 */
export const formatDate = (dateStr: string): string => {
    if (!dateStr) return '-';
    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('pt-BR');
    } catch {
        return dateStr;
    }
};

/**
 * Format percentage
 */
export const formatPercent = (value: number, decimals: number = 1): string => {
    return value.toFixed(decimals) + '%';
};
