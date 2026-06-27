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
                "Біцепс палкою": "Вівторок 27.06.26\n1п: 15кг 15р з 3\n2п: 20кг 12р з 2\nДля заміток: все супер\n\nНеділя 21.06.26\n1п: 15кг 12р з 4\nДля заміток: легка вага",
                "Тріцепс палкою": "Вівторок 27.06.26\n1п: 12кг 15р з 2\nДля заміток: ok"
            },
            "today_workout_exercises": ["Біцепс палкою", "Тріцепс палкою"],
            "today_workout_sets": {
                "Біцепс палкою": "1п: 15кг 15р 3з\n2п: 20кг 12р 2з\n3п: 20кг 12р 1з\n4п: 20кг 12р 1з\nДля заміток: 4 підхід останні 2 без техніки",
                "Тріцепс палкою": "1п: 15кг 15р 3з\nДля заміток:"
            },
            "today_comment": "спина, руки"
        }
    }

# --- 2. КЕРУВАННЯ У БОКОВОМУ МЕНЮ ---
st.sidebar.title("🗂️ Керування")
client_names = list(st.session_state.clients_data.keys())
selected_client = st.sidebar.selectbox("🙋‍♀️ Обери клієнтку:", client_names)

tabs = ["Сьогодні", "Список вправ", "Історія тренувань", "Історія вправи"]
current_tab = st.sidebar.radio("Перейти до:", tabs)

client = st.session_state.clients_data[selected_client]

# --- 3. ЛОГІКА ВКЛАДОК ---

if current_tab == "Сьогодні":
    st.header(f"📝 {selected_client}: Тренування сьогодні")
    
    # Фокус дня
    client["today_comment"] = st.text_input("Фокус дня (наприклад: спина, руки):", value=client["today_comment"])
    
    st.markdown("---")
    
    # Конструктор вправ
    with st.expander("➕ Додати/видалити вправи зі списку Юлі"):
        raw_exercises = [line.strip() for line in client["exercise_list"].split("\n") if line.strip()]
        new_selection = []
        for ex in raw_exercises:
            is_checked = ex in client["today_workout_exercises"]
            if st.checkbox(ex, value=is_checked, key=f"manage_{ex}"):
                new_selection.append(ex)
        
        st.markdown("---")
        new_custom_ex = st.text_input("✨ Вписати нову вправу руками (якщо немає в списку):")
        if st.button("Додати цю нову вправу на сьогодні"):
            if new_custom_ex.strip() and new_custom_ex.strip() not in new_selection:
                new_selection.append(new_custom_ex.strip())
                client["exercise_list"] = new_custom_ex.strip() + "\n" + client["exercise_list"]
                st.success(f"Вправу '{new_custom_ex.strip()}' додано!")
                
        client["today_workout_exercises"] = new_selection
        
    st.markdown("---")
    
    # ВИВЕДЕННЯ ВПРАВ 
    for i, ex in enumerate(client["today_workout_exercises"], 1):
        st.subheader(f"🏋️ {i}. {ex.upper()}")
        
        col_input, col_history = st.columns([1.2, 1.0])
        
        with col_input:
            # Твоє поле для активного заповнення (біле, звичне)
            current_sets_val = client["today_workout_sets"].get(ex, "1п: \n2п: \nДля заміток:")
            client["today_workout_sets"][ex] = st.text_area(
                f"Введи сьогоднішні підходи:", 
                value=current_sets_val, 
                height=180, 
                key=f"sets_{ex}_{i}"
            )
            
        with col_history:
            st.write("📜 **Минула історія (лише скрол):**")
            ex_history_text = client["exercise_history"].get(ex, "Історія цієї вправи поки порожня.")
            
            # НОВИЙ СПОСІБ: Виводимо історію в закритому контейнері з фіксованою висотою та скролом
            # Текст замінено на HTML-формат, щоб він точно зафіксувався
            formatted_text = ex_history_text.replace('\n', '<br>')
            st.markdown(
                f"""
                <div style="
                    height: 180px; 
                    overflow-y: auto; 
                    background-color: #f0f2f6; 
                    padding: 10px; 
                    border-radius: 5px; 
                    border: 1px solid #ccd1d9;
                    font-family: monospace;
                    font-size: 14px;
                    color: #333333;
                    line-height: 1.5;
                ">
                    {formatted_text}
                </div>
                """, 
                unsafe_allow_name=True, # Дозволяє рендерити стилі на старих версіях
                unsafe_allow_html=True
            )
            
        st.markdown("---")

    # КНОПКА ЗАВЕРШЕННЯ ТРЕНУВАННЯ
    if st.button(f"✅ Завершити тренування {selected_client}", type="primary", use_container_width=True):
        today_date = f"Сьогодні {st.date_input('Дата:', key='btn_dt').strftime('%d.%m.%y')}" if 'btn_dt' in locals() else "Сьогодні 29.06.26"
        day_title = f"{today_date} ({client['today_comment']})"
        
        for ex in client["today_workout_exercises"]:
            sets_data = client["today_workout_sets"].get(ex, "").strip()
            history_entry = f"{day_title}\n{sets_data}\n\n"
            client["exercise_history"][ex] = history_entry + client["exercise_history"].get(ex, "")
            
        new_workout_record = f"{day_title}\n"
        for i, ex in enumerate(client["today_workout_exercises"], 1):
            new_workout_record += f"{i}. {ex}\n"
        client["workout_history"] = new_workout_record + "\n\n" + client["workout_history"]
        
        client["today_workout_exercises"] = []
        client["today_workout_sets"] = {}
        client["today_comment"] = ""
        st.success("Дані успішно розподілено!")
        st.rerun()

# Інші вкладки
elif current_tab == "Список вправ":
    st.header(f"📋 Список вправ: {selected_client}")
    client["exercise_list"] = st.text_area("Редагувати список:", value=client["exercise_list"], height=500)

elif current_tab == "Історія тренувань":
    st.header(f"📅 Загальна історія: {selected_client}")
    client["workout_history"] = st.text_area("Перегляд історії:", value=client["workout_history"], height=500)

elif current_tab == "Історія вправи":
    st.header(f"🏋️‍♀️ Повний щоденник вправ: {selected_client}")
    all_ex = list(client["exercise_history"].keys())
    if all_ex:
        sel_ex = st.selectbox("Обери вправу:", all_ex)
        st.text_area(f"Повна історія по {sel_ex}", value=client["exercise_history"][sel_ex], height=450)
