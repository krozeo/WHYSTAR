import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Dropdown, Typography, Drawer, Button, Form, message, Space } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useSelector, useDispatch } from 'react-redux';
import { clearUser, clearHasLogin, setUser } from '../../store/reducers/user';
import { UpdateUsername, UpdatePassword, SetSecurityQuestion } from '../../api/apiInterface';
import ModalTemplate from '../ModalTemplate/modalTemplate';
import UserRanking from '../UserRankingItems/userRanking';
import './userInfoCard.css';

const { Title } = Typography;

const TitleStyle = {
    color: '#56a2ff',
    margin: '20px 0px',
    fontSize: '18px',
    fontWeight: 600,
}

const DividerStyle = {
    border: '1px solid rgb(0, 0, 0)',
    width: '100%',
    marginBottom: '0px'
}

const UserInfoCard = () => {

    const navigate = useNavigate();
    const dispatch = useDispatch();

    const items = [
        {
            label: (
                <a onClick={() => showAccountInformation()} target="_blank" rel="noopener noreferrer">
                    个人中心
                </a>
            ),
            key: '1',
        },
        {
            label: (
                <a onClick={() => logout()} target="_blank" rel="noopener noreferrer">
                    退出
                </a>
            ),
            key: '2',
        }
    ];

    const [openAccountInformation, setOpenAccountInformation] = useState(false);
    const [openRankingList, setOpenRankingList] = useState(false);
    const [openUpdateUsername, setOpenUpdateUsername] = useState(false);
    const [openUpdatePassword, setOpenUpdatePassword] = useState(false);
    const [openSetSecurityQuestion, setOpenSetSecurityQuestion] = useState(false);
    const [loading, setLoading] = useState(false);
    const [usernameForm] = Form.useForm();
    const [passwordForm] = Form.useForm();
    const [securityQuestionForm] = Form.useForm();
    const user = useSelector(state => state.user.user);
    const curPoints = useSelector(state => state.user.curPoints);
    const currentRank = useSelector(state => state.user.currentRank);

    const showAccountInformation = () => {
        setOpenAccountInformation(true);
    };

    const onClose = () => {
        setOpenAccountInformation(false);
    };

    const logout = () => {
        // 清除token和user信息
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        // 清除redux中的user和hasLogin信息
        dispatch(clearUser());
        dispatch(clearHasLogin());
        // 跳转至首页
        navigate('/home');
    }

    const showRankingList = () => {
        setOpenRankingList(true);
    };

    const onRankingListClose = () => {
        setOpenRankingList(false);
    };

    // 显示修改用户名模态框
    const showUpdateUsername = () => {
        setOpenUpdateUsername(true);
        usernameForm.setFieldsValue({ newUsername: user.username });
    };

    // 关闭修改用户名模态框
    const closeUpdateUsername = () => {
        setOpenUpdateUsername(false);
        usernameForm.resetFields();
    };

    // 显示修改密码模态框
    const showUpdatePassword = () => {
        setOpenUpdatePassword(true);
    };

    // 关闭修改密码模态框
    const closeUpdatePassword = () => {
        setOpenUpdatePassword(false);
        passwordForm.resetFields();
    };

    // 显示设置安全问题模态框
    const showSetSecurityQuestion = () => {
        setOpenSetSecurityQuestion(true);
    };

    // 关闭设置安全问题模态框
    const closeSetSecurityQuestion = () => {
        setOpenSetSecurityQuestion(false);
        securityQuestionForm.resetFields();
    };

    // 处理修改用户名
    const handleUpdateUsername = async () => {
        try {
            const values = await usernameForm.validateFields(); // 获取表单值
            setLoading(true);

            const response = await UpdateUsername({
                newUsername: values.newUsername
            });

            if (response && response.data && response.data.success) {
                message.success('用户名修改成功');
                // 更新Redux中的用户信息
                const updatedUser = { ...user, username: values.newUsername };
                dispatch(setUser(updatedUser));
                // 更新localStorage中的用户信息
                localStorage.setItem('user', JSON.stringify(updatedUser));
                closeUpdateUsername();
            } else {
                message.error(response?.data?.message || '用户名修改失败');
            }
        } catch (error) {
            if (error.errorFields) {
                // 表单验证错误
                return;
            }
            message.error('用户名修改失败，请稍后重试');
            console.error('修改用户名错误:', error);
        } finally {
            setLoading(false);
        }
    };

    // 处理修改密码
    const handleUpdatePassword = async () => {
        try {
            const values = await passwordForm.validateFields();
            setLoading(true);

            const response = await UpdatePassword({
                username: user.username,
                newPassword: values.newPassword
            });

            if (response && response.data && response.data.success) {
                message.success('密码修改成功');
                closeUpdatePassword();
            } else {
                message.error(response?.data?.message || '密码修改失败');
            }
        } catch (error) {
            if (error.errorFields) {
                // 表单验证错误
                return;
            }
            message.error('密码修改失败，请稍后重试');
            console.error('修改密码错误:', error);
        } finally {
            setLoading(false);
        }
    };

    // 处理设置安全问题
    const handleSetSecurityQuestion = async () => {
        try {
            const values = await securityQuestionForm.validateFields();
            setLoading(true);
            const response = await SetSecurityQuestion({
                username: user.username,
                question: values.question,
                answer: values.answer
            });
            if (response && response.data && response.data.success) {
                message.success('安全问题设置成功');
                closeSetSecurityQuestion();
            } else {
                message.error(response?.data?.message || '安全问题设置失败');
            }
        } catch (error) {
            if (error.errorFields) {
                // 表单验证错误
                return;
            }
            message.error('设置安全问题失败，请稍后重试');
            console.error('设置安全问题错误:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="nav-user-card">
            <Dropdown menu={{ items }} trigger={['click']}>
                <Title level={5} strong style={TitleStyle}> {user.username}</Title>
            </Dropdown>
            <Drawer title="个人中心" size={520} closable={false} onClose={onClose} open={openAccountInformation}>
                <div className="account-information-content">
                    <div>
                        <img src='/Images/User-Avatar.png' alt="user-avatar" className="IP-avatar" />
                    </div>
                    <hr style={DividerStyle} />
                    <div className="User-Basic-Information">
                        <Title level={5} strong > 用户名： {user.username} </Title>
                        <Button onClick={showUpdateUsername}>修改名称</Button>
                    </div>
                    <hr style={DividerStyle} />
                    <div className="User-Basic-Information">
                        <Title level={5} strong> 用户ID： {user.id} </Title>
                    </div>
                    <hr style={DividerStyle} />
                    <div className="User-Basic-Information">
                        <Title level={5} strong> 密码： ****** </Title>
                        <Space >
                            {/* <Button onClick={showUpdatePassword}>修改密码</Button>
                            <Button onClick={showSetSecurityQuestion}>设置安全问题</Button> */}
                        </Space>
                    </div>
                    <hr style={DividerStyle} />
                    <div className="User-Basic-Information">
                        <Title level={5} strong> 当前积分： {curPoints} </Title>
                        <Button type="primary">兑换</Button>
                    </div>
                    <hr style={DividerStyle} />
                    <div className="User-Basic-Information">
                        <Title level={5} strong> 答题排名： {currentRank || 0} </Title>
                        <Button type="primary" onClick={showRankingList}>查看排行榜</Button>
                    </div>
                    <hr style={DividerStyle} />
                </div>
                <Drawer title="排行榜" size={320} closable={false} onClose={onRankingListClose} open={openRankingList}>
                    <div className="Ranking-List-Content">
                        <div className="Person-Ranking-List">
                            <div className="Person-Ranking-Title">
                                <Title level={5} strong> {user.username} </Title>
                                <Title level={5} strong> 当前排名： {currentRank || 0} </Title>
                            </div>
                            <div>
                                <img src='/Images/RankListWinner.png' alt="winner-avatar" className="IP-avatar" />
                            </div>
                        </div>
                        <hr style={DividerStyle} />
                        <div className="user-ranking-list">
                            <UserRanking />
                        </div>
                    </div>
                </Drawer>
            </Drawer>

            {/* 修改用户名模态框 */}
            <ModalTemplate
                title="修改用户名"
                open={openUpdateUsername}
                onCancel={closeUpdateUsername}
                onOk={handleUpdateUsername}
                confirmLoading={loading}
                form={usernameForm}
                name="newUsername"
                label="新用户名"
                rules={[
                    { required: true, message: '请输入新用户名' },
                    { min: 2, message: '用户名长度至少2位' }
                ]}
                prefix={<UserOutlined />}
                placeholder=" 请输入新用户名"
                type={1}
            />

            {/* 修改密码模态框 */}
            {/* <ModalTemplate
                title="修改密码"
                open={openUpdatePassword}
                onCancel={closeUpdatePassword}
                onOk={handleUpdatePassword}
                confirmLoading={loading}
                form={passwordForm}
                name="newPassword"
                label="新密码"
                rules={[
                    { required: true, message: '请输入新密码' },
                    { min: 6, message: '密码长度至少6位' }
                ]}
                prefix={<LockOutlined />}
                placeholder="请输入新密码"
                type={1}
            /> */}

            {/* 设置安全问题模态框 */}
            {/* <ModalTemplate
                title="设置安全问题可帮助您找回密码"
                open={openSetSecurityQuestion}
                onCancel={closeSetSecurityQuestion}
                onOk={handleSetSecurityQuestion}
                confirmLoading={loading}
                form={securityQuestionForm}
                name="question"
                label="安全问题"
                rules={[
                    { required: true, message: '请输入安全问题' }
                ]}
                placeholder="请输入安全问题"
                type={2}
                childrenName="answer"
                childrenLabel="答案"
                childrenRules={[
                    { required: true, message: '请输入答案' }
                ]}
                childrenPlaceholder="请输入答案"
            /> */}
        </div>

    )
}

export default UserInfoCard;
