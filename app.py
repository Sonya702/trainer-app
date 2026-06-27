import streamlit as st
import re

st.set_page_config(page_title="Блокнот Тренера", page_icon="🏋️‍♀️", layout="centered")

# --- 1. СТВОРЕННЯ БАЗИ ДАНИХ ---
if 'clients_data' not in st.session_state:
    st.session_state.clients_data = {
        "Юля": {
            "exercise_list": "Жим штанги\nЖим гантель\nБіцепс гантелями\nБіцепс палкою\nТріцепс палкою\nПрес\n\nЖим ногами\nРозгинання ніг\nМісток",
            "workout_history": "Вівторок 27.06.26 (біцепс, тріцепс + плечі)\n1. Біцепс палкою\n2. Тріцепс палкою\n3. Біцепс молотки\n4. Тріцепс віджимання\n5. Плечі махи\n6. Прес",
            "exercise_history": {
                "Біцепс палкою": "Вівторок 27.06.26\n1п: 15кг 15р 3з\n2п: 20кг 12р 2з\nДля заміток: все супер",
                "Тріцепс палкою": "Вівторок 27.06.26\n1п: 12кг 15р 2з"
            },
            "today_workout_exercises": ["Біцепс палкою", "Тріцепс палкою"],
            "today_workout_sets": {
                "Біцепс палкою": "1п: 15кг 15р 3з\n2п: 20кг 12р 2з\n3п: 20кг 12р 1з\n4п: 20кг 12р 1з\nДля заміток: 4 підхід останні 2 без техніки",
                "Тріцепс палкою": "1п: 15кг 15р 3з\nДля заміток:"
            },
            "today_comment": "спина, руки"
        },
        "Олена": {
            "exercise_list": "Присідання\nВипади\nТяга верхнього блоку\nPlank",
            "workout_history": "П'ятниця 26.06.26 (Ноги)\n1. Присідання\n2. Випади",
            "exercise_history": {"Присідання": "П'ятниця 26.06.26\n1п: 30кг 12р 2з"},
            "today_workout_exercises": ["Тяга верхнього блоку"],
            "today_workout_sets": {"Тяга верхнього блоку": "1п: 25кг 12р 3з"},
            "today_comment": "Всього тіла"
        }
    }

if 'selected_exercise' not in st.session_state:
    st.session_state.selected_exercise = ""
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Сьогодні"

# --- 2. КЕРУВАННЯ У БОКОВОМУ МЕНЮ ---
st.sidebar.title("🗂️ Керування")
client_names = list(st.session_state.clients_data.keys())
selected_client = st.sidebar.selectbox("🙋‍♀️ Обери клієнтку:", client_names)

tabs = ["Сьогодні", "Список вправ", "Історія тренувань", "Історія вправи"]
st.session_state.current_tab = st.sidebar.radio("Перейти до:", tabs, index=tabs.index(st.session_state.current_tab))

client = st.session_state.clients_data[selected_client]

# --- 3. ЛОГІКА ВКЛАДОК ---

if st.session_state.current_tab == "Сьогодні":
    st.header(f"📝 {selected_client}: Тренування сьогодні")
    
    # Коментар до дня
    client["today_comment"] = st.text_input("Фокус дня (наприклад: спина, руки):", value=client["today_comment"])
    
    st.markdown("---")
    
    # Конструктор вправ на сьогодні
    with st.expander("➕ Додати/видалити вправи зі списку"):
        raw_exercises = [line.strip() for line in client["exercise_list"].split("\n") if line.strip()]
        new_selection = []
        for ex in raw_exercises:
            is_checked = ex in client["today_workout_exercises"]
            if st.checkbox(ex, value=is_checked, key=f"manage_{ex}"):
                new_selection.append(ex)
        
        # Можливість вписати абсолютно нову вправу руками
        new_custom_ex = st.text_input("✨ Вписати нову вправу руками (якщо немає в списку):")
        if st.button("Додати цю нову вправу"):
            if new_custom_ex.strip() and new_custom_ex.strip() not in client["today_workout_exercises"]:
                new_selection.append(new_custom_ex.strip())
                client["exercise_list"] = new_custom_ex.strip() + "\n" + client["exercise_list"]
                
        client["today_workout_exercises"] = new_selection
        
    st.markdown("---")
    
    # ВИВЕДЕННЯ СПИСКУ ВПРАВ ТА ПОЛІВ ВВОДУ
    st.write("📋 **План на сьогодні (Клікни на назву вправи для перегляду її історії):**")
    
    for i, ex in enumerate(client["today_workout_exercises"], 1):
        # Назва вправи оформлена як кнопка-лінк. Клік по ній переводить в історію
        if st.button(f"🔗 {i}. {ex.upper()}", key=f"link_{ex}_{i}", use_container_width=True):
            st.session_state.selected_exercise = ex
            st.session_state.current_tab = "Історія вправи"
            st.rerun()
            
        # Поле для введення підходів СУТО для цієї вправи
        current_sets_val = client["today_workout_sets"].get(ex, "1п: \n2п: \nДля заміток:")
        client["today_workout_sets"][ex] = st.text_area(
            f"Підходи для {ex}:", 
            value=current_sets_val, 
            height=120, 
            key=f"sets_{ex}_{i}",
            label_visibility="collapsed"
        )
        st.markdown(" ")

    st.markdown("---")
    
    # КНОПКА ЗАВЕРШЕННЯ ТРЕНУВАННЯ
    if st.button(f"✅ Завершити тренування {selected_client}", type="primary", use_container_width=True):
        today_date = "Сьогодні 29.06.26" # Для тесту фіксована
        day_title = f"{today_date} ({client['today_comment']})"
        
        # Розподіляємо по "Історіях вправ"
        for ex in client["today_workout_exercises"]:
            sets_data = client["today_workout_sets"].get(ex, "").strip()
            history_entry = f"{day_title}\n{sets_data}\n\n"
            client["exercise_history"][ex] = history_entry + client["exercise_history"].get(ex, "")
            
        # Записуємо в "Історію тренувань"
        new_workout_record = f"{day_title}\n"
        for i, ex in enumerate(client["today_workout_exercises"], 1):
            new_workout_record += f"{i}. {ex}\n"
        client["workout_history"] = new_workout_record + "\n\n" + client["workout_history"]
        
        # Очищаємо сьогоднішній день
        client["today_workout_exercises"] = []
        client["today_workout_sets"] = {}
        client["today_comment"] = ""
        st.success("Дані успішно розподілено по вкладках!")
        st.rerun()

# ВКЛАДКА: СПИСОК ВПРАВ
elif st.session_state.current_tab == "Список вправ":
    st.header(f"📋 Список вправ: {selected_client}")
    client["exercise_list"] = st.text_area("Редагувати список:", value=client["exercise_list"], height=500)

# ВКЛАДКА: ІСТОРІЯ ТРЕНУВАНЬ
elif st.session_state.current_tab == "Історія тренувань":
    st.header(f"📅 Загальна історія: {selected_client}")
    client["workout_history"] = st.text_area("Перегляд історії:", value=client["workout_history"], height=500)

# ВКЛАДКА: ІСТОРІЯ ВПРАВИ
elif st.session_state.current_tab == "Історія вправи":
    st.header(f"🏋️‍♀️ Щоденник вправи: {selected_client}")
    
    all_ex = list(client["exercise_history"].keys())
    if not st.session_state.selected_exercise or st.session_state.selected_exercise not in all_ex:
        if all_ex: st.session_state.selected_exercise = all_ex[0]
        
    if all_ex:
        st.session_state.selected_exercise = st.selectbox("Обери вправу:", all_ex, index=all_ex.index(st.session_state.selected_exercise) if st.session_state.selected_exercise in all_ex else 0)
        current_history = client["exercise_history"][st.session_state.selected_exercise]
        new_history = st.text_area(f"Історія по {st.session_state.selected_exercise}", value=current_history, height=450)
        client["exercise_history"][st.session_state.selected_exercise] = new_history
    else:
        st.info("В історії цієї клієнтки ще немає записів вправ.")
