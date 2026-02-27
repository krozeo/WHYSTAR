import { useNavigate } from 'react-router-dom';
import { useState } from 'react';
import './experiment.css';
import UserInfoCard from '../../component/UserInfoCard/userInfoCard';
import { Typography, Button, Modal} from 'antd';
import { GetExperimentTitle, GetExperimentContent } from '../../api/apiInterface';

const { Title } = Typography;

const TitleStyle = {
    color: '#56a2ff',
    margin: '0',
    fontSize: '18px',
    fontWeight: 600,
}

const experimentConfig = {
    'mechanic': '力学',
    'optical': '光学',
    'magnetism': '电磁学',
    'thermal': '热学',
    'acoustic': '声学'
}

const Experiment = () => {
    const Navigate = useNavigate();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [experimentList, setExperimentList] = useState([]);
    const [currentCategory, setCurrentCategory] = useState('');

    const handleRouter = (direction) => {
        const experimentCategory = experimentConfig[direction];
        setCurrentCategory(experimentCategory);
        
        const fetchExperimentInfo = async () => {
            try {
                // 获取该类别下的所有实验标题
                const res = await GetExperimentTitle({
                    category: experimentCategory
                });
                if (res.data && res.data.data.length > 0) {
                    setExperimentList(res.data.data);
                    setIsModalOpen(true);
                } else {
                    console.warn('No experiment titles found in response data');
                }
            } catch (error) {
                console.error('获取实验标题失败:', error);
            }
        }
        if (experimentCategory) {
            fetchExperimentInfo();
        } else {
            console.error('Experiment category is undefined. Direction:', direction);
        }
    }

    const handleExperimentClick = async (title) => {
        try {
            const contentRes = await GetExperimentContent({
                category: currentCategory,
                title: title
            });
            // 存在可跳转路径
            if (contentRes.data) {
                const relativeUrl = contentRes.data.data.content_url;
                const backendUrl = 'http://127.0.0.1:8000'; // 定义基础url
                const absoluteUrl = `${backendUrl}${relativeUrl.replace('/experiments-static', '/static/experiments')}`;
                window.location.href = absoluteUrl; //跳转到绝对路径
            }
        } catch (error) {
            console.error('获取实验内容失败:', error);
        }
    }

    const handleBack = () => {
        Navigate('/home');
    }

    return (
        <div className="page-list">
            <div className="nav-bar">
                <div className="nav-bar-left">
                    <Button onClick={handleBack}>返回</Button>
                    <Title level={5} strong style={TitleStyle}>为什么星球</Title>
                </div>
                <UserInfoCard />
            </div>
            <div className="main-content">
                <Title level={2}>请选择想要进行的物理实验：</Title>
                <Title level={5} style={{ color: '#b4b4b4' }}>通过实验亲自得出物理规律</Title>

                <div className="experiment-grid">
                    <div className="card card-1" onClick={() => handleRouter('mechanic')}>
                        <span className="card-pattern pattern-bl">
                            <i></i><i></i><i></i><i></i>
                        </span>
                    </div>
                    <div className="card card-2" onClick={() => handleRouter('optical')}>
                        <span className="card-pattern pattern-tl">
                            <i></i><i></i><i></i><i></i><i></i>
                        </span>
                    </div>
                    <div className="card card-3" onClick={() => handleRouter('magnetism')}>
                        <span className="card-pattern pattern-rc">
                            <i></i><i></i><i></i><i></i><i></i>
                        </span>
                    </div>
                    <div className="card card-4" onClick={() => handleRouter('thermal')}>
                        <span className="card-pattern pattern-tr">
                            <i></i><i></i><i></i><i></i><i></i>
                        </span>
                    </div>
                    <div className="card card-5" onClick={() => handleRouter('acoustic')}>
                        <span className="card-pattern pattern-bl">
                            <i></i><i></i><i></i><i></i><i></i>
                        </span>
                    </div>
                </div>
            </div>

            <Modal
                title={null}
                open={isModalOpen}
                onCancel={() => setIsModalOpen(false)}
                footer={null}
                destroyOnClose
                width={800}
                className="experiment-modal"
                centered
            >
                <div className="modal-header">
                    <div className="modal-title-text">选择{currentCategory}实验</div>
                </div>
                <div className="experiment-modal-grid">
                    {experimentList.map((item, index) => (
                        <div 
                            key={index} 
                            className="experiment-modal-card"
                            onClick={() => handleExperimentClick(item)}
                        >
                            <div className="experiment-name">{item}</div>
                        </div>
                    ))}
                </div>
            </Modal>
        </div>

    )
}

export default Experiment;
