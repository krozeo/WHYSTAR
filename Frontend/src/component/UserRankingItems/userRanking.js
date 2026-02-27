import React, { useEffect, useState } from 'react';
import { useDispatch } from 'react-redux';
import { message } from 'antd';
import { useSelector } from 'react-redux';
import { setCurrentRank, setCurPoints } from '../../store/reducers/user';
import { GetUserRanking } from '../../api/apiInterface';
import './userRanking.css';

const DividerStyle = {
    border: '1px solid rgb(0, 0, 0)',
    width: '100%',
}

const UserRanking = () => {
    const dispatch = useDispatch();
    const { user } = useSelector((state) => state.user);
    const [userRankingData, setUserRankingData] = useState([]);

    useEffect(() => {
        const fetchUserRanking = async () => {
            try {
                const res = await GetUserRanking();
                const payload = res?.data?.data ?? res?.data ?? [];
                if (Array.isArray(payload)) {
                    setUserRankingData(payload);
                    const currentUserItem = user?.username
                        ? payload.find((item) => item.username === user.username)
                        : null;
                    dispatch(setCurrentRank(currentUserItem?.rank ?? 0));
                    dispatch(setCurPoints(currentUserItem?.total_points ?? 0));
                } else {
                    console.error('User ranking payload is not an array:', payload, res);
                    if (res?.data?.success === false) {
                        message.error(res?.data?.message || '获取用户排行榜失败');
                    }
                }
            } catch (error) {
                console.error('获取用户排行榜失败', error);
            }
        };
        fetchUserRanking();
    }, [dispatch, user?.username]);

    return (
        <div className="user-ranking-list">
            {
                userRankingData.map((item) => (
                    <div key={item.username} className="user-ranking-item-container">
                        <div className="user-ranking-item-text">{item.rank} {item.username}</div>
                        <hr style={DividerStyle} />
                    </div>
                ))
            }
        </div>
    )
}

export default UserRanking;
