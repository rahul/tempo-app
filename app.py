import streamlit as st
import json
from datetime import datetime, date
import uuid
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

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

def display_meal_card(meal, show_date=True, tab_name=""):
    """Display a meal in a bordered container with its details"""
    with st.container(border=True):
        if show_date:
            meal_date = datetime.fromisoformat(meal["timestamp"]).strftime("%B %d, %Y %I:%M %p")
            st.write(f"**{meal_date}**")
        else:
            meal_time = datetime.fromisoformat(meal["timestamp"]).strftime("%I:%M %p")
            st.write(f"**{meal_time}**")
        st.write(meal["description"])
        if "interpretation" in meal:
            st.caption(meal['interpretation'])
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Protein", f"{meal['macros']['protein']}g")
        with col2:
            st.metric("Carbs", f"{meal['macros']['carbs']}g")
        with col3:
            st.metric("Fat", f"{meal['macros']['fat']}g")
        
        # Add action buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Delete", key=f"delete_{tab_name}_{meal['id']}"):
                meals_data = load_meals()
                # Remove the meal from the list
                meals_data["meals"] = [m for m in meals_data["meals"] if m["id"] != meal["id"]]
                save_meals(meals_data)
                st.session_state.notification = {
                    "message": "Meal deleted successfully!",
                    "type": "success"
                }
                st.rerun()
        with col2:
            if st.button("Repeat", key=f"repeat_{tab_name}_{meal['id']}"):
                # Create and save the repeated meal
                repeated_meal = {
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                    "description": meal["description"],
                    "macros": meal["macros"]
                }
                meals_data = load_meals()
                meals_data["meals"].append(repeated_meal)
                save_meals(meals_data)
                st.session_state.notification = {
                    "message": "Meal repeated successfully!",
                    "type": "success"
                }
                st.rerun()

def estimate_macros(meal_description):
    """Estimate macros using OpenAI API"""
    try:
        print(meal_description)
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are a nutrition expert. For the given meal description:
                1. First, explain what you understand about the meal (quantities, ingredients, preparation). Don't give feedback on the pros and cons of the meal.
                2. Then estimate the macronutrients (protein, carbs, fat in grams)
                
                Return a JSON object with:
                {
                    "interpretation": "Your understanding of the meal",
                    "macros": {"protein": X, "carbs": Y, "fat": Z}
                }"""},
                {"role": "user", "content": meal_description}
            ]
        )
        print(response)
        # Extract the JSON response
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        st.session_state.notification = {
            "message": f"Error estimating macros: {str(e)}",
            "type": "error"
        }
        return {
            "interpretation": "Unable to process the description",
            "macros": {"protein": 0, "carbs": 0, "fat": 0}
        }

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

# Create tabs
tab1, tab2 = st.tabs(["📅 Today", "📋 History"])

# Today Tab
with tab1:
    # Daily macro breakdown
    meals_data = load_meals()
    today_meals = get_today_meals(meals_data)
    daily_totals = calculate_daily_totals(today_meals)

    with st.container(border=True):
        st.write("### Today's Progress")
        col1, col2, col3 = st.columns(3)
        with col1:
            protein_diff = daily_totals["protein"] - protein_goal
            protein_percent = (daily_totals["protein"] / protein_goal) * 100
            st.metric("Protein", f"{daily_totals['protein']}g", 
                     f"{'+' if protein_diff > 0 else ''}{protein_diff}g",
                     delta_color="inverse" if protein_percent > 120 else "normal")
        with col2:
            st.metric("Carbs", f"{daily_totals['carbs']}g")
        with col3:
            st.metric("Fat", f"{daily_totals['fat']}g")

    # Meal logging
    st.subheader("What did you eat today?")
    with st.form("meal_input_form", clear_on_submit=True):
        meal_input = st.text_input("Meal Description", 
                                 placeholder="e.g., 2 rotis with dal and cucumber salad",
                                 help="Just type what you ate like you're telling a friend",
                                 label_visibility="collapsed")
        with st.container():
            st.markdown("""
                <style>
                div[data-testid="stDateInput"] {
                    width: 200px;
                }
                </style>
            """, unsafe_allow_html=True)
            meal_date = st.date_input("When did you eat this meal?", 
                                    value=date.today(),
                                    max_value=date.today(),
                                    label_visibility="collapsed")
        submitted = st.form_submit_button("Show Macros")
        
        if submitted and meal_input:
            # Create new meal entry and store in session state
            result = estimate_macros(meal_input)
            macros = result["macros"]

            if macros["protein"] == 0 and macros["carbs"] == 0 and macros["fat"] == 0:
                st.session_state.notification = {
                    "message": f"Error estimating macros. {result['interpretation']}",
                    "type": "error"
                }
                st.rerun()
            else:
                # Convert date to datetime for timestamp
                meal_datetime = datetime.combine(meal_date, datetime.now().time())
                st.session_state.pending_meal = {
                    "id": str(uuid.uuid4()),
                    "timestamp": meal_datetime.isoformat(),
                    "description": meal_input,
                    "macros": macros,
                    "interpretation": result["interpretation"]
                }

    # Show macro breakdown if we have a pending meal
    if st.session_state.pending_meal:
        st.write("### Macro Breakdown")
        st.caption(st.session_state.pending_meal['interpretation'])
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Protein", f"{st.session_state.pending_meal['macros']['protein']}g")
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

    # Today's meals
    st.write("### Today's Meals")
    if not today_meals:
        st.write("No meals logged yet today.")
    else:
        # Sort meals by timestamp (newest first)
        sorted_meals = sorted(today_meals, 
                            key=lambda x: x["timestamp"], 
                            reverse=True)
        for meal in sorted_meals:
            display_meal_card(meal, show_date=False, tab_name="today")

# History Tab
with tab2:
    st.write("### Past Meals")
    meals_data = load_meals()
    if not meals_data["meals"]:
        st.write("No meals logged yet.")
    else:
        # Sort meals by date (newest first)
        sorted_meals = sorted(meals_data["meals"], 
                            key=lambda x: x["timestamp"], 
                            reverse=True)
        
        for meal in sorted_meals:
            display_meal_card(meal, show_date=True, tab_name="history") 