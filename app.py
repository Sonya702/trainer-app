import streamlit as st
from streamlit_local_storage import LocalStorage
import json
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

# Ключ компонента захищено від дублювання перекладачем за допомогою суфікса '_secure'
local_storage = LocalStorage(key="st_local_storage_secure")

def get_local_db():
    saved = local_storage.getItem("trainer_workout_db_v2")
    if saved:
        try:
            return json.loads(saved)
        except:
            pass
    return {
        "Юля": {
            "exercise_list": "Біцепс палкою\nТріцепс палкою\nБіцепс молотки",
            "workout_history": "",
            "exercise_history": {},
            "today_exercises": ["Біцепс палкою", "Тріцепс палкою"],
            "today_sets": {},
            "today_focus": ""
        }
    }

def save_local_db(data):
    local_storage.setItem("trainer_workout_db_v2", json.dumps(data, ensure_ascii=False))

def get_last_client():
    cl = local_storage.getItem("last_active_client_v2")
    return cl if cl else "Юля"

def save_last_client(name):
    local_storage.setItem("last_active_client_v2", name)

db_data = get_local_db()

# --- БОКОВЕ МЕНЮ ---
st.sidebar.title("👥 Клієнтки")
client_names = sorted(list(db_data.keys()))

last_cl = get_last_client()
default_idx = client_names.index(last_cl) if last_cl in client_names else 0

selected_client = st.sidebar.selectbox("🙋‍♀️ Обери клієнтку:", client_names, index=default_idx, key="selectbox_client_secure")

if selected_client != last_cl:
    save_last_client(selected_client)
    st.rerun()

with st.sidebar.expander("➕ Додати нову клієнтку"):
    new_name = st.text_input("Ім'я:", key="input_new_client_secure")
    if st.button("Створити", key="btn_create_client_secure"):
        name_s = new_name.strip()
        if name_s and name_s not in db_data:
            db_data[name_s] = {
                "exercise_list": "", "workout_history": "", "exercise_history": {},
                "today_exercises": [], "today_sets": {}, "today_focus": ""
            }
            save_local_db(db_data)
            save_last_client(name_s)
            st.success(f"Клієнтку {name_s} додано!")
            st.rerun()

client = db_data[selected_client]

tab_history, tab_today, tab_list = st.tabs([
    "📅 Історія тренувань",
    "📝 Сьогоднішнє тренування", 
    "📋 Список вправ"
])

# ВКЛАДКА 1: ІСТОРІЯ ТРЕНУВАНЬ
with tab_history:
    st.subheader(f"📅 Загальна історія: {selected_client}")
    u_hist = st.text_area("Журнал:", value=client.get("workout_history", ""), height=400, key="area_workout_history_secure")
    if u_hist != client.get("workout_history", ""):
        client["workout_history"] = u_hist
        save_local_db(db_data)

# ВКЛАДКА 2: СЬОГОДНІШНЄ ТРЕНУВАННЯ
with tab_today:
    st.subheader(f"Тренування: {selected_client}")
    
    if st.button("💾 СИНХРОНІЗУВАТИ І ЗБЕРЕГТИ ЧЕРНЕТКУ", use_container_width=True, key="btn_sync_draft_secure"):
        save_local_db(db_data)
        st.success("Дані успішно зафіксовані в пам'яті телефону!")

    u_focus = st.text_input("Фокус дня:", value=client.get("today_focus", ""), key="input_today_focus_secure")
    if u_focus != client.get("today_focus", ""):
        client["today_focus"] = u_focus
        save_local_db(db_data)
        
    with st.expander("➕ Вибір вправ на сьогодні"):
        raw_list = [line.strip() for line in client.get("exercise_list", "").split("\n") if line.strip()]
        updated_sel = []
        for ex in raw_list:
            is_ch = ex in client.get("today_exercises", [])
            if st.checkbox(ex, value=is_ch, key=f"ch_secure_{ex}"):
                updated_sel.append(ex)
        if updated_sel != client.get("today_exercises", []):
            client["today_exercises"] = updated_sel
            save_local_db(db_data)

    st.markdown("---")
    
    today_exs = client.get("today_exercises", [])
    if not today_exs:
        st.info("Виберіть вправи вище.")
    else:
        for i, ex in enumerate(today_exs, 1):
            st.subheader(f"{i}. {ex.upper()}")
            
            c_sets = client.get("today_sets", {}).get(ex, "1п: \n2п: \n3п: \n4п: \nДля заміток:")
            n_sets = st.text_area(f"Введіть підходи для {ex}:", value=c_sets, height=180, key=f"area_sets_secure_{ex}_{i}", label_visibility="collapsed")
            
            if n_sets != c_sets:
                if "today_sets" not in client: client["today_sets"] = {}
                client["today_sets"][ex] = n_sets
                save_local_db(db_data)
                
            p_hist = client.get("exercise_history", {}).get(ex, "Історія вправи порожня.")
            st.text_area("📜 Минула історія:", value=p_hist, height=200, key=f"p_hist_secure_{ex}_{i}", disabled=True)
            st.markdown("---")

    if st.button(f"✅ Завершити тренування {selected_client}", type="primary", use_container_width=True, key="btn_finish_workout_secure"):
        if today_exs:
            days_ua = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
            now = datetime.datetime.now()
            today_date = f"{days_ua[now.weekday()]} {now.strftime('%d.%m.%y')}"
            day_header = f"{today_date} ({client.get('today_focus', '')})"
            
            for ex in today_exs:
                s_txt = client.get("today_sets", {}).get(ex, "").strip()
                if s_txt:
                    new_e = f"{day_header}\n{s_txt}\n\n"
                    if "exercise_history" not in client: client["exercise_history"] = {}
                    client["exercise_history"][ex] = new_e + client["exercise_history"].get(ex, "")
            
            new_w = f"{day_header}\n"
            for k, ex in enumerate(today_exs, 1):
                new_w += f"{k}. {ex}\n"
            client["workout_history"] = new_w + "\n\n" + client.get("workout_history", "")
            
            client["today_exercises"] = []
            client["today_sets"] = {}
            client["today_focus"] = ""
            
            save_local_db(db_data)
            st.success("Тренування збережено в історію!")
            st.rerun()

# ВКЛАДКА 3: СПИСОК ВПРАВ
with tab_list:
    st.subheader(f"📋 Список вправ: {selected_client}")
    u_list = st.text_area("Вправи (кожна з нового рядка):", value=client.get("exercise_list", ""), height=400, key="area_exercise_list_secure")
    if u_list != client.get("exercise_list", ""):
        client["exercise_list"] = u_list
        save_local_db(db_data)
