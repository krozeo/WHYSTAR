import { createSlice, current } from '@reduxjs/toolkit';

// 通过createSlice创建一个名为user的Slice
const userSlice = createSlice({
    name: 'user',
    initialState: {
        hasLogin: false,
        user: null,
        currentRank: 0,
        curPoints: 0,
    },
    reducers: {
        setCurrentRank: (state, action) => {
            state.currentRank = action.payload !== undefined ? action.payload : 0;
        },
        setCurPoints: (state, action) => {
            state.curPoints = action.payload !== undefined ? action.payload : 0;
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
        }
    },
})

// actions属性会包含我们定义的reducers方法
export const { setCurrentRank, setCurPoints, setHasLogin, setUser, clearUser, clearHasLogin } = userSlice.actions;
export default userSlice.reducer;
