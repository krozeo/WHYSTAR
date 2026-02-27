import React, { useState, useEffect, useMemo } from "react";
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button, Row, Col, Typography, Modal, Space, Skeleton, message } from 'antd';
import './quizzes.css';
import QuizzesCard from '../../component/QuizzesItems/quizzesItem';
import AnswerResultCard from '../../component/AnswerResultCard/AnswerResultCard';
import { GetQuizzesData, SubmitAnswer, GetNextQuestion, UpdateUserPoints } from '../../api/apiInterface';
import { setCurPoints } from '../../store/reducers/user';

const { Title } = Typography;


const buttonStyle = {
    color: '#ffffff',
    backgroundColor: '#2A8AFF',
    border: '1px solid #2783f2',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 400,
    height: '40px',
    padding: '0 30px'
};

const exitbuttonStyle = {
    color: '#000000',
    backgroundColor: '#ffffff',
    border: '1px solid #000000',
    borderRadius: '8px',
    fontSize: '16px',
    fontWeight: 400,
    height: '40px',
    padding: '0 30px'
}

const directionConfig = {
    'mechanic': 'mechanics',
    'optical': 'optics',
    'acoustic': 'acoustics',
    'thermal': 'thermodynamics',
    'magnetism': 'electromagnetism',
}

const Quizzes = () => {
    const Navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const direction = searchParams.get('direction');

    const dispatch = useDispatch();
    const curPoints = useSelector(state => state.user.curPoints);
    const user = useSelector(state => state.user.user);

    // 题目数据
    const [quizzesData, setQuizzesData] = useState({});
    const [question, setQuestion] = useState('');
    const [options, setOptions] = useState([]);
    const [questionId, setQuestionId] = useState(null);
    const [explanation, setExplanation] = useState('');
    const [correctAnswer, setCorrectAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    // 检查是否正确
    const [isCorrect, setIsCorrect] = useState(false);
    // 选择题选项
    const [selectedValue, setSelectedValue] = useState(null);
    const [score, setScore] = useState(0);
    // 题目解析弹窗确认
    const [modalOpen, setModalOpen] = useState(false);
    const [confirmLoading, setConfirmLoading] = useState(false);
    const [resultLoading, setResultLoading] = useState(false);

    // 使用useEffect监听题目数据变化
    useEffect(() => {
        // 如果没有选择方向，跳转回选择页面
        if (!direction || !directionConfig[direction]) {
            message.error('请先选择题目方向');
            Navigate('/quizzes-choose');
            return;
        }

        const fetchData = async () => {
            setLoading(true);
            try {
                const response = await GetQuizzesData(directionConfig[direction]);
                const data = response?.data || response;
                setQuizzesData(data);
            } catch (error) {
                console.error('获取题目数据失败:', error);
                setQuizzesData({});
                // 如果是401错误，axios拦截器会处理跳转，这里不需要额外处理
                // 如果是其他错误，提示用户
                if (error.response?.status !== 401) {
                    message.error('获取题目失败，请稍后重试');
                }
            } finally {
                setLoading(false);
            }
        };
        
        fetchData();
    }, [direction, Navigate]);

    // 监听题目数据变化，更新题目信息
    useEffect(() => {
        if (quizzesData && Object.keys(quizzesData).length > 0) {
            // 获取 question 对象
            const questionObj = quizzesData.question || quizzesData.data;

            if (questionObj) {
                const qText = questionObj.question_text;
                setQuestion(qText);
                // 处理选项
                let optionsArray = [];
                setQuestionId(questionObj.question_id);
                if (questionObj.options && typeof questionObj.options === 'object' && !Array.isArray(questionObj.options)) {
                    optionsArray = Object.keys(questionObj.options)
                        .sort()
                        .map(key => questionObj.options[key]);
                } else if (Array.isArray(questionObj.options)) {
                    optionsArray = questionObj.options;
                }
                setOptions(optionsArray);
            }
        }
    }, [quizzesData]);

    //处理方法
    // 展示结果
    const showModal = () => {
        if (!selectedValue) {
            return; // 如果没有选择答案，不显示弹窗
        }
        setModalOpen(true);
        setResultLoading(true);

        // 检查答案是否正确
        const fetchAnswer = async () => {
            try {
                const response = await SubmitAnswer({
                    question_id: questionId,
                    user_answer: selectedValue
                });
                const data = response?.data || response;
                const correct = data.is_correct;
                setCorrectAnswer(data.correct_answer);
                if (correct) {
                    setScore(score + 1); // 正确加1分
                } 
                setIsCorrect(data.is_correct);
                setExplanation(data.explanation);
            } catch (error) {
                console.error('提交答案失败:', error);
                setIsCorrect(false);
                setExplanation('提交答案失败');
            } finally {
                setResultLoading(false);
            }
        };
        fetchAnswer();
    };
    const handleOk = () => {
        setConfirmLoading(true);
        setTimeout(() => {
            setModalOpen(false); // 关闭弹窗
            setConfirmLoading(false); // 关闭加载状态
            setSelectedValue(null); // 清空选择题选项
            // 切换至下一题
            const fetchNextQuestion = async () => {
                setLoading(true);
                try {
                    const response = await GetNextQuestion(questionId, directionConfig[direction]);
                    const data = response?.data || response;
                    setQuizzesData(data);
                } catch (error) {
                    console.error('获取下一题失败:', error);
                } finally {
                    setLoading(false);
                }
            };
            fetchNextQuestion();
        }, 500);
    };
    const handleCancel = () => {
        setModalOpen(false); // 关闭弹窗
    };
    const handleExit = async () => {
        if (score > 0 && user && user.id) {
            try {
                // 更新后端数据库积分
                await UpdateUserPoints({
                    user_id: user.id,
                    points: score
                });
                // 更新前端 Redux 状态，使得个人中心积分同步显示
                dispatch(setCurPoints(curPoints + score));
            } catch (error) {
                console.error('更新积分失败:', error);
            }
        }
        Navigate('/home'); // 退出到首页
    }

    return (
        <div className="quizzes-page">
            <Row className="top-Container" align="middle">
                <Col>
                    <Title level={5} className="score-text">
                        当前累计得分: {score}
                    </Title>
                </Col>
            </Row>

            <div className="quizzes-Container">
                {loading ? (
                    <Skeleton active />
                ) : (
                    <QuizzesCard
                        Question={question}
                        Choices={options}
                        value={selectedValue}
                        onChange={setSelectedValue}
                    />
                )}
                <div className="confirm-button-wrapper">
                    <Space>
                        <Button
                            type="primary"
                            onClick={showModal}
                            style={buttonStyle}
                            disabled={!selectedValue}
                        >
                            确认
                        </Button>
                        <Button
                            type="primary"
                            style={exitbuttonStyle}
                            onClick={handleExit}
                        >
                            退出
                        </Button>
                    </Space>
                    <Modal
                        open={modalOpen}
                        onOk={handleOk}
                        confirmLoading={confirmLoading}
                        onCancel={handleCancel}
                        okText="下一题"
                        cancelText="取消"
                        width={500}
                        className={`answer-modal ${resultLoading ? '' : (isCorrect ? 'correct-modal' : 'incorrect-modal')}`}>
                        {resultLoading ? (
                            <Skeleton active paragraph={{ rows: 4 }} />
                        ) : (
                            <AnswerResultCard
                                isCorrect={isCorrect}
                                correctAnswer={correctAnswer || ''}
                                explanation={explanation}
                            />
                        )}
                    </Modal>
                </div>
            </div>
        </div>
    )
}

export default Quizzes;
