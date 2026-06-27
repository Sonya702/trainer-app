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
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Сьогодні"

# --- 2. ВИБІР КЛІЄНТКИ ТА ВКЛАДКИ У БОКОВОМУ МЕНЮ ---
st.sidebar.title("🗂️ Керування")

client_names = list(st.session_state.clients_data.keys())
selected_client = st.sidebar.selectbox("🙋‍♀️ Обери клієнтку:", client_names)

tabs = ["Сьогодні", "Список вправ", "Історія тренувань", "Історія вправи"]
st.session_state.current_tab = st.sidebar.radio("Перейти до:", tabs, index=tabs.index(st.session_state.current_tab))

client = st.session_state.clients_data[selected_client]

# --- 3. ЛОГІКА РОБОТИ ВКЛАДОК ---

# ВКЛАДКА: СЬОГОДНІ
if st.session_state.current_tab == "Сьогодні":
    st.header(f"📝 {selected_client}: Тренування сьогодні")
    
    # --- ВИБІР ВПРАВ ЗІ СПИСКУ ---
    with st.expander("➕ Додати вправи зі списку на сьогодні"):
        raw_exercises = [line.strip() for line in client["exercise_list"].split("\n") if line.strip()]
        st.write("Познач вправи:")
        selected_to_add = []
        for ex in raw_exercises:
            if st.checkbox(ex, key=f"check_{ex}"):
                selected_to_add.append(ex)
        
        if st.button("Вставити вибрані вправи в блокнот"):
            existing_matches = re.findall(r'^\d+\.\s*', client["today_workout"], flags=re.MULTILINE)
            current_count = len(existing_matches)
            
            new_lines = ""
            for i, ex in enumerate(selected_to_add, start=current_count + 1):
                new_lines += f"\n\n{i}. {ex}\n1п: \n2п: \nДля заміток:"
            
            client["today_workout"] += new_lines
            st.rerun()
            
    st.markdown("---")

    # Твоє улюблене суцільне поле, де ти пишеш як у Samsung Notes
    client["today_workout"] = st.text_area("Твій щоденник тренування:", value=client["today_workout"], height=400)
    
    # --- ШВИДКИЙ ПЕРЕХІД ДО ІСТОРІЇ (БЕЗ HTML, ЧИСТІ КНОПКИ КЛІЄНТА) ---
    current_exercises = re.findall(r'^\d+\.\s*(.+)', client["today_workout"], flags=re.MULTILINE)
    if current_exercises:
        st.markdown("---")
        st.write("🔍 **Подивитися минулу історію вправи:**")
        # Робимо випадаючий список суто з тих вправ, які ти СЬОГОДНІ вписала в текст
        chosen_ex = st.selectbox("Обери вправу, щоб глянути її минулі ваги:", [e.strip() for e in current_exercises], key="quick_search")
        if st.button(f"📖 Відкрити щоденник: {chosen_ex}"):
            st.session_state.selected_exercise = chosen_ex
            st.session_state.current_tab = "Історія вправи"
            st.rerun()

    st.markdown("---")
    # КНОПКА ЗАВЕРШЕННЯ
    if st.button(f"✅ Завершити тренування {selected_client}", type="primary", use_container_width=True):
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

            new_workout_record = f"{day_title}\n"
            for i, ex in enumerate(exercises_done, 1):
                new_workout_record += f"{i}. {ex}\n"
            client["workout_history"] = new_workout_record + "\n\n" + client["workout_history"]
            
            client["today_workout"] = "Сьогодні\n"
            st.success(f"Дані успішно збережено!")
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
