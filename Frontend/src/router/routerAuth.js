import React from 'react';
import { Navigate, useLocation } from "react-router-dom";

/**
 * @param {Object} props - 组件属性
 * @param {React.ReactNode} props.children - 子组件
 */
export const ProtectedRoute = ({ children }) => {
    const token = localStorage.getItem('token');
    const location = useLocation();

    const isTokenExpired = (value) => {
        try {
            const parts = String(value).split('.');
            if (parts.length < 2) return true;
            const base64Url = parts[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const jsonPayload = decodeURIComponent(
                atob(base64)
                    .split('')
                    .map(c => `%${`00${c.charCodeAt(0).toString(16)}`.slice(-2)}`)
                    .join('')
            );
            const payload = JSON.parse(jsonPayload);
            const exp = payload?.exp;
            if (typeof exp !== 'number') return true;
            return exp * 1000 <= Date.now();
        } catch {
            return true;
        }
    };

    // 如果没有 token，重定向到登录页面
    if (!token || isTokenExpired(token)) {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        return (<Navigate to="/login" replace state={{ from: location }} />);
    }

    if (location.pathname === '/login') {
        return (<Navigate to="/home" replace />);
    }

    return children;
}   
