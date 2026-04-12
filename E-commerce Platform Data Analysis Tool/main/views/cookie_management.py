"""
Page 4: Cookie管理 - 简化版（实时登录模式说明）
登录状态管理 | 使用指南 | 模式切换
"""

import streamlit as st
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))


def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent.parent


def render():
    """显示Cookie管理页面 - 实时登录模式说明版"""
    
    st.markdown('<h1 class="text-h1" style="display:flex;align-items:center;gap:12px;">'
                '<span>🍪</span><span>Cookie管理中心</span></h1>', unsafe_allow_html=True)
    
    # ===== 核心说明：当前使用实时登录模式 =====
    st.markdown('''
    <div style="
        background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
        border-left: 5px solid #2563EB;
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
    ">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
            <span style="font-size:36px;">✨</span>
            <div>
                <h2 style="margin:0;color:#1E40AF;font-size:20px;font-weight:700;">
                    当前模式：实时登录（推荐）
                </h2>
                <p style="margin:8px 0 0 0;color:#3B82F6;font-size:14px;">
                    每次数据采集时自动打开浏览器等待您登录，无需预先保存Cookie
                </p>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    # ===== 工作原理说明 =====
    st.markdown('<h2 style="font-size:18px;font-weight:600;color:#1E293B;margin-bottom:16px;">🔄 工作流程</h2>', 
               unsafe_allow_html=True)
    
    workflow_steps = [
        {
            "step": "1",
            "title": "点击开始采集",
            "desc": "在「数据采集」页面配置参数后，点击「🚀 开始采集」按钮",
            "icon": "🚀"
        },
        {
            "step": "2", 
            "title": "自动打开浏览器",
            "desc": "系统自动启动浏览器并跳转到淘宝登录页面",
            "icon": "🌐"
        },
        {
            "step": "3",
            "title": "完成账号登录",
            "desc": "在弹出的浏览器中使用扫码或密码方式登录淘宝/天猫账号",
            "icon": "🔐"
        },
        {
            "step": "4",
            "title": "确认并继续",
            "desc": "登录成功后，点击界面中的「✅ 我已完成登录」按钮继续采集",
            "icon": "✅"
        },
        {
            "step": "5",
            "title": "自动采集数据",
            "desc": "系统自动完成商品搜索、数据采集和结果保存",
            "icon": "📥"
        }
    ]
    
    for i, step_info in enumerate(workflow_steps):
        col_num, col_icon = st.columns([0.9, 0.1], gap="small")
        
        with col_num:
            if i == len(workflow_steps) - 1:
                st.markdown(f'''
                <div style="
                    background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
                    border-radius: 10px;
                    padding: 16px;
                    margin: 8px 0;
                    border-left: 4px solid #22C55E;
                ">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <span style="
                            width:32px;height:32px;border-radius:50%;
                            background:#22C55E;color:white;
                            display:inline-flex;align-items:center;
                            justify-content:center;font-weight:bold;font-size:14px;
                        ">{step_info["step"]}</span>
                        <div>
                            <strong style="color:#166534;font-size:15px;">{step_info["title"]}</strong>
                            <p style="margin:4px 0 0 0;color:#15803D;font-size:13px;line-height:1.5;">{step_info["desc"]}</p>
                        </div>
                        <span style="font-size:24px;margin-left:auto;">{step_info["icon"]}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div style="
                    background: linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%);
                    border-radius: 10px;
                    padding: 16px;
                    margin: 8px 0;
                    border-left: 4px solid #CBD5E1;
                ">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <span style="
                            width:32px;height:32px;border-radius:50%;
                            background:#64748B;color:white;
                            display:inline-flex;align-items:center;
                            justify-content:center;font-weight:bold;font-size:14px;
                        ">{step_info["step"]}</span>
                        <div>
                            <strong style="color:#334155;font-size:15px;">{step_info["title"]}</strong>
                            <p style="margin:4px 0 0 0;color:#64748B;font-size:13px;line-height:1.5;">{step_info["desc"]}</p>
                        </div>
                        <span style="font-size:24px;margin-left:auto;">{step_info["icon"]}</span>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
        
        with col_icon:
            if i < len(workflow_steps) - 1:
                st.markdown('''
                <div style="
                    text-align:center;
                    padding:8px 0;
                    color:#94A3B8;
                    font-size:20px;
                ">↓</div>
                ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== 优势对比 =====
    st.markdown('<h2 style="font-size:18px;font-weight:600;color:#1E293B;margin-bottom:16px;">⚡ 实时登录的优势</h2>', 
               unsafe_allow_html=True)
    
    advantages = [
        ("🔒 更安全", "无需存储Cookie文件到本地，避免凭证泄露风险"),
        ("🔄 更新鲜", "每次都使用最新登录状态，避免Cookie过期问题"),
        ("🎯 更简单", "一键操作，无需单独管理登录会话"),
        ("⏱️ 更灵活", "支持多账号切换，每次可使用不同账号登录")
    ]
    
    adv_cols = st.columns(len(advantages))
    
    for i, (adv_title, adv_desc) in enumerate(advantages):
        with adv_cols[i]:
            st.markdown(f'''
            <div style="
                background:white;
                border:2px solid #E2E8F0;
                border-radius:10px;
                padding:20px;text-align:center;
                height:100%;
                transition:all 0.3s;
            ">
                <div style="font-size:28px;margin-bottom:8px;">{adv_title.split(" ")[0]}</div>
                <strong style="color:#1E293B;font-size:14px;display:block;margin:8px 0;">
                    {adv_title.split(" ", 1)[1] if " " in adv_title else ""}
                </strong>
                <p style="color:#64748B;font-size:12px;line-height:1.5;margin:0;">{adv_desc}</p>
            </div>
            ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ===== 常见问题解答 =====
    st.markdown('<h2 style="font-size:18px;font-weight:600;color:#1E293B;margin-bottom:16px;">❓ 常见问题</h2>', 
               unsafe_allow_html=True)
    
    faqs = [
        (
            "Q: 需要每次都手动登录吗？",
            "A: 是的，这是为了保证登录状态的时效性和安全性。但整个过程只需30秒-1分钟。"
        ),
        (
            "Q: 可以使用扫码登录吗？",
            "A: ✅ 完全支持！打开的浏览器窗口中同时提供扫码登录和密码登录两种方式。"
        ),
        (
            "Q: 登录后可以关闭浏览器吗？",
            "A: ⚠️ 请勿关闭！登录完成后只需点击确认按钮，系统会自动继续采集并在完成后关闭浏览器。"
        ),
        (
            "Q: 如果不小心关闭了怎么办？",
            "A: 重新点击「开始采集」按钮即可，系统会重新启动浏览器让您登录。"
        )
    ]
    
    for question, answer in faqs:
        with st.expander(question):
            st.markdown(f'<p style="color:#374151;line-height:1.6;">{answer}</p>', unsafe_allow_html=True)
    
    # ===== 快速导航按钮 =====
    st.markdown("---")
    
    st.markdown('<h2 style="font-size:18px;font-weight:600;color:#1E293B;margin-bottom:16px;">🚀 快速开始</h2>', 
               unsafe_allow_html=True)
    
    nav_col1, nav_col2 = st.columns([2, 1], gap="medium")
    
    with nav_col1:
        if st.button("➡️ 前往数据采集页面", type="primary", use_container_width=True):
            st.session_state.current_page = "数据采集"
            st.rerun()
    
    with nav_col2:
        st.info("💡 推荐首次使用\n先进行测试模式")
