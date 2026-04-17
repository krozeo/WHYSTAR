import { useEffect, useState, useRef } from 'react';
import { Skeleton } from 'antd';
import { SoundOutlined } from '@ant-design/icons';
import { GetChatMemory, RestartNovelChat, ProgressNovelChat, SynthesizeNovelSpeech } from '../../api/apiInterface';
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
    const [ttsLoadingKey, setTtsLoadingKey] = useState('');
    const scrollRef = useRef(null);
    const audioRef = useRef(null);
    const audioUrlRef = useRef(null);

    const stopAudio = () => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.src = '';
            audioRef.current = null;
        }
        if (audioUrlRef.current) {
            URL.revokeObjectURL(audioUrlRef.current);
            audioUrlRef.current = null;
        }
    };

    useEffect(() => {
        return () => {
            stopAudio();
        };
    }, []);

    const getBubblePlainText = (item) => {
        const formatted = formatMessageContent(item.content, item.role);
        if (formatted === null || formatted === undefined) return '';
        if (typeof formatted === 'string') return formatted.replace(/\s+/g, ' ').trim();
        return String(formatted).replace(/\s+/g, ' ').trim();
    };

    const speakBubble = async (item, bubbleKey) => {
        const text = getBubblePlainText(item);
        if (!text) return;

        try {
            stopAudio();
            setTtsLoadingKey(bubbleKey);
            const response = await SynthesizeNovelSpeech({
                text,
                user_id: user?.id || ''
            });
            const audioBlob = response?.data;
            if (!audioBlob) throw new Error('语音合成失败');

            const url = URL.createObjectURL(audioBlob);
            audioUrlRef.current = url;
            const audio = new Audio(url);
            audioRef.current = audio;
            audio.onended = () => {
                stopAudio();
            };
            await audio.play();
        } catch (e) {
            console.error('语音合成失败:', e);
            let errMsg = e?.message || '语音合成失败';
            if (e?.response?.data instanceof Blob) {
                try {
                    const errText = await e.response.data.text();
                    const errJson = JSON.parse(errText);
                    errMsg = errJson?.detail || errMsg;
                } catch (parseError) { }
            } else if (e?.response?.data?.detail) {
                errMsg = e.response.data.detail;
            }
            alert(errMsg);
        } finally {
            setTtsLoadingKey('');
        }
    };

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
            {(loading ? [{ role: 'other', content: '' }, { role: 'other', content: '' }] : chatMessages).map((item, index) => {
                const bubbleKey = `${item.role}-${index}`;
                const isTtsLoading = ttsLoadingKey === bubbleKey;
                return (
                <div
                    key={bubbleKey}
                    className={`chat-message ${loading ? 'chat-message-other' : (item.role === 'user' ? 'chat-message-user' : 'chat-message-other')}`}
                >
                    <Skeleton active loading={loading}>
                        <div className={`chat-bubble ${!loading && item.role !== 'user' ? 'chat-bubble-with-audio' : ''}`}>
                            {!loading && formatMessageContent(item.content, item.role)}
                            {!loading && item.role !== 'user' && (
                                <button
                                    type="button"
                                    className={`chat-audio-button ${isTtsLoading ? 'is-loading' : ''}`}
                                    aria-label={isTtsLoading ? '正在准备音频' : '播放语音'}
                                    title={isTtsLoading ? '正在准备音频，请稍候' : '播放语音'}
                                    onClick={() => speakBubble(item, bubbleKey)}
                                    disabled={isTtsLoading}
                                >
                                    <SoundOutlined />
                                </button>
                            )}
                        </div>
                    </Skeleton>
                </div>
                );
            })}
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
