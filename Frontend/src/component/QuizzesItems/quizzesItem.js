import React, { useState } from "react";
import { Radio, Typography, Space } from 'antd';
import './quizzesItem.css';

const { Title } = Typography;

const QuizzesCard = ({ Question, Choices, value, onChange }) => {
    const handleChange = (e) => {
        if (onChange) {
            onChange(e.target.value);
        }
    };

    return (
        <div className="quizzes-card-wrapper">
            <div className="question-section">
                <Title level={4} className="question-title">{Question}</Title>
            </div>
            <div className="options-container">
                <Radio.Group 
                    onChange={handleChange} 
                    value={value} 
                    className="custom-radio-group"
                >
                    <Space orientation="vertical" size="middle" style={{ width: '100%' }}>
                        {Choices.map((choice, index) => {
                            const letter = String.fromCharCode(65 + index);
                            const isSelected = value === letter;
                            return (
                                <Radio 
                                    key={letter} 
                                    value={letter} 
                                    className={`custom-radio-item ${isSelected ? 'selected' : ''}`}
                                >
                                    <div className="option-content">
                                        <span className="option-letter">{letter}.</span>
                                        <span className="option-text">{choice}</span>
                                    </div>
                                </Radio>
                            );
                        })}
                    </Space>
                </Radio.Group>
            </div>
        </div>
    );
};

export default QuizzesCard;