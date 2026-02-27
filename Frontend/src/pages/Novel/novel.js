import React, { useEffect, useRef, useState, useMemo, useCallback } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Col, Row, Typography, Select, Space, Button, Modal, Input, Tour, ConfigProvider } from 'antd';
import { useSelector } from 'react-redux';
import zhCN from 'antd/locale/zh_CN';
import CharacterCard from '../../component/CharacterCards/characterCard';
import { GetNovelInfo, GetStory, RestartNovelChat } from '../../api/apiInterface'
import NovelChatMemory from '../../component/NovelChatMemory/novelChatMemory';
import './novel.css';

const { Title } = Typography;

const ChapterTitle = {
    'mechanic': '筒车章',
    'optic': '叆叇章',
    'acoustic': '琴瑟章',
    'thermal': '温鼎章',
    'magnetism': '司南章',
}

const directionConfig = {
    'mechanic': '力学',
    'optical': '光学',
    'acoustic': '声学',
    'thermal': '热学',
    'magnetism': '磁学',
}


// 提取常量样式对象避免每次渲染重新创建
const middleColumnStyle = {
    backgroundColor: '#ffffff',
    height: '100vh',
    display: 'flex',
    flexDirection: 'column'
};

const dividerStyle = {
    height: '3px',
    backgroundColor: '#94C4FF'
};

const clickableCardStyle = {
    cursor: 'pointer',
    width: '100%'
};

const modalContentStyle = { padding: '20px' };

const selectStyle = { width: 220, marginTop: '20px' };

// Select 选项配置提取到组件外部避免重复创建
const selectOptions = [
    { value: 'mechanic', label: '当前典籍：力学' },
    { value: 'optical', label: '当前典籍：光学' },
    { value: 'acoustic', label: '当前典籍：声学' },
    { value: 'thermal', label: '当前典籍：热学' },
    { value: 'magnetism', label: '当前典籍：磁学' },
];

const Novel = () => {
    const Navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const direction = searchParams.get('direction');
    const user = useSelector(state => state.user.user);

    const exitBtnRef = useRef(null);
    const resetBtnRef = useRef(null);
    const gameBtnRef = useRef(null);
    const [tour, setTour] = useState(false);

    // 小说相关
    const [characterList, setcharacterList] = useState([]);
    const [storySummary, setstorySummary] = useState('');
    const [storyContent, setstoryContent] = useState('');
    const [modalopen, setModalOpen] = useState(false);
    const [refreshChat, setRefreshChat] = useState(0); // 用于触发对话记忆刷新
    const [inputValue, setInputValue] = useState(''); // 输入框内容
    const [isSending, setIsSending] = useState(false); // 发送状态

    // 使用 useMemo 缓存 steps 数组，避免每次渲染重新创建
    const steps = useMemo(() => [
        {
            title: '退出',
            description: '点击这里退出阅读小说内容',
            target: () => exitBtnRef.current,
        },
        {
            title: '常用功能',
            description: '重置阅读进度',
            target: () => resetBtnRef.current,
        },
        {
            title: '拓展体验',
            description: '进入同款互动游戏',
            target: () => gameBtnRef.current,
        }
    ], []);

    useEffect(() => {
        // 如果 direction 无效，提前返回避免不必要的 API 调用
        if (!direction || !directionConfig[direction]) {
            setcharacterList([]);
            setstorySummary('');
            setstoryContent('');
            return;
        }

        let isCancelled = false; // 用于取消已卸载组件的状态更新

        const fetchCharacterInfo = async () => {
            try {
                const [novelResult, storyResult] = await Promise.allSettled([
                    GetNovelInfo({ category: directionConfig[direction] }),
                    GetStory({ category: directionConfig[direction] })
                ]);

                if (isCancelled) return;

                let nextCharacterList = [];
                let nextStorySummary = '';
                let nextStoryContent = '';

                if (novelResult.status === 'fulfilled') {
                    const responseData = novelResult.value?.data?.data || novelResult.value?.data;
                    if (responseData) {
                        const characters = responseData.characters || [];
                        nextCharacterList = characters.map(char => ({
                            Name: char.name,
                            Introduction: char.intro
                        }));
                        nextStorySummary = responseData.story?.intro || '';
                        nextStoryContent = responseData.story?.content || '';
                    } else {
                        console.error('响应数据格式错误:', novelResult.value);
                    }
                } else {
                    console.error('获取小说角色信息失败:', novelResult.reason);
                }

                if (storyResult.status === 'fulfilled') {
                    const storyData = storyResult.value?.data?.data || storyResult.value?.data;
                    if (storyData) {
                        if (storyData.story_intro) {
                            nextStorySummary = storyData.story_intro;
                        }
                        if (storyData.story_content) {
                            nextStoryContent = storyData.story_content;
                        }
                    } else {
                        console.error('响应数据格式错误:', storyResult.value);
                    }
                } else {
                    console.error('获取小说剧情失败:', storyResult.reason);
                }

                setcharacterList(nextCharacterList);
                setstorySummary(nextStorySummary);
                setstoryContent(nextStoryContent);
            } catch (error) {
                // 如果组件已卸载，不更新状态
                if (isCancelled) return;
                console.error('获取小说角色信息失败:', error);
                setcharacterList([]);
                setstorySummary('');
                setstoryContent('');
            }
        }

        fetchCharacterInfo();

        // 清理函数：组件卸载时取消状态更新
        return () => {
            isCancelled = true;
        };
    }, [direction])

    // 使用 useCallback 缓存事件处理函数，避免子组件不必要的重新渲染
    const showModal = useCallback(() => {
        setModalOpen(true);
    }, []);

    const handleChange = useCallback((direction) => {
        Navigate(`/novel-reading?direction=${direction}`);
    }, [Navigate]);

    const handleCancel = useCallback(() => {
        setModalOpen(false);
    }, []);

    const handleExit = useCallback(() => {
        Navigate('/home');
    }, [Navigate]);

    const handleEnterGame = useCallback(() => {
        Navigate(`/ChapterGame?gameType=${direction}`);
    }, [Navigate, direction]);

    const handleTourOpen = useCallback(() => {
        setTour(true);
    }, []);

    const handleTourClose = useCallback(() => {
        setTour(false);
    }, []);

    const handleReset = useCallback(async () => {
        try {
            const response = await RestartNovelChat({
                user_id: user.id,
                category: directionConfig[direction]
            });

            if (response?.data?.code === 200) {
                // 重置成功后刷新对话记忆
                setRefreshChat({
                    type: 'reset',
                    timestamp: Date.now()
                });
            } else {
                console.error('重置对话失败:', response?.data?.message || '未知错误');
            }
        } catch (error) {
            console.error('重置对话异常:', error);
        }
    }, [user.id, direction]);

    const handleSend = useCallback(async () => {
        if (!inputValue.trim() || isSending) return;

        setIsSending(true);
        try {
            // 通过修改 refreshChat 触发 NovelChatMemory 组件内的发送逻辑
            // 这里我们传递一个对象，包含要发送的消息和时间戳，确保每次都能触发
            setRefreshChat({
                type: 'send',
                content: inputValue,
                timestamp: Date.now()
            });
            setInputValue(''); // 清空输入框
        } catch (error) {
            console.error('发送消息失败:', error);
        } finally {
            setIsSending(false);
        }
    }, [inputValue, isSending]);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <Row>
            <Col span={4} className="left-column novel-col">
                <Title level={5} strong className="novel-title">角色档案</Title>
                <div className="Character-Card-Container">
                    {characterList && characterList.map((item, index) => {
                        // 使用 name 作为 key，如果 name 唯一的话；否则使用组合 key
                        const key = item.Name ? `${item.Name}-${index}` : index;
                        return <CharacterCard
                            key={key}
                            characterName={item.Name}
                            characterInfo={item.Introduction}
                        />
                    })}
                </div>
            </Col>
            <Col span={16} className="middle-column" style={middleColumnStyle}>
                <div style={{ flexShrink: 1 }}>
                    <Row className="btn-Container">
                        <Space>
                            <Button type="primary" className="novel-begin-btn" onClick={handleTourOpen}>教学</Button>
                            <Button type="primary" className="novel-begin-btn" ref={exitBtnRef} onClick={handleExit}>退出</Button>
                            <Button type="primary" className="novel-top-btn" ref={resetBtnRef} onClick={handleReset}>重置</Button>
                        </Space>
                    </Row>
                </div>
                <div className="middle-content" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, overflow: 'hidden' }}>
                    <div style={dividerStyle} />
                    <NovelChatMemory
                        direction={direction}
                        directionConfig={directionConfig}
                        refreshTrigger={refreshChat}
                    />
                </div>
                <div style={{ flexShrink: 1 }}>
                    <Input
                        className="input-bottom novel-input"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="请输入对话内容..."
                        suffix={
                            <Button type="primary" size="small" onClick={handleSend} loading={isSending}
                                style={{
                                    backgroundColor: '#1890ff',
                                    borderColor: '#1890ff',
                                    borderRadius: '4px',
                                    fontWeight: 400
                                }}
                            >
                                发送
                            </Button>
                        }
                    />
                </div>
            </Col>
            <Col span={4} className="right-column novel-col">
                <Space wrap>
                    <Select
                        defaultValue={direction}
                        style={selectStyle}
                        onChange={handleChange}
                        options={selectOptions}
                    />
                </Space>
                <div className="Story-Container">
                    <div
                        onClick={showModal}
                        style={clickableCardStyle}
                    >
                        <CharacterCard
                            characterName="查看全文"
                            characterInfo={storySummary}
                        />
                    </div>
                    <Modal
                        title="全文阅读"
                        open={modalopen}
                        onCancel={handleCancel}
                        okText="确认"
                        cancelButtonProps={{ style: { display: 'none' } }}
                        footer={null}
                    >
                        <div style={modalContentStyle}>
                            <h3>{ChapterTitle[direction]}</h3>
                            <p className="story-content">{storyContent}</p>
                        </div>
                    </Modal>
                    <Button type="primary" className="novel-btn" ref={gameBtnRef} onClick={handleEnterGame}>点击进入游戏模式</Button>
                </div>
            </Col>
            <ConfigProvider locale={zhCN}>
                <Tour
                    open={tour}
                    onClose={handleTourClose}
                    steps={steps}
                />
            </ConfigProvider>
        </Row >
    )
}

export default Novel;
