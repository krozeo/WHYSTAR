import React from "react";
import { Typography } from 'antd';
import './characterCard.css';

const { Title } = Typography;
const TitleStyle = {
    color: '#000000',
    margin: '0px 10px',
    fontSize: '13px',
    fontWeight: 600,
    textAlign: 'left'
}

const CharacterCard = ({ characterName, characterInfo }) => {
    return (
        <div className="Card-Container">
            <Title
                level={5}
                style={TitleStyle}>
                {characterName}
            </Title>
            <Title
                level={5}
                style={{
                    color: '#737373',
                    margin: '5px 10px',
                    fontSize: '13px',
                    fontWeight: 400,
                    textAlign: 'left',
                    whiteSpace: 'pre-wrap'
                }}>
                {characterInfo}
            </Title>
        </div>
    )
}

export default CharacterCard;