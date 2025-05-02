# tempo-app
# 🥗 Tempo

**Tempo** is a minimalist, open-source meal tracking app that lets you log what you eat in natural language and tracks your daily macronutrient progress — effortlessly.

No barcode scanning. No food databases. Just type your meals like you speak, and Tempo handles the rest using an LLM-powered backend.

---

## 🎯 Features

- 🧠 **Natural Language Meal Logging**  
  Just type: `"2 rotis with dal and cucumber salad"` — Tempo estimates your macros instantly.

- 📊 **Daily Macro Tracking**  
  Get real-time feedback on your calories, protein, carbs, and fat goals.

- 💬 **Conversational Coaching (Coming Soon)**  
  Gentle nudges to help you stay aligned with your health goals.

- 🗃️ **Self-hosted & Private**  
  Runs locally or on your own server — no data sent anywhere unless you choose.

---

## 🛠️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/your-username/tempo.git
cd tempo
```

### 2. Install Poetry (if not already installed)
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### 3. Install dependencies
```bash
poetry install
```

### 4. Set your OpenAI API key
Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-openai-api-key
```

(You can get an API key from [https://platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys))

> ✅ Tempo automatically loads your `.env` file using `python-dotenv`.

### 5. Run the app
```bash
poetry run streamlit run app.py
```

---

## 🧠 How It Works

Tempo uses a custom **Model Context Protocol (MCP)** server that:
1. Takes your meal description
2. Sends it to GPT-4 with a structured prompt
3. Receives macros in JSON format
4. Logs and displays your daily progress

All data is stored locally using SQLite (or JSON fallback for ultra-lightweight mode).

---

## 📂 Project Structure

```
tempo/
│
├── app.py                  # Main Streamlit app
├── mcp/
│   ├── prompt_engine.py    # ChatGPT prompt logic
│   └── parser.py           # LLM output handling
├── storage/
│   └── db.py               # Local database (SQLite)
├── .env.example            # Example environment variables
├── pyproject.toml          # Poetry config
├── README.md
```

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

To contribute:
1. Fork this repo
2. Create a feature branch (`git checkout -b feature-name`)
3. Commit your changes
4. Push to your fork
5. Open a pull request

---

## 📄 License

MIT License. See `LICENSE` file for details.

---

## ✨ Future Plans

- Conversational meal planning
- Weekly macro trends
- Multi-user mode
- Offline mode (LLM fallback)
- Mobile-ready interface

---

Built with ❤️ by [Your Name or GitHub Handle]