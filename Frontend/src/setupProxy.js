const { createProxyMiddleware } = require('http-proxy-middleware');

// 后端服务地址
const BACKEND_TARGET = 'http://127.0.0.1:8000';

module.exports = function (app) {
    // 优先：/question 下所有请求
    app.use(
        '/question',
        createProxyMiddleware({
            target: BACKEND_TARGET,
            changeOrigin: true,
            pathRewrite: {
                '^/': '/question/'
            },
            onProxyReq: (proxyReq, req) => {
                console.log('[proxy] question ->', req.method, req.url);
            },
            onError: (err, req, res) => {
                console.error('[proxy] question error:', err.message);
            }
        })
    );

    // 其他 /api 请求
    app.use(
        '/api',
        createProxyMiddleware({
            target: BACKEND_TARGET,
            changeOrigin: true,
            pathRewrite: {
                '^/': '/api/'
            }
        })
    );

    // 认证等 /auth 请求
    app.use(
        '/auth',
        createProxyMiddleware({
            target: BACKEND_TARGET,
            changeOrigin: true,
            pathRewrite: {
                '^/': '/auth/'
            }
        })
    );

    app.use(
        '/user',
        createProxyMiddleware({
            target: BACKEND_TARGET,
            changeOrigin: true,
            pathRewrite: {
                '^/': '/user/'
            }
        })
    );

    app.use(
        '/experiment',
        createProxyMiddleware({
            target: BACKEND_TARGET,
            changeOrigin: true,
            pathRewrite: {
                '^/api': '/experiment/api',
                '^/': '/experiment/'
            }
        })
    );

    app.use(
        '/shop',
        createProxyMiddleware({
            target: BACKEND_TARGET,
            changeOrigin: true,
            pathRewrite: {
                '^/': '/shop/'
            }
        })
    );
};
