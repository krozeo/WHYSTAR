import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useSelector } from 'react-redux';
import { Flex, Layout, Typography, Button } from 'antd';
import './home.css';
import FeatureCards from '../../component/FeatureCards/featureCard';
import UserInfoCard from '../../component/UserInfoCard/userInfoCard';
import ChatWidget from '../../component/ChatWidget/chatWidget';

const { Title } = Typography;
const { Header, Footer, Content } = Layout;

const TitleStyle = {
    color: '#56a2ff',
    margin: '20px 0px',
    fontSize: '18px',
    fontWeight: 600,
}

const IpStyle = {
    width: '120px',
    height: 'auto',
    margin: '0',
    padding: '0'
}

const Home = () => {
    const Navigate = useNavigate();
    const hasLogin = useSelector(state => state.user.hasLogin);
    const user = useSelector(state => state.user.user);
    const equippedAvatarUrl = useSelector(state => state.user.equippedAvatarUrl);
    const footerAvatar = equippedAvatarUrl || localStorage.getItem('equippedAvatarUrl') || '/Images/IP.png';
    const [chatOpen, setChatOpen] = useState(false);
    const [chatMessages, setChatMessages] = useState([
        {
            role: 'assistant',
            content: '小朋友们好，我是仓小造！一只爱鼓捣的小仓鼠🐹！我口袋里装工具，脑子里装问号，有点小迷糊，但最不怕失败！有啥物理问题尽管问我，让我想想办法！'
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [sending, setSending] = useState(false);
    const [conversationId, setConversationId] = useState(null);
    const messageListRef = useRef(null);

    const handleLogin = () => {
        Navigate('/login');
    }

    useEffect(() => {
        if (messageListRef.current) {
            messageListRef.current.scrollTop = messageListRef.current.scrollHeight;
        }
    }, [chatMessages, chatOpen, sending]);

    const appendAssistantDelta = (assistantMessageId, delta) => {
        setChatMessages(prev => prev.map(m => {
            if (m.id !== assistantMessageId) return m;
            return { ...m, content: `${m.content || ''}${delta}` };
        }));
    };

    const markAssistantDone = (assistantMessageId) => {
        setChatMessages(prev => prev.map(m => {
            if (m.id !== assistantMessageId) return m;
            if (!m.streaming) return m;
            const { streaming, ...rest } = m;
            return rest;
        }));
    };

    const handleSend = async () => {
        const trimmed = inputValue.trim();
        if (!trimmed || sending) return;
        const userMsg = { role: 'user', content: trimmed };
        const requestHistory = [...chatMessages, userMsg]
            .filter(m => m && m.role && typeof m.content === 'string' && m.content.trim() && !m.streaming)
            .map(m => ({ role: m.role, content: m.content }));
        setChatMessages(prev => [...prev, userMsg]);
        setInputValue('');
        setSending(true);
        try {
            const assistantMessageId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
            setChatMessages(prev => [...prev, { id: assistantMessageId, role: 'assistant', content: '', streaming: true }]);

            const resp = await fetch('/api/chat-memory/zhipu-chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'text/event-stream'
                },
                body: JSON.stringify({
                    user_id: user?.id ? String(user.id) : 'guest',
                    message: trimmed,
                    conversation_id: conversationId,
                    stream: true,
                    history: requestHistory.slice(-20)
                })
            });

            if (!resp.ok) {
                const text = await resp.text();
                throw new Error(text || `HTTP ${resp.status}`);
            }
            if (!resp.body) {
                throw new Error('浏览器不支持流式响应');
            }

            const reader = resp.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                buffer += decoder.decode(value, { stream: true });

                const parts = buffer.split('\n\n');
                buffer = parts.pop() || '';

                for (const part of parts) {
                    const lines = part.split('\n').map(l => l.trim()).filter(Boolean);
                    for (const line of lines) {
                        if (!line.startsWith('data:')) continue;
                        const payload = line.slice(5).trim();
                        if (!payload) continue;
                        if (payload === '[DONE]') continue;

                        let evt;
                        try {
                            evt = JSON.parse(payload);
                        } catch (e) {
                            continue;
                        }

                        const nextConversationId = evt?.conversation_id;
                        if (nextConversationId) setConversationId(nextConversationId);

                        if (evt?.delta) {
                            appendAssistantDelta(assistantMessageId, evt.delta);
                        }
                        if (evt?.done) {
                            markAssistantDone(assistantMessageId);
                        }
                    }
                }
            }

            markAssistantDone(assistantMessageId);
        } catch (error) {
            const detail = error?.response?.data?.detail || error?.message;
            setChatMessages(prev => [
                ...prev,
                { role: 'assistant', content: detail ? `对话失败：${detail}` : '对话失败，请稍后再试' }
            ]);
        } finally {
            setSending(false);
        }
    };

    const handleKeyDown = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSend();
        }
    };

    return (
        <Flex gap="middle" wrap>
            <Layout className="layout">
                <Header className="header">
                    <div className="top-container">
                        <Title
                            level={5}
                            strong style={TitleStyle}>
                            为什么星球
                        </Title>
                        {hasLogin ?
                            <UserInfoCard /> :
                            <Button onClick={handleLogin} type="primary" style={{ margin: '20px' }}>登录</Button>}
                        {/* <Avatar style={{margin:'20px'}} size={36} src={require("../../assets/Avatar.jpg")} /> */}
                    </div>
                    <div className="middle-container">
                        <Title className="main-title">专门为小学生打造的物理兴趣平台</Title>
                        <Title level={5} className="sub-title">在这里，看不见的力会变成有趣的故事，神奇的光影藏着秘密等你发现！
                            你可以动手"玩转"有趣的科学现象，在故事里破解物理谜题，还能进行智慧大闯关</Title>
                    </div>
                </Header>
                <Content className="content">
                    <FeatureCards
                        order="1"
                        title="物理奇遇记"
                        description="翻开它，就像翻开一本古代的《格林童话》，只是这里的魔法，都叫做“物理”"
                        image={{
                            src: "/Images/Novel.jpeg",
                            alt: "Novel"
                        }}
                    />
                    <FeatureCards
                        order="2"
                        title="物理游乐场"
                        description="用“好玩”的方式，打开严肃的物理法则。每一次实验，都是一次神奇的游玩"
                        image={{
                            src: "/Images/Experiment.jpeg",
                            alt: "Experiment"
                        }}
                        layout="imageLeft"
                    />
                    <FeatureCards
                        order="3"
                        title="物理猜猜看"
                        description="快来喂饱这只“物理小怪兽”！每答对一题，它就吃下一颗积分星星，陪你一起长大变聪明"
                        image={{
                            src: "/Images/Quizzes.jpg",
                            alt: "Quizzes"
                        }}
                    />
                </Content>
                <Footer className="footer">
                    <div className="footer-container">
                        <img src={footerAvatar} alt="IP图标" style={IpStyle} />
                        <Title level={5} strong style={{ margin: '0', padding: '0' }}>仓小造</Title>
                    </div>
                </Footer>
            </Layout>
            <ChatWidget
                chatOpen={chatOpen}
                onOpen={() => setChatOpen(true)}
                onClose={() => setChatOpen(false)}
                messages={chatMessages}
                sending={sending}
                inputValue={inputValue}
                onInputChange={setInputValue}
                onKeyDown={handleKeyDown}
                onSend={handleSend}
                messageListRef={messageListRef}
            />
        </Flex>
    )
}

export default Home;
