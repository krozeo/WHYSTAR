import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from 'antd';
import './quizzesChoose.css';

const QuizzesChoose = () => {
    const navigate = useNavigate();

    // 处理选择典籍方向
    const handleChoose = (direction) => {
        navigate(`/knowledge-quizzes?direction=${direction}`);
    };

    return (
        <div className="quizzes-choose-page-auth">
            <div className="quizzes-choose-auth-card">
                <div className="quizzes-choose-auth-left">
                    <div className="quizzes-choose-auth-logo">请选择题目方向：</div>
                    <img src="/Images/QuizzesPart.png" alt="题目方向" className="quizzes-choose-auth-avatar" />
                </div>
                <div className="quizzes-choose-auth-right">
                    <Button className="quizzes-choose-choose-button" onClick={() => handleChoose('mechanic')}>力学</Button>
                    <Button className="quizzes-choose-choose-button" onClick={() => handleChoose('optical')}>光学</Button>
                    <Button className="quizzes-choose-choose-button" onClick={() => handleChoose('magnetism')}>磁学</Button>
                    <Button className="quizzes-choose-choose-button" onClick={() => handleChoose('thermal')}>热学</Button>
                    <Button className="quizzes-choose-choose-button" onClick={() => handleChoose('acoustic')}>声学</Button>
                </div>
            </div>
        </div>
    )
};

export default QuizzesChoose;