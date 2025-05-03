import streamlit as st
import json
from datetime import datetime, date
import uuid

def load_meals():
    try:
        with open('meals.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Create meals.json with empty structure if it doesn't exist
        initial_data = {"meals": []}
        with open('meals.json', 'w') as f:
            json.dump(initial_data, f, indent=2)
        return initial_data

def save_meals(meals_data):
    with open('meals.json', 'w') as f:
        json.dump(meals_data, f, indent=2)

def get_today_meals(meals_data):
    today = date.today().isoformat()
    today_meals = [meal for meal in meals_data["meals"] 
                  if meal["timestamp"].startswith(today)]
    return today_meals

def calculate_daily_totals(meals):
    totals = {
        "protein": 0,
        "carbs": 0,
        "fat": 0
    }
    for meal in meals:
        for macro in totals:
            totals[macro] += meal["macros"][macro]
    return totals

# Initialize session state
if 'pending_meal' not in st.session_state:
    st.session_state.pending_meal = None
if 'notification' not in st.session_state:
    st.session_state.notification = {"message": None, "type": None}

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

# Show notification if needed
if st.session_state.notification["message"]:
    if st.session_state.notification["type"] == "success":
        st.toast(st.session_state.notification["message"], icon="✅")
    elif st.session_state.notification["type"] == "error":
        st.toast(st.session_state.notification["message"], icon="❌")
    elif st.session_state.notification["type"] == "warning":
        st.toast(st.session_state.notification["message"], icon="⚠️")
    st.session_state.notification = {"message": None, "type": None}

# Daily macro breakdown
meals_data = load_meals()
today_meals = get_today_meals(meals_data)
daily_totals = calculate_daily_totals(today_meals)

with st.container(border=True):
    st.write("### Today's Progress")
    col1, col2, col3 = st.columns(3)
    with col1:
        protein_percent = (daily_totals["protein"] / protein_goal) * 100
        st.metric("Protein", f"{daily_totals['protein']}g", f"{protein_percent:.0f}% of goal")
    with col2:
        st.metric("Carbs", f"{daily_totals['carbs']}g")
    with col3:
        st.metric("Fat", f"{daily_totals['fat']}g")

# Meal logging
st.subheader("What did you eat today?")
with st.form("meal_input_form", clear_on_submit=True):
    meal_input = st.text_input("", 
                             placeholder="e.g., 2 rotis with dal and cucumber salad",
                             help="Just type what you ate like you're telling a friend")
    submitted = st.form_submit_button("Show Macros")
    
    if submitted and meal_input:
        # Create new meal entry and store in session state
        st.session_state.pending_meal = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "description": meal_input,
            "macros": {
                "protein": 25,  # Dummy value for now
                "carbs": 45,    # Dummy value for now
                "fat": 12       # Dummy value for now
            }
        }

# Show macro breakdown if we have a pending meal
if st.session_state.pending_meal:
    st.write("### Macro Breakdown")
    col1, col2, col3 = st.columns(3)
    with col1:
        protein_percent = (st.session_state.pending_meal["macros"]["protein"] / protein_goal) * 100
        st.metric("Protein", f"{st.session_state.pending_meal['macros']['protein']}g", f"{protein_percent:.0f}% of goal")
    with col2:
        st.metric("Carbs", f"{st.session_state.pending_meal['macros']['carbs']}g")
    with col3:
        st.metric("Fat", f"{st.session_state.pending_meal['macros']['fat']}g")
    
    # Second form for confirmation
    with st.form("meal_confirm_form"):
        st.write("### Ready to save this meal?")
        confirmed = st.form_submit_button("Save Meal")
        if confirmed:
            # Add new meal and save
            meals_data["meals"].append(st.session_state.pending_meal)
            save_meals(meals_data)
            # Set notification to show after reload
            st.session_state.notification = {
                "message": "Meal added successfully!",
                "type": "success"
            }
            # Clear the pending meal
            st.session_state.pending_meal = None
            # Reload the page
            st.rerun() 