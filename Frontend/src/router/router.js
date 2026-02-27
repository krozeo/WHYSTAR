import Login from '../pages/Login/login';
import Home from '../pages/Home/home';
import { Suspense, lazy } from 'react';
import { createBrowserRouter, Navigate } from "react-router-dom";
import { ProtectedRoute } from './routerAuth';

// 使用lazy进行懒加载
const Novel = lazy(() => import('../pages/Novel/novel'));
const NovelChoose = lazy(() => import('../pages/NovelChoose/novelChoose'));
const Experiment = lazy(() => import('../pages/Experiment/experiment'));
const QuizzesChoose = lazy(() => import('../pages/QuizzesChoose/quizzesChoose'));
const Knowledge = lazy(() => import('../pages/Quizzes/quizzes'));
const ChapterGame = lazy(() => import('../component/WebGames/chapterGame'));

// 创建Suspense包装器
const withSuspense = (Component) => (
    <Suspense fallback={<div>页面加载中</div>}>
        <Component />
    </Suspense>
);

const routers = [
    {
        path: '/login',
        element: <Login />
    },
    {
        path: '/',  // 根路径重定向到 home
        element: <Navigate to="/home" replace />
    },
    {
        path: '/home',
        element: <Home />
    },
    {
        path: '/novel-choose',
        element: (
            <ProtectedRoute>
                {withSuspense(NovelChoose)}
            </ProtectedRoute>
        )
    },
    {
        path: '/novel-reading',
        element: (
            <ProtectedRoute>
                {withSuspense(Novel)}
            </ProtectedRoute>
        )
    },
    {
        path: '/ChapterGame',
        element: (
            <ProtectedRoute>
                {withSuspense(ChapterGame)}
            </ProtectedRoute>
        )
    },
    {
        path: '/physics-experiment',
        element: (
            <ProtectedRoute>
                {withSuspense(Experiment)}
            </ProtectedRoute>
        )
    },
    {
        path: '/quizzes-choose',
        element: (
            <ProtectedRoute>
                {withSuspense(QuizzesChoose)}
            </ProtectedRoute>
        )
    },
    {
        path: '/knowledge-quizzes',
        element: (
            <ProtectedRoute>
                {withSuspense(Knowledge)}
            </ProtectedRoute>
        )
    }
];

export default createBrowserRouter(routers);