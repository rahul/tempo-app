# Tempo - Minimalist Meal Tracking App

A simple meal tracking app that helps you stay on top of your nutrition goals.

## Features

- **Meal Logging**: Log your meals with a simple description
- **Macro Tracking**: Automatically estimates protein, carbs, and fat content
- **Daily Goals**: Set and track daily calorie and protein goals
- **Protein Preferences**: Choose your preferred protein sources
- **Smart Suggestions**: Get meal suggestions based on:
  - Remaining daily goals
  - Time until your last meal
  - Preferred protein sources
- **History View**: Review your past meals

## Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   poetry install
   ```
3. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## Usage

### Logging Meals
- Enter a simple description of what you ate
- The app will estimate the macronutrients
- Review and confirm the estimates
- Save the meal to your log

### Setting Goals
- Set your daily calorie and protein goals

### Getting Suggestions
- Choose your preferred protein sources
- Set your last meal time of the day
- Click "Get Meal Suggestions" to see what to eat next
- Suggestions are based on:
  - Your remaining daily goals
  - Time until your last meal
  - Your preferred protein sources

### Viewing History
- See all your past meals
- Review your progress over time
- Repeat or delete past meals

## Data Storage

The app stores your data in JSON files:
- `meals.json`: Your meal history
- `goals.json`: Your daily goals
- `preferences.json`: Your preferences

## Contributing

Feel free to submit issues and enhancement requests!

## Development

This is a work in progress. Current focus areas:
- Adding macro estimation from meal descriptions
- Improving the UI/UX
- Adding more detailed progress tracking