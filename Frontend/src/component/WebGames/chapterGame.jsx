import { useEffect, useRef } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import './chapterGame.css';

// 游戏配置映射
const gameConfigs = {
    'mechanic': {
        gameFolder: 'WebdrumCar',
        gameName: 'WebdrumCar',
        productName: '筒车章',
        buildUrl: 'Build'
    },
    'optical': {
        gameFolder: 'WebAidai',
        gameName: 'WebAidai',
        productName: '叆叇章',
        buildUrl: 'Build'
    },
    'acoustic': {
        gameFolder: 'WebQinse',
        gameName: 'WebQinse',
        productName: '琴瑟章',
        buildUrl: 'Build'
    },
    'thermal': {
        gameFolder: 'WebWending',
        gameName: 'WebWending',
        productName: '温鼎章',
        buildUrl: 'Build'
    },
    'magnetism': {
        gameFolder: 'WebSinan',
        gameName: 'WebSinan',
        productName: '司南章',
        buildUrl: 'Build'
    }
};

// 筒车章
const DrumCarGame = ({ gameType }) => {
    console.log('gameType', gameType);
    const [searchParams] = useSearchParams();
    const currentGameType = gameType || searchParams.get('gameType') || 'mechanic';
    const gameConfig = gameConfigs[currentGameType] || gameConfigs['mechanic'];

    const navigate = useNavigate();
    const handleBack = () => {
        navigate(-1);
    }

    const containerRef = useRef(null); // 控制器
    const canvasRef = useRef(null); // 游戏画布
    const loadingBarRef = useRef(null); // 加载进度条
    const progressBarFullRef = useRef(null); // 编译进度条
    const loadingTipRef = useRef(null); // 加载提示文案
    const loadingPercentRef = useRef(null); // 加载百分比
    const fullscreenButtonRef = useRef(null);
    const warningBannerRef = useRef(null);
    const unityInstanceRef = useRef(null);

    useEffect(() => {
        const container = containerRef.current;
        const canvas = canvasRef.current;
        const loadingBar = loadingBarRef.current;
        const progressBarFull = progressBarFullRef.current;
        const loadingTip = loadingTipRef.current;
        const loadingPercent = loadingPercentRef.current;
        const fullscreenButton = fullscreenButtonRef.current;
        const warningBanner = warningBannerRef.current;

        // 添加 body 样式类
        document.body.classList.add('chapter-game-body');

        if (!container || !canvas || !loadingBar || !progressBarFull || !fullscreenButton || !warningBanner) {
            return;
        }

        // Unity 提示信息显示函数
        function unityShowBanner(msg, type) {
            function updateBannerVisibility() {
                warningBanner.style.display = warningBanner.children.length ? 'block' : 'none';
            }
            const div = document.createElement('div');
            div.innerHTML = msg;
            warningBanner.appendChild(div);
            if (type === 'error') {
                div.style = 'background: red; padding: 10px;';
            } else {
                if (type === 'warning') {
                    div.style = 'background: yellow; padding: 10px;';
                }
                setTimeout(function () {
                    warningBanner.removeChild(div);
                    updateBannerVisibility();
                }, 5000);
            }
            updateBannerVisibility();
        }

        const buildUrl = gameConfig.buildUrl;
        const loaderUrl = `${buildUrl}/${gameConfig.gameFolder}/${gameConfig.gameName}.loader.js`;
        const config = {
            dataUrl: `${buildUrl}/${gameConfig.gameFolder}/${gameConfig.gameName}.data`,
            frameworkUrl: `${buildUrl}/${gameConfig.gameFolder}/${gameConfig.gameName}.framework.js`,
            codeUrl: `${buildUrl}/${gameConfig.gameFolder}/${gameConfig.gameName}.wasm`,
            streamingAssetsUrl: "StreamingAssets",
            companyName: "Why the planet",
            productName: gameConfig.productName,
            productVersion: "1.0",
            showBanner: unityShowBanner,
        };

        let meta = null;
        // 检测移动设备
        if (/iPhone|iPad|iPod|Android/i.test(navigator.userAgent)) {
            // 移动设备样式：游戏画布填满整个浏览器客户端区域
            meta = document.createElement('meta');
            meta.name = 'viewport';
            meta.content = 'width=device-width, height=device-height, initial-scale=1.0, user-scalable=no, shrink-to-fit=yes';
            document.getElementsByTagName('head')[0].appendChild(meta);
            container.className = "unity-mobile";
            canvas.className = "unity-mobile";
        } else {
            canvas.style.width = "960px";
            canvas.style.height = "600px";
        }

        loadingBar.style.display = "flex";
        if (loadingTip) {
            loadingTip.textContent = `正在准备《${gameConfig.productName}》`;
        }
        if (loadingPercent) {
            loadingPercent.textContent = "0%";
        }

        const script = document.createElement("script");
        script.src = loaderUrl;

        // 标记组件是否已挂载
        let isMounted = true;

        script.onload = () => {
            if (!isMounted) return;
            if (window.createUnityInstance) {
                window.createUnityInstance(canvas, config, (progress) => {
                    if (isMounted) {
                        const percent = Math.max(0, Math.min(100, Math.round(progress * 100)));
                        progressBarFull.style.width = `${percent}%`;
                        if (loadingPercent) {
                            loadingPercent.textContent = `${percent}%`;
                        }
                        if (loadingTip) {
                            loadingTip.textContent = percent >= 100 ? "资源已完成加载，马上进入游戏" : `正在加载《${gameConfig.productName}》`;
                        }
                    }
                }).then((unityInstance) => {
                    if (isMounted) {
                        // 如果之前已经有一个实例，先销毁它
                        if (unityInstanceRef.current && unityInstanceRef.current !== unityInstance) {
                            unityInstanceRef.current.Quit().catch(() => { });
                        }

                        unityInstanceRef.current = unityInstance;
                        loadingBar.style.display = "none";
                        if (loadingPercent) {
                            loadingPercent.textContent = "100%";
                        }
                        fullscreenButton.onclick = () => {
                            unityInstance.SetFullscreen(1);
                        };
                    } else {
                        // 如果加载完成时组件已卸载，立即退出
                        unityInstance.Quit().catch(() => { });
                    }
                }).catch((message) => {
                    if (isMounted) {
                        alert(message);
                    }
                });
            }
        };

        document.body.appendChild(script);

        // 清理函数
        return () => {
            isMounted = false;
            // 移除 body 样式类
            document.body.classList.remove('chapter-game-body');

            if (unityInstanceRef.current) {
                unityInstanceRef.current.Quit().catch(() => {
                    console.log("Unity Quit failed or already quit");
                });
                unityInstanceRef.current = null;
            }
            if (script.parentNode) {
                script.parentNode.removeChild(script);
            }
            if (meta && meta.parentNode) {
                meta.parentNode.removeChild(meta);
            }
        };
    }, [currentGameType, gameConfig]);

    return (
        <>
            <button id="back-button" type="button" onClick={handleBack}>返回</button>
            <div id="unity-container" ref={containerRef} className="unity-desktop">
                <canvas
                    id="unity-canvas"
                    ref={canvasRef}
                    width={960}
                    height={600}
                    tabIndex={-1}
                />
                <div id="unity-loading-bar" ref={loadingBarRef}>
                    <div className="loading-card">
                        <div className="loading-spinner" aria-hidden="true"></div>
                        <div id="unity-loading-tip" ref={loadingTipRef}>内容还在加载，请耐心等候</div>
                        <div id="unity-loading-percent" ref={loadingPercentRef}>0%</div>
                        <div id="unity-progress-bar-empty">
                            <div id="unity-progress-bar-full" ref={progressBarFullRef}></div>
                        </div>
                    </div>
                </div>
                <div id="unity-warning" ref={warningBannerRef}></div>
                <div id="unity-footer">
                    <div id="unity-fullscreen-button" ref={fullscreenButtonRef}></div>
                </div>
            </div>
        </>
    );
};

export default DrumCarGame;