from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from configs.config import config
from services.animation_manager import AnimationManager
from services.plugin import plugin
from .schemas import AnimationRequest, SayAction, AnimateAction, EmotionAction
from services.audio_player import AudioPlayer
from contextlib import asynccontextmanager
import asyncio
import animations.blink_controller as blink_mod
import animations.breathing_controller as breath_mod
import animations.body_swing_controller as body_mod
import animations.mouth_expression_controller as mouth_mod
from utils.logger import setup_logging, logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    global animation_manager, audio_player
    # 初始化日志
    setup_logging(config.plugin.debug_mode)
    logger.info(f"启动插件: {config.plugin.plugin_name}")

    # 启动时认证插件并启动 idle 动画
    await plugin.connect_and_authenticate()
    
    animation_manager = AnimationManager()
    # 注册 idle 动画
    if config.blink.enabled:
        animation_manager.register_idle_controller(blink_mod.BlinkController(),False)
    if config.breathing.enabled:
        animation_manager.register_idle_controller(breath_mod.BreathingController(),True)
    if config.body_swing.enabled:
        animation_manager.register_idle_controller(body_mod.BodySwingController(),True)
    if config.mouth_expression.enabled:
        animation_manager.register_idle_controller(mouth_mod.MouthExpressionController(),False)
    await animation_manager.start()
    logger.info("AnimationManager 已启动并注册idle动画。")

    # 初始化音频播放器
    if config.speech_synthesis.enabled:
        logger.info("语音合成功能已启用。正在初始化AudioPlayer...")
        try:
            audio_player = AudioPlayer(
                audio_file_path=config.speech_synthesis.audio_file_path,
                text_rate=config.speech_synthesis.text_per_second_rate,
                volume=config.speech_synthesis.volume
            )
            logger.info("AudioPlayer 初始化成功。")
        except Exception as e:
            logger.error(f"AudioPlayer 初始化失败: {e}")
            audio_player = None
    else:
        logger.info("语音合成功能未启用。")

    try:
        yield
    finally:
        # 关闭时停止动画并断开插件
        logger.info("开始关闭插件...")
        if audio_player:
            audio_player.stop_all_sounds()
            logger.info("AudioPlayer 已停止所有声音。")
        await animation_manager.stop()
        logger.info("AnimationManager 已停止。")
        await plugin.disconnect()
        logger.info("插件已断开连接。插件关闭完成。")

app = FastAPI(
    title=config.plugin.plugin_name,
    version="1.0.0",
    description="VTS 面部控制插件 API",
    lifespan=lifespan
)

# 跨域设置（如有需要）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# 全局动画管理器和音频播放器实例
animation_manager: AnimationManager
audio_player: Optional[AudioPlayer] = None

@app.post("/animation")
async def post_animation(req: AnimationRequest):
    logger.debug(f"接收到动画请求: {req.model_dump_json(indent=2)}")
    animation_actions_for_manager = []
    audio_tasks = []
    exp_tasks = []

    for action in req.actions:
        if isinstance(action, AnimateAction):
            logger.debug(f"处理 AnimateAction: {action.parameter} at {action.startTime}s")
            animation_actions_for_manager.append({
                "parameter": action.parameter,
                "from": action.from_value,
                "to": action.to,
                "duration": action.duration,
                "startTime": action.startTime, 
                "easing": action.easing,
            })
        elif isinstance(action, SayAction):
            logger.debug(f"处理 SayAction: 文本片段数量 {len(action.text)}, 开始时间 {action.startTime}s")
            if audio_player and config.speech_synthesis.enabled:
                current_audio_player = audio_player 
                async def delayed_speech_task(current_action: SayAction):
                    if not current_audio_player: 
                        logger.warning("AudioPlayer 实例在任务执行前变为None，无法播放。")
                        return
                    try:
                        await asyncio.sleep(current_action.startTime)
                        first_segment_preview = current_action.text[0][:20] if current_action.text else "[空文本列表]"
                        logger.debug(f"开始播放语音 (首片段预览: '{first_segment_preview}...')")
                        await current_audio_player.play_text_as_speech(current_action.text, current_action.speeds)
                    except asyncio.CancelledError:
                        first_segment_preview = current_action.text[0][:20] if current_action.text else "[空文本列表]"
                        logger.info(f"语音任务 (首片段预览: '{first_segment_preview}...') 被取消")
                    except Exception as e:
                        first_segment_preview = current_action.text[0][:20] if current_action.text else "[空文本列表]"
                        logger.error(f"播放语音 (首片段预览: '{first_segment_preview}...') 时发生错误: {e}")
                
                audio_tasks.append(asyncio.create_task(delayed_speech_task(action)))
            else:
                logger.warning("AudioPlayer 未启用或未初始化，无法播放语音。")

    animation_successful = True
    if animation_actions_for_manager:
        logger.debug(f"发送 {len(animation_actions_for_manager)} 个动画动作到 AnimationManager")
        data_for_manager = {"actions": animation_actions_for_manager, "loop": req.loop}
        try:
            success = await animation_manager.run_animation(data_for_manager)
            if not success:
                animation_successful = False
                logger.error("AnimationManager 运行动画失败。")
        except Exception as e:
            animation_successful = False
            logger.error(f"调用 AnimationManager 时发生异常: {e}")

    if audio_tasks:
        logger.debug(f"等待 {len(audio_tasks)} 个音频任务完成...")
        results = await asyncio.gather(*audio_tasks, return_exceptions=True)
        for i, result in enumerate(results):
            if isinstance(result, Exception) and not isinstance(result, asyncio.CancelledError):
                logger.error(f"音频任务 {i} 执行失败: {result}")
        logger.debug("所有音频任务已处理完毕。")
    
    if not animation_successful:
        raise HTTPException(status_code=500, detail="运行动画序列时发生错误，部分动画可能未执行。")

    return {"success": True} 

@app.get("/expressions", response_model=List[dict])
async def get_model_expressions():
    """
    获取当前加载模型的所有可用表情列表。
    """
    logger.info("接收到获取模型表情列表的请求。")
    try:
        expressions = await plugin.get_expressions()
        logger.debug(f"成功获取到 {len(expressions)} 个表情。")
        return expressions
    except Exception as e:
        logger.error(f"获取模型表情列表时发生错误: {e}")
        raise HTTPException(status_code=500, detail=f"获取表情列表失败: {str(e)}") 