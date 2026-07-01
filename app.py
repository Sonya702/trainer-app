import streamlit as st
import pandas as pd
import datetime

# --- НАЛАШТУВАННЯ СТОРІНКИ ---
st.set_page_config(
    page_title="Блокнот Тренера", 
    page_icon="🏋️‍♀️", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Великі шрифти для зручності у залі
st.markdown(
    """
    <style>
    html, body, [data-testid="stMarkdownContainer"] p { font-size: 20px !important; }
    .stMarkdown h3 { font-size: 26px !important; font-weight: bold !important; color: #1E88E5 !important; }
    textarea { font-size: 20px !important; font-family: sans-serif !important; line-height: 1.5 !important; }
    .stButton button { font-size: 20px !important; height: auto !important; padding: 10px 20px !important; }
    label p { font-size: 18px !important; font-weight: bold !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# Ініціалізація внутрішньої пам'яті програми, яка НЕ злітає при перезавантаженні
if "db_data" not in st.session_state:
    st.session_state.db_data = {
        "Юля": {
            "exercise_list": "Біцепс палкою\nТріцепс палкою\nБіцепс молотки",
            "workout_history": "",
            "exercise_history": {},
            "today_exercises": ["Біцепс палкою", "Тріцепс палкою"],
            "today_sets": {},
            "today_focus": ""
        }
    }

db_data = st.session_state.db_data

# --- БОКОВЕ МЕНЮ ---
st.sidebar.title("👥 Клієнтки")
client_names = sorted(list(db_data.keys()))

if "active_client" not in st.session_state:
    st.session_state.active_client = client_names[0]

selected_client = st.sidebar.selectbox(
    "🙋‍♀️ Обери клієнтку:", 
    client_names, 
    index=client_names.index(st.session_state.active_client) if st.session_state.active_client in client_names else 0
)
st.session_state.active_client = selected_client

client = db_data[selected_client]

# Додавання нової дівчини
with st.sidebar.expander("➕ Додати нову клієнтку"):
    new_name = st.text_input("Ім'я:")
    if st.button("Створити"):
        name_s = new_name.strip()
        if name_s and name_s not in db_data:
            db_data[name_s] = {
                "exercise_list": "Нова вправа", 
                "workout_history": "", 
                "exercise_history": {},
                "today_exercises": [], 
                "today_sets": {}, 
                "today_focus": ""
            }
            st.session_state.active_client = name_s
            st.success(f"Клієнтку {name_s} додано!")
            st.rerun()

# Вкладки додатка
tab_history, tab_today, tab_list = st.tabs([
    "📅 Історія тренувань",
    "📝 Сьогоднішнє тренування", 
    "📋 Список вправ"
])

# ВКЛАДКА 1: ІСТОРІЯ ТРЕНУВАНЬ
with tab_history:
    st.subheader(f"📅 Загальна історія: {selected_client}")
    u_hist = st.text_area("Журнал історії:", value=client.get("workout_history", ""), height=400, key="history_view_key")
    if u_hist != client.get("workout_history", ""):
        client["workout_history"] = u_hist

# ВКЛАДКА 2: СЬОГОДНІШНЄ ТРЕНУВАННЯ
with tab_today:
    st.subheader(f"Тренування: {selected_client}")
    
    u_focus = st.text_input("Фокус дня:", value=client.get("today_focus", ""), key="focus_input_field")
    if u_focus != client.get("today_focus", ""):
        client["today_focus"] = u_focus
    
    with st.expander("➕ Вибір вправ на сьогодні (Постав галочки)"):
        raw_list = [line.strip() for line in client.get("exercise_list", "").split("\n") if line.strip()]
        
        updated_sel = []
        for ex in raw_list:
            is_ch = ex in client.get("today_exercises", [])
            if st.checkbox(ex, value=is_ch, key=f"chk_{selected_client}_{ex}"):
                updated_sel.append(ex)
                
        if updated_sel != client.get("today_exercises", []):
            client["today_exercises"] = updated_sel
            st.rerun()

    st.markdown("---")
    
    today_exs = client.get("today_exercises", [])
    if not today_exs:
        st.info("Будь ласка, створіть або виберіть вправи у вкладці 'Список вправ' або розгорніть блок вище.")
    else:
        for i, ex in enumerate(today_exs, 1):
            st.subheader(f"{i}. {ex.upper()}")
            
            c_sets = client["today_sets"].get(ex, "1п: \n2п: \n3п: \n4п: \nДля заміток:")
            n_sets = st.text_area(f"Введіть підходи для {ex}:", value=c_sets, height=200, key=f"txt_{selected_client}_{ex}_{i}", label_visibility="collapsed")
            
            if n_sets != c_sets:
                client["today_sets"][ex] = n_sets

            p_hist = client.get("exercise_history", {}).get(ex, "Історія вправи порожня.")
            st.text_area("📜 Минула історія цієї вправи:", value=p_hist, height=200, key=f"past_{selected_client}_{ex}_{i}", disabled=True)
            st.markdown("---")

    # КНОПКА ЗАВЕРШЕННЯ ТРЕНУВАННЯ
    if st.button(f"✅ Завершити тренування {selected_client}", type="primary", use_container_width=True):
        if today_exs:
            days_ua = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
            now = datetime.datetime.now()
            today_date = f"{days_ua[now.weekday()]} {now.strftime('%d.%m.%y')}"
            day_header = f"{today_date} ({client.get('today_focus', '')})"
            
            new_w = f"{day_header}\n"
            for k, ex in enumerate(today_exs, 1):
                s_txt = client["today_sets"].get(ex, "").strip()
                new_w += f"{k}. {ex}\n{s_txt}\n\n"
                
                # Записуємо в індивідуальну історію вправи
                client["exercise_history"][ex] = f"{day_header}\n{s_txt}\n\n" + client["exercise_history"].get(ex, "")
            
            client["workout_history"] = new_w + "\n\n" + client.get("workout_history", "")
            
            # Очищуємо поля чернетки на сьогодні
            client["today_exercises"] = []
            client["today_sets"] = {}
            client["today_focus"] = ""
            
            st.success("Тренування повністю збережено в історію!")
            st.rerun()

# ВКЛАДКА 3: СПИСОК ВПРАВ (СЮДИ ТИ МОЖЕШ ВПИСУВАТИ НОВІ ВПРАВИ)
with tab_list:
    st.subheader(f"📋 Створити/Редагувати список ВСІХ вправ")
    st.write("Впиши сюди нові вправи (кожна з нового рядка), і вони з'являться в списку галочок сьогоднішнього тренування:")
    u_list = st.text_area("Список вправ:", value=client.get("exercise_list", ""), height=400, key="exercise_list_editor_key")
    if u_list != client.get("exercise_list", ""):
        client["exercise_list"] = u_list
