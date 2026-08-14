/**
 * NutriStar - Client Interactive Behavior (Vanilla JavaScript)
 */

let searchTimeout = null;
let currentFoodData = null;
let currentEditFoodData = null;
window.foodCache = {};

// ==========================================
// DATE NAVIGATION & PERSISTENCE
// ==========================================

function initDateControls() {
    const dateInput = document.getElementById('active-date-input');
    const prevBtn = document.getElementById('btn-prev-day');
    const nextBtn = document.getElementById('btn-next-day');
    const todayBtn = document.getElementById('btn-today');

    if (!dateInput) return;

    dateInput.addEventListener('change', (e) => {
        setActiveDate(e.target.value);
    });

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
            const current = new Date(dateInput.value);
            current.setDate(current.getDate() - 1);
            setActiveDate(formatDate(current));
        });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
            const current = new Date(dateInput.value);
            current.setDate(current.getDate() + 1);
            setActiveDate(formatDate(current));
        });
    }

    if (todayBtn) {
        todayBtn.addEventListener('click', () => {
            const today = new Date();
            setActiveDate(formatDate(today));
        });
    }
}

function formatDate(d) {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

async function setActiveDate(dateStr) {
    try {
        const res = await fetch('/api/active-date', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ date: dateStr })
        });
        if (res.ok) {
            window.location.reload();
        }
    } catch (e) {
        console.error('Failed to set active date', e);
    }
}

// ==========================================
// FOOD SEARCH
// ==========================================

function handleFoodSearch(query) {
    const clearBtn = document.getElementById('clear-search-btn');
    if (clearBtn) {
        clearBtn.style.display = query.trim() ? 'block' : 'none';
    }

    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(async () => {
        try {
            const res = await fetch(`/api/foods/search?q=${encodeURIComponent(query.trim())}`);
            const foods = await res.json();
            renderSearchResults(foods);
        } catch (e) {
            console.error('Search error', e);
        }
    }, 150);
}

function clearFoodSearch() {
    const input = document.getElementById('food-search-input');
    if (input) {
        input.value = '';
        input.focus();
        handleFoodSearch('');
    }
}

function renderSearchResults(foods) {
    const container = document.getElementById('food-results-list');
    if (!container) return;

    if (!foods || foods.length === 0) {
        container.innerHTML = `<div class="empty-meal text-secondary" style="text-align: center; padding: 32px 0;">No matching foods found.</div>`;
        return;
    }

    // Cache foods for instant lookup
    foods.forEach(f => { window.foodCache[f.id] = f; });

    container.innerHTML = foods.map(food => {
        const servingCals = Math.round((food.calories_100g * food.grams_per_serving) / 100);
        const servingProt = Math.round((food.protein_100g * food.grams_per_serving) / 100);
        const servingCarb = Math.round((food.carbs_100g * food.grams_per_serving) / 100);
        const servingFat = Math.round((food.fat_100g * food.grams_per_serving) / 100);

        return `
            <div class="food-card" onclick="openPortionModal('${food.id}')">
                <div class="food-info">
                    <div class="food-title-row">
                        <span class="food-name">${escapeHtml(food.name)}</span>
                        ${food.hindi_name ? `<span class="food-hindi">${escapeHtml(food.hindi_name)}</span>` : ''}
                    </div>
                    <span class="food-portion text-secondary">${food.serving_size} ${food.serving_unit} (${Math.round(food.grams_per_serving)}g)</span>
                </div>
                <div class="food-macros">
                    <span class="food-cal">${servingCals} kcal</span>
                    <span class="macro-badge">P ${servingProt}g</span>
                    <span class="macro-badge">C ${servingCarb}g</span>
                    <span class="macro-badge">F ${servingFat}g</span>
                </div>
            </div>
        `;
    }).join('');
}

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

// ==========================================
// PORTION CUSTOMIZER MODAL (LOGGING FOOD)
// ==========================================

async function openPortionModal(foodId) {
    let food = window.foodCache[foodId];

    // Fetch full food details if not already in cache or to get unit options
    try {
        const res = await fetch(`/api/foods/${foodId}`);
        food = await res.json();
        window.foodCache[foodId] = food;
    } catch (e) {
        console.error('Failed to load food details', e);
    }

    if (!food) return;

    currentFoodData = {
        id: food.id,
        name: food.name,
        hindiName: food.hindi_name || '',
        servingSize: food.serving_size || 1.0,
        servingUnit: food.serving_unit || 'serving',
        grams: food.grams_per_serving || 100.0,
        cal100: food.calories_100g || 0.0,
        prot100: food.protein_100g || 0.0,
        carb100: food.carbs_100g || 0.0,
        fat100: food.fat_100g || 0.0
    };

    document.getElementById('selected-food-id').value = food.id;
    document.getElementById('portion-food-name').innerText = food.name;
    document.getElementById('portion-food-hindi').innerText = food.hindi_name || '';
    document.getElementById('portion-quantity').value = food.serving_size || 1;

    const unitSelect = document.getElementById('portion-unit');
    const unitOpts = food.unit_options || [
        { value: food.serving_unit || 'serving', label: `${food.serving_unit || 'Serving'} (${Math.round(food.grams_per_serving || 100)}g)` },
        { value: 'g', label: 'Grams (g)' }
    ];

    unitSelect.innerHTML = unitOpts.map(opt => `
        <option value="${opt.value}" ${opt.value === food.serving_unit ? 'selected' : ''}>${opt.label}</option>
    `).join('');

    recalculatePortionNutrition();
    document.getElementById('portion-modal').style.display = 'flex';
}

function closePortionModal() {
    document.getElementById('portion-modal').style.display = 'none';
}

async function recalculatePortionNutrition() {
    if (!currentFoodData) return;

    const quantity = parseFloat(document.getElementById('portion-quantity').value) || 1;
    const unit = document.getElementById('portion-unit').value || currentFoodData.servingUnit;

    try {
        const res = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                food_id: currentFoodData.id,
                quantity: quantity,
                unit: unit
            })
        });
        const n = await res.json();

        document.getElementById('portion-preview-cals').innerText = `${Math.round(n.calories)} kcal`;
        document.getElementById('portion-preview-protein').innerText = `${Math.round(n.protein)}g`;
        document.getElementById('portion-preview-carbs').innerText = `${Math.round(n.carbs)}g`;
        document.getElementById('portion-preview-fat').innerText = `${Math.round(n.fat)}g`;
    } catch (e) {
        console.error('Failed to recalculate nutrition', e);
    }
}

async function handleLogFoodSubmit(e) {
    e.preventDefault();

    const foodId = document.getElementById('selected-food-id').value;
    const mealType = document.getElementById('selected-meal-type').value || 'lunch';
    const quantity = parseFloat(document.getElementById('portion-quantity').value) || 1;
    const unit = document.getElementById('portion-unit').value || 'serving';

    const btn = document.getElementById('btn-submit-log');
    btn.disabled = true;
    btn.innerText = 'Logging...';

    try {
        const res = await fetch('/api/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                food_id: foodId,
                meal_type: mealType,
                quantity: quantity,
                unit: unit
            })
        });

        if (res.ok) {
            window.location.href = '/dashboard';
        } else {
            alert('Failed to log food. Please try again.');
            btn.disabled = false;
            btn.innerText = 'Log Food';
        }
    } catch (err) {
        alert('Something went wrong.');
        btn.disabled = false;
        btn.innerText = 'Log Food';
    }
}

// ==========================================
// IN-PLACE EDIT MODAL
// ==========================================

async function openEditModal(itemId, foodId, foodName, quantity, unit, mealType) {
    document.getElementById('edit-item-id').value = itemId;
    document.getElementById('edit-food-id').value = foodId;
    document.getElementById('edit-modal-title').innerText = `Edit ${foodName}`;
    document.getElementById('edit-quantity').value = quantity;
    document.getElementById('edit-meal-type').value = mealType;

    currentEditFoodData = { id: foodId, name: foodName };

    try {
        const res = await fetch(`/api/foods/${foodId}`);
        const data = await res.json();
        const unitSelect = document.getElementById('edit-unit');
        unitSelect.innerHTML = (data.unit_options || []).map(opt => `
            <option value="${opt.value}" ${opt.value === unit ? 'selected' : ''}>${opt.label}</option>
        `).join('');
    } catch (e) {
        console.error('Failed to load unit options', e);
    }

    recalculateEditNutrition();
    document.getElementById('edit-modal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('edit-modal').style.display = 'none';
}

async function recalculateEditNutrition() {
    if (!currentEditFoodData) return;

    const quantity = parseFloat(document.getElementById('edit-quantity').value) || 1;
    const unit = document.getElementById('edit-unit').value || 'serving';

    try {
        const res = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                food_id: currentEditFoodData.id,
                quantity: quantity,
                unit: unit
            })
        });
        const n = await res.json();

        document.getElementById('preview-cals').innerText = `${Math.round(n.calories)} kcal`;
        document.getElementById('preview-protein').innerText = `${Math.round(n.protein)}g`;
        document.getElementById('preview-carbs').innerText = `${Math.round(n.carbs)}g`;
        document.getElementById('preview-fat').innerText = `${Math.round(n.fat)}g`;
    } catch (e) {
        console.error('Recalculate edit error', e);
    }
}

async function handleEditSubmit(e) {
    e.preventDefault();

    const itemId = document.getElementById('edit-item-id').value;
    const quantity = parseFloat(document.getElementById('edit-quantity').value) || 1;
    const unit = document.getElementById('edit-unit').value;
    const mealType = document.getElementById('edit-meal-type').value;

    try {
        const res = await fetch(`/api/meal-items/${itemId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                quantity: quantity,
                unit: unit,
                meal_type: mealType
            })
        });

        if (res.ok) {
            window.location.reload();
        } else {
            alert('Failed to update meal item.');
        }
    } catch (err) {
        alert('Network error while updating item.');
    }
}

async function handleDeleteLoggedItem() {
    const itemId = document.getElementById('edit-item-id').value;
    if (!confirm('Are you sure you want to delete this logged item?')) return;

    try {
        const res = await fetch(`/api/meal-items/${itemId}`, {
            method: 'DELETE'
        });

        if (res.ok) {
            window.location.reload();
        } else {
            alert('Failed to delete meal item.');
        }
    } catch (err) {
        alert('Network error while deleting item.');
    }
}
