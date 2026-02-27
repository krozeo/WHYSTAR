import { useEffect, useState, useRef } from 'react';
import { Skeleton } from 'antd';
import { GetChatMemory, RestartNovelChat, ProgressNovelChat } from '../../api/apiInterface';
import { useSelector } from 'react-redux';
import './novelChatMemory.css';

const formatMessageContent = (content, role) => {
    if (role === 'user' || typeof content !== 'string') return content;

    let formatted = content.replace(/\s*(【.*?】)\s*/g, '\n\n$1');
    formatted = formatted.replace(/([A-D][.、．])/g, '\n$1');
    return formatted.trim();
};

const NovelChatMemory = ({ direction, directionConfig, refreshTrigger }) => {
    const user = useSelector(state => state.user.user);
    const [chatMessages, setChatMessages] = useState([]);
    const [loading, setLoading] = useState(false);
    const [appending, setAppending] = useState(false);
    const scrollRef = useRef(null);

    // 滚动到底部
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [chatMessages, loading, appending]);

    useEffect(() => {
        if (!direction || !directionConfig[direction] || !user?.id) {
            setChatMessages([]);
            return;
        }

        let isCancelled = false; // 取消标志位

        const handleRestart = async () => {
            setLoading(true);
            try {
                const restartResponse = await RestartNovelChat({
                    user_id: user.id,
                    category: directionConfig[direction]
                });

                if (isCancelled) return;
                console.log('重启对话响应:', restartResponse);

                if (restartResponse?.data?.code === 200) {
                    const displayChat = restartResponse?.data?.data?.display_chat || [];
                    setChatMessages(Array.isArray(displayChat) ? displayChat : []);
                } else {
                    console.error('重启对话失败:', restartResponse?.data?.message || '未知错误');
                    setChatMessages([]);
                }
            } catch (restartError) {
                if (isCancelled) return;
                console.error('重启对话异常:', restartError);
                setChatMessages([]);
            } finally {
                if (!isCancelled) {
                    setLoading(false);
                }
            }
        };

        const handleAppend = async (content) => {
            if (appending) return;
            setAppending(true);

            // 先显示用户发送的消息
            const tempUserMsg = { role: 'user', content: content };
            setChatMessages(prev => [...prev, tempUserMsg]);

            try {
                const response = await ProgressNovelChat({
                    user_id: user.id,
                    category: directionConfig[direction],
                    user_msg: content
                });

                if (isCancelled) return;

                if (response?.data?.code === 200) {
                    const displayChat = response?.data?.data?.display_chat || [];
                    if (Array.isArray(displayChat)) {
                        setChatMessages(displayChat);
                    }
                } else {
                    console.error('发送消息失败:', response?.data?.message || '未知错误');
                    setChatMessages(prev => prev.filter(msg => msg !== tempUserMsg));
                }
            } catch (error) {
                if (isCancelled) return;
                console.error('发送消息异常:', error);
                setChatMessages(prev => prev.filter(msg => msg !== tempUserMsg));
            } finally {
                if (!isCancelled) {
                    setAppending(false);
                }
            }
        };

        const fetchChatMemory = async () => {
            setLoading(true);
            try {
                const response = await GetChatMemory({
                    user_id: user.id,
                    category: directionConfig[direction]
                });
                if (isCancelled) return; // 如果组件已卸载，提前退出

                let displayChat = response?.data?.data?.display_chat || [];

                // 如果对话记忆为空，尝试重新开始对话
                if (displayChat.length === 0) {
                    await handleRestart();
                    return;
                }

                if (!isCancelled) {
                    setChatMessages(Array.isArray(displayChat) ? displayChat : []);
                    setLoading(false);
                }
            } catch (error) {
                if (isCancelled) return; // 如果组件已卸载，提前退出

                if (error.response && error.response.status === 404) {
                    await handleRestart();
                    return;
                }
                console.error('获取对话记忆失败:', error);
                setChatMessages([]);
                setLoading(false);
            }
        };

        // 根据 refreshTrigger 的类型执行不同操作
        if (refreshTrigger && typeof refreshTrigger === 'object' && refreshTrigger.type === 'send') {
            handleAppend(refreshTrigger.content);
        } else {
            // 初始化或普通加载
            fetchChatMemory();
        }

        return () => {
            isCancelled = true;
        };
    }, [direction, user?.id, directionConfig, refreshTrigger]);

    return (
        <div className="chat-message-list" ref={scrollRef}>
            {(loading ? [{ role: 'other', content: '' }, { role: 'other', content: '' }] : chatMessages).map((item, index) => (
                <div
                    key={`${item.role}-${index}`}
                    className={`chat-message ${loading ? 'chat-message-other' : (item.role === 'user' ? 'chat-message-user' : 'chat-message-other')}`}
                >
                    <Skeleton active loading={loading}>
                        <div className="chat-bubble">
                            {!loading && formatMessageContent(item.content, item.role)}
                        </div>
                    </Skeleton>
                </div>
            ))}
            {appending && (
                 <div className="chat-message chat-message-other">
                    <div className="chat-bubble" style={{ width: '70%' }}>
                        <Skeleton active paragraph={{ rows: 3 }} title={false} />
                    </div>
                 </div>
            )}
        </div>
    );
};

export default NovelChatMemory;
