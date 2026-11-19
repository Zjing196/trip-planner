import json
import os
from html import escape

import altair as alt
import requests
import streamlit as st

st.set_page_config(page_title="AI Travel Companion", page_icon="🧸", layout="wide", initial_sidebar_state="collapsed")

ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL_ID = os.getenv("ARK_MODEL_ID", "")
ARK_API_KEY = os.getenv("ARK_API_KEY", "")
if not MODEL_ID or not ARK_API_KEY:
    try:
        if not MODEL_ID:
            MODEL_ID = st.secrets.get("ARK_MODEL_ID", "")
        if not ARK_API_KEY:
            ARK_API_KEY = st.secrets.get("ARK_API_KEY", "")
    except st.errors.StreamlitSecretNotFoundError:
        pass

TEXT = {
    "zh": {
        "title": "你好，周梦媛公主", "subtitle": "把想去的地方交给 AI，一起把旅程安排得从容又清晰。",
        "tab_import": "✈️  AI 对话", "tab_itinerary": "🧭  每日行程", "tab_progress": "✓  旅程进度",
        "tab_settings": "⚙️  设置", "settings_title": "偏好设置",
        "nav_itinerary": "每日行程", "nav_progress": "旅程进度", "nav_settings": "设置", "back_to_chat": "返回",
        "language_label": "界面语言", "language_help": "选择你偏好的界面显示语言。",
        "import_title": "你好，我是你的旅行搭子", "import_desc": "告诉我你想去哪、什么时候出发，我来帮你把旅程安排得轻松又清楚。",
        "placeholder": "聊聊你想去的地方、日期、预算或旅行偏好…",
        "chat_reply": "收到，我已经整理好这版行程啦。你可以继续告诉我想调整的地方，或去「每日行程」查看详情。",
        "missing_api": "请先在环境变量或 Streamlit secrets 中配置 ARK_API_KEY 和 ARK_MODEL_ID，再使用 AI 解析。",
        "waiting": "正在为你整理旅程，请稍候……", "parse_ok": "行程已准备好，去「每日行程」看看吧。",
        "parse_error": "行程解析失败", "configure": "配置说明：在环境变量或 Streamlit secrets 中设置 ARK_API_KEY 和 ARK_MODEL_ID。",
        "empty_plan": "先和 AI 聊聊你的旅行想法，生成后就会显示在这里。", "itinerary_title": "你的每日行程",
        "budget": "旅程预算参考（2 人）", "base_total": "基础预算", "emergency": "应急备用金",
        "grand_total": "预算总范围", "budget_excludes": "基础费用不包含机票和住宿费用；如有需要，可在「旅程费用」补充已支付费用。",
        "extra_costs": "补充已支付费用（选填）", "extra_costs_help": "填写基础预算未包含的已支付费用，将同时计入预计总消费和已支出；请勿在每日支出中重复登记。",
        "extra_transport": "额外交通费", "flight_cost": "机票费用", "accommodation_cost": "住宿费用",
        "day": "第 {} 天", "start": "出发地", "transport": "交通",
        "duration": "耗时", "cost": "费用", "ticket": "门票", "stay": "建议停留", "hours": "开放时间",
        "remark": "旅行提示", "progress_title": "把计划，一步步走成回忆", "progress_desc": "每完成一站就打个勾，随时查看旅程进度。",
        "done_count": "已完成", "left_count": "待完成", "completion": "完成率", "checklist": "旅程打卡",
        "completed": "已经完成", "remaining": "接下来要去", "no_items": "当前计划里还没有景点安排。",
        "all_done": "太棒了，这趟旅程的计划都完成啦！", "day_short": "第{}天",
        "expenses": "旅程费用", "planned_spend": "按计划预计",
        "expense_chart": "支出分类", "expense_chart_empty": "记录支出后，这里会显示分类占比。",
        "expense_chart_hint": "点击饼图查看分类详情。",
        "actual_spend": "已经消费", "projected_spend": "预计总消费",
        "expense_note": "预计总消费 = 第二模块预算总范围 + 补充已支付费用；已支出 = 每日支出 + 补充已支付费用。",
        "stop_expense": "景点打卡与支出",
        "add_expense": "记一笔", "expense_category": "支出类型",
        "expense_amount": "金额（元）", "expense_amount_required": "请填写大于 0 的金额，然后点击「记一笔」。",
        "save_expense": "添加支出", "no_expenses": "该景点还没有记录支出。",
        "delete_expense": "删除",
        "category_transport": "交通费", "category_ticket": "门票",
        "category_food": "吃饭", "category_other": "其他",
        "category_custom": "自定义", "custom_category_placeholder": "输入支出名称", "choose_category": "选择已有类型",
        "custom_category_required": "请输入自定义支出名称。",
        "checkin_action": "√ 点击打卡", "checked_action": "✓ 已完成",
    },
    "en": {
        "title": "Hello, Princess Zhou Mengyuan", "subtitle": "Share your ideas with AI and shape a trip that feels clear and unhurried.",
        "tab_import": "✈️  AI chat", "tab_itinerary": "🧭  Itinerary", "tab_progress": "✓  Trip progress",
        "tab_settings": "⚙️  Settings", "settings_title": "Preferences",
        "nav_itinerary": "Itinerary", "nav_progress": "Progress", "nav_settings": "Settings", "back_to_chat": "Back",
        "language_label": "Display language", "language_help": "Choose your preferred interface language.",
        "import_title": "Hi, I'm your travel buddy", "import_desc": "Tell me where you'd like to go and when. I'll help make the trip easy to follow.",
        "placeholder": "Where would you like to go? Share dates, budget, or travel style…",
        "chat_reply": "Your itinerary draft is ready. Tell me what you'd like to change, or open Itinerary to see the details.",
        "missing_api": "Set ARK_API_KEY and ARK_MODEL_ID in environment variables or Streamlit secrets to use AI planning.",
        "waiting": "Putting your trip together...", "parse_ok": "Your itinerary is ready. Explore it in Itinerary.",
        "parse_error": "Could not parse the itinerary", "configure": "Setup: add ARK_API_KEY and ARK_MODEL_ID to environment variables or Streamlit secrets.",
        "empty_plan": "Tell the AI about your trip and it will appear here once generated.", "itinerary_title": "Your day-by-day itinerary",
        "budget": "Estimated budget (2 travelers)", "base_total": "Base budget", "emergency": "Emergency reserve",
        "grand_total": "Estimated total", "budget_excludes": "Base budget excludes flights and accommodation. Add paid costs under Trip expenses if needed.",
        "extra_costs": "Additional paid costs (optional)", "extra_costs_help": "Add paid costs not included in the base budget. They count toward both the projected total and spent so far; do not record them again as daily expenses.",
        "extra_transport": "Additional transport", "flight_cost": "Flights", "accommodation_cost": "Accommodation",
        "day": "Day {}", "start": "Starting point", "transport": "Transport",
        "duration": "Duration", "cost": "Cost", "ticket": "Tickets", "stay": "Suggested stay", "hours": "Opening hours",
        "remark": "Travel notes", "progress_title": "Turn your plans into memories", "progress_desc": "Check off each stop as you go and keep an eye on your progress.",
        "done_count": "Completed", "left_count": "Remaining", "completion": "Complete", "checklist": "Trip checklist",
        "completed": "Done", "remaining": "Up next", "no_items": "There are no stops in this itinerary yet.",
        "all_done": "Wonderful! You have completed every planned stop.", "day_short": "Day {}",
        "expenses": "Trip expenses", "planned_spend": "Planned estimate",
        "expense_chart": "Spending breakdown", "expense_chart_empty": "Add expenses to see your spending breakdown.",
        "expense_chart_hint": "Tap a slice to see its details.",
        "actual_spend": "Spent so far", "projected_spend": "Projected total",
        "expense_note": "Projected total = itinerary budget range + additional paid costs; spent so far = daily expenses + additional paid costs.",
        "stop_expense": "Stop check-in & expenses",
        "add_expense": "Add", "expense_category": "Category",
        "expense_amount": "Amount (RMB)", "expense_amount_required": "Enter an amount greater than 0, then select Add.",
        "save_expense": "Add expense", "no_expenses": "No expenses recorded for this stop.",
        "delete_expense": "Delete",
        "category_transport": "Transport", "category_ticket": "Tickets",
        "category_food": "Food", "category_other": "Other",
        "category_custom": "Custom", "custom_category_placeholder": "Enter expense name", "choose_category": "Choose a category",
        "custom_category_required": "Enter a custom expense name.",
        "checkin_action": "√ Check in", "checked_action": "✓ Completed",
    },
    "id": {
        "title": "Halo, Putri Zhou Mengyuan", "subtitle": "Ceritakan keinginanmu kepada AI dan susun perjalanan yang nyaman dan jelas.",
        "tab_import": "✈️  Chat AI", "tab_itinerary": "🧭  Itinerary", "tab_progress": "✓  Progres perjalanan",
        "tab_settings": "⚙️  Pengaturan", "settings_title": "Preferensi",
        "nav_itinerary": "Itinerary", "nav_progress": "Progres", "nav_settings": "Pengaturan", "back_to_chat": "Kembali",
        "language_label": "Bahasa antarmuka", "language_help": "Pilih bahasa yang ingin digunakan di antarmuka.",
        "import_title": "Hai, aku teman perjalananmu", "import_desc": "Ceritakan tujuan dan tanggal perjalananmu. Aku akan membantu menyusun rencana yang nyaman.",
        "placeholder": "Mau pergi ke mana? Ceritakan tanggal, anggaran, atau gaya perjalananmu…",
        "chat_reply": "Draf itinerary sudah siap. Ceritakan apa yang ingin diubah, atau buka Itinerary untuk melihat detailnya.",
        "missing_api": "Atur ARK_API_KEY dan ARK_MODEL_ID di variabel lingkungan atau Streamlit secrets untuk menggunakan AI.",
        "waiting": "Sedang menyusun perjalananmu...", "parse_ok": "Itinerary siap. Lihat di halaman Itinerary.",
        "parse_error": "Gagal menguraikan itinerary", "configure": "Pengaturan: tambahkan ARK_API_KEY dan ARK_MODEL_ID ke variabel lingkungan atau Streamlit secrets.",
        "empty_plan": "Ceritakan ide perjalananmu kepada AI. Hasilnya akan muncul di sini.", "itinerary_title": "Itinerary harianmu",
        "budget": "Perkiraan anggaran (2 orang)", "base_total": "Anggaran dasar", "emergency": "Dana darurat",
        "grand_total": "Total perkiraan", "budget_excludes": "Anggaran dasar tidak termasuk tiket pesawat dan akomodasi. Tambahkan biaya yang sudah dibayar di Pengeluaran perjalanan jika perlu.",
        "extra_costs": "Biaya tambahan yang sudah dibayar (opsional)", "extra_costs_help": "Isi biaya yang sudah dibayar dan belum termasuk dalam anggaran dasar. Biaya ini masuk ke total perkiraan dan pengeluaran; jangan catat lagi sebagai pengeluaran harian.",
        "extra_transport": "Transportasi tambahan", "flight_cost": "Tiket pesawat", "accommodation_cost": "Akomodasi",
        "day": "Hari {}", "start": "Titik awal", "transport": "Transportasi",
        "duration": "Durasi", "cost": "Biaya", "ticket": "Tiket", "stay": "Durasi kunjungan", "hours": "Jam buka",
        "remark": "Catatan perjalanan", "progress_title": "Ubah rencana menjadi kenangan", "progress_desc": "Tandai setiap tempat yang sudah dikunjungi dan pantau progresmu.",
        "done_count": "Selesai", "left_count": "Belum selesai", "completion": "Selesai", "checklist": "Daftar perjalanan",
        "completed": "Sudah selesai", "remaining": "Berikutnya", "no_items": "Belum ada tempat dalam itinerary ini.",
        "all_done": "Hebat! Semua tempat yang direncanakan sudah selesai.", "day_short": "Hari {}",
        "expenses": "Pengeluaran perjalanan", "planned_spend": "Perkiraan rencana",
        "expense_chart": "Rincian pengeluaran", "expense_chart_empty": "Catat pengeluaran untuk melihat rinciannya.",
        "expense_chart_hint": "Ketuk bagian diagram untuk melihat rinciannya.",
        "actual_spend": "Sudah dibelanjakan", "projected_spend": "Perkiraan total",
        "expense_note": "Total perkiraan = rentang anggaran itinerary + biaya tambahan yang sudah dibayar; pengeluaran = pengeluaran harian + biaya tambahan yang sudah dibayar.",
        "stop_expense": "Check-in & pengeluaran tempat", "add_expense": "Tambah",
        "expense_category": "Jenis pengeluaran",
        "expense_amount": "Jumlah (RMB)", "expense_amount_required": "Masukkan jumlah lebih dari 0, lalu pilih Tambah.",
        "save_expense": "Tambah pengeluaran", "no_expenses": "Belum ada pengeluaran di tempat ini.",
        "delete_expense": "Hapus",
        "category_transport": "Transportasi", "category_ticket": "Tiket",
        "category_food": "Makanan", "category_other": "Lainnya",
        "category_custom": "Kustom", "custom_category_placeholder": "Masukkan nama pengeluaran", "choose_category": "Pilih jenis",
        "custom_category_required": "Masukkan nama pengeluaran khusus.",
        "checkin_action": "√ Tandai selesai", "checked_action": "✓ Selesai",
    },
}

st.markdown(
    """
    <style>
    .stApp {
      background:
        radial-gradient(circle at 8% 8%, rgba(255, 255, 255, .82), transparent 28%),
        radial-gradient(circle at 92% 18%, rgba(255, 213, 224, .66), transparent 32%),
        linear-gradient(135deg, #f8dff0 0%, #e4d8f8 46%, #f9e6d9 100%);
    }
    [data-testid="stHeader"] { background: rgba(255, 239, 247, .58); }
    .block-container { max-width: 1050px; padding: 3.5rem 1rem 5rem; }
    h1, h2, h3 { color: #30204f; letter-spacing: -.025em; }
    [data-testid="stSidebar"], [data-testid="stExpandSidebarButton"] { display: none !important; }
    .st-key-nav_itinerary button, .st-key-nav_progress button, .st-key-nav_settings button {
      min-height: 112px !important;
      display: flex;
      flex-direction: column;
      gap: .5rem;
      padding: .8rem .35rem;
      border: 1px solid rgba(255, 255, 255, .82);
      border-radius: 18px !important;
      background: linear-gradient(
        135deg,
        rgba(255,255,255,.66),
        rgba(255,245,251,.34)
      );
      color: #4b2b70;
      box-shadow:
        0 12px 28px rgba(126, 67, 151, .12),
        inset 0 1px 0 rgba(255,255,255,.96),
        inset 0 -1px 0 rgba(255,255,255,.35);
      backdrop-filter: blur(24px) saturate(140%);
      -webkit-backdrop-filter: blur(24px) saturate(140%);
    }
    .st-key-nav_itinerary button:hover, .st-key-nav_progress button:hover, .st-key-nav_settings button:hover {
      border-color: #ff8db0;
      background: linear-gradient(
        135deg,
        rgba(255,255,255,.8),
        rgba(255,220,236,.56)
      );
      color: #e83f72;
    }
    .st-key-nav_itinerary button [data-testid="stIconMaterial"],
    .st-key-nav_progress button [data-testid="stIconMaterial"],
    .st-key-nav_settings button [data-testid="stIconMaterial"] { font-size: 2rem; }
    .st-key-nav_itinerary button [data-has-shortcut],
    .st-key-nav_progress button [data-has-shortcut],
    .st-key-nav_settings button [data-has-shortcut] {
      display: flex;
      flex-direction: column;
      justify-content: center;
      gap: .45rem;
      white-space: normal;
      text-align: center;
    }
    .st-key-return_to_chat {
      position: fixed;
      right: max(1rem, env(safe-area-inset-right));
      bottom: max(1rem, env(safe-area-inset-bottom));
      z-index: 1000;
      width: auto !important;
    }
    .st-key-return_to_chat button {
      min-height: 48px !important;
      border-radius: 18px !important;
      background: #ff4f81;
      border-color: #ff4f81;
      color: white;
      box-shadow: 0 6px 18px rgba(255, 79, 129, .25);
    }
    .st-key-return_to_chat button:hover { background: #e83f72; border-color: #e83f72; color: white; }
    [data-testid="stMetric"] { background: rgba(255,255,255,.9); border: 1px solid #f2d8e6; border-radius: 18px; padding: 16px 18px; }
    div.stButton > button[kind="primary"] { background: #ff4f81; border-color: #ff4f81; border-radius: 14px; padding: .65rem 1.15rem; }
    div.stButton > button[kind="primary"]:hover { background: #e83f72; border-color: #e83f72; }
    div[data-testid="stButton"] > button[kind="primary"] { color: #fff !important; }
    div[data-testid="stButton"] > button { min-height: 2.8rem; border-radius: 14px; }
    [data-testid="stChatMessage"] { background: rgba(255,255,255,.92); border: 1px solid #f0dcec; border-radius: 18px; padding: .9rem 1rem; }
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) { background: #fff0f6; border-color: #ffd2e2; }
    [data-testid="stChatInput"] { background: white; border: 1px solid #f2d4e5; border-radius: 18px; box-shadow: 0 8px 26px rgba(126, 67, 151, .1); }
    [data-testid="stChatInputTextArea"] { min-height: 100px !important; }
    .chat-welcome { background: linear-gradient(135deg, #ffe1ec, #e9ddff); border: 1px solid #f2cfe2; border-radius: 28px; padding: 1.8rem; margin: .5rem 0 1.5rem; box-shadow: 0 12px 30px rgba(126, 67, 151, .12); }
    .chat-badge { color: #e83f72; font-size: .82rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; }
    .expense-chart-legend { display: grid; gap: .55rem; }
    .expense-chart-row { display: flex; align-items: flex-start; gap: .45rem; color: #5e4778; font-size: .85rem; line-height: 1.35; }
    .expense-chart-dot { flex: 0 0 10px; height: 10px; border-radius: 50%; margin-top: .25rem; }
    .expense-chart-name { flex: 1 1 auto; min-width: 0; overflow-wrap: anywhere; }
    .expense-chart-value { flex: 0 0 auto; text-align: right; white-space: nowrap; }
    .expense-analysis-title {
      margin: .15rem 0 .7rem;
      color: #4b2b70;
      font-size: 1.05rem;
      font-weight: 800;
    }
    .expense-analysis-total {
      margin: 0 0 .85rem;
      color: #4b2b70;
      font-size: 1.65rem;
      font-weight: 800;
    }
    .expense-analysis-total small {
      display: block;
      margin-top: .15rem;
      color: #806b91;
      font-size: .78rem;
      font-weight: 500;
    }
    .expense-donut {
      display: block;
      width: min(100%, 220px);
      height: auto;
      margin: .15rem auto .3rem;
      overflow: visible;
    }
    [data-testid="stVegaLiteChart"] {
      padding: .35rem;
      border-radius: 20px;
      background: transparent !important;
    }
    div[data-testid="stExpander"] {
      border: 1px solid #ecd8ef;
      border-radius: 22px;
      overflow: hidden;
      background: linear-gradient(135deg, rgba(255,255,255,.62), rgba(255,247,251,.34));
      backdrop-filter: blur(24px) saturate(135%);
      -webkit-backdrop-filter: blur(24px) saturate(135%);
      box-shadow:
        0 14px 32px rgba(126, 67, 151, .12),
        inset 0 1px 0 rgba(255,255,255,.94),
        inset 0 -1px 0 rgba(255,255,255,.32);
    }
    div[data-testid="stExpander"] details summary {
      padding: .9rem 1rem;
      background: rgba(255, 245, 250, .82);
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
      border-radius: 20px;
      border: 1px solid rgba(255,255,255,.78);
      background: linear-gradient(135deg, rgba(255,255,255,.66), rgba(255,248,252,.32));
      backdrop-filter: blur(24px) saturate(140%);
      -webkit-backdrop-filter: blur(24px) saturate(140%);
      box-shadow:
        0 12px 28px rgba(126, 67, 151, .1),
        inset 0 1px 0 rgba(255,255,255,.95),
        inset 0 -1px 0 rgba(255,255,255,.3);
    }
    [data-testid="stAlert"] {
      border-radius: 18px;
      border-width: 1px;
    }
    [data-testid="stProgress"] > div {
      border-radius: 999px;
      overflow: hidden;
    }
    [data-testid="stMetric"] {
      box-shadow: 0 8px 20px rgba(126, 67, 151, .07);
    }
    @media (max-width: 640px) {
      .block-container { padding: 4rem .8rem 6rem; }
      [data-testid="stMain"] h1 { font-size: clamp(1.6rem, 6.2vw, 2rem) !important; line-height: 1.15; }
      [data-testid="stMain"] h2 { font-size: clamp(1.35rem, 5.2vw, 1.7rem) !important; line-height: 1.2; }
      [data-testid="stMain"] h3 { font-size: 1.3rem !important; line-height: 1.25; }
      .chat-welcome { border-radius: 20px; padding: 1.2rem; }
      [data-testid="stHorizontalBlock"]:has(.st-key-nav_itinerary) > [data-testid="stColumn"] {
        flex: 1 1 0% !important;
        width: 0 !important;
        min-width: 0 !important;
      }
      [data-testid="stMetric"] { padding: 12px; }
      [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) {
        flex-wrap: nowrap !important;
      }
      [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"])
        > [data-testid="stColumn"] {
        min-width: 0 !important;
        width: 0 !important;
        flex: 1 1 0% !important;
      }
      [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"])
        [data-testid="stMetricValue"] {
        white-space: nowrap !important;
        font-size: clamp(1.25rem, 6vw, 2rem) !important;
      }
      [data-testid="stHorizontalBlock"]:has([data-testid="stVegaLiteChart"]) {
        flex-wrap: nowrap !important;
      }
      [data-testid="stHorizontalBlock"]:has([data-testid="stVegaLiteChart"])
        > [data-testid="stColumn"] {
        min-width: 0 !important;
        width: 0 !important;
        flex: 1 1 0% !important;
      }
      [data-testid="stChatInput"] {
        width: 100% !important;
        max-width: 100% !important;
        left: 0 !important;
        right: 0 !important;
      }
      [data-testid="stChatInputTextArea"] {
        width: 100% !important;
        min-height: 100px !important;
      }
      [data-testid="stHorizontalBlock"]:has(.st-key-chat_composer) {
        display: block !important;
      }
      [data-testid="stHorizontalBlock"]:has(.st-key-chat_composer) > [data-testid="stColumn"] {
        width: 100% !important;
        flex: 1 1 100% !important;
      }
      [data-testid="stHorizontalBlock"]:has(.st-key-chat_composer)
        > [data-testid="stColumn"]:not(:has(.st-key-chat_composer)) {
        display: none !important;
      }
      [data-testid="stHorizontalBlock"]:has([class*="st-key-checkin_button_"]) {
        flex-wrap: nowrap !important;
      }
      [data-testid="stHorizontalBlock"]:has([class*="st-key-checkin_button_"])
        > [data-testid="stColumn"] {
        min-width: 0 !important;
        flex: 1 1 0% !important;
        width: 0 !important;
        overflow: hidden !important;
      }
      [data-testid="stHorizontalBlock"]:has([class*="st-key-checkin_button_"])
        > [data-testid="stColumn"]:first-child p,
      [data-testid="stHorizontalBlock"]:has([class*="st-key-checkin_button_"])
        > [data-testid="stColumn"]:first-child h4 {
        max-width: 100% !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        word-break: break-word !important;
      }
      [data-testid="stForm"] [data-testid="stHorizontalBlock"],
      [data-testid="stHorizontalBlock"]:has([class*="st-key-expense_category_"]),
      [data-testid="stHorizontalBlock"]:has([class*="st-key-delete_expense_"]) {
        flex-wrap: nowrap !important;
      }
      [data-testid="stForm"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
      [data-testid="stHorizontalBlock"]:has([class*="st-key-expense_category_"])
        > [data-testid="stColumn"],
      [data-testid="stHorizontalBlock"]:has([class*="st-key-delete_expense_"])
        > [data-testid="stColumn"] {
        min-width: 0 !important;
        flex: 1 1 0% !important;
        width: 0 !important;
      }
      [data-testid="stHorizontalBlock"]:has([class*="st-key-delete_expense_"])
        > [data-testid="stColumn"]:nth-child(1) {
        flex: 1 1 0% !important;
      }
      [data-testid="stHorizontalBlock"]:has([class*="st-key-delete_expense_"])
        > [data-testid="stColumn"]:nth-child(2) {
        flex: 1 1 0% !important;
      }
      [data-testid="stHorizontalBlock"]:has([class*="st-key-delete_expense_"])
        > [data-testid="stColumn"]:nth-child(3) {
        flex: .35 1 0% !important;
      }
      [data-testid="stHorizontalBlock"]:has([class*="st-key-delete_expense_"])
        p {
        white-space: nowrap;
      }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "language" not in st.session_state:
    st.session_state["language"] = "zh"
lang = st.session_state["language"]
T = TEXT[lang]

for state_key, default in (
    ("trip_data", []),
    ("budget_data", {}),
    ("trip_revision", 0),
    ("chat_history", []),
    ("travel_expenses", []),
    ("next_expense_id", 1),
    ("extra_trip_costs", {"transport": 0.0, "flight": 0.0, "accommodation": 0.0}),
    ("active_module", "chat"),
):
    if state_key not in st.session_state:
        st.session_state[state_key] = default

if st.query_params.get("demo") == "1" and not st.session_state["trip_data"]:
    st.session_state["trip_data"] = [
        {
            "day_no": 1,
            "date_text": "2027-01-01",
            "start_location": "上海人民广场",
            "plan_items": [
                {
                    "start_time": "09:00",
                    "place_cn": "外滩",
                    "place_en": "The Bund",
                    "transport": "步行",
                    "trans_duration": "20 分钟",
                    "trans_cost": "0 元/人",
                    "ticket": "无需门票",
                    "stay_duration": "2.5 小时",
                    "opening_hour": "全天",
                    "remark": "欣赏外滩万国建筑博览群，建议傍晚前往观赏夜景。",
                    "is_done": True,
                },
                {
                    "start_time": "12:00",
                    "place_cn": "东方明珠广播电视塔",
                    "place_en": "Oriental Pearl Tower",
                    "transport": "地铁 2 号线",
                    "trans_duration": "15 分钟",
                    "trans_cost": "5 元/人",
                    "ticket": "199 元/人",
                    "stay_duration": "2 小时",
                    "opening_hour": "08:00 - 21:30",
                    "remark": "建议提前线上购票，避开周末高峰时段。",
                },
            ],
        },
        {
            "day_no": 2,
            "date_text": "2027-01-02",
            "start_location": "上海人民广场",
            "plan_items": [
                {
                    "start_time": "09:30",
                    "place_cn": "豫园",
                    "place_en": "Yu Garden",
                    "transport": "地铁 10 号线",
                    "trans_duration": "25 分钟",
                    "trans_cost": "4 元/人",
                    "ticket": "40 元/人",
                    "stay_duration": "2 小时",
                    "opening_hour": "09:00 - 16:30",
                    "remark": "适合上午游览，园内亭台楼阁和江南园林景观很有特色。",
                }
            ],
        },
    ]
    st.session_state["budget_data"] = {
        "subtotal_min": 680,
        "subtotal_max": 980,
        "emergency": 100,
        "grand_min": 780,
        "grand_max": 1080,
    }
    st.session_state["travel_expenses"] = [
        {"id": 1, "day_index": 0, "item_index": 0, "category": "food", "amount": 32.0},
        {"id": 2, "day_index": 0, "item_index": 1, "category": "ticket", "amount": 199.0},
    ]
    st.session_state["next_expense_id"] = 3
    st.session_state["trip_revision"] += 1
    requested_module = st.query_params.get("module")
    if requested_module in ("itinerary", "progress"):
        st.session_state["active_module"] = requested_module

if st.session_state["active_module"] in ("chat", "settings"):
    st.title(f"🧸 {T['title']}")
    st.caption(T["subtitle"])

if st.session_state["active_module"] != "chat":
    if st.button(T["back_to_chat"], key="return_to_chat", icon=":material/arrow_back:"):
        st.session_state["active_module"] = "chat"
        st.rerun()


def parse_full_itinerary(text, language):
    display_language = {"zh": "Chinese", "en": "English", "id": "Indonesian"}[language]
    system_prompt = f"""
You are a professional travel itinerary planner. The user may provide a long request in Chinese,
English, Indonesian, or a mixture. Return valid JSON only, with no markdown or extra text.
Use {display_language} for explanatory content and remarks. Include localized place names in
place_cn (Chinese), place_en (English), and place_id (Indonesian).

JSON structure:
{{
  "itinerary_list": [
    {{
      "day_no": 1,
      "date_text": "25 Des 2026",
      "start_location": "starting point",
      "plan_items": [
        {{
          "start_time": "08:00", "place_cn": "中文名称",
          "place_en": "English name", "place_id": "Nama Indonesia",
          "transport": "Metro / Bus / Taxi / Walk", "trans_duration": "30 min",
          "trans_cost": "150 RMB/person", "ticket": "120 RMB/person or no ticket",
          "stay_duration": "2 hours", "opening_hour": "07:00 - 22:00",
          "remark": "Important tips or optional status"
        }}
      ]
    }}
  ],
  "budget_summary": {{
    "paid": [{{"name":"item","cost":100}}],
    "unpaid_mandatory": [{{"name":"item","cost_min":100,"cost_max":200}}],
    "unpaid_optional": [{{"name":"item","cost_min":100,"cost_max":200}}],
    "subtotal_min": 200, "subtotal_max": 400, "emergency": 100,
    "grand_min": 300, "grand_max": 500
  }}
}}

Respect fixed travel times, include required places, mark optional stops, group nearby places,
and order stops by visit time. Use RMB for the two-person budget and label per-person prices.
Mark uncertain opening hours or prices as unconfirmed. Understand Indonesian travel instructions
such as departure point, opening hours, charter bus, and sleeping at the airport. Ensure every
string is valid JSON, escape embedded quotation marks, and do not truncate the JSON object.
"""
    headers = {"Authorization": f"Bearer {ARK_API_KEY}", "Content-Type": "application/json"}
     payload = {
        "model": MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "max_tokens": 4096
    }

    response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    choices = result.get("choices")
    if not isinstance(choices, list) or not choices:
        raise ValueError("AI response did not contain any choices.")
    choice = choices[0]
    if choice.get("finish_reason") == "length":
        raise ValueError(
            "AI output was truncated before the itinerary was complete. "
            "Try shortening the request or splitting it into fewer travel days."
        )
    content = choice["message"]["content"]
    if not isinstance(content, str):
        raise ValueError("AI response content must be a JSON string.")
    try:
        parsed = json.loads(content.strip())
    except json.JSONDecodeError as error:
        raise ValueError(
            "AI returned invalid JSON "
            f"(line {error.lineno}, column {error.colno}). "
            "Please try generating the itinerary again."
        ) from error
    if not isinstance(parsed, dict) or not isinstance(parsed.get("itinerary_list"), list):
        raise ValueError("AI response is missing an itinerary_list array.")
    for day in parsed["itinerary_list"]:
        if not isinstance(day, dict) or not isinstance(day.get("plan_items"), list):
            raise ValueError("Each itinerary day must contain a plan_items array.")
        if any(not isinstance(item, dict) for item in day["plan_items"]):
            raise ValueError("Every itinerary item must be a JSON object.")
    if not isinstance(parsed.get("budget_summary", {}), dict):
        raise ValueError("AI response budget_summary must be a JSON object.")
    return parsed


if st.session_state["active_module"] == "chat":
    if not st.session_state["chat_history"]:
        st.markdown(
            f"""
            <div class="chat-welcome">
              <div class="chat-badge">YOUR TRAVEL BUDDY</div>
              <h2>{T['import_title']}</h2>
              <p>{T['import_desc']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    chat_messages = st.container()
    spot_columns = st.columns([1.1, 0.9], gap="large", wrap=False)
    with spot_columns[0]:
        submitted_prompt = st.chat_input(T["placeholder"], key="chat_composer")

    navigation_columns = st.columns(3, gap="small", wrap=False)
    for column, module, icon in zip(
        navigation_columns,
        ("itinerary", "progress", "settings"),
        (":material/explore:", ":material/task_alt:", ":material/settings:"),
    ):
        if column.button(T[f"nav_{module}"], key=f"nav_{module}", icon=icon, width="stretch"):
            st.session_state["active_module"] = module
            st.rerun()

    if submitted_prompt:
        st.session_state["chat_history"].append(
            {"role": "user", "content": submitted_prompt}
        )
        if not ARK_API_KEY or not MODEL_ID:
            st.error(T["missing_api"])
            st.caption(T["configure"])
            st.session_state["chat_history"].append(
                {"role": "assistant", "content": T["missing_api"]}
            )
        else:
            try:
                previous_requests = [
                    message["content"]
                    for message in st.session_state["chat_history"][:-1]
                    if message["role"] == "user"
                ][-5:]
                conversation_context = "\n".join(
                    f"Previous request: {request}" for request in previous_requests
                )
                current_trip_context = (
                    "\nCurrent itinerary to refine:\n"
                    + json.dumps(st.session_state["trip_data"], ensure_ascii=False)
                    if st.session_state["trip_data"]
                    else ""
                )
                planner_request = (
                    f"{conversation_context}\n{current_trip_context}\n"
                    f"Latest request: {submitted_prompt}"
                ).strip()
                with st.spinner(T["waiting"]):
                    result = parse_full_itinerary(planner_request, lang)
                st.session_state["trip_data"] = result["itinerary_list"]
                st.session_state["budget_data"] = result.get("budget_summary", {})
                st.session_state["trip_revision"] += 1
                st.session_state["travel_expenses"] = []
                st.session_state["extra_trip_costs"] = {
                    "transport": 0.0,
                    "flight": 0.0,
                    "accommodation": 0.0,
                }
                st.success(T["parse_ok"])
                st.session_state["chat_history"].append(
                    {"role": "assistant", "content": T["chat_reply"]}
                )
            except (requests.RequestException, ValueError, KeyError, TypeError) as error:
                st.error(f"{T['parse_error']}: {error}")
                st.session_state["chat_history"].append(
                    {"role": "assistant", "content": f"{T['parse_error']}: {error}"}
                )

    with chat_messages:
        for message in st.session_state["chat_history"]:
            avatar = "✈️" if message["role"] == "assistant" else "🙂"
            with st.chat_message(message["role"], avatar=avatar):
                st.write(message["content"])


def save_language_preference():
    st.session_state["language"] = st.session_state["language_selector"]


if st.session_state["active_module"] == "settings":
    st.header(T["settings_title"])
    st.session_state["language_selector"] = lang
    st.selectbox(
        T["language_label"],
        ["zh", "en", "id"],
        format_func=lambda value: {"zh": "中文", "en": "English", "id": "Bahasa Indonesia"}[value],
        help=T["language_help"],
        key="language_selector",
        on_change=save_language_preference,
    )

trip = st.session_state["trip_data"]
budget = st.session_state["budget_data"]
place_fields = {"zh": "place_cn", "en": "place_en", "id": "place_id"}
revision = st.session_state["trip_revision"]
expense_categories = {
    "transport": T["category_transport"],
    "ticket": T["category_ticket"],
    "food": T["category_food"],
    "other": T["category_other"],
}


def render_item_expenses(day_index, item_index):
    day_expenses = [
        expense for expense in st.session_state["travel_expenses"]
        if expense["day_index"] == day_index and expense["item_index"] == item_index
    ]
    day_total = sum(expense["amount"] for expense in day_expenses)
    st.markdown(f"**{T['stop_expense']} · ¥{day_total:,.2f}**")
    form_key = f"expense_form_{revision}_{day_index}_{item_index}"
    category_key = f"expense_category_{revision}_{day_index}_{item_index}"
    custom_mode_key = f"custom_category_mode_{revision}_{day_index}_{item_index}"
    with st.container(border=True):
        if st.session_state.get(custom_mode_key, False):
            selected_category = st.text_input(
                T["expense_category"], placeholder=T["custom_category_placeholder"],
                key=f"custom_category_input_{revision}_{day_index}_{item_index}",
            )
            if st.button(
                T["choose_category"], key=f"choose_category_{revision}_{day_index}_{item_index}",
            ):
                st.session_state[custom_mode_key] = False
                st.session_state[category_key] = "transport"
                st.rerun()
            is_standard_category = False
        else:
            selected_category = st.selectbox(
                T["expense_category"], ["transport", "ticket", "food", "custom"],
                format_func=lambda value: (
                    T["category_custom"] if value == "custom" else expense_categories[value]
                ),
                key=category_key,
            )
            if selected_category == "custom":
                st.session_state[custom_mode_key] = True
                st.rerun()
            is_standard_category = True
        with st.form(form_key, clear_on_submit=True, border=False):
            amount = st.number_input(
                T["expense_amount"], min_value=0.0, step=1.0,
            )
            submitted = st.form_submit_button(T["add_expense"], use_container_width=True)
    if submitted:
        if amount <= 0:
            st.warning(T["expense_amount_required"])
        elif not selected_category or not selected_category.strip():
            st.warning(T["custom_category_required"])
        else:
            category = selected_category.strip()
            st.session_state["travel_expenses"].append({
                "id": st.session_state["next_expense_id"],
                "day_index": day_index,
                "item_index": item_index,
                "category": category if is_standard_category else "other",
                "custom_category": "" if is_standard_category else category,
                "amount": amount,
            })
            st.session_state["next_expense_id"] += 1
            st.rerun()

    if not day_expenses:
        st.caption(T["no_expenses"])
    for expense in day_expenses:
        expense_columns = st.columns([1, 0.8, 0.35])
        category_label = expense_categories[expense["category"]]
        if expense["category"] == "other" and expense.get("custom_category"):
            category_label = expense["custom_category"]
        expense_columns[0].write(category_label)
        expense_columns[1].write(f"¥{expense['amount']:,.2f}")
        if expense_columns[2].button(
            "×", key=f"delete_expense_{revision}_{expense['id']}", help=T["delete_expense"],
        ):
            st.session_state["travel_expenses"] = [
                entry for entry in st.session_state["travel_expenses"] if entry["id"] != expense["id"]
            ]
            st.rerun()

if st.session_state["active_module"] == "itinerary":
    st.header(T["itinerary_title"])
    if not trip:
        st.info(T["empty_plan"])
    else:
        for day_index, day_data in enumerate(trip):
            day_title = T["day"].format(day_data.get("day_no", day_index + 1))
            date_text = day_data.get("date_text", "")
            start_location = day_data.get("start_location", "")
            header_parts = [part for part in (day_title, date_text) if part]
            if start_location:
                header_parts.append(f"{T['start']}: {start_location}")
            with st.expander(" · ".join(header_parts), expanded=True):
                items = day_data.get("plan_items", [])
                for item_index, item in enumerate(items):
                    place = item.get(place_fields[lang]) or item.get("place_en") or item.get("place_cn", "")
                    spot_columns = st.columns([1.1, 0.9], gap="large", wrap=False)
                    with spot_columns[0]:
                        st.markdown(f"#### ⏰ {item.get('start_time', '')}  ·  {place}")
                        st.write(
                            f"🚗 {T['transport']}: {item.get('transport', '—')}  ·  "
                            f"{T['duration']}: {item.get('trans_duration', '—')}  ·  "
                            f"{T['cost']}: {item.get('trans_cost', '—')}"
                        )
                        st.write(
                            f"🎫 {T['ticket']}: {item.get('ticket', '—')}  ·  "
                            f"🕰️ {T['stay']}: {item.get('stay_duration', '—')}  ·  "
                            f"{T['hours']}: {item.get('opening_hour', '—')}"
                        )
                        if item.get("remark"):
                            st.caption(f"🌱 {T['remark']}: {item['remark']}")
                        key = f"done_{revision}_{day_index}_{item_index}"
                        is_done = st.session_state.get(key, bool(item.get("is_done", False)))
                        if st.button(
                            T["checked_action"] if is_done else T["checkin_action"],
                            key=f"checkin_button_{revision}_{day_index}_{item_index}",
                            type="primary" if is_done else "secondary",
                        ):
                            st.session_state[key] = not is_done
                            st.rerun()
                    with spot_columns[1]:
                        render_item_expenses(day_index, item_index)
                    st.divider()

if st.session_state["active_module"] == "progress":
    st.header(T["progress_title"])
    st.write(T["progress_desc"])
    all_items = [
        (day_index, item_index, day_data, item)
        for day_index, day_data in enumerate(trip)
        for item_index, item in enumerate(day_data.get("plan_items", []))
    ]
    if not all_items:
        st.info(T["no_items"])
    else:
        total = len(all_items)
        completed_items = []
        remaining_items = []
        actual_total = sum(expense["amount"] for expense in st.session_state["travel_expenses"])

        if budget:
            st.info(
                f"{T['base_total']}: {budget.get('subtotal_min', '—')} – "
                f"{budget.get('subtotal_max', '—')} RMB  ·  "
                f"{T['emergency']}: {budget.get('emergency', '—')} RMB  ·  "
                f"{T['grand_total']}: {budget.get('grand_min', '—')} – "
                f"{budget.get('grand_max', '—')} RMB"
            )
            st.caption(T["budget_excludes"])

        st.subheader(T["expenses"])
        extra_costs = st.session_state["extra_trip_costs"]
        with st.expander(T["extra_costs"]):
            st.caption(T["extra_costs_help"])
            extra_cost_columns = st.columns(3)
            extra_cost_columns[0].number_input(
                T["extra_transport"],
                min_value=0.0,
                step=50.0,
                value=float(extra_costs.get("transport", 0.0)),
                key=f"extra_transport_{revision}",
            )
            extra_cost_columns[1].number_input(
                T["flight_cost"],
                min_value=0.0,
                step=100.0,
                value=float(extra_costs.get("flight", 0.0)),
                key=f"extra_flight_{revision}",
            )
            extra_cost_columns[2].number_input(
                T["accommodation_cost"],
                min_value=0.0,
                step=100.0,
                value=float(extra_costs.get("accommodation", 0.0)),
                key=f"extra_accommodation_{revision}",
            )
        extra_costs = {
            "transport": st.session_state[f"extra_transport_{revision}"],
            "flight": st.session_state[f"extra_flight_{revision}"],
            "accommodation": st.session_state[f"extra_accommodation_{revision}"],
        }
        st.session_state["extra_trip_costs"] = extra_costs
        extra_total = sum(extra_costs.values())
        actual_total += extra_total

        projected_min = budget.get("grand_min")
        projected_max = budget.get("grand_max")
        if isinstance(projected_min, (int, float)) and isinstance(projected_max, (int, float)):
            projected_min += extra_total
            projected_max += extra_total
        else:
            projected_min = projected_max = None

        projected_display = (
            f"¥{projected_min:,.0f}–{projected_max:,.0f}"
            if projected_min is not None and projected_max is not None
            else "—"
        )
        expense_metrics = st.columns(2, gap="large")
        expense_metrics[0].metric(T["projected_spend"], projected_display)
        expense_metrics[1].metric(T["actual_spend"], f"¥{actual_total:,.2f}")
        for day_index, item_index, day_data, item in all_items:
            key = f"done_{revision}_{day_index}_{item_index}"
            is_done = st.session_state.get(key, bool(item.get("is_done", False)))
            place = item.get(place_fields[lang]) or item.get("place_en") or item.get("place_cn", "")
            day_number = day_data.get("day_no", day_index + 1)
            label = f"{item.get('start_time', '')}  ·  {place}"
            summary = f"{T['day_short'].format(day_number)} · {label}"
            (completed_items if is_done else remaining_items).append(summary)

        completed = len(completed_items)
        ratio = completed / total
        metric_columns = st.columns(3)
        metric_columns[0].metric(T["done_count"], f"{completed} / {total}")
        metric_columns[1].metric(T["left_count"], total - completed)
        metric_columns[2].metric(T["completion"], f"{ratio:.0%}")
        st.progress(ratio)
        status_columns = st.columns(2)
        with status_columns[0]:
            st.markdown(f"**✅ {T['completed']}**")
            for item in completed_items:
                st.write(f"• {item}")
            if not completed_items:
                st.caption("—")
        with status_columns[1]:
            st.markdown(f"**🌿 {T['remaining']}**")
            for item in remaining_items:
                st.write(f"• {item}")
            if not remaining_items:
                st.success(T["all_done"])

        st.subheader(T["expense_chart"])
        category_totals = {}
        for expense in st.session_state["travel_expenses"]:
            category = expense_categories[expense["category"]]
            if expense["category"] == "other" and expense.get("custom_category"):
                category = expense["custom_category"]
            category_totals[category] = category_totals.get(category, 0.0) + expense["amount"]
        for key, label in (
            ("transport", T["category_transport"]),
            ("flight", T["flight_cost"]),
            ("accommodation", T["accommodation_cost"]),
        ):
            if extra_costs[key] > 0:
                category_totals[label] = category_totals.get(label, 0.0) + extra_costs[key]

        if actual_total <= 0:
            st.caption(T["expense_chart_empty"])
        else:
            colors = ("#ff4f81", "#8b5cf6", "#22c7a8", "#ffc857", "#5ec8ff", "#ff8f70")
            legend = []
            chart_data = []
            for index, (category, amount) in enumerate(category_totals.items()):
                percentage = amount / actual_total * 100
                color = colors[index % len(colors)]
                chart_data.append({"category": category, "amount": amount, "percentage": percentage})
                legend.append(
                    f'<div class="expense-chart-row"><span class="expense-chart-dot" style="background:{color}"></span>'
                    f'<span class="expense-chart-name">{escape(category)}</span>'
                    f'<span class="expense-chart-value">¥{amount:,.2f} · {percentage:.1f}%</span></div>'
                )
            selection = alt.selection_point(fields=["category"], name="category_selection")
            chart_source = alt.Chart(alt.Data(values=chart_data))
            shadow_chart = (
                chart_source
                .mark_arc(innerRadius=58, outerRadius=104, color="#8b5cf6", opacity=.18)
                .encode(theta=alt.Theta("amount:Q"))
            )
            main_chart = (
                chart_source
                .mark_arc(
                    innerRadius=58,
                    outerRadius=94,
                    cornerRadius=12,
                    padAngle=.025,
                    stroke="#fff4fb",
                    strokeWidth=2,
                )
                .encode(
                    theta=alt.Theta("amount:Q"),
                    color=alt.Color(
                        "category:N",
                        scale=alt.Scale(
                            domain=list(category_totals),
                            range=[colors[i % len(colors)] for i in range(len(category_totals))],
                        ),
                        legend=None,
                    ),
                    opacity=alt.condition(selection, alt.value(1), alt.value(.9)),
                    tooltip=[
                        alt.Tooltip("category:N", title=T["expense_category"]),
                        alt.Tooltip("amount:Q", title=T["expense_amount"], format=",.2f"),
                        alt.Tooltip("percentage:Q", title="%", format=".1f"),
                    ],
                )
                .add_params(selection)
            )
            center_chart = (
                alt.Chart(alt.Data(values=[{"label": f"¥{actual_total:,.0f}"}]))
                .mark_text(fontSize=21, fontWeight="bold", color="#4b2b70")
                .encode(text="label:N")
            )
            chart = (
                alt.layer(shadow_chart, main_chart, center_chart)
                .properties(height=260)
                .configure(background="transparent")
                .configure_view(stroke=None)
            )
            with st.container(border=True):
                st.caption(T["expense_chart_hint"])
                event = st.altair_chart(
                    chart,
                    width="stretch",
                    theme=None,
                    key=f"expense_chart_{revision}",
                    on_select="rerun",
                    selection_mode="category_selection",
                )
                selected = event.selection.get("category_selection", [])
                st.html(
                    f'<div class="expense-analysis-total">¥{actual_total:,.2f}'
                    f'<small>{escape(T["actual_spend"])}</small></div>'
                    f'<div class="expense-chart-legend">{"".join(legend)}</div>'
                )
                if selected:
                    selected_category = selected[0].get("category")
                    if selected_category in category_totals:
                        amount = category_totals[selected_category]
                        st.success(
                            f"{selected_category}: ¥{amount:,.2f} · "
                            f"{amount / actual_total:.1%}"
                        )
