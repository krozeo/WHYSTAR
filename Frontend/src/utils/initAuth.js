// 初始化认证状态 - 从 localStorage 恢复登录状态
// AI辅助生成：DeepSeek-v 3.2, 2026-2月
import { setHasLogin, setUser, setEquippedAvatar, clearEquippedAvatar } from '../store/reducers/user';

const isTokenExpired = (token) => {
    try {
        const parts = String(token).split('.');
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

/**
 * 从 localStorage 中读取 token 和 user 信息，如果存在则恢复 Redux 状态
 * @param {Function} dispatch - Redux dispatch 函数
 */
export const initAuth = (dispatch) => {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');

    if (token && userStr && !isTokenExpired(token)) {
        const user = JSON.parse(userStr);
        const equippedAvatarId = localStorage.getItem('equippedAvatarId');
        const equippedAvatarUrl = localStorage.getItem('equippedAvatarUrl');
        // 恢复登录状态
        dispatch(setHasLogin(true));
        dispatch(setUser(user));
        if (equippedAvatarId || equippedAvatarUrl) {
            dispatch(setEquippedAvatar({
                id: equippedAvatarId ? Number(equippedAvatarId) : null,
                url: equippedAvatarUrl || ''
            }));
        }
    } else {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        dispatch(setHasLogin(false));
        dispatch(setUser(null));
        dispatch(clearEquippedAvatar());
    }
}
