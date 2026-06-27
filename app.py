import streamlit as st
import json
import os
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

DB_FILE = "clients_backup_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
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

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Завантажуємо базу даних один раз за сесію
if "trainer_db" not in st.session_state:
    st.session_state.trainer_db = load_data()

db_data = st.session_state.trainer_db

# --- БОКОВЕ МЕНЮ ---
st.sidebar.title("👥 Клієнтки")
client_names = sorted(list(db_data.keys()))

if "active_client_name" not in st.session_state:
    st.session_state.active_client_name = client_names[0]

selected_client = st.sidebar.selectbox(
    "🙋‍♀️ Обери клієнтку:", 
    client_names, 
    index=client_names.index(st.session_state.active_client_name) if st.session_state.active_client_name in client_names else 0
)

if selected_client != st.session_state.active_client_name:
    st.session_state.active_client_name = selected_client
    st.rerun()

with st.sidebar.expander("➕ Додати нову клієнтку"):
    new_name = st.text_input("Ім'я:")
    if st.button("Створити"):
        name_s = new_name.strip()
        if name_s and name_s not in db_data:
            db_data[name_s] = {
                "exercise_list": "", "workout_history": "", "exercise_history": {},
                "today_exercises": [], "today_sets": {}, "today_focus": ""
            }
            save_data(db_data)
            st.session_state.active_client_name = name_s
            st.success(f"Клієнтку {name_s} додано!")
            st.rerun()

client = db_data[selected_client]

# Гарантуємо наявність необхідних ключів у профілі клієнтки
if "today_exercises" not in client: client["today_exercises"] = []
if "today_sets" not in client: client["today_sets"] = {}
if "exercise_history" not in client: client["exercise_history"] = {}

# --- ГОЛОВНІ ВКЛАДКИ ---
tab_history, tab_today, tab_list = st.tabs([
    "📅 Історія тренувань",
    "📝 Сьогоднішнє тренування", 
    "📋 Список вправ"
])

# ВКЛАДКА 1: ІСТОРІЯ ТРЕНУВАНЬ
with tab_history:
    st.subheader(f"📅 Загальна історія: {selected_client}")
    u_hist = st.text_area("Журнал:", value=client.get("workout_history", ""), height=400, key="hist_area_key")
    if u_hist != client.get("workout_history", ""):
        client["workout_history"] = u_hist
        save_data(db_data)

# ВКЛАДКА 2: СЬОГОДНІШНЄ ТРЕНУВАННЯ
with tab_today:
    st.subheader(f"Тренування: {selected_client}")
    
    u_focus = st.text_input("Фокус дня:", value=client.get("today_focus", ""), key="focus_input_key")
    if u_focus != client.get("today_focus", ""):
        client["today_focus"] = u_focus
        save_data(db_data)
        
    with st.expander("➕ Вибір та додавання вправ на сьогодні"):
        st.markdown("**✨ Створити нову вправу:**")
        fast_new_ex = st.text_input("Введіть назву нової вправи:", key="fast_ex_input_key", placeholder="Наприклад: Присідання плиє")
        
        if st.button("➕ Додати цю вправу в план", use_container_width=True):
            ex_cleaned = fast_new_ex.strip()
            if ex_cleaned:
                if ex_cleaned not in client["today_exercises"]:
                    client["today_exercises"].append(ex_cleaned)
                
                # Додаємо в загальний список
                current_list = [line.strip() for line in client.get("exercise_list", "").split("\n") if line.strip()]
                if ex_cleaned not in current_list:
                    current_list.append(ex_cleaned)
                    client["exercise_list"] = "\n".join(current_list)
                
                save_data(db_data)
                st.success(f"Вправу '{ex_cleaned}' додано!")
                st.rerun()
                
        st.markdown("---")
        st.markdown("**📋 Вибрати з існуючих:**")
        
        raw_list = [line.strip() for line in client.get("exercise_list", "").split("\n") if line.strip()]
        updated_sel = []
        for ex in raw_list:
            is_ch = ex in client["today_exercises"]
            if st.checkbox(ex, value=is_ch, key=f"check_ex_{ex}"):
                updated_sel.append(ex)
                
        if updated_sel != client["today_exercises"]:
            client["today_exercises"] = updated_sel
            save_data(db_data)
            st.rerun()

    st.markdown("---")
    
    today_exs = client["today_exercises"]
    if not today_exs:
        st.info("Виберіть або створіть вправи в блоці вище.")
    else:
        for i, ex in enumerate(today_exs, 1):
            st.subheader(f"{i}. {ex.upper()}")
            
            # Стандартний шаблон, якщо поле пусте
            default_template = "1п: \n2п: \n3п: \n4п: \nДля заміток:"
            c_sets = client["today_sets"].get(ex, default_template)
            if not c_sets.strip():
                c_sets = default_template
            
            input_key = f"textarea_sets_{selected_client}_{ex}_{i}"
            
            # Слідкуємо за тим, щоб збережене значення завжди відображалося правильно
            n_sets = st.text_area(
                f"Введіть підходи для {ex}:", 
                value=c_sets, 
                height=200, 
                key=input_key, 
                label_visibility="collapsed"
            )
            
            # Якщо текст у полі змінився, записуємо його в сесію
            if n_sets != client["today_sets"].get(ex):
                client["today_sets"][ex] = n_sets

            # ЗАЛІЗОБЕТОННА КНОПКА ФІКСАЦІЇ
            if st.button(f"💾 Фіксувати ваги для вправи №{i}", key=f"btn_save_item_{ex}_{i}", use_container_width=True):
                # Примусово беремо поточний стан саме з цього текстового поля
                client["today_sets"][ex] = st.session_state[input_key]
                save_data(db_data)
                st.toast(f"Вправа №{i} ({ex}) збережена в чернетку!")

            # Минула історія
            p_hist = client["exercise_history"].get(ex, "Історія вправи порожня.")
            st.text_area("📜 Минула історія:", value=p_hist, height=310, key=f"past_history_view_{ex}_{i}", disabled=True)
            st.markdown("---")

    # ЗАВЕРШЕННЯ ТРЕНУВАННЯ
    if st.button(f"✅ Завершити тренування {selected_client}", type="primary", use_container_width=True, key="finish_tr_key"):
        if today_exs:
            days_ua = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
            now = datetime.datetime.now()
            today_date = f"{days_ua[now.weekday()]} {now.strftime('%d.%m.%y')}"
            day_header = f"{today_date} ({client.get('today_focus', '')})"
            
            for ex in today_exs:
                s_txt = client["today_sets"].get(ex, "").strip()
                if s_txt:
                    new_e = f"{day_header}\n{s_txt}\n\n"
                    client["exercise_history"][ex] = new_e + client["exercise_history"].get(ex, "")
            
            new_w = f"{day_header}\n"
            for k, ex in enumerate(today_exs, 1):
                new_w += f"{k}. {ex}\n"
            client["workout_history"] = new_w + "\n\n" + client.get("workout_history", "")
            
            client["today_exercises"] = []
            client["today_sets"] = {}
            client["today_focus"] = ""
            
            save_data(db_data)
            st.success("Тренування успішно збережено в історію!")
            st.rerun()

# ВКЛАДКА 3: СПИСОК ВПРАВ
with tab_list:
    st.subheader(f"📋 Список вправ: {selected_client}")
    u_list = st.text_area("Вправи (кожна з нового рядка):", value=client.get("exercise_list", ""), height=400, key="list_area_key")
    if u_list != client.get("exercise_list", ""):
        client["exercise_list"] = u_list
        save_data(db_data)
