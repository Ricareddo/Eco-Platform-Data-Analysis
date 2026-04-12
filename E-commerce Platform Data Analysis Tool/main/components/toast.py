"""
Toast 通知组件 - 企业级B端规范 v8.0
稳定方案：components.html() + 绝对定位 + 时间防重复
"""

import streamlit as st
import time
import random


class ToastNotification:
    """Toast 通知管理器 - 可靠版本"""
    
    def __init__(self):
        pass
    
    def _ensure_toasts_exist(self):
        if 'toasts' not in st.session_state:
            st.session_state.toasts = []
        if '_toast_last_time' not in st.session_state:
            st.session_state._toast_last_time = {}
    
    def show(self, message: str, toast_type: str = 'info', duration: int = 3000, icon: str = None):
        """
        显示 Toast 通知
        
        Args:
            message: 通知消息内容
            toast_type: success/error/warning/info
            duration: 显示时长(毫秒), 0=不自动消失
            icon: 自定义图标
        """
        self._ensure_toasts_exist()
        
        # 防重复检查：基于时间戳（5秒内相同消息不重复显示）
        current_time = time.time()
        msg_key = message + "|" + toast_type
        
        last_time = st.session_state._toast_last_time.get(msg_key, 0)
        if current_time - last_time < 5:
            return  # 5秒内重复消息跳过
        
        st.session_state._toast_last_time[msg_key] = current_time
        
        # 图标映射
        icons_map = {'success': '✓', 'error': '✕', 'warning': '⚠', 'info': 'ℹ'}
        toast_icon = icon or icons_map.get(toast_type, 'ℹ')
        toast_id = "t" + str(random.randint(10000, 99999))
        
        # 颜色配置
        colors = {
            'success': ('rgba(16,185,129,0.97)', '#059669'),
            'error': ('rgba(239,68,68,0.97)', '#DC2626'),
            'warning': ('rgba(245,158,11,0.97)', '#D97706'),
            'info': ('rgba(59,130,246,0.97)', '#2563EB')
        }
        bg_color, border_color = colors.get(toast_type, colors['info'])
        
        # 构建完整HTML文档（用于components.html）
        html_parts = []
        
        html_parts.append('<!DOCTYPE html><html><head><meta charset="utf-8">')
        
        # CSS样式
        html_parts.append('<style>')
        html_parts.append('*{margin:0;padding:0;box-sizing:border-box;}')
        html_parts.append('body{background:transparent;overflow:hidden;height:100%;}')
        html_parts.append('@keyframes slideIn{from{transform:translateX(120%);opacity:0}to{transform:translateX(0);opacity:1}}')
        html_parts.append('@keyframes slideOut{from{transform:translateX(0);opacity:1}to{transform:translateX(120%);opacity:0}}')
        html_parts.append('@keyframes progressBar{from{width:100%}to{width:0%}}')
        html_parts.append('.toast-container{position:absolute;top:0;right:0;z-index:99999;display:flex;flex-direction:column;gap:10px;pointer-events:none;padding:10px;}')
        html_parts.append('.toast-item{position:relative;min-width:280px;max-width:380px;padding:14px 18px;border-radius:8px;background:' + bg_color + ';color:#FFF;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;box-shadow:0 8px 20px rgba(0,0,0,0.18),0 4px 10px rgba(0,0,0,0.12);border-left:4px solid ' + border_color + ';display:flex;align-items:center;gap:12px;margin-bottom:10px;animation:slideIn 0.35s ease-out;pointer-events:auto;}')
        html_parts.append('.toast-content{display:flex;align-items:center;gap:10px;flex:1;}')
        html_parts.append('.toast-icon{font-size:20px;}')
        html_parts.append('.toast-message{font-size:14px;font-weight:500;line-height:1.4;}')
        html_parts.append('.toast-close{background:rgba(255,255,255,0.25);border:none;color:#fff;width:26px;height:26px;border-radius:50%;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:14px;transition:all 0.2s;flex-shrink:0;}')
        html_parts.append('.toast-close:hover{background:rgba(255,255,255,0.4);transform:scale(1.1);}')
        html_parts.append('.toast-progress{position:absolute;bottom:0;left:0;height:3px;background:rgba(255,255,255,0.5);border-radius:0 0 8px 8px;}')
        html_parts.append('</style>')
        
        html_parts.append('</head><body>')
        
        # Toast容器
        html_parts.append('<div class="toast-container">')
        
        # Toast项
        html_parts.append('<div id="' + toast_id + '" class="toast-item">')
        html_parts.append('<div class="toast-content">')
        html_parts.append('<span class="toast-icon">' + toast_icon + '</span>')
        html_parts.append('<span class="toast-message">' + message + '</span>')
        html_parts.append('</div>')
        html_parts.append('<button class="toast-close" onclick="closeToast(\'' + toast_id + '\')">&#10005;</button>')
        
        # 进度条
        if duration > 0:
            html_parts.append('<div class="toast-progress" style="animation:progressBar ' + str(duration) + 'ms linear forwards;"></div>')
        
        html_parts.append('</div>')  # 结束 toast-item
        
        html_parts.append('</div>')  # 结束 toast-container
        
        # JavaScript
        html_parts.append('<script>')
        html_parts.append('function closeToast(id){')
        html_parts.append('var el=document.getElementById(id);')
        html_parts.append('if(el){')
        html_parts.append('el.style.animation="slideOut 0.3s ease-in forwards";')
        html_parts.append('setTimeout(function(){if(el.parentNode)el.parentNode.removeChild(el);},300);')
        html_parts.append('}')
        html_parts.append('}')
        
        # 自动关闭
        if duration > 0:
            html_parts.append('setTimeout(function(){closeToast("' + toast_id + '");},' + str(duration) + ');')
        
        html_parts.append('</script>')
        
        html_parts.append('</body></html>')
        
        toast_html = ''.join(html_parts)
        
        # 添加到列表
        if hasattr(st.session_state, 'toasts') and isinstance(st.session_state.toasts, list):
            st.session_state.toasts.append({
                'id': toast_id,
                'html': toast_html,
                'type': toast_type,
                'timestamp': time.time(),
                'duration': duration
            })
        else:
            st.session_state.toasts = [{
                'id': toast_id,
                'html': toast_html,
                'type': toast_type,
                'timestamp': time.time(),
                'duration': duration
            }]
    
    def success(self, message: str, duration: int = 3000):
        self.show(message, 'success', duration)
    
    def error(self, message: str, duration: int = 5000):
        self.show(message, 'error', duration)
    
    def warning(self, message: str, duration: int = 4000):
        self.show(message, 'warning', duration)
    
    def info(self, message: str, duration: int = 3000):
        self.show(message, 'info', duration)
    
    def render(self):
        """渲染所有活跃的 Toast 通知"""
        toasts = getattr(st.session_state, 'toasts', [])
        
        if not toasts:
            return
        
        # 清理过期Toast（超过20秒的移除）
        current_time = time.time()
        active_toasts = [t for t in toasts[-10:] if current_time - t['timestamp'] < 20]
        
        if not active_toasts:
            st.session_state.toasts = []
            return
        
        st.session_state.toasts = active_toasts
        
        # 只显示最新的一个Toast（避免堆叠问题）
        latest_toast = active_toasts[-1]
        
        # 使用components.html渲染 - JS可以执行！
        st.components.v1.html(latest_toast['html'], height=80, scrolling=False)
    
    def clear(self):
        if hasattr(st.session_state, 'toasts'):
            st.session_state.toasts = []
        if hasattr(st.session_state, '_toast_last_time'):
            st.session_state._toast_last_time.clear()


# 全局单例
_toast_instance = None

def get_toast() -> ToastNotification:
    global _toast_instance
    if _toast_instance is None:
        _toast_instance = ToastNotification()
    return _toast_instance

def render_toasts():
    get_toast().render()
