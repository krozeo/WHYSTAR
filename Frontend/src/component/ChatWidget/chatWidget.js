import React from "react";
import { Avatar, Button, Input } from 'antd';
import { MessageOutlined } from '@ant-design/icons';
import './chatWidget.css';

const ChatWidget = ({
    chatOpen,
    onOpen,
    onClose,
    messages,
    sending,
    inputValue,
    onInputChange,
    onKeyDown,
    onSend,
    messageListRef
}) => {
    return (
        <>
            <div className={`chat-panel ${chatOpen ? 'open' : ''}`}>
                <div className="chat-panel-header">
                    <div className="chat-panel-title">
                        <span className="chat-panel-title-text">仓小造</span>
                        <span className="chat-panel-subtitle">随时为你解答物理问题</span>
                    </div>
                    <button className="chat-panel-close" onClick={onClose}>×</button>
                </div>
                <div className="chat-panel-messages" ref={messageListRef}>
                    {messages.map((msg, index) => (
                        <div
                            key={`${msg.role}-${index}`}
                            className={`chat-row ${msg.role === 'user' ? 'chat-row-user' : 'chat-row-ai'}`}
                        >
                            {msg.role !== 'user' && (
                                <Avatar size={32} src="/Images/IP.png" />
                            )}
                            <div className="chat-bubble">
                                {msg.streaming && !msg.content ? (
                                    <span className="chat-typing">
                                        <span className="dot"></span>
                                        <span className="dot"></span>
                                        <span className="dot"></span>
                                    </span>
                                ) : (
                                    msg.content
                                )}
                            </div>
                            {msg.role === 'user' && (
                                <Avatar size={32} src="/Images/star.png" />
                            )}
                        </div>
                    ))}
                </div>
                <div className="chat-panel-input">
                    <Input
                        value={inputValue}
                        onChange={(event) => onInputChange(event.target.value)}
                        onKeyDown={onKeyDown}
                        placeholder="输入你的问题"
                        className="chat-input"
                    />
                    <Button type="primary" onClick={onSend} loading={sending} className="chat-send-button">
                        发送
                    </Button>
                </div>
            </div>
            <button className="chat-float-button" onClick={onOpen}>
                <MessageOutlined />
            </button>
        </>
    );
}

export default ChatWidget;
