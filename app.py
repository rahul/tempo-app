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