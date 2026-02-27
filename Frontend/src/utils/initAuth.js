// 初始化认证状态 - 从 localStorage 恢复登录状态
import { setHasLogin, setUser } from '../store/reducers/user';

/**
 * 初始化用户认证状态
 * 从 localStorage 中读取 token 和 user 信息，如果存在则恢复 Redux 状态
 * @param {Function} dispatch - Redux dispatch 函数
 */
export const initAuth = (dispatch) => {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');

    if (token && userStr) {
        const user = JSON.parse(userStr);
        // 恢复登录状态
        dispatch(setHasLogin(true));
        dispatch(setUser(user));

    }
}
