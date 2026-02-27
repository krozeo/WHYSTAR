import { useState } from "react";
import { useDispatch } from 'react-redux';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { Typography, Input, Button, Form, message } from 'antd';
import { useNavigate } from 'react-router-dom';
import { setHasLogin, setUser } from '../../store/reducers/user';
import './login.css'
import { VerifyUserInformation } from "../../api/apiInterface";
import ForgotPasswordModal from '../../component/ForgotPasswordModal/ForgotPasswordModal';

const { Title } = Typography;

const Login = () => {

    // 使用useDispatch hook获取dispatch函数
    const dispatch = useDispatch();
    const [form] = Form.useForm(); // 表单实例，控制表单
    const navigate = useNavigate();
    const [isLogin, setIsLogin] = useState(true); // 判断是登录还是注册
    const [showForgotPassword, setShowForgotPassword] = useState(false); // 是否显示忘记密码
    const [loading, setLoading] = useState(false);

    // 处理登录/注册提交
    const handleSubmit = async (values) => {
        setLoading(true);
        const action = isLogin ? 'login' : 'register';

        try {
            const response = await VerifyUserInformation({
                username: values.username,
                password: values.password,
                action
            });

            const { success, message: msg, data } = response?.data || {};

            if (success) {
                message.success(msg);

                if (isLogin) {
                    // 处理登录成功逻辑
                    const { token, user, id } = data || {};
                    // 先清除旧数据
                    localStorage.removeItem('token');
                    localStorage.removeItem('user');
                    
                    if (token) localStorage.setItem('token', token);
                    if (user) localStorage.setItem('user', JSON.stringify(user));

                    dispatch(setHasLogin(true));
                    dispatch(setUser(user));
                    navigate('/home');
                } else {
                    // 处理注册成功逻辑
                    setIsLogin(true);
                    form.resetFields();
                }
            } else {
                // 处理业务逻辑失败
                message.error(msg);
            }
        } catch (error) {
            console.error(`${action} error:`, error);
            message.error("操作失败，请稍后重试");
        } finally {
            setLoading(false);
        }
    };

    // 切换登录/注册
    const handleSwitchMode = () => {
        setIsLogin(!isLogin);
        form.resetFields();
    };

    // 忘记密码成功回调
    const handleForgotPasswordSuccess = () => {
        setIsLogin(true);
        form.resetFields();
    };

    return (
        <div className="page-auth">
            <div className="auth-card">
                <div className="auth-left">
                    <div className="auth-logo">为什么星球</div>
                    <img src="/Images/IP.png" alt="IP图标" className="auth-avatar" />
                    <Title level={5} strong style={{ margin: '0', padding: '0' }}>仓小造</Title>
                    <div className="auth-welcome">让我想想办法！</div>
                </div>
                <div className="auth-right" style={isLogin ? { marginTop: '10px' } : { marginTop: '-10px' }}>
                    {/* 登录/注册标题 */}
                    <Title className="auth-title" level={4}>{isLogin ? '登录' : '注册'}</Title>
                    {/* 登录/注册表单 */}
                    <Form
                        form={form}
                        className="auth-form"
                        onFinish={handleSubmit}
                        layout="vertical"
                    >
                        <Form.Item
                            name="username"
                            style={{ marginBottom: '10px' }}
                            rules={[{ required: true, message: '请输入用户名' }]}
                        >
                            <Input
                                size="large"
                                fontSize={14}
                                placeholder=" 请输入用户名"
                                prefix={<UserOutlined />}
                            />
                        </Form.Item>
                        <Form.Item
                            name="password"
                            style={{ marginBottom: '10px' }}
                            rules={[
                                { required: true, message: '请输入密码' },
                                { min: 6, message: '密码长度至少6位' }
                            ]}
                        >
                            <Input.Password
                                size="large"
                                placeholder=" 请输入密码"
                                prefix={<LockOutlined />}
                            />
                        </Form.Item>
                        {/* 注册表单 */}
                        {!isLogin && (
                            <Form.Item
                                name="confirmPassword"
                                dependencies={['password']}
                                style={{ marginBottom: '10px' }}
                                rules={[
                                    { required: true, message: '请确认密码' },
                                    ({ getFieldValue }) => ({
                                        validator(_, value) {
                                            if (!value || getFieldValue('password') === value) {
                                                return Promise.resolve();
                                            }
                                            return Promise.reject(new Error('两次输入的密码不一致'));
                                        }
                                    })
                                ]}
                            >
                                <Input.Password
                                    size="large"
                                    placeholder=" 请确认密码"
                                    prefix={<LockOutlined />}
                                />
                            </Form.Item>
                        )}
                        <div className="link-bottom-container">
                            {/* 右下角登录/注册切换按钮 */}
                            <div className="auth-switch-bottom">
                                <Button
                                    type="link"
                                    className="switch-link-bottom"
                                    onClick={handleSwitchMode}
                                >
                                    {isLogin ? '注册' : '登录'}
                                </Button>
                            </div>
                            {/* 登录表单 - 忘记密码 */}
                            {/*isLogin && (
                                <div className="auth-switch-bottom">
                                    <Button
                                        type="link"
                                        className="switch-link-bottom"
                                        onClick={() => setShowForgotPassword(true)}
                                    >
                                        忘记密码？
                                    </Button>
                                </div>
                            )*/}
                        </div>
                        <Button
                            type="primary"
                            htmlType="submit"
                            className="btn-submit"
                            block
                            loading={loading}
                        >
                            提交
                        </Button>
                    </Form>
                </div>
            </div>
            {/* 忘记密码模态框 */}
            <ForgotPasswordModal
                open={showForgotPassword}
                onCancel={() => setShowForgotPassword(false)}
                onSuccess={handleForgotPasswordSuccess}
            />
        </div>
    )
}

export default Login;