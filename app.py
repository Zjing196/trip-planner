import json
import os

import requests
import streamlit as st

st.set_page_config(page_title="AI Travel Companion", page_icon="🌿", layout="wide")

ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
MODEL_ID = os.getenv("ARK_MODEL_ID", "")
ARK_API_KEY = os.getenv("ARK_API_KEY", "")

TEXT = {
    "zh": {
        "title": "慢游 · 旅行计划", "subtitle": "把想去的地方交给 AI，一起把旅程安排得从容又清晰。",
        "tab_import": "01  计划导入", "tab_itinerary": "02  每日行程", "tab_progress": "03  旅程进度",
        "import_title": "从一段想法，开始一场旅行", "import_desc": "上传 TXT / Markdown 计划，或直接粘贴中文、英文、印尼语行程需求。",
        "upload": "导入旅行计划（TXT / MD）", "prompt": "告诉 AI 这趟旅行的想法",
        "placeholder": "例如：计划在哈尔滨旅行 3 天，喜欢自然风光和当地美食……",
        "parse": "✨ 生成我的旅行计划", "missing_api": "请先配置 ARK_API_KEY 和 ARK_MODEL_ID 环境变量，再使用 AI 解析。",
        "waiting": "正在为你整理旅程，请稍候……", "parse_ok": "行程已准备好，去「每日行程」看看吧。",
        "parse_error": "行程解析失败", "configure": "配置说明：在系统环境变量中设置 ARK_API_KEY 和 ARK_MODEL_ID。",
        "empty_plan": "先导入或粘贴旅行计划，再点击生成。", "itinerary_title": "你的每日行程",
        "budget": "旅程预算参考（2 人）", "paid": "已支付", "mandatory": "待支付 · 必选",
        "optional": "待支付 · 可选", "base_total": "基础预算", "emergency": "应急备用金",
        "grand_total": "预算总范围", "day": "第 {} 天", "start": "出发地", "transport": "交通",
        "duration": "耗时", "cost": "费用", "ticket": "门票", "stay": "建议停留", "hours": "开放时间",
        "remark": "旅行提示", "progress_title": "把计划，一步步走成回忆", "progress_desc": "每完成一站就打个勾，随时查看旅程进度。",
        "done_count": "已完成", "left_count": "待完成", "completion": "完成率", "checklist": "旅程打卡",
        "completed": "已经完成", "remaining": "接下来要去", "no_items": "当前计划里还没有景点安排。",
        "all_done": "太棒了，这趟旅程的计划都完成啦！", "day_short": "第{}天",
        "expenses": "旅程费用", "planned_spend": "按计划预计",
        "actual_spend": "已经消费", "projected_spend": "预计总消费",
        "expense_note": "预计总消费与每日行程中的预算总范围一致；已支出为你记录的实际消费合计。",
        "daily_expense": "每日打卡与支出", "add_expense": "记一笔",
        "expense_place": "关联景点", "expense_category": "支出类型",
        "expense_amount": "金额（元）",
        "save_expense": "添加支出", "no_expenses": "今天还没有记录支出。",
        "delete_expense": "删除", "unlinked_place": "不关联景点",
        "category_transport": "交通费", "category_ticket": "门票",
        "category_food": "吃饭", "category_other": "其他",
        "checkin_action": "√ 点击打卡", "checked_action": "✓ 已完成",
    },
    "en": {
        "title": "Slow Days · Trip Planner", "subtitle": "Share your ideas with AI and shape a trip that feels clear and unhurried.",
        "tab_import": "01  Import plan", "tab_itinerary": "02  Itinerary", "tab_progress": "03  Trip progress",
        "import_title": "Every journey starts with an idea", "import_desc": "Upload a TXT / Markdown plan, or paste your travel ideas in Chinese, English, or Indonesian.",
        "upload": "Import a trip plan (TXT / MD)", "prompt": "Tell AI about your trip",
        "placeholder": "For example: 3 days in Harbin, with nature, local food, and a relaxed pace...",
        "parse": "✨ Build my trip plan", "missing_api": "Set the ARK_API_KEY and ARK_MODEL_ID environment variables to use AI planning.",
        "waiting": "Putting your trip together...", "parse_ok": "Your itinerary is ready. Explore it in Itinerary.",
        "parse_error": "Could not parse the itinerary", "configure": "Setup: add ARK_API_KEY and ARK_MODEL_ID to your environment variables.",
        "empty_plan": "Import or paste a trip plan, then build your itinerary.", "itinerary_title": "Your day-by-day itinerary",
        "budget": "Estimated budget (2 travelers)", "paid": "Paid", "mandatory": "Unpaid · Essential",
        "optional": "Unpaid · Optional", "base_total": "Estimated subtotal", "emergency": "Emergency reserve",
        "grand_total": "Estimated total", "day": "Day {}", "start": "Starting point", "transport": "Transport",
        "duration": "Duration", "cost": "Cost", "ticket": "Tickets", "stay": "Suggested stay", "hours": "Opening hours",
        "remark": "Travel notes", "progress_title": "Turn your plans into memories", "progress_desc": "Check off each stop as you go and keep an eye on your progress.",
        "done_count": "Completed", "left_count": "Remaining", "completion": "Complete", "checklist": "Trip checklist",
        "completed": "Done", "remaining": "Up next", "no_items": "There are no stops in this itinerary yet.",
        "all_done": "Wonderful! You have completed every planned stop.", "day_short": "Day {}",
        "expenses": "Trip expenses", "planned_spend": "Planned estimate",
        "actual_spend": "Spent so far", "projected_spend": "Projected total",
        "expense_note": "Projected total matches the budget range in your itinerary; spent so far is the sum of recorded expenses.",
        "daily_expense": "Daily check-in & spending", "add_expense": "Add",
        "expense_place": "Related stop", "expense_category": "Category",
        "expense_amount": "Amount (RMB)",
        "save_expense": "Add expense", "no_expenses": "No expenses recorded today.",
        "delete_expense": "Delete", "unlinked_place": "No linked stop",
        "category_transport": "Transport", "category_ticket": "Tickets",
        "category_food": "Food", "category_other": "Other",
        "checkin_action": "√ Check in", "checked_action": "✓ Completed",
    },
    "id": {
        "title": "Hari Santai · Rencana Perjalanan", "subtitle": "Ceritakan keinginanmu kepada AI dan susun perjalanan yang nyaman dan jelas.",
        "tab_import": "01  Impor rencana", "tab_itinerary": "02  Itinerary", "tab_progress": "03  Progres perjalanan",
        "import_title": "Setiap perjalanan dimulai dari sebuah ide", "import_desc": "Unggah rencana TXT / Markdown, atau tempel ide perjalanan dalam bahasa Mandarin, Inggris, atau Indonesia.",
        "upload": "Impor rencana perjalanan (TXT / MD)", "prompt": "Ceritakan perjalananmu kepada AI",
        "placeholder": "Contoh: 3 hari di Harbin, suka alam, kuliner lokal, dan perjalanan santai...",
        "parse": "✨ Buat rencana perjalanan", "missing_api": "Atur variabel lingkungan ARK_API_KEY dan ARK_MODEL_ID untuk menggunakan AI.",
        "waiting": "Sedang menyusun perjalananmu...", "parse_ok": "Itinerary siap. Lihat di halaman Itinerary.",
        "parse_error": "Gagal menguraikan itinerary", "configure": "Pengaturan: tambahkan ARK_API_KEY dan ARK_MODEL_ID ke variabel lingkungan.",
        "empty_plan": "Impor atau tempel rencana perjalanan, lalu buat itinerary.", "itinerary_title": "Itinerary harianmu",
        "budget": "Perkiraan anggaran (2 orang)", "paid": "Sudah dibayar", "mandatory": "Belum dibayar · Wajib",
        "optional": "Belum dibayar · Opsional", "base_total": "Subtotal perkiraan", "emergency": "Dana darurat",
        "grand_total": "Total perkiraan", "day": "Hari {}", "start": "Titik awal", "transport": "Transportasi",
        "duration": "Durasi", "cost": "Biaya", "ticket": "Tiket", "stay": "Durasi kunjungan", "hours": "Jam buka",
        "remark": "Catatan perjalanan", "progress_title": "Ubah rencana menjadi kenangan", "progress_desc": "Tandai setiap tempat yang sudah dikunjungi dan pantau progresmu.",
        "done_count": "Selesai", "left_count": "Belum selesai", "completion": "Selesai", "checklist": "Daftar perjalanan",
        "completed": "Sudah selesai", "remaining": "Berikutnya", "no_items": "Belum ada tempat dalam itinerary ini.",
        "all_done": "Hebat! Semua tempat yang direncanakan sudah selesai.", "day_short": "Hari {}",
        "expenses": "Pengeluaran perjalanan", "planned_spend": "Perkiraan rencana",
        "actual_spend": "Sudah dibelanjakan", "projected_spend": "Perkiraan total",
        "expense_note": "Total perkiraan sama dengan rentang anggaran di itinerary; pengeluaran aktual adalah jumlah semua catatan pengeluaran.",
        "daily_expense": "Check-in & pengeluaran harian", "add_expense": "Tambah",
        "expense_place": "Tempat terkait", "expense_category": "Jenis pengeluaran",
        "expense_amount": "Jumlah (RMB)",
        "save_expense": "Tambah pengeluaran", "no_expenses": "Belum ada pengeluaran hari ini.",
        "delete_expense": "Hapus", "unlinked_place": "Tanpa tempat terkait",
        "category_transport": "Transportasi", "category_ticket": "Tiket",
        "category_food": "Makanan", "category_other": "Lainnya",
        "checkin_action": "√ Tandai selesai", "checked_action": "✓ Selesai",
    },
}

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #f3f8f3 0%, #fbfcf8 42%, #f8faf6 100%); }
    [data-testid="stHeader"] { background: rgba(243, 248, 243, .85); }
    .block-container { max-width: 1180px; padding-top: 2rem; }
    h1, h2, h3 { color: #23483c; letter-spacing: -.025em; }
    [data-testid="stTabs"] button { color: #526b60; font-weight: 600; }
    [data-testid="stTabs"] button[aria-selected="true"] { color: #26765b; border-bottom-color: #54a77e; }
    [data-testid="stMetric"] { background: rgba(255,255,255,.82); border: 1px solid #e3ece3; border-radius: 16px; padding: 16px 18px; }
    div.stButton > button[kind="primary"] { background: #347b5d; border-color: #347b5d; border-radius: 12px; padding: .65rem 1.15rem; }
    div.stButton > button[kind="primary"]:hover { background: #28664c; border-color: #28664c; }
    div[data-testid="stButton"] > button[kind="primary"] { color: #fff !important; }
    div[data-testid="stButton"] > button { min-height: 2.8rem; border-radius: 12px; }
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem;
            padding-right: 0.5rem;
            max-width: unset;
        }
        div[data-testid="stColumn"] {
            width:100% !important;
            flex: unset !important;
        }
        h1 {font-size:1.6rem;}
        h2 {font-size:1.3rem;}
    }
    </style>
    """,
    unsafe_allow_html=True,
)

lang = st.session_state.get("language", "zh")
T = TEXT[lang]

for state_key, default in (
    ("trip_data", []),
    ("budget_data", {}),
    ("trip_revision", 0),
    ("trip_input", ""),
    ("travel_expenses", []),
    ("next_expense_id", 1),
):
    if state_key not in st.session_state:
        st.session_state[state_key] = default

st.title(f"🌿 {T['title']}")
st.caption(T["subtitle"])
tabs = st.tabs([T["tab_import"], T["tab_itinerary"], T["tab_progress"]])


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


with tabs[0]:
    lang = st.selectbox(
        "Language / 语言 / Bahasa",
        ["zh", "en", "id"],
        format_func=lambda value: {"zh": "中文", "en": "English", "id": "Bahasa Indonesia"}[value],
        key="language",
    )
    T = TEXT[lang]
    st.header(T["import_title"])
    st.write(T["import_desc"])
    uploaded_file = st.file_uploader(T["upload"], type=["txt", "md"])
    if uploaded_file is not None:
        uploaded_content = uploaded_file.getvalue()
        upload_id = (uploaded_file.name, len(uploaded_content))
        if st.session_state.get("loaded_upload_id") != upload_id:
            try:
                st.session_state["trip_input"] = uploaded_content.decode("utf-8-sig")
                st.session_state["loaded_upload_id"] = upload_id
            except UnicodeDecodeError:
                st.error("File must be encoded as UTF-8.")

    st.text_area(T["prompt"], placeholder=T["placeholder"], height=240, key="trip_input")
    if st.button(T["parse"], type="primary"):
        if not ARK_API_KEY or not MODEL_ID:
            st.error(T["missing_api"])
            st.caption(T["configure"])
        elif not st.session_state["trip_input"].strip():
            st.warning(T["empty_plan"])
        else:
            try:
                with st.spinner(T["waiting"]):
                    result = parse_full_itinerary(st.session_state["trip_input"], lang)
                st.session_state["trip_data"] = result["itinerary_list"]
                st.session_state["budget_data"] = result.get("budget_summary", {})
                st.session_state["trip_revision"] += 1
                st.session_state["travel_expenses"] = []
                st.success(T["parse_ok"])
            except (requests.RequestException, ValueError, KeyError, TypeError) as error:
                st.error(f"{T['parse_error']}: {error}")


trip = st.session_state["trip_data"]
budget = st.session_state["budget_data"]
place_fields = {"zh": "place_cn", "en": "place_en", "id": "place_id"}

with tabs[1]:
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
                for item in day_data.get("plan_items", []):
                    place = item.get(place_fields[lang]) or item.get("place_en") or item.get("place_cn", "")
                    with st.container():
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
                        st.divider()

        if budget:
            st.subheader(T["budget"])
            budget_columns = st.columns(3)
            for column, key, label in zip(
                budget_columns,
                ("paid", "unpaid_mandatory", "unpaid_optional"),
                (T["paid"], T["mandatory"], T["optional"]),
            ):
                with column:
                    st.markdown(f"**{label}**")
                    entries = budget.get(key, [])
                    if not entries:
                        st.caption("—")
                    for entry in entries:
                        if key == "paid":
                            amount = f"{entry.get('cost', '—')} RMB"
                        else:
                            amount = f"{entry.get('cost_min', '—')} – {entry.get('cost_max', '—')} RMB"
                        st.write(f"{entry.get('name', '—')}: {amount}")
            st.info(
                f"{T['base_total']}: {budget.get('subtotal_min', '—')} – "
                f"{budget.get('subtotal_max', '—')} RMB  ·  "
                f"{T['emergency']}: {budget.get('emergency', '—')} RMB  ·  "
                f"{T['grand_total']}: {budget.get('grand_min', '—')} – "
                f"{budget.get('grand_max', '—')} RMB"
            )

with tabs[2]:
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
        revision = st.session_state["trip_revision"]
        total = len(all_items)
        completed_items = []
        remaining_items = []
        expenses_by_day = {}
        actual_total = 0.0
        for expense in st.session_state["travel_expenses"]:
            expenses_by_day.setdefault(expense["day_index"], []).append(expense)
            actual_total += expense["amount"]

        projected_min = budget.get("grand_min")
        projected_max = budget.get("grand_max")
        if projected_min is None or projected_max is None:
            projected_min = projected_max = None

        st.subheader(T["expenses"])
        expense_metrics = st.columns(2, gap="large")
        projected_display = (
            f"¥{projected_min:,.0f}–{projected_max:,.0f}"
            if projected_min is not None and projected_max is not None
            else "—"
        )
        expense_metrics[0].metric(T["projected_spend"], projected_display)
        expense_metrics[1].metric(T["actual_spend"], f"¥{actual_total:,.2f}")
        st.caption(T["expense_note"])
        expense_categories = {
            "transport": T["category_transport"],
            "ticket": T["category_ticket"],
            "food": T["category_food"],
            "other": T["category_other"],
        }
        checklist_column, summary_column = st.columns([1.2, 1], gap="large")
        with checklist_column:
            st.subheader(T["daily_expense"])
            for day_index, day_data in enumerate(trip):
                items = day_data.get("plan_items", [])
                day_number = day_data.get("day_no", day_index + 1)
                day_expenses = expenses_by_day.get(day_index, [])
                day_total = sum(expense["amount"] for expense in day_expenses)
                with st.expander(
                    f"{T['day'].format(day_number)} · {T['actual_spend']}: ¥{day_total:,.2f}",
                    expanded=True,
                ):
                    if items:
                        st.caption(T["checklist"])
                    for item_index, item in enumerate(items):
                        key = f"done_{revision}_{day_index}_{item_index}"
                        place = item.get(place_fields[lang]) or item.get("place_en") or item.get("place_cn", "")
                        label = f"{item.get('start_time', '')}  ·  {place}"
                        is_done = st.session_state.get(key, bool(item.get("is_done", False)))
                        if st.button(
                            f"{T['checked_action'] if is_done else T['checkin_action']}　{label}",
                            key=f"checkin_button_{revision}_{day_index}_{item_index}",
                            type="primary" if is_done else "secondary",
                            use_container_width=True,
                        ):
                            st.session_state[key] = not is_done
                            st.rerun()
                        summary = f"{T['day_short'].format(day_number)} · {label}"
                        (completed_items if is_done else remaining_items).append(summary)

                    stop_options = list(range(len(items))) if items else [None]
                    stop_labels = {None: T["unlinked_place"]}
                    for item_index, item in enumerate(items):
                        place = item.get(place_fields[lang]) or item.get("place_en") or item.get("place_cn", "")
                        stop_labels[item_index] = f"{item.get('start_time', '')} · {place}"
                    if items:
                        stop_options.append(None)

                    form_key = f"expense_form_{revision}_{day_index}"
                    with st.form(form_key, clear_on_submit=True):
                        stop_and_category = st.columns([1.4, 1])
                        selected_stop = stop_and_category[0].selectbox(
                            T["expense_place"],
                            stop_options,
                            format_func=lambda value: stop_labels[value],
                        )
                        selected_category = stop_and_category[1].selectbox(
                            T["expense_category"],
                            list(expense_categories),
                            format_func=lambda value: expense_categories[value],
                        )
                        amount_and_submit = st.columns([1, 1])
                        amount = amount_and_submit[0].number_input(
                            T["expense_amount"],
                            min_value=0.0,
                            step=1.0,
                        )
                        amount_and_submit[1].markdown(
                            '<div style="height: 1.8rem"></div>',
                            unsafe_allow_html=True,
                        )
                        submitted = amount_and_submit[1].form_submit_button(
                            T["add_expense"],
                            use_container_width=True,
                        )
                    if submitted:
                        if amount <= 0:
                            st.warning(T["expense_amount"])
                        else:
                            st.session_state["travel_expenses"].append(
                                {
                                    "id": st.session_state["next_expense_id"],
                                    "day_index": day_index,
                                    "item_index": selected_stop,
                                    "category": selected_category,
                                    "amount": amount,
                                }
                            )
                            st.session_state["next_expense_id"] += 1
                            st.rerun()

                    if not day_expenses:
                        st.caption(T["no_expenses"])
                    for expense in day_expenses:
                        expense_columns = st.columns([1.3, 1, 0.8, 0.5])
                        expense_columns[0].write(
                            stop_labels.get(expense["item_index"], T["unlinked_place"])
                        )
                        expense_columns[1].write(expense_categories[expense["category"]])
                        expense_columns[2].write(f"¥{expense['amount']:,.2f}")
                        if expense_columns[3].button(
                            "×",
                            key=f"delete_expense_{revision}_{expense['id']}",
                            help=T["delete_expense"],
                        ):
                            st.session_state["travel_expenses"] = [
                                entry
                                for entry in st.session_state["travel_expenses"]
                                if entry["id"] != expense["id"]
                            ]
                            st.rerun()

        with summary_column:
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
