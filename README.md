# 🥗 Tempo

A minimalist meal tracking app that helps you stay on top of your nutrition goals.

## Features

- **Daily Progress Tracking**
  - View your daily macro totals (protein, carbs, fat)
  - See protein progress as a percentage of your goal
  - Automatically updates as you log meals

- **Simple Meal Logging**
  - Quick text input for meal descriptions
  - Two-step process: log meal → confirm and save
  - Temporary toast notifications for feedback

- **Settings**
  - Set your daily calorie goal
  - Configure your protein target

## Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Data Storage

- Meals are stored locally in `meals.json`
- Each meal entry includes:
  - Unique ID
  - Timestamp
  - Description
  - Macro breakdown (protein, carbs, fat)

## Development

This is a work in progress. Current focus areas:
- Adding macro estimation from meal descriptions
- Improving the UI/UX
- Adding more detailed progress tracking