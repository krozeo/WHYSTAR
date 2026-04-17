import { createSlice } from '@reduxjs/toolkit';
// AI辅助生成：DeepSeek-v 3.2, 2026-1-30
// 通过createSlice创建一个名为user的Slice
const userSlice = createSlice({
    name: 'user',
    initialState: {
        hasLogin: false,
        user: null,
        currentRank: 0,
        curPoints: 0,
        equippedAvatarId: null,
        equippedAvatarUrl: '',
    },
    reducers: {
        setCurrentRank: (state, action) => {
            state.currentRank = action.payload !== undefined ? action.payload : 0;
        },
        setCurPoints: (state, action) => {
            state.curPoints = action.payload !== undefined ? action.payload : 0;
        },
        setEquippedAvatar: (state, action) => {
            state.equippedAvatarId = action.payload?.id ?? null;
            state.equippedAvatarUrl = action.payload?.url || '';
        },
        setHasLogin: (state, action) => {
            state.hasLogin = action.payload !== undefined ? action.payload : false;
        },
        setUser: (state, { payload: val }) => {
            state.user = val;
        },
        clearUser: (state) => {
            state.user = null;
        },
        clearHasLogin: (state) => {
            state.hasLogin = false;
        },
        clearEquippedAvatar: (state) => {
            state.equippedAvatarId = null;
            state.equippedAvatarUrl = '';
        }
    },
})

// actions属性会包含我们定义的reducers方法
export const { setCurrentRank, setCurPoints, setEquippedAvatar, setHasLogin, setUser, clearUser, clearHasLogin, clearEquippedAvatar } = userSlice.actions;
export default userSlice.reducer;
