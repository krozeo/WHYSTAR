import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from 'antd';
import './novelChoose.css';

const NovelChoose = () => {
    const navigate = useNavigate();

    // 处理选择典籍方向
    const handleChoose = (direction) => {
        navigate(`/novel-reading?direction=${direction}`);
    };

    return (
        <div className="novel-choose-page-auth">
            <div className="novel-choose-auth-card">
                <div className="novel-choose-auth-left">
                    <div className="novel-choose-auth-logo">请选择典籍方向：</div>
                    <img src="/Images/ReadingPart.png" alt="阅读方向" className="novel-choose-auth-avatar" />
                </div>
                <div className="novel-choose-auth-right">
                    <Button className="choose-button" onClick={() => handleChoose('mechanic')}>力学</Button>
                    <Button className="choose-button" onClick={() => handleChoose('optical')}>光学</Button>
                    <Button className="choose-button" onClick={() => handleChoose('magnetism')}>磁学</Button>
                    <Button className="choose-button" onClick={() => handleChoose('thermal')}>热学</Button>
                    <Button className="choose-button" onClick={() => handleChoose('acoustic')}>声学</Button>
                </div>
            </div>
        </div>
    )
};

export default NovelChoose;