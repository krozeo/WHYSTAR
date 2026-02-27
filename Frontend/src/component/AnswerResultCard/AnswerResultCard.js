import React from 'react';
import './AnswerResultCard.css';

const AnswerResultCard = ({ isCorrect, correctAnswer, explanation }) => {
    return (
        <div className={`answer-result-card ${isCorrect ? 'correct' : 'incorrect'}`}>
            <div className="result-status-text">
                {isCorrect ? '回答正确！' : '回答错误!'}
            </div>
            <div className="correct-answer-info">
                正确答案: {correctAnswer}
            </div>
            {explanation && (
                <div className="explanation-content">
                    {explanation}
                </div>
            )}
        </div>
    );
};

export default AnswerResultCard;
