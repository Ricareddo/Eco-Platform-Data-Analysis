"""
加载状态组件 - 骨架屏与加载动画
对标 Google Material Design / Tableau 加载体验
"""

import streamlit as st
from typing import Optional, Literal


def create_skeleton_loader(
    loader_type: Literal['card', 'table', 'chart', 'spinner'] = 'spinner',
    message: str = "加载中...",
    count: int = 1
) -> str:
    """
    创建骨架屏/加载动画
    
    Args:
        loader_type: 加载类型
            - card: 卡片骨架屏
            - table: 表格骨架屏
            - chart: 图表骨架屏
            - spinner: 旋转加载动画
        message: 提示文字
        count: 数量(用于卡片/表格行数)
    
    Returns:
        HTML 字符串
    """
    
    templates = {
        'card': f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 16px; margin: 16px 0;">
            {''.join([f'''
            <div class="skeleton-card">
                <div class="skeleton-line skeleton-title"></div>
                <div class="skeleton-line skeleton-value"></div>
            </div>
            '''] * count)}
        </div>
        """,
        
        'table': f"""
        <div class="skeleton-table" style="margin: 16px 0;">
            {''.join([f'''
            <div class="skeleton-row">
                <div class="skeleton-cell"></div>
                <div class="skeleton-cell"></div>
                <div class="skeleton-cell"></div>
                <div class="skeleton-cell"></div>
            </div>
            '''] * (count + 1))}
        </div>
        """,
        
        'chart': """
        <div style="padding: 24px; background: white; border-radius: 12px; border: 1px solid #E2E8F0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <div style="display: flex; align-items: flex-end; gap: 12px; height: 300px; padding: 20px;">
                <div class="skeleton-bar" style="width: 15%; height: 60%; border-radius: 8px;"></div>
                <div class="skeleton-bar" style="width: 15%; height: 85%; border-radius: 8px;"></div>
                <div class="skeleton-bar" style="width: 15%; height: 45%; border-radius: 8px;"></div>
                <div class="skeleton-bar" style="width: 15%; height: 70%; border-radius: 8px;"></div>
                <div class="skeleton-bar" style="width: 15%; height: 55%; border-radius: 8px;"></div>
                <div class="skeleton-bar" style="width: 15%; height: 90%; border-radius: 8px;"></div>
            </div>
        </div>
        """,
        
        'spinner': f"""
        <div class="loading-spinner">
            <div class="spinner-ring"></div>
            <p>{message}</p>
        </div>
        """
    }
    
    return templates.get(loader_type, templates['spinner'])


@st.cache_data(ttl=60)
def cached_skeleton(loader_type: str, count: int = 1) -> str:
    """缓存版本（避免重复生成）"""
    return create_skeleton_loader(loader_type, count=count)


class LoadingState:
    """加载状态上下文管理器"""
    
    def __init__(
        self,
        message: str = "处理中...",
        loader_type: Literal['card', 'table', 'chart', 'spinner'] = 'spinner'
    ):
        self.message = message
        self.loader_type = loader_type
        self._container = None
        self._placeholder = None
    
    def __enter__(self):
        """进入加载状态"""
        self._placeholder = st.empty()
        with self._placeholder:
            st.markdown(create_skeleton_loader(self.loader_type, self.message), unsafe_allow_html=True)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出加载状态"""
        if self._placeholder:
            self._placeholder.empty()
        return False


def with_loading(
    func,
    message: str = "加载中...",
    loader_type: Literal['card', 'table', 'chart', 'spinner'] = 'spinner',
    *args,
    **kwargs
):
    """
    装饰器/包装函数：为操作添加加载状态
    
    使用示例:
        result = with_loading(load_data, "正在加载数据...", 'table')
    """
    placeholder = st.empty()
    
    try:
        with placeholder:
            st.markdown(create_skeleton_loader(loader_type, message), unsafe_allow_html=True)
        
        result = func(*args, **kwargs)
        
        placeholder.empty()
        return result
        
    except Exception as e:
        placeholder.error(f"加载失败: {str(e)}")
        raise e


def render_progress_with_steps(steps: list, current_step: int = 0):
    """
    渲染分步进度指示器（简洁版）
    
    Args:
        steps: 步骤列表 [{"label": "...", "icon": "..."}]
        current_step: 当前步骤索引(从0开始)
    """
    
    # 使用Streamlit原生组件构建步骤指示器
    step_labels = []
    for i, step in enumerate(steps):
        is_completed = i < current_step
        is_current = i == current_step
        
        icon = "✅" if is_completed else (step.get('icon', str(i+1)) if is_current else "⏳")
        
        if is_completed:
            label = f"✅ {step['label']}"
        elif is_current:
            label = f"🔄 {step['label']} *(当前)*"
        else:
            label = f"⏳ {step['label']}"
        
        step_labels.append(label)
    
    # 显示进度文本
    progress_text = " → ".join(step_labels)
    st.info(f"**进度：** {progress_text}")
    
    # 显示当前步骤详情
    if current_step < len(steps):
        current_step_info = steps[current_step]
        st.markdown(f"> 📍 **当前步骤：** {current_step_info['icon']} {current_step_info['label']}")



def show_empty_state(
    title: str,
    description: str,
    icon: str = "📭",
    actions: list = None,
    features: list = None
):
    """
    渲染空状态界面(对标 Notion/Airtable)
    
    Args:
        title: 标题
        description: 描述文字
        icon: emoji 图标
        actions: 操作按钮 [{"label": "...", "callback": ...}]
        features: 功能特点列表 ["..."]
    """
    
    empty_html = f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <h3 class="empty-state-title">{title}</h3>
        <p class="empty-state-description">{description}</p>
    """
    
    if actions:
        empty_html += '<div class="empty-state-actions">'
        for action in actions:
            empty_html += f'<button class="action-btn primary">{action["label"]}</button>'
        empty_html += '</div>'
    
    if features:
        empty_html += '<div style="margin-top: 32px;"><h4 style="color: #64748B; font-size: 14px;">您将获得</h4><ul style="list-style: none; padding: 0; text-align: left; max-width: 300px; margin: 12px auto 0;">'
        for feature in features:
            empty_html += f'<li style="padding: 6px 0; color: #475569;">✅ {feature}</li>'
        empty_html += '</ul></div>'
    
    empty_html += '</div>'
    
    st.markdown(empty_html, unsafe_allow_html=True)
    
    # 渲染实际按钮
    if actions:
        cols = st.columns(len(actions))
        for i, action in enumerate(actions):
            with cols[i]:
                if st.button(action['label'], use_container_width=True, key=f"empty_action_{i}"):
                    if 'callback' in action and callable(action['callback']):
                        action['callback']()
                    # 触发页面刷新以应用导航变更
                    if 'current_page' in st.session_state:
                        st.rerun()


def render_coming_soon(feature_name: str, description: str, icon: str = "🚧", progress: int = 0):
    """
    渲染即将推出的功能占位符
    
    Args:
        feature_name: 功能名称
        description: 功能描述
        icon: 图标
        progress: 开发进度(0-100)
    """
    
    coming_soon_html = f"""
    <div style="
        padding: 48px 32px;
        text-align: center;
        background: linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%);
        border-radius: 16px;
        border: 2px dashed #CBD5E1;
        margin: 24px 0;
    ">
        <div style="font-size: 4rem; margin-bottom: 16px;">{icon}</div>
        <h3 style="font-size: 1.5rem; font-weight: 600; color: #1E293B; margin-bottom: 8px;">
            {feature_name} 即将推出
        </h3>
        <p style="color: #64748B; margin-bottom: 24px; line-height: 1.6;">{description}</p>
        
        {f'''
        <div style="margin-top: 24px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-size: 13px; color: #64748B;">
                <span>开发进度</span>
                <span>{progress}%</span>
            </div>
            <div style="height: 8px; background: #E2E8F0; border-radius: 9999px; overflow: hidden;">
                <div style="
                    height: 100%;
                    width: {progress}%;
                    background: linear-gradient(90deg, #2563EB 0%, #7C3AED 100%);
                    border-radius: 9999px;
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        ''' if progress > 0 else ''}
        
        <button style="
            margin-top: 24px;
            padding: 10px 24px;
            background: transparent;
            border: 2px solid #2563EB;
            color: #2563EB;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        "
        onmouseover="this.style.background='#2563EB'; this.style.color='white';"
        onmouseout="this.style.background='transparent'; this.style.color='#2563EB';"
        >
            🔔 通知我
        </button>
    </div>
    """
    
    st.markdown(coming_soon_html, unsafe_allow_html=True)
