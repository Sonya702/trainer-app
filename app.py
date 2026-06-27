import streamlit as st
import re
import datetime

# --- НАЛАШТУВАННЯ СТОРІНКИ ---
st.set_page_config(
    page_title="Блокнот Тренера", 
    page_icon="🏋️‍♀️", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- МУЛЬТИ-НАЛАШТУВАННЯ ВЕЛИКИХ ШРИФТІВ ДЛЯ ТЕЛЕФОНУ ---
st.markdown(
    """
    <style>
    /* Робимо весь звичайний текст та поля вводу великими */
    html, body, [data-testid="stMarkdownContainer"] p {
        font-size: 20px !important;
    }
    /* Збільшуємо назви вправ */
    .stMarkdown h3 {
        font-size: 26px !important;
        font-weight: bold !important;
        color: #1E88E5 !important;
    }
    /* Збільшуємо текст всередині текстових полей (сьогодні і історія) */
    textarea {
        font-size: 20px !important;
        font-family: sans-serif !important;
        line-height: 1.5 !important;
    }
    /* Збільшуємо шрифт підписів та кнопок */
    .stButton button {
        font-size: 20px !important;
        height: auto !important;
        padding: 10px 20px !important;
    }
    /* Стиль для підказок над полями */
    label p {
        font-size: 18px !important;
        font-weight: bold !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- 1. СТВОРЕННЯ ТА ЗБЕРЕЖЕННЯ БАЗИ ДАНИХ КЛІЄНТОК ---
if 'clients_data' not in st.session_state:
    st.session_state.clients_data = {
        "Юля": {
            "exercise_list": "Біцепс палкою\nТріцепс палкою\nБіцепс молотки\nТріцепс віджимання\nПлечі махи\nПрес",
            "workout_history": "Вівторок 27.06.26 (біцепс, тріцепс + плечі)\n1. Біцепс палкою\n2. Тріцепс палкою\n3. Біцепс молотки\n4. Тріцепс віджимання\n5. Плечі махи\n6. Прес",
            "exercise_history": {
                "Біцепс палкою": "Вівторок 27.06.26\n1п: 15кг 15р 3з\n2п: 20кг 12р 2з\n3п: 20кг 12р 1з\n4п: 20кг 12р 1з\nДля заміток: 4 підхід останні 2 без техніки\n\nНеділя 25.06.26\n1п: 15кг 15р RIR 4",
                "Тріцепс палкою": "Вівторок 27.06.26\n1п: 15кг 15р 3з\n2п: 20кг 12р 2з\nДля заміток:\n\nНеділя 25.06.26\n1п: 15кг 15р RIR 4"
            },
            "today_exercises": ["Біцепс палкою", "Тріцепс палкою"],
            "today_sets": {
                "Біцепс палкою": "1п: 15кг 15р 3з\n2п: 20кг 12р 2з\n3п: 20кг 12р 1з\n4п: 20кг 12р 1з\nДля заміток: 4 підхід останні 2 без техніки",
                "Тріцепс палкою": "1п: 15кг 15р 3з\n2п: 20кг 12р 2з\n3п: 20кг 12р 1з\n4п: 20кг 12р 1з\nДля заміток:"
            },
            "today_focus": "біцепс, тріцепс + плечі"
        }
    }

# --- 2. БОКОВЕ МЕНЮ (Вибір/додавання людей) ---
st.sidebar.title("👥 Клієнтки")

client_names = sorted(list(st.session_state.clients_data.keys()))
selected_client = st.sidebar.selectbox("🙋‍♀️ Обери клієнтку:", client_names)

st.sidebar.markdown("---")
with st.sidebar.expander("➕ Додати нову клієнтку"):
    new_client_name = st.text_input("Ім'я клієнтки:", key="new_client_name_input")
    if st.button("Створити профіль"):
        name_striped = new_client_name.strip()
        if name_striped:
            if name_striped not in st.session_state.clients_data:
                st.session_state.clients_data[name_striped] = {
                    "exercise_list": "",
                    "workout_history": "",
                    "exercise_history": {},
                    "today_exercises": [],
                    "today_sets": {},
                    "today_focus": ""
                }
                st.success(f"Клієнтку {name_striped} додано!")
                st.rerun()
            else:
                st.warning("Клієнтка з таким іменем вже існує!")
        else:
            st.error("Введіть ім'я!")

client = st.session_state.clients_data[selected_client]

# --- 3. ГОЛОВНІ ВКЛАДКИ НАД СТОРІНКОЮ ---
tab_history, tab_today, tab_list = st.tabs([
    "📅 Історія тренувань",
    "📝 Сьогоднішнє тренування", 
    "📋 Список вправ"
])

# --- 4. ЛОГІКА РОБОТИ ВКЛАДОК ---

# ВКЛАДКА 1: ІСТОРІЯ ТРЕНУВАНЬ
with tab_history:
    st.subheader(f"📅 Загальна історія: {selected_client}")
    client["workout_history"] = st.text_area("Перегляд історії:", value=client["workout_history"], height=500, key="history_textarea")

# ВКЛАДКА 2: СЬОГОДНІШНЄ ТРЕНУВАННЯ
with tab_today:
    st.subheader(f"Тренування: {selected_client}")
    
    client["today_focus"] = st.text_input("Фокус дня:", value=client["today_focus"], key="focus_input")
    
    with st.expander("➕ Повибирати вправи зі списку або дописати нову"):
        raw_list = [line.strip() for line in client["exercise_list"].split("\n") if line.strip()]
        updated_selection = []
        for ex in raw_list:
            is_chosen = ex in client["today_exercises"]
            if st.checkbox(ex, value=is_chosen, key=f"select_{ex}"):
                updated_selection.append(ex)
                
        new_ex_input = st.text_input("Дописати нову вправу руками:")
        if st.button("Додати в план"):
            if new_ex_input.strip() and new_ex_input.strip() not in updated_selection:
                updated_selection.append(new_ex_input.strip())
                if client["exercise_list"]:
                    client["exercise_list"] = new_ex_input.strip() + "\n" + client["exercise_list"]
                else:
                    client["exercise_list"] = new_ex_input.strip()
                st.rerun()
                
        client["today_exercises"] = updated_selection

    st.markdown("---")
    
    if not client["today_exercises"]:
        st.info("Виберіть або допишіть вправи вище.")
    else:
        for i, ex in enumerate(client["today_exercises"], 1):
            st.subheader(f"{i}. {ex.upper()}") # Назва вправи тепер КАПСОМ для кращої видимості
            
            # 1. ЗБІЛЬШЕНЕ ПЕРШЕ ВІКОНЦЕ (Сьогоднішні підходи, висота 180)
            current_val = client["today_sets"].get(ex, "1п: \n2п: \n3п: \n4п: \nДля заміток:")
            client["today_sets"][ex] = st.text_area(
                f"Впиши підходи для {ex}:", 
                value=current_val, 
                height=180, 
                key=f"input_{ex}_{i}",
                label_visibility="collapsed"
            )
            
            # 2. ПОДОВЖЕНЕ ДРУГЕ ВІКОНЦЕ (Минула історія, висота 250)
            past_history = client["exercise_history"].get(ex, "Історія порожня (це перше тренування для цієї вправи).")
            st.text_area(
                f"📜 Минула історія:", 
                value=past_history, 
                height=250, 
                key=f"history_{ex}_{i}", 
                disabled=True
            )
            st.markdown("<br>", unsafe_allow_html=True) # Додатковий відступ між вправами
            st.markdown("---")

    if st.button(f"✅ Завершити тренування {selected_client}", type="primary", use_container_width=True):
        days_ua = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
        now = datetime.datetime.now()
        today_date = f"{days_ua[now.weekday()]} {now.strftime('%d.%m.%y')}"
        
        day_header = f"{today_date} ({client['today_focus']})"
        
        for ex in client["today_exercises"]:
            sets_text = client["today_sets"].get(ex, "").strip()
            if sets_text:
                new_entry = f"{day_header}\n{sets_text}\n\n"
                client["exercise_history"][ex] = new_entry + client["exercise_history"].get(ex, "")
        
        new_workout = f"{day_header}\n"
        for i, ex in enumerate(client["today_exercises"], 1):
            new_workout += f"{i}. {ex}\n"
        client["workout_history"] = new_workout + "\n\n" + client["workout_history"]
        
        client["today_exercises"] = []
        client["today_sets"] = {}
        client["today_focus"] = ""
        st.success("Дані збережено!")
        st.rerun()

# ВКЛАДКА 3: СПИСОК ВПРАВ
with tab_list:
    st.subheader(f"📋 Список вправ: {selected_client}")
    client["exercise_list"] = st.text_area("Редагувати список:", value=client["exercise_list"], height=500, key="list_textarea")
