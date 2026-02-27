import React from "react";
import { useNavigate } from "react-router-dom";
import { useSelector } from 'react-redux';
import { Flex, Layout, Typography, Button, Avatar } from 'antd';
import './home.css';
import FeatureCards from '../../component/FeatureCards/featureCard';
import UserInfoCard from '../../component/UserInfoCard/userInfoCard';

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
    // 导航处理
    const Navigate = useNavigate();
    // 使用解构赋值获取store中的状态
    const hasLogin = useSelector(state => state.user.hasLogin);
    // 处理登录
    const handleLogin = () => {
        Navigate('/login');
    }

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
                        <img src="/Images/IP.png" alt="IP图标" style={IpStyle} />
                        <Title level={5} strong style={{ margin: '0', padding: '0' }}>仓小造</Title>
                    </div>
                </Footer>
            </Layout>
        </Flex>
    )
}

export default Home;