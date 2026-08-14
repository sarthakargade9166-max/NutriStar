"""Page routes — serves HTML templates."""

from flask import Blueprint, render_template

pages = Blueprint('pages', __name__)


@pages.route('/')
def index():
    return render_template('onboarding.html')


@pages.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@pages.route('/onboarding')
def onboarding():
    return render_template('onboarding.html')


@pages.route('/log-food')
def log_food():
    return render_template('log_food.html')


@pages.route('/meals')
def meals():
    return render_template('meals.html')


@pages.route('/analytics')
def analytics():
    return render_template('analytics.html')


@pages.route('/ai-insights')
def ai_insights():
    return render_template('ai_insights.html')


@pages.route('/profile')
def profile():
    return render_template('profile.html')


@pages.route('/settings')
def settings():
    return render_template('settings.html')
