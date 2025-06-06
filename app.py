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

def get_protein_choices():
    """Get list of popular protein choices in India from ChatGPT"""
    try:
        with open('cache.json', 'r') as f:
            cache = json.load(f)
            if "protein_choices" in cache:
                return cache["protein_choices"]
    except FileNotFoundError:
        cache = {}

    # If not in cache, try to get from OpenAI
    try:
        response = openai.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": """You are a nutrition expert familiar with Indian cuisine."""},
                {"role": "user", "content": """List top 5 most popular protein sources (not recipes or combinations) used by fitness enthusiasts and athletes in India.
                Return ONLY a JSON array of strings, no explanations.
                Example: ["Chicken", "Paneer", "Whey Protein"]"""}
            ]
        )
        protein_choices = json.loads(response.choices[0].message.content)
    except Exception as e:
        # Fallback to default list if API call fails
        protein_choices = [
            "Chicken", "Paneer", "Whey Protein",
            "Eggs", "Dal"
        ]

    # Save choices to cache
    cache["protein_choices"] = protein_choices
    with open('cache.json', 'w') as f:
        json.dump(cache, f, indent=2)

    # Now handle preferences
    try:
        preferences = load_preferences()
    except FileNotFoundError:
        preferences = {"protein_sources": []}
        save_preferences(preferences)

    # Filter out preferences that aren't in the choices
    preferences["protein_sources"] = [
        protein for protein in preferences["protein_sources"]
        if protein in protein_choices
    ]
    save_preferences(preferences)

    return protein_choices

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
    # Calculate total calories
    totals["calories"] = (totals["protein"] * 4) + (totals["carbs"] * 4) + (totals["fat"] * 9)
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

def load_goals():
    try:
        with open('goals.json', 'r') as f:
            goals = json.load(f)
            # Add last_meal_time if it doesn't exist
            if "last_meal_time" not in goals:
                goals["last_meal_time"] = "18:00"
                save_goals(goals)
            return goals
    except FileNotFoundError:
        # Create goals.json with default values if it doesn't exist
        default_goals = {
            "daily_calories": 2000,
            "protein_goal": 150,
            "last_meal_time": "18:00"  # Default to 6 PM
        }
        with open('goals.json', 'w') as f:
            json.dump(default_goals, f, indent=2)
        return default_goals

def save_goals(goals):
    with open('goals.json', 'w') as f:
        json.dump(goals, f, indent=2)

def load_preferences():
    try:
        with open('preferences.json', 'r') as f:
            preferences = json.load(f)
            # Add last_meal_time if it doesn't exist
            if "last_meal_time" not in preferences:
                preferences["last_meal_time"] = "18:00"
                save_preferences(preferences)
            return preferences
    except FileNotFoundError:
        # Create preferences.json with default values if it doesn't exist
        default_preferences = {
            "protein_sources": [],
            "last_meal_time": "18:00"  # Default to 6 PM
        }
        with open('preferences.json', 'w') as f:
            json.dump(default_preferences, f, indent=2)
        return default_preferences

def save_preferences(preferences):
    with open('preferences.json', 'w') as f:
        json.dump(preferences, f, indent=2)

def get_meal_suggestions(goals, preferences, today_meals):
    """Get meal suggestions from ChatGPT based on goals and progress"""
    # Calculate remaining time
    current_time = datetime.now()
    last_meal_time = datetime.combine(current_time.date(), datetime.strptime(preferences["last_meal_time"], "%H:%M").time())
    hours_remaining = (last_meal_time - current_time).total_seconds() / 3600
    
    # Calculate remaining macros
    daily_totals = calculate_daily_totals(today_meals)
    remaining_protein = goals["protein_goal"] - daily_totals["protein"]
    remaining_calories = goals["daily_calories"] - daily_totals["calories"]
    
    # Prepare the prompt
    prompt = f"""You are a nutrition expert helping with meal planning. Here's the situation:
- Time left until last meal of the day ({preferences['last_meal_time']}): {hours_remaining:.1f} hours
- Remaining protein goal: {remaining_protein}g
- Remaining calories: {remaining_calories} kcal
- Preferred protein sources: {', '.join(preferences['protein_sources'])}

Please suggest 1-2 meals that:
1. Use the preferred protein sources
2. Help make significant progress towards the remaining goals
3. Are realistic and healthy (no extreme suggestions)
4. Include portion sizes
5. Are appropriate for the time of day

If there's not enough time to make significant progress, say so and explain why.

Return a JSON object with:
{{
    "suggestions": [
        {{
            "meal": "meal description with portions",
            "protein": protein_in_grams,
            "carbs": carbs_in_grams,
            "fat": fat_in_grams,
            "calories": calories
        }}
    ],
    "note": "any important notes about timing or feasibility"
}}"""

    try:
        response = openai.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": prompt}
            ]
        )
        response_text = response.choices[0].message.content.strip()
        if not response_text:
            raise ValueError("Empty response from ChatGPT")
            
        try:
            suggestions = json.loads(response_text)
            if not isinstance(suggestions, dict) or "suggestions" not in suggestions:
                raise ValueError("Invalid response format")
            return suggestions
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response: {response_text}")
            
    except Exception as e:
        return {
            "suggestions": [],
            "note": f"Error getting suggestions: {str(e)}"
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
    
    # Load current goals and preferences
    goals = load_goals()
    preferences = load_preferences()
    
    # Add some basic settings
    daily_calories = st.number_input("Daily Calorie Goal", min_value=1000, max_value=5000, value=goals["daily_calories"], step=100)
    protein_goal = st.number_input("Protein Goal (g)", min_value=0, max_value=500, value=goals["protein_goal"], step=5)
    
    # Last meal time setting
    last_meal_time = st.time_input(
        "Last Meal Time",
        value=datetime.strptime(preferences["last_meal_time"], "%H:%M").time(),
        help="This is used to calculate how many meals you can have before the end of the day"
    )
    
    # Save goals if they've changed
    if daily_calories != goals["daily_calories"] or protein_goal != goals["protein_goal"]:
        new_goals = {
            "daily_calories": daily_calories,
            "protein_goal": protein_goal
        }
        save_goals(new_goals)
        st.session_state.notification = {
            "message": "Goals updated successfully!",
            "type": "success"
        }
        st.rerun()

    # Save preferences if they've changed
    if last_meal_time.strftime("%H:%M") != preferences["last_meal_time"]:
        new_preferences = {
            "protein_sources": preferences["protein_sources"],
            "last_meal_time": last_meal_time.strftime("%H:%M")
        }
        save_preferences(new_preferences)
        st.session_state.notification = {
            "message": "Preferences updated successfully!",
            "type": "success"
        }
        st.rerun()

    # Protein Preferences
    st.write("### Protein Preferences")
    st.write("Select your preferred protein sources")
    
    # Get protein choices from cache or ChatGPT
    protein_options = get_protein_choices()
    
    # Add refresh button
    if st.button("🔄 Refresh Protein Choices"):
        # Delete cache to force refresh
        try:
            os.remove('cache.json')
        except FileNotFoundError:
            pass
        st.rerun()
    
    # Filter out invalid preferences
    valid_preferences = [
        protein for protein in preferences["protein_sources"]
        if protein in protein_options
    ]
    
    # Show protein options as checkboxes
    selected_proteins = []
    for protein in protein_options:
        if st.checkbox(protein, value=protein in valid_preferences):
            selected_proteins.append(protein)
    
    # Save preferences if they've changed
    if selected_proteins != preferences["protein_sources"]:
        new_preferences = {
            "protein_sources": selected_proteins
        }
        save_preferences(new_preferences)
        st.session_state.notification = {
            "message": "Protein preferences updated!",
            "type": "success"
        }
        st.rerun()

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
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            protein_diff = daily_totals["protein"] - protein_goal
            protein_percent = (daily_totals["protein"] / protein_goal) * 100
            delta_color = "normal"  # default color
            if protein_percent > 120:
                delta_color = "inverse"  # red when over 120%
            elif 95 <= protein_percent <= 105:
                delta_color = "normal"  # green when within ±5%
            st.metric("Protein", f"{daily_totals['protein']}g", 
                     f"{'+' if protein_diff > 0 else ''}{protein_diff}g",
                     delta_color=delta_color)
        with col2:
            st.metric("Carbs", f"{daily_totals['carbs']}g")
        with col3:
            st.metric("Fat", f"{daily_totals['fat']}g")
        with col4:
            calories_diff = daily_totals["calories"] - daily_calories
            calories_percent = (daily_totals["calories"] / daily_calories) * 100
            delta_color = "normal"  # default color
            if calories_percent > 110:
                delta_color = "inverse"  # red when over 110%
            elif 90 <= calories_percent <= 110:
                delta_color = "normal"  # green when within ±10%
            st.metric("Calories", f"{daily_totals['calories']} kcal", 
                     f"{'+' if calories_diff > 0 else ''}{calories_diff} kcal",
                     delta_color=delta_color)

    # Get meal suggestions
    if st.button("Get Meal Suggestions"):
        goals = load_goals()
        preferences = load_preferences()
        suggestions = get_meal_suggestions(goals, preferences, today_meals)
        
        st.write("### Meal Suggestions")
        if suggestions["suggestions"]:
            for suggestion in suggestions["suggestions"]:
                with st.container(border=True):
                    st.write(f"**{suggestion['meal']}**")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Protein", f"{suggestion['protein']}g")
                    with col2:
                        st.metric("Carbs", f"{suggestion['carbs']}g")
                    with col3:
                        st.metric("Fat", f"{suggestion['fat']}g")
                    with col4:
                        st.metric("Calories", f"{suggestion['calories']} kcal")
        if suggestions["note"]:
            st.info(suggestions["note"])

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

            if result["interpretation"] == "Unable to process the description":
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