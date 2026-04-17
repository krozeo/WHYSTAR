// 发起请求，完成接口调用
import Http from './axios';

/*-----登录界面-----*/
// 验证用户账户信息 
export const VerifyUserInformation = async ({ action, username, password, confirmPassword }) => {
    const isRegister = action === 'register';
    const config = {
        url: isRegister ? '/auth/register' : '/auth/login',
        method: 'post',
        data: {
            username,
            password,
            ...(isRegister && {
                password_confirm: confirmPassword || password,
                password_question: "用户默认问题",
                password_answer: "用户默认答案"
            })
        }
    };

    try {
        const response = await Http.request(config);

        // 构造统一成功响应
        return {
            data: {
                success: true,
                message: isRegister ? "注册成功" : "登录成功",
                data: isRegister ? response.data : {
                    token: response.data.access_token,
                    user: {
                        id: response.data.id,
                        username,
                    }
                }
            }
        };
    } catch (error) {
        console.error("API Error:", error);
        return {
            data: {
                success: false,
                message: error.response?.data?.detail || "请求失败"
            }
        };
    }
}

// 根据用户名获取数据库里用户设置的安全问题
export const GetSecurityQuestions = (username) => {
    return Http.request({
        url: '/auth/password-question',
        method: 'get',
        params: { username }
    })
}

// 根据用户名和安全问题答案验证数据库里用户设置的安全问题
// 后端目前没有直接对应的验证接口
export const VerifySecurityQuestions = (data) => {
    return Http.request({
        url: '/verifySecurityQuestions',
        method: 'post',
        data
    })
}

// 根据用户名和密码重置用户存储在数据库里的密码
export const UpdatePassword = (data) => {
    return Http.request({
        url: '/auth/change-password',
        method: 'post',
        data
    })
}

// （保留但无用）现在我已经将coze切换成智谱
export const CozeChat = (data) => {
    return Http.request({
        url: '/api/chat-memory/coze-chat',
        method: 'post',
        data
    })
}

export const ZhipuChat = (data) => {
    return Http.request({
        url: '/api/chat-memory/zhipu-chat',
        method: 'post',
        data
    })
}

/*-----账户信息界面-----*/
// 根据用户名和密码重置用户存储在数据库里的用户名
export const UpdateUsername = async (data) => {
    try {
        const response = await Http.request({
            url: '/auth/change-username',
            method: 'post',
            data: {
                new_username: data.newUsername
            }
        });
        if (response && response.data) {
            return {
                data: {
                    success: true,
                    message: '用户名修改成功',
                    data: response.data
                }
            };
        }
        return {
            data: {
                success: false,
                message: '用户名修改失败'
            }
        };
    } catch (error) {
        console.error('修改用户名错误:', error);
        return {
            data: {
                success: false,
                message: error.response?.data?.detail || '用户名修改失败，请稍后重试'
            }
        };
    }
}

// 设置安全问题
export const SetSecurityQuestion = (data) => {
    return Http.request({
        url: '/setSecurityQuestion',
        method: 'post',
        data
    })
}

// 获取用户排行榜
export const GetUserRanking = () => {
    return Http.request({
        baseURL: '',
        url: '/user/api/leaderboard',
        method: 'get'
    })
}

/*-----题目相关-----*/

// 获取题目相关数据
export const GetQuizzesData = async (Category) => {
    try {
        const response = await Http.request({
            baseURL: '',
            url: `/question/api/start/${Category}`,
            method: 'get',
        });

        if (response && response.data) {
            // 检查返回的数据结构
            if (response.data.questions && Array.isArray(response.data.questions)) {
                return {
                    data: response.data.questions
                };
            }
            return {
                data: response.data
            };
        }
        return {
            data: []
        };
    } catch (error) {
        console.error('获取题目数据错误:', error);
        throw error;
    }
}

// 提交答案
export const SubmitAnswer = (data) => {
    return Http.request({
        baseURL: '',
        url: '/question/api/submit',
        method: 'post',
        data
    })
}

// 切换至下一题
export const GetNextQuestion = (current_id, category_id) => {
    return Http.request({
        baseURL: '',
        url: `/question/api/next/${current_id}/${category_id}`,
        method: 'get',
    })
}

// 更新用户积分
export const UpdateUserPoints = (data) => {
    return Http.request({
        baseURL: '',
        url: '/user/api/points/add',
        method: 'post',
        params: data
    })
}

/*-----小说相关-----*/
// 获取小说数据
export const GetNovelInfo = (params) => {
    return Http.request({
        url: '/api/story-character/get-story-character',
        method: 'get',
        params: { category: params.category }
    })
}

export const GetStory = (params) => {
    return Http.request({
        url: '/api/story-character/get-story',
        method: 'get',
        params: { category: params.category }
    })
}

// 查询小说对话记忆
export const GetChatMemory = (params) => {
    return Http.request({
        url: '/api/chat-memory/get',
        method: 'get',
        params: { user_id: params.user_id, category: params.category }
    })
}

// 进入小说交互剧情
export const RestartNovelChat = (data) => {
    return Http.request({
        url: '/api/chat-memory/restart',
        method: 'post',
        data
    })
}

// 推进小说剧情
export const ProgressNovelChat = (data) => {
    return Http.request({
        url: '/api/chat-memory/append',
        method: 'post',
        data
    })
}

// 小说语音合成
export const SynthesizeNovelSpeech = (data) => {
    return Http.request({
        url: '/api/chat-memory/tts',
        method: 'post',
        data,
        responseType: 'blob'
    })
}
/*-----实验相关-----*/
// 获取该实验方向下的所有实验标题
export const GetExperimentTitle = (params) => {
    return Http.request({
        url: '/experiment/api/titles',
        method: 'get',
        params: { category: params.category }
    })
}
// 获取具体实验内容
export const GetExperimentContent = (params) => {
    return Http.request({
        url: '/experiment/api/content-path',
        method: 'get',
        params: { category: params.category, title: params.title }
    })
}
