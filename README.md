# NutriStar

A clinical, minimalist Indian food nutrition and macronutrient tracker built with Flask.

## Features

- **Indian Food Database**: 80+ validated Indian food items (IFCT-2017 & USDA) with authentic regional aliases and household portion measures (*katori/bowl, piece, cup, glass, tablespoon, plate*).
- **Mifflin-St Jeor Calculator**: Computes personalized daily energy targets, BMR, TDEE, and macro ratios (Protein, Carbs, Fats, Fiber).
- **Focused Food Logger**: Quick food search with real-time portion customizer and expandable meal tray.
- **Monochrome Design System**: High-contrast, minimal black-and-white visual interface.
- **Local Data Persistence**: Client-side storage with zero tracking and full JSON export/import capability.
- **Security Hardened**: Built-in Content Security Policy, XSS escaping, strict physiological input boundaries, and non-negative quantity validation.

## Project Structure

```
nutritrack-flask/
├── app.py              # Application entry point & security middleware
├── config.py           # Configuration and environment management
├── models.py           # Category, activity, and goal data types
├── data/
│   ├── __init__.py
│   └── foods.py        # Curated Indian foods dataset and search engine
├── nutrition/
│   ├── __init__.py
│   ├── calculator.py   # Nutrition calculation & gram conversion
│   ├── targets.py      # Mifflin-St Jeor target calculation
│   └── units.py        # Household unit to gram conversions
├── routes/
│   ├── __init__.py
│   ├── api.py          # RESTful JSON endpoints with input validation
│   └── pages.py        # Flask template routes
├── static/
│   ├── css/
│   │   └── styles.css  # Strict monochrome CSS design system
│   └── js/
│       └── app.js      # State management, local storage, XSS sanitization
├── templates/
│   ├── base.html       # Base shell with desktop and mobile navigation
│   ├── dashboard.html  # Daily target overview and meal timeline
│   ├── log_food.html   # Focused food search and logging interface
│   ├── meals.html      # 14-day history and daily meal breakdown
│   ├── profile.html    # Personal metrics, BMI, target editor, backups
│   ├── onboarding.html # 7-step initial setup wizard
│   ├── analytics.html  # Intake averages and trend tracking
│   ├── ai_insights.html# Dietary gap analysis
│   └── settings.html   # Preferences and data management
├── .env.example        # Environment variable template
├── .gitignore          # Repository hygiene rules
├── requirements.txt    # Python dependencies
├── test_app.py         # Automated unit, integration & security test suite
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/nutritrack.git
   cd nutritrack-flask
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

5. Run the application:
   ```bash
   python app.py
   ```
   Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Running Tests

Run the automated test suite:
```bash
python test_app.py
```

## License

MIT License.
