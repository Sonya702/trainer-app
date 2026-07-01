import streamlit as st
from streamlit_gsheets import GSheetsConnection
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

# Підключаємося до Google Таблиці
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(worksheet="workouts", ttl=0)
except:
    df = pd.DataFrame(columns=["client", "date", "focus", "exercise", "sets", "history"])

# Перетворюємо дані з таблиці у зручний для програми формат (словник)
db_data = {}
for idx, row in df.iterrows():
    cl_name = str(row["client"]).strip()
    if cl_name and cl_name != "nan":
        if cl_name not in db_data:
            db_data[cl_name] = {
                "exercise_list": "", "workout_history": str(row["history"]) if str(row["history"]) != "nan" else "",
                "exercise_history": {}, "today_exercises": [], "today_sets": {}, "today_focus": str(row["focus"]) if str(row["focus"]) != "nan" else ""
            }
        
        ex_name = str(row["exercise"]).strip()
        if ex_name and ex_name != "nan":
            if ex_name not in db_data[cl_name]["today_exercises"]:
                db_data[cl_name]["today_exercises"].append(ex_name)
            db_data[cl_name]["today_sets"][ex_name] = str(row["sets"]) if str(row["sets"]) != "nan" else ""

# Базова Юля, якщо таблиця ще зовсім порожня
if "Юля" not in db_data:
    db_data["Юля"] = {
        "exercise_list": "Біцепс палкою\nТріцепс палкою\nБіцепс молотки",
        "workout_history": "", "exercise_history": {},
        "today_exercises": ["Біцепс палкою", "Тріцепс палкою"], "today_sets": {}, "today_focus": ""
    }

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
            new_row = pd.DataFrame([{"client": name_s, "date": "", "focus": "", "exercise": "", "sets": "", "history": ""}])
            df = pd.concat([df, new_row], ignore_index=True)
            conn.update(worksheet="workouts", data=df)
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
    st.text_area("Журнал:", value=client.get("workout_history", ""), height=400, disabled=True)

# ВКЛАДКА 2: СЬОГОДНІШНЄ ТРЕНУВАННЯ
with tab_today:
    st.subheader(f"Тренування: {selected_client}")
    
    u_focus = st.text_input("Фокус дня:", value=client.get("today_focus", ""))
    
    with st.expander("➕ Вибір вправ на сьогодні"):
        raw_list = [line.strip() for line in client.get("exercise_list", "").split("\n") if line.strip()]
        if not raw_list:
            raw_list = ["Біцепс палкою", "Тріцепс палкою", "Біцепс молотки"] # базовий набір
        
        updated_sel = []
        for ex in raw_list:
            is_ch = ex in client.get("today_exercises", [])
            if st.checkbox(ex, value=is_ch, key=f"chk_{ex}"):
                updated_sel.append(ex)

    st.markdown("---")
    
    today_exs = updated_sel
    if not today_exs:
        st.info("Виберіть вправи в блоці вище.")
    else:
        for i, ex in enumerate(today_exs, 1):
            st.subheader(f"{i}. {ex.upper()}")
            
            c_sets = client["today_sets"].get(ex, "1п: \n2п: \n3п: \n4п: \nДля заміток:")
            n_sets = st.text_area(f"Введіть підходи для {ex}:", value=c_sets, height=200, key=f"txt_{ex}_{i}", label_visibility="collapsed")
            
            if n_sets != c_sets:
                client["today_sets"][ex] = n_sets

            # КНОПКА ФІКСАЦІЇ ВПРАВИ В GOOGLE ТАБЛИЦЮ
            if st.button(f"💾 Фіксувати ваги для вправи №{i}", key=f"btn_{ex}_{i}", use_container_width=True):
                # Видаляємо старі рядки цієї вправи для цієї клієнтки, щоб не дублювати
                df = df[~((df["client"] == selected_client) & (df["exercise"] == ex))]
                
                # Додаємо оновлений рядок
                new_row = pd.DataFrame([{
                    "client": selected_client,
                    "date": datetime.datetime.now().strftime('%d.%m.%y'),
                    "focus": u_focus,
                    "exercise": ex,
                    "sets": n_sets,
                    "history": client.get("workout_history", "")
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                conn.update(worksheet="workouts", data=df)
                st.toast(f"Вправа №{i} надійно збережена в Google Таблицю!")

    # КНОПКА ЗАВЕРШЕННЯ ТРЕНУВАННЯ
    if st.button(f"✅ Завершити тренування {selected_client}", type="primary", use_container_width=True):
        if today_exs:
            days_ua = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
            now = datetime.datetime.now()
            today_date = f"{days_ua[now.weekday()]} {now.strftime('%d.%m.%y')}"
            day_header = f"{today_date} ({u_focus})"
            
            new_w = f"{day_header}\n"
            for k, ex in enumerate(today_exs, 1):
                s_txt = client["today_sets"].get(ex, "").strip()
                new_w += f"{k}. {ex}\n{s_txt}\n\n"
            
            full_history = new_w + "\n\n" + client.get("workout_history", "")
            
            # Чистимо поточний день у таблиці і записуємо все в історію
            df = df[df["client"] != selected_client]
            final_row = pd.DataFrame([{
                "client": selected_client, "date": today_date, "focus": "", "exercise": "", "sets": "", "history": full_history
            }])
            df = pd.concat([df, final_row], ignore_index=True)
            conn.update(worksheet="workouts", data=df)
            
            st.success("Тренування повністю збережено в архів історії!")
            st.rerun()

# ВКЛАДКА 3: СПИСОК ВПРАВ
with tab_list:
    st.subheader(f"📋 Список вправ: {selected_client}")
    u_list = st.text_area("Вправи (кожна з нового рядка):", value=client.get("exercise_list", ""), height=400)
    if u_list != client.get("exercise_list", ""):
        client["exercise_list"] = u_list
