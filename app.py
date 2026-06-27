import streamlit as st
import re

st.set_page_config(page_title="Блокнот Тренера", page_icon="🏋️‍♀️", layout="centered")

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

# --- 2. БОКОВЕ МЕНЮ (Керування клієнтками та вкладки) ---
st.sidebar.title("🗂️ Керування")

# Вибір клієнтки
client_names = sorted(list(st.session_state.clients_data.keys()))
selected_client = st.sidebar.selectbox("🙋‍♀️ Обери клієнтку:", client_names)

# --- НОВА ФІШКА: СТВОРЕННЯ НОВОЇ КЛІЄНТКИ ---
st.sidebar.markdown("---")
with st.sidebar.expander("➕ Додати нову клієнтку"):
    new_client_name = st.text_input("Ім'я клієнтки:", key="new_client_name_input")
    if st.button("Створити профіль"):
        name_striped = new_client_name.strip()
        if name_striped:
            if name_striped not in st.session_state.clients_data:
                # Створюємо пустий шаблон для нової дівчини
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

st.sidebar.markdown("---")

# Вкладки додатка
tabs = ["Сьогоднішнє тренування", "Список вправ", "Історія тренувань"]
current_tab = st.sidebar.radio("Перейти до:", tabs)

# Посилання на дані вибраної клієнтки
client = st.session_state.clients_data[selected_client]

# --- 3. ЛОГІКА РОБОТИ ВКЛАДОК ---

# ВКЛАДКА: СЬОГОДНІШНЄ ТРЕНУВАННЯ
if current_tab == "Сьогоднішнє тренування":
    st.header(f"📝 {selected_client}: Сьогоднішнє тренування")
    
    # Фокус дня
    client["today_focus"] = st.text_input("Фокус дня (наприклад: сідниці, спина/руки):", value=client["today_focus"])
    
    # Блок додавання вправ
    with st.expander("➕ Повибирати вправи зі списку або дописати нову"):
        raw_list = [line.strip() for line in client["exercise_list"].split("\n") if line.strip()]
        
        # Галочки для вибору
        updated_selection = []
        for ex in raw_list:
            is_chosen = ex in client["today_exercises"]
            if st.checkbox(ex, value=is_chosen, key=f"select_{ex}"):
                updated_selection.append(ex)
                
        # Дописати нову самостійно
        new_ex_input = st.text_input("Дописати нову вправу руками (якщо немає в списку):")
        if st.button("Додати нову вправу в план"):
            if new_ex_input.strip() and new_ex_input.strip() not in updated_selection:
                updated_selection.append(new_ex_input.strip())
                if client["exercise_list"]:
                    client["exercise_list"] = new_ex_input.strip() + "\n" + client["exercise_list"]
                else:
                    client["exercise_list"] = new_ex_input.strip()
                st.rerun()
                
        client["today_exercises"] = updated_selection

    st.markdown("---")
    
    # СТРІЧКА ТРЕНУВАННЯ
    if not client["today_exercises"]:
        st.info("Будь ласка, вибери або допиши вправи в блоці вище, щоб розпочати.")
    else:
        for i, ex in enumerate(client["today_exercises"], 1):
            st.subheader(f"{i}. {ex}")
            
            # 1. Поле введення сьогоднішніх підходів
            current_val = client["today_sets"].get(ex, "1п: \n2п: \nДля заміток:")
            client["today_sets"][ex] = st.text_area(
                f"Впиши підходи для {ex}:", 
                value=current_val, 
                height=150, 
                key=f"input_{ex}_{i}",
                label_visibility="collapsed"
            )
            
            # 2. МИНУЛА ІСТОРІЯ ПРЯМО НИЖЧЕ (Скрол у вікні)
            past_history = client["exercise_history"].get(ex, "Історія порожня (це перше тренування для цієї вправи).")
            st.text_area(
                f"📜 Минула історія по вправі «{ex}» (лише скрол):", 
                value=past_history, 
                height=120, 
                key=f"history_{ex}_{i}", 
                disabled=True
            )
            st.markdown("---")

    # КНОПКА ЗАВЕРШЕННЯ
    if st.button(f"✅ Завершити тренування {selected_client}", type="primary", use_container_width=True):
        import datetime
        # Автоматично беремо сьогоднішню дату українською
        days_ua = ["Понеділок", "Вівторок", "Середа", "Четвер", "П'ятниця", "Субота", "Неділя"]
        now = datetime.datetime.now()
        today_date = f"{days_ua[now.weekday()]} {now.strftime('%d.%m.%y')}"
        
        day_header = f"{today_date} ({client['today_focus']})"
        
        # Розкидаємо по історіях вправ
        for ex in client["today_exercises"]:
            sets_text = client["today_sets"].get(ex, "").strip()
            if sets_text:
                new_entry = f"{day_header}\n{sets_text}\n\n"
                client["exercise_history"][ex] = new_entry + client["exercise_history"].get(ex, "")
        
        # Записуємо в загальну історію тренувань
        new_workout = f"{day_header}\n"
        for i, ex in enumerate(client["today_exercises"], 1):
            new_workout += f"{i}. {ex}\n"
        client["workout_history"] = new_workout + "\n\n" + client["workout_history"]
        
        # Очищаємо екран
        client["today_exercises"] = []
        client["today_sets"] = {}
        client["today_focus"] = ""
        st.success("Тренування завершено! Дані збережені в архіви.")
        st.rerun()

# ВКЛАДКА: СПИСОК ВПРАВ
elif current_tab == "Список вправ":
    st.header(f"📋 Список вправ: {selected_client}")
    st.info("Тут ти можеш вставити або відредагувати весь список вправ для цієї клієнтки (кожна вправа з нового рядка).")
    client["exercise_list"] = st.text_area("Редагувати список:", value=client["exercise_list"], height=500)

# ВКЛАДКА: ІСТОРІЯ ТРЕНУВАНЬ
elif current_tab == "Історія тренувань":
    st.header(f"📅 Загальна історія тренувань: {selected_client}")
    client["workout_history"] = st.text_area("Перегляд історії:", value=client["workout_history"], height=500)
