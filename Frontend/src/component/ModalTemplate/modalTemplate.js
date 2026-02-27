import React from 'react';
import { Modal, Form, Input } from 'antd';
import './modalTemplate.css';

const ModalTemplate = ({ title, open, onCancel, onOk, confirmLoading, form, name, label,
    rules, prefix, placeholder, type, childrenName, childrenLabel, childrenRules,
    childrenPrefix, childrenPlaceholder }) => {

    return (
        <Modal
            title={title}
            open={open}
            onCancel={onCancel}
            onOk={onOk}
            confirmLoading={confirmLoading}
            okText='确认修改'
            cancelText='取消'
        >
            <Form form={form} layout='vertical'>
                <Form.Item
                    name={name}
                    label={label}
                    rules={rules}>
                    <Input
                        size='large'
                        prefix={prefix}
                        placeholder={placeholder}
                    />
                </Form.Item>
                {type === 2 && (
                    <Form.Item
                        name={childrenName}
                        label={childrenLabel}
                        rules={childrenRules}>
                        <Input
                            size='large'
                            prefix={childrenPrefix}
                            placeholder={childrenPlaceholder}
                        />
                    </Form.Item>
                )}
            </Form>
        </Modal>
    )
}

export default ModalTemplate;