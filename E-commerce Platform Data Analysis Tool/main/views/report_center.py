"""
Page 3: 报告中心 - B端专业版 v3.0
文件管理 | 批量操作 | 预览下载
"""

import streamlit as st
import json
import os
import sys
import time
import zipfile
import io
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
    """显示报告中心 - B端专业版 v3.0"""

    st.markdown('<h1 class="text-h1" style="display:flex;align-items:center;gap:12px;">'
                '<span>📊</span><span>报告中心</span></h1>', unsafe_allow_html=True)

    output_dir = get_output_dir()

    if not output_dir.exists() or not list(output_dir.glob('*')):
        # ===== 空状态设计 - 场景化引导 =====
        empty_html = '<div style="max-width:800px;margin:40px auto;padding:0;">'
        empty_html += '<div style="background:linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);border:1px solid #BBF7D0;border-radius:16px;padding:48px 40px;text-align:center;box-shadow:0 4px 12px rgba(34,197,94,0.08);">'
        empty_html += '<div style="width:120px;height:120px;background:linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 24px;box-shadow:0 8px 24px rgba(34,197,94,0.15);"><span style="font-size:56px;">📄</span></div>'
        empty_html += '<h2 style="font-size:24px;font-weight:700;color:#1E293B;margin-bottom:12px;line-height:1.4;">还没有生成任何报告～</h2>'
        empty_html += '<p style="font-size:15px;color:#475569;line-height:1.8;max-width:600px;margin:0 auto 28px;">完成<span style="color:#2563EB;font-weight:600;background:#DBEAFE;padding:2px 8px;border-radius:4px;">数据采集与分析</span>后，报告将自动保存在这里，包括日志文件、分析报告、导出数据等 📊</p>'
        empty_html += '</div>'

        empty_html += '<div style="margin-top:32px;background:white;border:1px solid #E5E7EB;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,0.04);">'
        empty_html += '<h3 style="font-size:16px;font-weight:700;color:#1E293B;margin-bottom:20px;text-align:center;">📋 报告类型预览</h3>'
        empty_html += '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;">'

        empty_html += '<div style="background:#F8FAFC;border-radius:8px;padding:16px;text-align:center;"><div style="font-size:32px;margin-bottom:8px;">📝</div><div style="font-size:14px;font-weight:600;color:#1E293B;">日志文件</div><div style="font-size:12px;color:#6B7280;margin-top:4px;">.log / .txt</div></div>'
        empty_html += '<div style="background:#F8FAFC;border-radius:8px;padding:16px;text-align:center;"><div style="font-size:32px;margin-bottom:8px;">📊</div><div style="font-size:14px;font-weight:600;color:#1E293B;">分析报告</div><div style="font-size:12px;color:#6B7280;margin-top:4px;">.md / .html</div></div>'
        empty_html += '<div style="background:#F8FAFC;border-radius:8px;padding:16px;text-align:center;"><div style="font-size:32px;margin-bottom:8px;">📈</div><div style="font-size:14px;font-weight:600;color:#1E293B;">导出数据</div><div style="font-size:12px;color:#6B7280;margin-top:4px;">.xlsx / .csv</div></div>'

        empty_html += '</div></div></div>'
        st.markdown(empty_html, unsafe_allow_html=True)

        col_center = st.columns([1, 2, 1])
        with col_center[1]:
            if st.button("🚀 开始采集数据", type="primary", use_container_width=True,
                        key="reports_go_to_crawl", help="跳转到数据采集页面"):
                st.session_state.current_page = '数据采集'
                st.rerun()
        return

    all_files = [f for f in output_dir.glob('*') if f.is_file()]

    if not all_files:
        empty_html2 = '<div style="max-width:800px;margin:40px auto;padding:0;">'
        empty_html2 += '<div style="background:linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);border:1px solid #FCD34D;border-radius:16px;padding:48px 40px;text-align:center;box-shadow:0 4px 12px rgba(245,158,11,0.08);">'
        empty_html2 += '<div style="width:120px;height:120px;background:linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 24px;"><span style="font-size:56px;">📭</span></div>'
        empty_html2 += '<h2 style="font-size:24px;font-weight:700;color:#92400E;margin-bottom:12px;">输出目录为空</h2>'
        empty_html2 += '<p style="font-size:15px;color:#78350F;line-height:1.8;">尚未生成任何报告文件，请先进行数据采集操作。</p>'
        empty_html2 += '</div></div>'
        st.markdown(empty_html2, unsafe_allow_html=True)
        return

    # ===== 筛选功能区 - 简化版（100%可靠）=====
    st.markdown("### 🔍 文件筛选与搜索")

    filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 1], gap="medium")

    with filter_col1:
        file_types_selected = st.multiselect(
            "📁 文件类型",
            options=[
                "日志文件 (.log/.txt)",
                "JSON数据 (.json)",
                "分析报告 (.md/.html)",
                "表格数据 (.csv/.xlsx)"
            ],
            default=[  # 使用硬编码默认值，避免session_state冲突
                "日志文件 (.log/.txt)",
                "JSON数据 (.json)",
                "分析报告 (.md/.html)",
                "表格数据 (.csv/.xlsx)"
            ],
            help="选择要显示的文件类型",
            key="report_file_filter"
        )

        if not file_types_selected:  # 防御性：防止空列表
            file_types_selected = [
                "日志文件 (.log/.txt)",
                "JSON数据 (.json)",
                "分析报告 (.md/.html)",
                "表格数据 (.csv/.xlsx)"
            ]

    with filter_col2:
        search_keyword = st.text_input(
            "🔎 搜索文件名",
            placeholder="输入关键词搜索...",
            help="支持按文件名模糊搜索"
        )

    with filter_col3:
        sort_option = st.selectbox(
            "↕️ 排序方式",
            options=["按时间降序", "按时间升序", "按大小降序", "按大小升序", "按名称升序"],
            index=0,
            help="选择文件的排序方式"
        )

    # 文件过滤逻辑 - 使用动态查找（兼容Streamlit环境）
    files_to_show = []

    # 从 session_state 读取筛选条件
    raw_selection = st.session_state.get('report_file_filter', [])
    actual_selection = list(raw_selection) if raw_selection else [
        "日志文件 (.log/.txt)",
        "JSON数据 (.json)",
        "分析报告 (.md/.html)",
        "表格数据 (.csv/.xlsx)"
    ]

    for f in all_files:
        suffix = f.suffix.lower()

        # 使用 any() 动态查找选项（避免 Streamlit 中 'in' 操作符的异常行为）
        has_log_option = any("日志" in item for item in actual_selection)
        has_json_option = any("JSON" in item for item in actual_selection)
        has_report_option = any("分析报告" in item for item in actual_selection)
        has_table_option = any("表格" in item for item in actual_selection)

        # 文件类型匹配
        file_type_match = (
            (has_log_option and suffix in ['.log', '.txt']) or
            (has_json_option and suffix == '.json') or
            (has_report_option and suffix in ['.md', '.html']) or
            (has_table_option and suffix in ['.csv', '.xlsx'])
        )

        # 关键词过滤
        keyword_match = True
        if search_keyword and search_keyword.strip():
            keyword_match = search_keyword.lower() in f.name.lower()

        if file_type_match and keyword_match:
            files_to_show.append(f)

    # 排序逻辑
    if sort_option == "按时间降序":
        files_to_show.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    elif sort_option == "按时间升序":
        files_to_show.sort(key=lambda x: x.stat().st_mtime, reverse=False)
    elif sort_option == "按大小降序":
        files_to_show.sort(key=lambda x: x.stat().st_size, reverse=True)
    elif sort_option == "按大小升序":
        files_to_show.sort(key=lambda x: x.stat().st_size, reverse=False)
    elif sort_option == "按名称升序":
        files_to_show.sort(key=lambda x: x.name.lower(), reverse=False)

    if not files_to_show:
        st.warning(f"⚠️ 没有找到符合筛选条件的文件（共 {len(all_files)} 个文件）")
        
        # 显示调试信息和快捷操作
        with st.expander("🔧 排查帮助", expanded=False):
            st.markdown("**当前筛选条件：**")
            st.json({
                "已选文件类型": file_types_selected,
                "搜索关键词": search_keyword if search_keyword else "(无)",
                "排序方式": sort_option
            })
            
            st.markdown("**目录中的实际文件：**")
            for f in all_files:
                suffix = f.suffix.lower()
                file_type = "未知"
                if suffix in ['.log', '.txt']:
                    file_type = "日志文件"
                elif suffix == '.json':
                    file_type = "JSON数据"
                elif suffix in ['.md', '.html']:
                    file_type = "分析报告"
                elif suffix in ['.csv', '.xlsx']:
                    file_type = "表格数据"
                
                st.markdown(f"- `{f.name}` ({file_type}, {f.stat().st_size/1024:.1f} KB)")
        
        # 快捷操作：一键显示全部
        col_help1, col_help2 = st.columns(2)
        with col_help1:
            if st.button("🔄 显示全部文件", type="primary", use_container_width=True,
                         key="show_all_files_btn"):
                # 清除multiselect的session_state，强制重新初始化
                if 'report_file_filter' in st.session_state:
                    del st.session_state['report_file_filter']
                st.rerun()
        
        with col_help2:
            if st.button("🗑️ 清除搜索关键词", use_container_width=True,
                         key="clear_search_btn"):
                st.rerun()
        
        return

    # 通知提示 - 限制数量最多2条
    toast = get_toast()
    toast.info(f"找到 {len(files_to_show)} 个文件", duration=2500)

    # ===== 批量操作栏 =====
    st.markdown("---")
    batch_col1, batch_col2, batch_col3, batch_col4 = st.columns([1, 1, 1, 2])

    with batch_col1:
        select_all = st.checkbox("全选所有文件", value=False, key="select_all_reports")

    with batch_col2:
        if select_all:
            batch_download_disabled = False
        else:
            selected_count = sum(1 for i in range(len(files_to_show)) if st.session_state.get(f'report_file_{i}', False))
            batch_download_disabled = (selected_count == 0)

        batch_download = st.button(
            "📥 批量下载",
            type="secondary",
            use_container_width=True,
            disabled=batch_download_disabled,
            help=f"下载选中的文件（已选{selected_count if not select_all else len(files_to_show)}个）" if not batch_download_disabled else "请先选择文件"
        )

    with batch_col3:
        batch_delete = st.button(
            "🗑️ 批量删除",
            use_container_width=True,
            disabled=batch_download_disabled,
            help="删除选中的文件（谨慎操作）"
        )

    with batch_col4:
        st.markdown(f'<div style="padding:10px;text-align:right;color:#6B7280;font-size:13px;">'
                   f'共 <strong style="color:#2563EB;">{len(files_to_show)}</strong> 个文件 | '
                   f'总大小 <strong style="color:#059669;">{sum(f.stat().st_size for f in files_to_show) / 1024:.1f} KB</strong>'
                   f'</div>', unsafe_allow_html=True)

    st.markdown("---")

    # ===== 文件列表展示区 - 增强版 =====
    for idx, file_path in enumerate(files_to_show[:30]):
        try:
            file_size = file_path.stat().st_size
            mod_time = datetime.fromtimestamp(file_path.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            suffix = file_path.suffix.lower()

            # 文件类型图标映射
            if suffix in ['.log', '.txt']:
                icon = '📝'
                color_tag = '#3B82F6'
                type_name = '日志文件'
            elif suffix == '.json':
                icon = '📋'
                color_tag = '#F59E0B'
                type_name = 'JSON数据'
            elif suffix in ['.md', '.html']:
                icon = '📊'
                color_tag = '#8B5CF6'
                type_name = '分析报告'
            elif suffix in ['.csv', '.xlsx']:
                icon = '📈'
                color_tag = '#059669'
                type_name = '表格数据'
            else:
                icon = '📄'
                color_tag = '#6B7280'
                type_name = '其他文件'

            # 文件卡片头部
            file_header_html = f'''
            <div style="background:linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%);
                        border:1px solid #E5E7EB;border-left:4px solid {color_tag};
                        border-radius:10px;padding:16px 20px;margin:8px 0;
                        box-shadow:0 2px 6px rgba(0,0,0,0.04);
                        transition:all 0.3s ease;">
                <div style="display:flex;align-items:center;justify-content:space-between;">
                    <div style="display:flex;align-items:center;gap:12px;">
                        <div style="width:44px;height:44px;background:{color_tag}15;
                                    border-radius:10px;display:flex;align-items:center;
                                    justify-content:center;font-size:22px;">
                            {icon}
                        </div>
                        <div>
                            <div style="font-size:16px;font-weight:600;color:#1E293B;display:flex;align-items:center;gap:8px;">
                                {file_path.name}
                                <span style="font-size:11px;font-weight:500;background:{color_tag}20;
                                              color:{color_tag};padding:2px 8px;border-radius:4px;">
                                    {type_name}
                                </span>
                            </div>
                            <div style="font-size:13px;color:#6B7280;margin-top:4px;display:flex;gap:16px;">
                                <span>📅 {mod_time}</span>
                                <span>💾 {file_size / 1024:.2f} KB</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            '''
            st.markdown(file_header_html, unsafe_allow_html=True)

            # 选择框 + 操作按钮行
            sel_col, act_col1, act_col2, act_col3 = st.columns([0.5, 1.5, 1.5, 1.5])

            with sel_col:
                is_selected = st.checkbox("", value=st.session_state.get(f'report_file_{idx}', False),
                                          key=f'report_file_{idx}', label_visibility="collapsed")

            with act_col1:
                preview_button = st.button(f"👁️ 预览", use_container_width=True,
                                           key=f'preview_{idx}', help="在线查看文件内容")

            with act_col2:
                download_single = st.download_button(
                    label="⬇️ 下载",
                    data=open(file_path, 'rb').read(),
                    file_name=file_path.name,
                    mime="application/octet-stream",
                    use_container_width=True,
                    key=f'download_{idx}'
                )

            with act_col3:
                delete_button = st.button("🗑️ 删除", use_container_width=True,
                                         key=f'delete_{idx}', help="删除此文件（不可恢复）")

            # 预览功能实现
            if preview_button:
                if file_size < 10 * 1024 * 1024:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        if suffix == '.json':
                            try:
                                data = json.loads(content)
                                preview_content = json.dumps(data, ensure_ascii=False, indent=2)[:3000]
                            except:
                                preview_content = content[:3000]
                        else:
                            preview_content = content[:3000]

                        with st.expander(f"📂 {file_path.name} - 内容预览", expanded=True):
                            st.code(preview_content, language='json' if suffix == '.json' else None)

                        toast.success(f"✅ 已加载预览：{file_path.name}", duration=2000)

                    except Exception as e:
                        st.error(f"❌ 预览失败: {str(e)[:100]}")
                else:
                    st.warning("⚠️ 文件过大（>10MB），建议下载后本地查看")

            # 单个删除确认
            if delete_button:
                try:
                    file_path.unlink()
                    toast.success(f"🗑️ 已删除：{file_path.name}", duration=2000)
                    time.sleep(0.5)
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ 删除失败: {str(e)[:100]}")

        except Exception as e:
            st.error(f"❌ 读取文件出错: {str(e)[:100]}")

    # 批量下载处理
    if batch_download and (select_all or any(st.session_state.get(f'report_file_{i}', False) for i in range(len(files_to_show)))):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for idx, file_path in enumerate(files_to_show):
                if select_all or st.session_state.get(f'report_file_{idx}', False):
                    zipf.write(file_path, file_path.name)

        zip_buffer.seek(0)
        st.download_button(
            label="💾 下载打包文件",
            data=zip_buffer,
            file_name=f"reports_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
            mime="application/zip",
            key="batch_download_zip"
        )
        toast.success(f"📦 已准备 {len([f for f in files_to_show if select_all or st.session_state.get(f'report_file_{files_to_show.index(f)}', False)])} 个文件用于下载", duration=3000)

    # 批量删除处理
    if batch_delete and (select_all or any(st.session_state.get(f'report_file_{i}', False) for i in range(len(files_to_show)))):
        deleted_count = 0
        for idx, file_path in enumerate(files_to_show):
            if select_all or st.session_state.get(f'report_file_{idx}', False):
                try:
                    file_path.unlink()
                    deleted_count += 1
                except:
                    pass

        if deleted_count > 0:
            toast.success(f"🗑️ 成功删除 {deleted_count} 个文件", duration=2500)
            time.sleep(0.5)
            st.rerun()
        else:
            st.warning("⚠️ 没有可删除的文件")
