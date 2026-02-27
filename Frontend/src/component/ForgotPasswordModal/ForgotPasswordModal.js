import React, { useState, useEffect } from "react";
import { UserOutlined, LockOutlined, QuestionCircleOutlined } from '@ant-design/icons';
import { Input, Button, Modal, Form, message } from 'antd';
import { GetSecurityQuestions, VerifySecurityQuestions, UpdatePassword } from "../../api/apiInterface";
import './ForgotPasswordModal.css';

// 定义忘记密码模态框
const ForgotPasswordModal = ({ open, onCancel, onSuccess }) => {
    const [form] = Form.useForm();
    const [step, setStep] = useState(1); // 1: 输入用户名，2: 回答问题，3: 重置密码
    const [username, setUsername] = useState("");
    const [securityQuestion, setSecurityQuestion] = useState("");
    const [loading, setLoading] = useState(false);

    // 重置初始状态
    useEffect(() => {
        if (!open) {
            setStep(1); // 重置步骤为1
            setUsername(""); // 重置用户名为空
            setSecurityQuestion(""); // 重置安全问题为空
        }
    }, [open, form]);

    // 步骤1：验证用户名并获取安全问题
    const handleStep1 = async () => {
        try {
            const values = await form.validateFields(['username']);
            const usernameValue = values.username;
            setLoading(true);

            // 调用API获取用户设置的安全问题
            const response = await GetSecurityQuestions(usernameValue);

            if (response && response.data && response.data.question) {
                setUsername(usernameValue); // 设置用户名
                setSecurityQuestion(response.data.question); // 设置安全问题
                setStep(2); // 设置步骤为2 
            } else {
                message.error("未找到该用户或未设置安全问题");
            }
        } catch (error) {
            if (error.errorFields) {
                // 表单验证错误
                return;
            }
            message.error("获取安全问题失败，请稍后重试"); // 显示错误消息
            console.error("获取安全问题错误:", error); // 打印错误信息
        } finally {
            setLoading(false);// 设置加载状态为false
        }
    };

    // 步骤2：验证安全问题答案
    const handleStep2 = async () => {
        try {
            const values = await form.validateFields(['answer']);
            setLoading(true);

            // 调用API验证答案
            const response = await VerifySecurityQuestions({
                username: username,
                securityAnswer: values.answer
            });

            if (response && response.data && response.data.verified) {
                setStep(3);
            } else {
                message.error("答案错误");
            }
        } catch (error) {
            message.error("验证失败，请稍后重试");
            console.error("验证答案错误:", error);
        } finally {
            setLoading(false);
        }
    };

    // 步骤3：重置密码
    const handleStep3 = async () => {
        try {
            const values = await form.validateFields(['newPassword', 'confirmPassword']);
            setLoading(true);

            // 调用API重置密码
            const response = await UpdatePassword({
                username: username,
                newPassword: values.newPassword
            });

            if (response && response.data && response.data.success) {
                message.success("密码重置成功，请使用新密码登录");
                onSuccess && onSuccess();
                handleCancel(); // 调用取消回调函数，保证模态框关闭
            } else {
                message.error("密码重置失败");
            }
        } catch (error) {
            message.error("密码重置失败，请稍后重试");
            console.error("重置密码错误:", error);
        } finally {
            setLoading(false);
        }
    };

    // 取消按钮
    const handleCancel = () => {
        setStep(1);
        setUsername("");
        setSecurityQuestion("");
        form.resetFields();
        onCancel(); // 调用取消回调函数
    };

    // 下一步按钮
    const handleNext = () => {
        if (step === 1) {
            handleStep1();
        } else if (step === 2) {
            handleStep2();
        } else if (step === 3) {
            handleStep3();
        }
    };

    return (
        <Modal
            title="找回密码"
            open={open}
            onCancel={handleCancel}
            footer={[
                <Button key="back" onClick={handleCancel}>
                    取消
                </Button>,
                <Button
                    key="submit"
                    type="primary"
                    onClick={handleNext}
                    loading={loading}
                >
                    {step === 1 ? '下一步' : step === 2 ? '验证答案' : '重置密码'}
                </Button>,
            ]}
            className="forgot-password-modal"
        >
            <Form form={form} layout="vertical" className="forgot-password-form">
                {/* 步骤1：输入用户名 */}
                {step === 1 && (
                    <Form.Item
                        name="username"
                        label="请输入您的用户名"
                        rules={[{ required: true, message: '请输入用户名' }]}
                    >
                        <Input
                            size="large"
                            prefix={<UserOutlined />}
                        />
                    </Form.Item>
                )}

                {/* 步骤2：数据库内置的安全问题 */}
                {step === 2 && (
                    <Form.Item
                        name="answer"
                        label={securityQuestion || "请回答您的安全问题"}
                        rules={[{ required: true, message: '请输入答案' }]}
                    >
                        <Input
                            size="large"
                            prefix={<QuestionCircleOutlined />}
                        />
                    </Form.Item>
                )}

                {/* 步骤3：设置新密码 */}
                {step === 3 && (
                    <>
                        <Form.Item
                            name="newPassword"
                            label="新密码"
                            rules={[
                                { required: true, message: '请输入新密码' },
                                { min: 6, message: '密码长度至少6位' }
                            ]}
                        >
                            <Input.Password
                                size="large"
                                prefix={<LockOutlined />}
                            />
                        </Form.Item>
                        <Form.Item
                            name="confirmPassword"
                            label="确认新密码"
                            dependencies={['newPassword']}
                            rules={[
                                { required: true, message: '请确认新密码' },
                                ({ getFieldValue }) => ({
                                    validator(_, value) {
                                        if (!value || getFieldValue('newPassword') === value) {
                                            return Promise.resolve();
                                        }
                                        return Promise.reject(new Error('两次输入的密码不一致'));
                                    }
                                })
                            ]}
                        >
                            <Input.Password
                                size="large"
                                placeholder="请再次输入新密码"
                                prefix={<LockOutlined />}
                            />
                        </Form.Item>
                    </>
                )}
            </Form>
        </Modal>
    );
};

export default ForgotPasswordModal;
