// Axios 是一个基于 promise 的网络请求库
import axios from "axios";

const baseURL = '';

// axios 二次封装的核心
class HttpRequest {
    // 构造函数存储基础url
    constructor(baseURL) {
        this.baseURL = baseURL;
    }
    // 获取默认配置
    getInsideConfig() {
        const config = {
            baseURL: this.baseURL,
            headers: {}
        }
        return config;
    }
    // 配置拦截器
    interceptions(instance) {
        // 添加请求拦截器
        instance.interceptors.request.use(function (config) {
            // 从 localStorage 获取 token 并添加到请求头
            const token = localStorage.getItem('token');
            if (token) {
                config.headers = config.headers || {};
                // 兼容处理 headers 对象
                if (config.headers.set) {
                    config.headers.set('Authorization', `Bearer ${token}`);
                } else {
                    config.headers.Authorization = `Bearer ${token}`;
                }
            }
            return config;
        }, function (error) {
            // 对请求错误做些什么
            return Promise.reject(error);
        });

        // 添加响应拦截器
        instance.interceptors.response.use(function (response) {
            // 2xx 范围内的状态码都会触发该函数。
            // 对响应数据做点什么
            return response;
        }, function (error) {
            // 超出 2xx 范围的状态码都会触发该函数。
            // 对响应错误做点什么
            if (error.response?.status === 401) {
                localStorage.removeItem('token');
                if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
                    window.location.href = '/login';
                }
            }
            return Promise.reject(error);
        });
    }
    // 建立请求
    request(configurations) {
        configurations = { ...this.getInsideConfig(), ...configurations };
        // 建立axois实例
        const instance = axios.create();
        // 配置实例化拦截器
        this.interceptions(instance);
        // 发起请求
        return instance(configurations);
    }
}

export default new HttpRequest(baseURL);