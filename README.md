# NutriStar

> Nutrition tracking should be accessible enough to become a daily habit, not expensive enough to become a barrier.

> Built around the foods people actually eat, the portions they actually consume, and the nutrition data they actually need.

NutriStar is a nutrition tracking web application built with Python and Flask. It lets users search for authentic Indian and regional foods, choose practical household serving sizes, track calories and macronutrients, edit logged meals, and review recent history.

## Why NutriStar?

Nutrition tracking can often feel like repetitive administrative work. People usually eat many of the same foods every week. If someone drinks tea or coffee every morning, has chapati and dal for lunch, and eats rice for dinner, logging those foods should be straightforward and quick.

NutriStar focuses on user habits:
- Fast food search with instant debounced filtering
- Quick Add based on recent food frequency and recency
- Serving sizes tailored to each food type (cups, pieces, katori/bowls, glasses, tablespoons, grams)
- A focused 10-day rolling history window instead of an endless archive
- Persistent active date tracking across page transitions

## Built to Be Accessible

The project is designed around the idea that essential nutrition tracking should remain accessible. Core functionality like logging food, editing meals, and tracking daily macros should not require a paid subscription or account creation friction.

## Features

- **Dashboard**: Displays daily calories, remaining caloric budget, and macronutrient targets (Protein, Carbohydrates, and Fat).
- **Food Logging**: Search through 580+ Indian foods, regional recipes, and packaged grocery items with Hindi scripts.
- **Personalized Quick Add**: Shows top foods based on the user's 10-day logging frequency and recency, with staple fallbacks.
- **Food-Specific Serving Units**: Contextual units for each food type (milliliters/cups/glasses for beverages, pieces for rotis/eggs, katori/cups for rice and curries, tablespoons/teaspoons for fats).
- **Dynamic Nutrition Calculation**: Updates calories and macros automatically as portion quantities and serving units change.
- **In-Place Food Editing**: Directly edit logged meals (adjust portions, change meal types, or delete entries) while preserving chronological creation order.
- **10-Day History Calendar**: View daily calorie targets, macro breakdowns, and backfill meals across recent days.
- **Indian and Maharashtra Foods**: Over 580 items with authentic regional recipes, dual-language names, and standardized portion metrics.
- **Profile & Goal Setup**: Set weight goals using weekly target rate (kg/week) or target timeline (total weeks) with automatic Mifflin-St Jeor TDEE calculation.
- **Monochrome Interface**: High-contrast, minimal dark design system with responsive desktop and mobile navigation.
- **Data Portability**: Download a full JSON export of profile biometrics, targets, and meal logs.

## Tech Stack

- **Backend**: Python 3.12, Flask 3.0 (Modular Blueprints, Application Factory)
- **Database & ORM**: SQLite 3, Flask-SQLAlchemy 3.1
- **Frontend & Templating**: Jinja2 HTML Templates, Vanilla CSS3, Vanilla JavaScript (ES6+)
- **Calculations**: Custom Python scaling algorithms and Mifflin-St Jeor TDEE engine
- **Timezone**: `pytz` (Asia/Kolkata IST)
- **Testing**: Python `unittest` test suite

## Project Structure

```text
NutriStar/
├── app.py              # Application entry point, factory & security middleware
├── config.py           # Configuration and environment management
├── database.py         # SQLAlchemy database instance declaration
├── models.py           # Relational models (User, Profile, Food, MealItem)
├── nutrition.py        # Core calculations: units, scaling, TDEE, Quick Add
├── routes.py           # Page routes and RESTful JSON API endpoints
├── seed_data.py        # Database seeding utility for food catalog
├── test_app.py         # Automated test suite (unittest)
├── data/
│   ├── __init__.py     # Data package initializer
│   └── foods.py        # 580+ Indian foods reference dataset
├── static/
│   ├── css/style.css   # Monochrome CSS design system
│   └── js/app.js       # Live search, async API controllers, modal logic
├── templates/
│   ├── base.html       # Base shell with desktop and mobile navigation
│   ├── dashboard.html  # Daily target overview and meal timeline
│   ├── log_food.html   # Focused food search and logging interface
│   ├── history.html    # 10-day rolling history calendar
│   ├── history_day.html# Historical single-day breakdown
│   ├── profile.html    # Personal metrics and target editor
│   ├── onboarding.html # Initial setup wizard
│   └── settings.html   # Preferences and data export
├── .env.example        # Environment variable template
├── .gitignore          # Repository hygiene rules
├── LICENSE             # MIT License
├── NOTICE.md           # Project attribution and copyright notice
└── requirements.txt    # Python dependencies
```

## How It Works

1. **User logs food**: The user selects a meal category (breakfast, lunch, snack, dinner) and searches for an item.
2. **Serving selection**: The user enters a quantity and selects a household unit (katori, piece, cup, glass, ml, grams).
3. **Calculation**: The calculation engine computes estimated calories and macronutrients based on the reference portion grammage.
4. **Storage**: The entry is saved to the SQLite database linked to the user's isolated guest session.
5. **Dashboard update**: Daily totals, progress bars, and remaining calories update immediately.

## Nutrition Data

Nutrition values are estimates based on standard recipes, food composition tables (IFCT-2017 / USDA references), and official manufacturer labels where available.

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

## Security & Architecture

- **Session & Identity Model**: NutriStar operates with an anonymous guest session model (cryptographic session UUID linked to an isolated database profile) allowing instant, zero-friction tracking without requiring public password registration.
- **Secret Key Hardening**: In production mode, `SECRET_KEY` is strictly required from environment variables (`config.py`); server startup halts if unset.
- **Session & Cookie Security**: `SESSION_COOKIE_HTTPONLY = True`, `SESSION_COOKIE_SAMESITE = 'Lax'`, and `SESSION_COOKIE_SECURE = True` under production/HTTPS.
- **CSRF Protection**: Synchronizer token pattern enforced across all state-changing routes (`POST`, `PUT`, `DELETE`) via hidden form tokens and `X-CSRFToken` request headers.
- **Content Security Policy (CSP)**: Explicit policy whitelisting application assets, Google Fonts, and blocking clickjacking via `frame-ancestors 'none'`.
- **HSTS & Security Headers**: Enforces `Strict-Transport-Security` in production HTTPS, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, and `Permissions-Policy: geolocation=(), microphone=(), camera=()`.
- **Trusted Host Validation**: Host header validation via configurable `TRUSTED_HOSTS` in production.
- **User Isolation & IDOR Defense**: Strict user-scoped database queries (`user_id == user.id`) on all read, update, delete, and export operations.
- **Server-Side Input Validation**: Strict whitelisting on meal categories (`breakfast`, `lunch`, `snack`, `dinner`), serving units, portion bounds (0.01 to 1000), biometrics, and 10-day rolling date window restrictions.
- **SQL Injection Defense**: Parameterized SQLAlchemy ORM queries exclusively.
- **XSS Defense**: Jinja2 server-side auto-escaping and client-side DOM escaping (`escapeHtml`).

## Running Locally

### Prerequisites
- Python 3.10 or higher
- pip

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/sarthakargade9166-max/NutriStar.git
   cd NutriStar
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

6. **Run the automated test suite**:
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

## Author

NutriStar is an independent project developed by Sarthak.
