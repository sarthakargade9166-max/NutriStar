# NutriStar

> Nutrition tracking should be accessible enough to become a daily habit, not expensive enough to become a barrier.

> Built around the foods people actually eat, the portions they actually consume, and the nutrition data they actually need.

NutriStar is a nutrition tracking web application built with Python and Flask. It lets users search for authentic Indian and regional foods, choose practical household serving sizes, track calories and macronutrients, edit logged meals, and review recent history.

## Why NutriStar?

Nutrition tracking can often feel like repetitive administrative work. People usually eat many of the same foods every week. If someone drinks tea or coffee every morning, has chapati and dal for lunch, and eats rice for dinner, logging those foods should be straightforward and quick.

NutriStar focuses on user habits:
- Fast food search with instant filtering
- Quick Add based on recent food frequency
- Serving sizes tailored to each food type (cups, pieces, katori/bowls, ml, grams)
- A focused rolling history window instead of an endless archive

## Built to Be Accessible

Nutrition tracking should be accessible enough to become a daily habit, not expensive enough to become a barrier.

The project is designed around the idea that essential nutrition tracking should remain accessible. Core functionality like logging food, editing meals, and tracking daily macros should not require a paid subscription.

## Features

- **Dashboard**: Displays daily calories, remaining caloric budget, and macronutrient progress rings (Protein, Carbohydrates, and Fat).
- **Food Logging**: Search through 580+ Indian foods, regional recipes, and packaged grocery items with Hindi scripts.
- **Personalized Quick Add**: Shows top foods based on the user's recent logging frequency and recency.
- **Food-Specific Serving Units**: Uses appropriate units for each food type (milliliters for beverages, pieces for rotis/eggs, katori/cups for rice and curries).
- **Dynamic Nutrition Calculation**: Updates calories and macros automatically as portion quantities and serving units change.
- **In-Place Food Editing**: Directly edit logged meals (adjust portions, change meal types, swap foods, or delete entries).
- **History Calendar**: View and backfill meals across recent days with persistent viewing date navigation.
- **Indian and Maharashtra Foods**: Over 580 items with authentic regional recipes, dual-language names, and standardized portion metrics.
- **Profile & Goal Setup**: Set weight goals using weekly target rate (kg/week) or target timeline (total weeks) with automatic Mifflin-St Jeor TDEE calculation.
- **Monochrome Interface**: High-contrast, minimal design system with responsive desktop and mobile navigation.

## Tech Stack

- **Backend**: Python 3.12, Flask (Modular Blueprints)
- **Frontend & Templating**: Jinja2 HTML Templates, Vanilla CSS, Vanilla JavaScript
- **Calculations**: Custom Python nutrition and unit-conversion engines
- **Storage**: Client-side storage with zero tracking and full JSON export/import capability
- **Testing**: Python `unittest` test suite

## Project Structure

```
nutritrack-flask/
├── app.py              # Application entry point & security middleware
├── config.py           # Configuration and environment management
├── models.py           # Category, activity, and goal data types
├── data/
│   └── foods.py        # 580+ Indian foods dataset and search engine
├── nutrition/
│   ├── calculator.py   # Nutrition calculation & gram conversion
│   ├── targets.py      # Mifflin-St Jeor target calculation
│   └── units.py        # Household unit to gram conversions
├── routes/
│   ├── api.py          # RESTful JSON endpoints with input validation
│   └── pages.py        # Flask template routes
├── static/
│   ├── css/styles.css  # Monochrome CSS design system
│   └── js/app.js       # State management, local storage, XSS sanitization
├── templates/
│   ├── base.html       # Base shell with desktop and mobile navigation
│   ├── dashboard.html  # Daily target overview and meal timeline
│   ├── log_food.html   # Focused food search and logging interface
│   ├── meals.html      # History timeline and daily meal breakdown
│   ├── profile.html    # Personal metrics, target editor, data backups
│   ├── onboarding.html # Initial setup wizard
│   └── settings.html   # Preferences and data management
├── .env.example        # Environment variable template
├── .gitignore          # Repository hygiene rules
├── requirements.txt    # Python dependencies
├── test_app.py         # Automated unit, integration & security test suite
└── README.md
```

## How It Works

1. **User logs food**: The user selects a meal category (breakfast, lunch, snack, dinner) and searches for an item.
2. **Serving selection**: The user enters a quantity and selects a household unit (katori, piece, cup, ml, grams).
3. **Calculation**: The server/client engine computes exact calories and macronutrients based on the reference portion grammage.
4. **Storage**: The entry is saved to local storage for instant offline access.
5. **Dashboard update**: Daily totals, macronutrient rings, and remaining calories update immediately.

## Nutrition Data

Nutrition values are estimates based on standard recipes, food composition tables (IFCT/USDA references), and official manufacturer labels where available.

Nutrition can vary depending on:
- Cooking methods and oils used
- Specific homemade recipes
- Restaurant preparation methods
- Commercial brand reformulations

For packaged foods, official Indian product labels are used where available. NutriStar is an informational tracking tool and does not provide medical advice.

## AI-Assisted Development

Approximately 20% of the development process involved Agentic AI assistance for code suggestions, debugging, repetitive development tasks, and exploring solutions.

The architecture, feature decisions, integration, testing, and final review were handled by the developer.

AI was used as a development tool to assist with implementation efficiency, while all code, routes, and logic were verified and tested by the developer.

## Security

- **Security Headers**: `app.py` enforces HTTP security headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`, Content Security Policy).
- **Input Boundaries**: Strict physiological boundaries prevent invalid negative numbers or extreme values from corrupting daily totals.
- **Zero Logging of Sensitive Data**: No personal metrics or private information are logged to server outputs.
- **Environment Isolation**: Secret keys are loaded via environment variables in `config.py` and excluded from Git.

## Running Locally

### Prerequisites
- Python 3.10 or higher
- pip

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sarthakargade9166-max/nutritrack-flask.git
   cd nutritrack-flask
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

5. **Start the application**:
   ```bash
   python app.py
   ```
   Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

6. **Run the test suite**:
   ```bash
   python test_app.py
   ```

## Limitations

- Prepared dish macros are estimates based on standard recipes; individual preparations will vary.
- The food database covers 580+ common Indian foods and staples, but is not exhaustive.
- NutriStar is not a clinical tool and should not be used as medical advice.

## Future Work

- Barcode lookup integration for packaged goods
- Expanded regional food databases across additional cuisines
- Meal planning and recipe builder features
