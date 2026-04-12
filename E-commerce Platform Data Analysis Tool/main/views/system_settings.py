"""
Page 5: 系统设置 - B端专业版 v3.0
配置管理 | 偏好设置 | 数据清理
"""

import streamlit as st
import json
import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from components import get_toast


def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent.parent


def get_output_dir():
    """获取输出目录"""
    return get_project_root() / "output"


def render():
    """显示系统设置 - B端专业版 v3.0"""

    st.markdown('<h1 class="text-h1" style="display:flex;align-items:center;gap:12px;">'
                '<span>⚙️</span><span>系统设置</span></h1>', unsafe_allow_html=True)

    config_file = get_project_root() / "config" / "config.json"
    settings_file = get_project_root() / "settings.json"

    # ===== 1. 基本设置区 - 两列网格布局 =====
    st.markdown("### 📝 基本设置")

    basic_col1, basic_col2 = st.columns(2, gap="large")

    with basic_col1:
        default_keyword = st.text_input(
            "🔍 默认搜索关键词",
            value="食品",
            help="数据采集时的默认搜索词，可在采集页面修改"
        )

        st.markdown("")  # 间距

        default_product_count = st.number_input(
            "📦 默认采集数量",
            min_value=10,
            max_value=500,
            value=50,
            step=10,
            help="单次采集任务的商品数量上限，建议50-200以获得更好性能"
        )

    with basic_col2:
        default_review_count = st.number_input(
            "💬 默认评价数量",
            min_value=0,
            max_value=500,
            value=100,
            step=10,
            help="每个商品采集的评价数量，0表示不采集评价"
        )

        st.markdown("")  # 间距

        output_format = st.selectbox(
            "📄 输出格式",
            options=["JSON", "CSV", "Excel (.xlsx)", "全部格式"],
            index=0,
            help="选择数据导出的默认文件格式"
        )

    # ===== 2. 高级设置区 - 增强Tooltip =====
    st.markdown("---")
    st.markdown("### ⚡ 高级设置")

    adv_col1, adv_col2 = st.columns(2, gap="large")

    with adv_col1:
        headless_mode = st.checkbox(
            "🤖 默认无头模式",
            value=False,
            help="开启后，采集任务默认后台运行，不显示浏览器窗口，可提升采集效率并节省系统资源"
        )

        st.markdown("")  # 间距

        auto_save = st.checkbox(
            "💾 自动保存结果",
            value=True,
            help="开启后，采集数据自动保存到本地输出目录，无需手动导出操作"
        )

    with adv_col2:
        timeout_setting = st.slider(
            "⏱️ 请求超时时间（秒）",
            min_value=10,
            max_value=120,
            value=30,
            step=5,
            help="单个网络请求的最大等待时间，超时则自动重试，建议30-60秒以保证稳定性"
        )
        st.markdown(f'<div style="text-align:right;padding:4px 0;color:#6B7280;font-size:13px;">'
                   f'当前值: <strong style="color:#2563EB;">{timeout_setting} 秒</strong></div>',
                   unsafe_allow_html=True)

        st.markdown("")  # 间距

        retry_count = st.number_input(
            "🔄 失败重试次数",
            min_value=0,
            max_value=5,
            value=3,
            step=1,
            help="请求失败后的自动重试次数，建议2-5次以应对网络波动"
        )

    # ===== 3. 按钮与风险控制区 =====
    st.markdown("---")
    st.markdown("### 💾 设置操作")

    btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 2], gap="medium")

    with btn_col1:
        save_btn = st.button(
            "✅ 保存设置",
            type="primary",
            use_container_width=True,
            help="将当前配置保存到本地文件"
        )
        if save_btn:
            settings = {
                'default_keyword': default_keyword,
                'default_product_count': default_product_count,
                'default_review_count': default_review_count,
                'output_format': output_format,
                'headless_mode': headless_mode,
                'auto_save': auto_save,
                'timeout': timeout_setting,
                'retry_count': retry_count,
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            try:
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, ensure_ascii=False, indent=2)

                toast = get_toast()
                toast.success("✅ 设置已保存成功", duration=2500)

                success_html = '<div style="background:linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);border:1px solid #059669;border-radius:10px;padding:16px;margin:12px 0;text-align:center;">'
                success_html += '<div style="font-size:16px;font-weight:600;color:#059669;display:flex;align-items:center;justify-content:center;gap:8px;"><span>✅</span><span>设置已成功保存！</span></div>'
                success_html += '<div style="font-size:13px;color:#047857;margin-top:6px;">配置已写入本地文件，下次启动将自动加载</div></div>'
                st.markdown(success_html, unsafe_allow_html=True)

                time.sleep(1)

            except Exception as e:
                st.error(f"❌ 保存失败: {str(e)[:100]}")

    with btn_col2:
        restore_btn = st.button(
            "🔄 恢复默认设置",
            use_container_width=True,
            help="将所有设置恢复为初始默认值（需确认）"
        )

        if restore_btn:
            confirm_restore = '<div style="background:linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);border:2px solid #FCA5A5;border-radius:12px;padding:20px;margin:12px 0;">'
            confirm_restore += '<div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">'
            confirm_restore += '<span style="font-size:32px;">⚠️</span>'
            confirm_restore += '<div><strong style="font-size:17px;color:#991B1B;line-height:24px;">确定要恢复所有设置为默认值吗？</strong><br><span style="color:#7F1D1D;font-size:14px;line-height:20px;">此操作不可撤销，当前自定义配置将丢失</span></div>'
            confirm_restore += '</div></div>'
            st.markdown(confirm_restore, unsafe_allow_html=True)

            conf_rst_col1, conf_rst_col2 = st.columns(2)
            with conf_rst_col1:
                if st.button("✅ 确认恢复", type="primary", use_container_width=True):
                    if settings_file.exists():
                        settings_file.unlink()

                    toast = get_toast()
                    toast.success("🔄 已恢复默认设置", duration=2500)
                    time.sleep(0.5)
                    st.rerun()
            with conf_rst_col2:
                if st.button("❌ 取消", type="secondary", use_container_width=True):
                    st.rerun()

    with btn_col3:
        export_btn = st.button(
            "📤 导出配置",
            type="secondary",
            use_container_width=True,
            help="将当前设置导出为JSON文件，方便备份或迁移"
        )
        if export_btn and settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                config_data = f.read()
            st.download_button(
                label="💾 下载配置文件",
                data=config_data,
                file_name=f"settings_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                key="download_settings"
            )
            toast = get_toast()
            toast.info("📤 配置文件已准备下载", duration=2000)

    # ===== 4. 系统信息卡片 =====
    st.markdown("---")
    st.markdown("### 📊 系统信息")

    info_html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin:16px 0;">'

    info_items = [
        {"icon": "🐍", "label": "Python版本", "value": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", "color": "#2563EB"},
        {"icon": "📁", "label": "工作目录", "value": str(get_project_root()).split('\\')[-1], "color": "#059669"},
        {"icon": "📄", "label": "输出文件数", "value": f"{len(list(get_output_dir().glob('*'))) if get_output_dir().exists() else 0}", "color": "#F59E0B"},
        {"icon": "💾", "label": "配置状态", "value": "已保存 ✅" if settings_file.exists() else "未配置", "color": "#8B5CF6"}
    ]

    for item in info_items:
        info_html += f'<div style="background:white;border:1px solid #E5E7EB;border-radius:10px;padding:18px;box-shadow:0 2px 6px rgba(0,0,0,0.04);">'
        info_html += f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">'
        info_html += f'<span style="font-size:22px;">{item["icon"]}</span>'
        info_html += f'<span style="font-size:13px;color:#6B7280;">{item["label"]}</span></div>'
        info_html += f'<div style="font-size:18px;font-weight:700;color:{item["color"]};">{item["value"]}</div></div>'

    info_html += '</div>'
    st.markdown(info_html, unsafe_allow_html=True)

    # ===== 5. 数据管理区 =====
    st.markdown("---")
    st.markdown("### 🗑️ 数据管理")

    clear_data = st.selectbox(
        "选择要清理的数据类型",
        options=[
            "不清理",
            "仅清理日志文件 (.log)",
            "仅清理输出数据 (JSON/CSV)",
            "清理所有临时文件",
            "清理所有数据（危险操作）"
        ],
        help="选择要清理的文件类型，谨慎选择'清理所有数据'"
    )

    if clear_data != "不清理":
        danger_color = "#DC2626" if "危险" in clear_data or "所有" in clear_data else "#F59E0B"

        warning_html = f'<div style="background:linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%);border:2px solid {danger_color};border-radius:10px;padding:16px;margin:12px 0;">'
        warning_html += f'<div style="display:flex;align-items:center;gap:10px;"><span style="font-size:24px;">⚠️</span>'
        warning_html += f'<span style="font-size:15px;font-weight:600;color:{danger_color};">即将执行: {clear_data}</span></div></div>'
        st.markdown(warning_html, unsafe_allow_html=True)

        exec_clear = st.button("🗑️ 确认执行清理", type="secondary", use_container_width=True)
        if exec_clear:
            logs_dir = get_project_root() / "logs"
            output_dir = get_output_dir()

            cleared = []

            if "日志" in clear_data and logs_dir.exists():
                for log_file in logs_dir.glob('*.log'):
                    log_file.unlink()
                    cleared.append(log_file.name)

            if "输出" in clear_data and output_dir.exists():
                for out_file in output_dir.glob('*'):
                    out_file.unlink()
                    cleared.append(out_file.name)

            if cleared:
                toast = get_toast()
                toast.success(f"🗑️ 已成功清理 {len(cleared)} 个文件", duration=2500)
                time.sleep(0.5)
                st.rerun()
            else:
                st.info("ℹ️ 没有找到需要清理的文件")
