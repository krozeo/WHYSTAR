import React from 'react';
import { Navigate, useLocation } from "react-router-dom";

/**
 * 路由守卫组件 - 保护需要登录才能访问的路由
 * @param {Object} props - 组件属性
 * @param {React.ReactNode} props.children - 子组件
 */
export const ProtectedRoute = ({ children }) => {
    const token = localStorage.getItem('token');
    const location = useLocation();

    // 如果没有 token，重定向到登录页面
    if (!token) {
        return (<Navigate to="/home" replace />);
    }

    if (location.pathname === '/login') {
        return (<Navigate to="/home" replace />);
    }

    return children;
}   