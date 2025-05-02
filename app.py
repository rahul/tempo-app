import streamlit as st

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
        st.write("### Macro Breakdown")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Protein", "25g", "17% of goal")
        with col2:
            st.metric("Carbs", "45g")
        with col3:
            st.metric("Fat", "12g") 