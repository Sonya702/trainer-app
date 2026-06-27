import streamlit as st
import re

st.set_page_config(page_title="Блокнот Тренера", page_icon="🏋️‍♀️", layout="centered")

# --- 1. СТВОРЕННЯ БАЗИ ДАНИХ ДЛЯ БАГАТЬОХ КЛІЄНТОК ---
if 'clients_data' not in st.session_state:
    st.session_state.clients_data = {
        "Юля": {
            "exercise_list": "Жим штанги\nЖим гантель\nБіцепс гантелями\nБіцепс палкою\nТріцепс палкою\nПрес\n\nЖим ногами\nРозгинання ніг\nМісток",
            "workout_history": "Вівторок 27.06.26 (біцепс, тріцепс + плечі)\n1. Біцепс палкою\n2. Тріцепс палкою\n3. Біцепс молотки\n4. Тріцепс віджимання\n5. Плечі махи\n6. Прес",
            "exercise_history": {
                "Біцепс палкою": "Вівторок 27.06.26\n1п: 15кг 15р 3з\n2п: 20кг 12р 2з\nДля заміток: все супер"
            },
            "today_workout": "Сьогодні 29.06.26 (спина, руки)\n\n1. Біцепс палкою\n1п: 15кг 15р 3з\n\n2. Тріцепс палкою\n1п: 15кг 15р 3з"
        },
        "Олена": {
            "exercise_list": "Присідання\nВипади\nТяга верхнього блоку\nPlank",
            "workout_history": "П'ятниця 26.06.26 (Ноги)\n1. Присідання\n2. Випади",
            "exercise_history": {
                "Присідання": "П'ятниця 26.06.26\n1п: 30кг 12р 2з"
            },
            "today_workout": "Сьогодні 29.06.26 (Всього тіла)\n\n1. Тяга верхнього блоку\n1п: 25кг 12р 3з"
        }
    }

if 'selected_exercise' not in st.session_state:
    st.session_state.selected_exercise = ""

# --- 2. ВИБІР КЛІЄНТКИ ТА ВКЛАДКИ У БОКОВОМУ МЕНЮ ---
st.sidebar.title("🗂️ Керування")

# Вибір дівчини
client_names = list(st.session_state.clients_data.keys())
selected_client = st.sidebar.selectbox("🙋‍♀️ Обери клієнтку:", client_names)

# Меню вкладок для вибраної дівчини
tabs = ["Сьогодні", "Список вправ", "Історія тренувань", "Історія вправи"]
current_tab = st.sidebar.radio("Перейти до:", tabs)

# Створюємо зручне посилання на дані саме цієї дівчини, щоб не писати довгий код
client = st.session_state.clients_data[selected_client]

# --- 3. ЛОГІКА РОБОТИ ВКЛАДОК ---

# ВКЛАДКА: СЬОГОДНІ
if current_tab == "Сьогодні":
    st.header(f"📝 {selected_client}: Тренування сьогодні")
    
    # Поле заповнення (індивідуальне для кожної дівчини)
    client["today_workout"] = st.text_area("Заповнюй підходи тут:", value=client["today_workout"], height=350)
    
    # Кнопки швидкого переходу до історії конкретної вправи
    st.markdown("---")
    st.write("🔍 **Швидкий перехід до історії вправи:**")
    current_exercises = re.findall(r'^\d+\.\s*(.+)', client["today_workout"], flags=re.MULTILINE)
    
    cols = st.columns(4)
    for i, ex in enumerate(current_exercises):
        with cols[i % 4]:
            if st.button(f"📖 {ex.strip()}"):
                st.session_state.selected_exercise = ex.strip()
                st.info(f"Перейди на вкладку 'Історія вправи' у лівому меню, щоб побачити щоденник для: {ex.strip()}")
                st.rerun()

    st.markdown("---")
    # КНОПКА ЗАВЕРШЕННЯ
    if st.button(f"✅ Завершити тренування {selected_client}", type="primary"):
        lines = client["today_workout"].split('\n')
        if lines:
            day_title = lines[0].strip()
            current_ex = None
            current_sets = []
            exercises_done = []
            
            for line in lines[1:]:
                match = re.match(r'^\d+\.\s*(.+)', line.strip())
                if match:
                    if current_ex:
                        history_entry = f"{day_title}\n" + "\n".join(current_sets) + "\n\n"
                        client["exercise_history"][current_ex] = history_entry + client["exercise_history"].get(current_ex, "")
                        if current_ex not in client["exercise_list"]:
                            client["exercise_list"] = f"{current_ex}\n" + client["exercise_list"]
                    
                    current_ex = match.group(1).strip()
                    exercises_done.append(current_ex)
                    current_sets = []
                elif line.strip():
                    current_sets.append(line.strip())
            
            if current_ex:
                history_entry = f"{day_title}\n" + "\n".join(current_sets) + "\n\n"
                client["exercise_history"][current_ex] = history_entry + client["exercise_history"].get(current_ex, "")
                if current_ex not in client["exercise_list"]:
                    client["exercise_list"] = f"{current_ex}\n" + client["exercise_list"]

            # Запис в загальну історію
            new_workout_record = f"{day_title}\n"
            for i, ex in enumerate(exercises_done, 1):
                new_workout_record += f"{i}. {ex}\n"
            client["workout_history"] = new_workout_record + "\n\n" + client["workout_history"]
            
            # Очищення
            client["today_workout"] = ""
            st.success(f"Дані Олени/Юлі успішно розподілено!")
            st.rerun()

# ВКЛАДКА: СПИСОК ВПРАВ
elif current_tab == "Список вправ":
    st.header(f"📋 Список вправ: {selected_client}")
    client["exercise_list"] = st.text_area("Редагувати список:", value=client["exercise_list"], height=500)

# ВКЛАДКА: ІСТОРІЯ ТРЕНУВАНЬ
elif current_tab == "Історія тренувань":
    st.header(f"📅 Загальна історія: {selected_client}")
    client["workout_history"] = st.text_area("Перегляд історії:", value=client["workout_history"], height=500)

# ВКЛАДКА: ІСТОРІЯ ВПРАВИ
elif current_tab == "Історія вправи":
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
