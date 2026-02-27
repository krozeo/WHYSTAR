import React from "react";
import { useNavigate } from "react-router-dom";
import { useSelector } from 'react-redux';
import { Col, Row, Typography, Button, message } from 'antd';
import './featureCard.css'

const { Title } = Typography;

const routerMap = {
    1: '/novel-choose',
    2: '/physics-experiment',
    3: '/quizzes-choose',
}

// 使用配置对象定义组件卡片
const FeatureCards = ({ order = 0, title, description, layout = 'imageRight', image = {} }) => {
    const curOrder = layout === 'imageRight' ? ['text', 'image'] : ['image', 'text'];
    const navigate = useNavigate();

    const hasLogin = useSelector(state => state.user.hasLogin);
    const handleEnter = () => {
        if (!hasLogin) {
            message.error('请先登录');
            return;
        }
        navigate(routerMap[order]);
    };

    return (
        <div className="cardContainer">
            <Row gutter={[48, 48]} align="middle">
                {curOrder.map((type, index) => (
                    <Col key={index} xs={24} lg={12}>
                        {type === 'text' ? (
                            <div className="text-Container">
                                <Title
                                    style={{
                                        color: '#000000',
                                        marginBottom: '16px'
                                    }}
                                >
                                    {title}
                                </Title>
                                <Title
                                    level={5}
                                    style={{
                                        color: '#737373',
                                        fontWeight: 'normal',
                                        lineHeight: '1.8'
                                    }}
                                >
                                    {description}
                                </Title>
                                <Button type="primary" onClick={handleEnter}>进入</Button>
                            </div>
                        ) : (<img
                            src={image?.src || '/Images/IP.png'}
                            alt={image?.alt || title || '功能图片'}
                            style={{
                                width: '100%',
                                maxWidth: '500px',
                                height: 'auto',
                                borderRadius: '50px',
                                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
                            }}
                        />
                        )}
                    </Col>
                ))}
            </Row>
        </div>
    )
}

export default FeatureCards;