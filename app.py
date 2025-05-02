import streamlit as st
import json
from datetime import datetime
import uuid

def load_meals():
    try:
        with open('meals.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"meals": []}

def save_meals(meals_data):
    with open('meals.json', 'w') as f:
        json.dump(meals_data, f, indent=2)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    st.write("Configure your meal tracking preferences")
    
    # Add some basic settings
    daily_calories = st.number_input("Daily Calorie Goal", min_value=1000, max_value=5000, value=2000, step=100)
    protein_goal = st.number_input("Protein Goal (g)", min_value=0, max_value=500, value=150, step=5)

# Main content
st.title("🥗 Tempo")
st.write("Hello World! Welcome to Tempo - your minimalist meal tracking app.")

# Meal logging
st.subheader("What did you eat today?")
with st.form("meal_form"):
    meal_input = st.text_input("", 
                             placeholder="e.g., 2 rotis with dal and cucumber salad",
                             help="Just type what you ate like you're telling a friend")
    submitted = st.form_submit_button("Log Meal")
    
    if submitted and meal_input:
        # Load existing meals
        meals_data = load_meals()
        
        # Create new meal entry
        new_meal = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "description": meal_input,
            "macros": {
                "protein": 25,  # Dummy value for now
                "carbs": 45,    # Dummy value for now
                "fat": 12       # Dummy value for now
            }
        }
        
        # Add new meal and save
        meals_data["meals"].append(new_meal)
        save_meals(meals_data)
        
        st.write("### Macro Breakdown")
        col1, col2, col3 = st.columns(3)
        with col1:
            protein_percent = (new_meal["macros"]["protein"] / protein_goal) * 100
            st.metric("Protein", f"{new_meal['macros']['protein']}g", f"{protein_percent:.0f}% of goal")
        with col2:
            st.metric("Carbs", f"{new_meal['macros']['carbs']}g")
        with col3:
            st.metric("Fat", f"{new_meal['macros']['fat']}g") 