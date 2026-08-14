import json
import os

foods_data = [
    # CEREALS (~12)
    ("wheat-flour", "Wheat Flour (Atta)", ["atta", "whole wheat flour"], "cereals", "pan-india", 1, "cup", 120, 340, 12, 72, 1.7, 10.7, "", "IFCT-2017", "high"),
    ("rice-raw", "Raw Rice", ["chawal", "white rice raw"], "cereals", "pan-india", 1, "cup", 200, 350, 6.8, 78, 0.5, 1.0, "", "IFCT-2017", "high"),
    ("rice-cooked", "Cooked White Rice", ["chawal cooked", "steamed rice"], "cereals", "pan-india", 1, "bowl", 150, 130, 2.7, 28, 0.3, 0.4, "boiled", "IFCT-2017", "high"),
    ("brown-rice-cooked", "Cooked Brown Rice", ["brown chawal"], "cereals", "pan-india", 1, "bowl", 150, 110, 2.6, 23, 0.9, 1.8, "boiled", "USDA", "high"),
    ("rava", "Rava (Sooji)", ["semolina", "suji"], "cereals", "pan-india", 1, "cup", 160, 360, 10.4, 73, 1.0, 3.9, "", "IFCT-2017", "high"),
    ("poha-flakes", "Poha (Rice Flakes)", ["beaten rice", "chivda raw"], "cereals", "pan-india", 1, "cup", 50, 346, 6.6, 77, 1.2, 0.7, "", "IFCT-2017", "high"),
    ("oats", "Oats (Rolled)", ["jai"], "cereals", "pan-india", 1, "cup", 80, 389, 16.9, 66.3, 6.9, 10.6, "", "USDA", "high"),
    ("bajra", "Bajra (Pearl Millet)", ["kambu", "sajje"], "cereals", "pan-india", 1, "cup", 130, 361, 11.6, 65, 5, 11, "", "IFCT-2017", "high"),
    ("jowar", "Jowar (Sorghum)", ["cholam", "jola"], "cereals", "pan-india", 1, "cup", 130, 349, 10.4, 72.6, 1.9, 9.7, "", "IFCT-2017", "high"),
    ("ragi", "Ragi (Finger Millet)", ["nachni", "kezhvaragu"], "cereals", "south", 1, "cup", 130, 336, 7.3, 72, 1.3, 11.2, "", "IFCT-2017", "high"),
    ("maida", "Maida (Refined Wheat Flour)", ["all purpose flour"], "cereals", "pan-india", 1, "cup", 125, 364, 10.3, 76.3, 0.9, 2.7, "", "IFCT-2017", "high"),
    ("besan", "Besan (Gram Flour)", ["chickpea flour"], "cereals", "pan-india", 1, "cup", 92, 387, 22.4, 57.8, 6.7, 10.8, "", "IFCT-2017", "high"),

    # BREADS (~12)
    ("chapati", "Chapati (Roti)", ["roti", "phulka"], "breads", "north", 1, "piece", 40, 297, 9.5, 55, 3.5, 9.7, "roasted", "IFCT-2017", "high"),
    ("paratha-plain", "Plain Paratha", ["parotta", "pan fried flatbread"], "breads", "north", 1, "piece", 60, 330, 8, 48, 12, 7, "pan-fried", "IFCT-2017", "medium"),
    ("aloo-paratha", "Aloo Paratha", ["potato stuffed paratha"], "breads", "north", 1, "piece", 150, 260, 5, 35, 11, 4, "pan-fried", "IFCT-2017", "high"),
    ("puri", "Puri", ["poori"], "breads", "pan-india", 1, "piece", 30, 420, 7, 45, 25, 5, "deep-fried", "IFCT-2017", "medium"),
    ("naan", "Naan", ["tandoori naan"], "breads", "north", 1, "piece", 90, 310, 9, 52, 6, 3, "tandoor", "IFCT-2017", "medium"),
    ("bhakri", "Bhakri", ["jowar roti", "bajra roti"], "breads", "west", 1, "piece", 50, 280, 8, 55, 3, 9, "roasted", "IFCT-2017", "medium"),
    ("thepla", "Methi Thepla", ["thepla"], "breads", "west", 1, "piece", 40, 320, 9, 45, 12, 7, "pan-fried", "IFCT-2017", "medium"),
    ("kulcha", "Kulcha", ["amritsari kulcha"], "breads", "north", 1, "piece", 80, 280, 8, 48, 5, 3, "tandoor", "IFCT-2017", "medium"),
    ("missi-roti", "Missi Roti", ["besan roti"], "breads", "north", 1, "piece", 50, 320, 12, 50, 6, 9, "roasted", "IFCT-2017", "medium"),
    ("makki-roti", "Makki Roti", ["cornmeal flatbread"], "breads", "north", 1, "piece", 60, 300, 7, 58, 4, 8, "roasted", "IFCT-2017", "medium"),
    ("bread-white", "White Bread", ["sliced bread"], "breads", "pan-india", 1, "slice", 25, 265, 8.8, 49, 3.2, 2.7, "baked", "USDA", "high"),
    ("rumali-roti", "Rumali Roti", ["handkerchief bread"], "breads", "north", 1, "piece", 60, 290, 9, 52, 4, 3, "roasted", "IFCT-2017", "medium"),

    # RICE DISHES (~8)
    ("jeera-rice", "Jeera Rice", ["cumin rice"], "rice", "north", 1, "bowl", 150, 160, 3, 30, 3, 0.5, "boiled", "IFCT-2017", "high"),
    ("veg-biryani", "Vegetable Biryani", ["veg pulao", "biriyani"], "rice", "pan-india", 1, "bowl", 250, 180, 4, 25, 6, 2, "steamed", "IFCT-2017", "medium"),
    ("chicken-biryani", "Chicken Biryani", ["murgh biryani"], "rice", "pan-india", 1, "bowl", 300, 220, 12, 25, 8, 1.5, "steamed", "IFCT-2017", "high"),
    ("veg-pulao", "Veg Pulao", ["pilaf"], "rice", "pan-india", 1, "bowl", 200, 170, 4, 28, 5, 2, "steamed", "IFCT-2017", "medium"),
    ("khichdi", "Khichdi (Moong Dal)", ["dal rice"], "rice", "pan-india", 1, "bowl", 250, 150, 5, 25, 3, 3, "boiled", "IFCT-2017", "high"),
    ("lemon-rice", "Lemon Rice", ["chitranna"], "rice", "south", 1, "bowl", 150, 190, 3, 30, 6, 1, "tempered", "IFCT-2017", "medium"),
    ("curd-rice", "Curd Rice", ["thayir sadam"], "rice", "south", 1, "bowl", 200, 140, 4, 18, 4, 0.5, "mixed", "IFCT-2017", "medium"),
    ("tamarind-rice", "Tamarind Rice", ["puliyogare"], "rice", "south", 1, "bowl", 150, 210, 3, 32, 7, 2, "tempered", "IFCT-2017", "medium"),

    # DALS (~15)
    ("toor-dal", "Toor Dal (Raw)", ["arhar dal", "pigeon pea"], "dals", "pan-india", 1, "cup", 200, 343, 21.7, 62.8, 1.5, 15, "", "IFCT-2017", "high"),
    ("moong-dal", "Moong Dal (Raw)", ["yellow dal", "green gram split"], "dals", "pan-india", 1, "cup", 200, 348, 24.5, 59.9, 1.2, 8, "", "IFCT-2017", "high"),
    ("chana-dal", "Chana Dal (Raw)", ["bengal gram split"], "dals", "pan-india", 1, "cup", 200, 372, 20.8, 59.8, 5.6, 11, "", "IFCT-2017", "high"),
    ("masoor-dal", "Masoor Dal (Raw)", ["red lentil"], "dals", "pan-india", 1, "cup", 200, 346, 24.2, 59, 1.3, 11, "", "IFCT-2017", "high"),
    ("urad-dal", "Urad Dal (Raw)", ["black gram split"], "dals", "pan-india", 1, "cup", 200, 347, 24, 59.6, 1.4, 11.7, "", "IFCT-2017", "high"),
    ("rajma", "Rajma (Raw Kidney Beans)", ["kidney beans"], "dals", "north", 1, "cup", 200, 333, 23.6, 60, 0.8, 15.2, "", "USDA", "high"),
    ("chole", "Chole (Raw Chickpeas)", ["kabuli chana", "garbanzo beans"], "dals", "north", 1, "cup", 200, 364, 19.3, 60.6, 6, 17.4, "", "USDA", "high"),
    ("lobia", "Lobia (Raw Black Eyed Peas)", ["cowpea", "chawli"], "dals", "pan-india", 1, "cup", 200, 336, 23.5, 60, 1.2, 10.6, "", "USDA", "high"),
    ("moong-sprouts", "Moong Sprouts (Raw)", ["sprouted moong"], "dals", "pan-india", 1, "cup", 104, 30, 3, 5.9, 0.2, 1.8, "", "USDA", "high"),
    ("soybean", "Soybean (Raw)", ["soya beans"], "dals", "pan-india", 1, "cup", 186, 446, 36.5, 30.2, 19.9, 9.3, "", "USDA", "high"),
    ("soy-chunks", "Soy Chunks", ["soya wadi", "nutrela"], "dals", "pan-india", 1, "cup", 50, 345, 52, 33, 0.5, 13, "", "IFCT-2017", "medium"),
    ("dal-fry", "Dal Fry (Cooked)", ["yellow dal tadka"], "dals", "pan-india", 1, "bowl", 150, 120, 6, 15, 4, 3, "boiled", "IFCT-2017", "medium"),
    ("sambar", "Sambar", ["sambhar"], "dals", "south", 1, "bowl", 150, 90, 4, 12, 3, 3, "boiled", "IFCT-2017", "medium"),
    ("rasam", "Rasam", ["south indian soup"], "dals", "south", 1, "bowl", 150, 40, 1, 6, 1, 1, "boiled", "IFCT-2017", "medium"),
    ("dal-makhani", "Dal Makhani", ["black dal creamy"], "dals", "north", 1, "bowl", 150, 180, 7, 16, 10, 5, "boiled", "IFCT-2017", "medium"),

    # VEGETABLES (~20)
    ("potato", "Potato (Raw)", ["aloo"], "vegetables", "pan-india", 1, "piece", 150, 77, 2, 17, 0.1, 2.2, "", "USDA", "high"),
    ("onion", "Onion (Raw)", ["pyaaz"], "vegetables", "pan-india", 1, "piece", 100, 40, 1.1, 9.3, 0.1, 1.7, "", "USDA", "high"),
    ("tomato", "Tomato (Raw)", ["tamatar"], "vegetables", "pan-india", 1, "piece", 100, 18, 0.9, 3.9, 0.2, 1.2, "", "USDA", "high"),
    ("palak", "Palak (Raw Spinach)", ["spinach"], "vegetables", "pan-india", 1, "cup", 30, 23, 2.9, 3.6, 0.4, 2.2, "", "USDA", "high"),
    ("bhindi", "Bhindi (Raw Okra)", ["lady finger", "okra"], "vegetables", "pan-india", 1, "cup", 100, 33, 1.9, 7.5, 0.2, 3.2, "", "USDA", "high"),
    ("gobi", "Gobi (Raw Cauliflower)", ["cauliflower"], "vegetables", "pan-india", 1, "cup", 100, 25, 1.9, 5, 0.3, 2, "", "USDA", "high"),
    ("baingan", "Baingan (Raw Eggplant)", ["brinjal", "eggplant"], "vegetables", "pan-india", 1, "piece", 200, 25, 1, 6, 0.2, 3, "", "USDA", "high"),
    ("lauki", "Lauki (Raw Bottle Gourd)", ["dudhi", "bottle gourd"], "vegetables", "pan-india", 1, "cup", 100, 14, 0.6, 3.4, 0.1, 1.2, "", "USDA", "high"),
    ("tori", "Tori (Raw Ridge Gourd)", ["ridge gourd", "turai"], "vegetables", "pan-india", 1, "cup", 100, 17, 0.8, 3.8, 0.2, 1.5, "", "IFCT-2017", "high"),
    ("karela", "Karela (Raw Bitter Gourd)", ["bitter gourd", "pavakkai"], "vegetables", "pan-india", 1, "piece", 100, 17, 1, 3.7, 0.2, 2.8, "", "USDA", "high"),
    ("matar", "Matar (Raw Green Peas)", ["green peas"], "vegetables", "pan-india", 1, "cup", 145, 81, 5.4, 14.5, 0.4, 5.7, "", "USDA", "high"),
    ("french-beans", "French Beans (Raw)", ["green beans", "farasbi"], "vegetables", "pan-india", 1, "cup", 100, 31, 1.8, 7, 0.2, 2.7, "", "USDA", "high"),
    ("cabbage", "Cabbage (Raw)", ["patta gobi"], "vegetables", "pan-india", 1, "cup", 89, 25, 1.3, 5.8, 0.1, 2.5, "", "USDA", "high"),
    ("capsicum", "Capsicum (Raw Bell Pepper)", ["shimla mirch", "bell pepper"], "vegetables", "pan-india", 1, "piece", 119, 20, 0.9, 4.6, 0.2, 1.7, "", "USDA", "high"),
    ("carrot", "Carrot (Raw)", ["gajar"], "vegetables", "pan-india", 1, "piece", 61, 41, 0.9, 9.6, 0.2, 2.8, "", "USDA", "high"),
    ("beetroot", "Beetroot (Raw)", ["chukandar"], "vegetables", "pan-india", 1, "piece", 82, 43, 1.6, 9.6, 0.2, 2.8, "", "USDA", "high"),
    ("mushroom", "Mushroom (Raw Button)", ["khumbi"], "vegetables", "pan-india", 1, "cup", 70, 22, 3.1, 3.3, 0.3, 1, "", "USDA", "high"),
    ("corn", "Sweet Corn (Raw)", ["bhutta", "makai"], "vegetables", "pan-india", 1, "cup", 145, 86, 3.2, 18.7, 1.2, 2, "", "USDA", "high"),
    ("cucumber", "Cucumber (Raw)", ["kheera", "kakdi"], "vegetables", "pan-india", 1, "piece", 200, 15, 0.7, 3.6, 0.1, 0.5, "", "USDA", "high"),
    ("radish", "Radish (Raw)", ["mooli"], "vegetables", "pan-india", 1, "piece", 150, 16, 0.7, 3.4, 0.1, 1.6, "", "USDA", "high"),

    # DAIRY (~11)
    ("paneer", "Paneer (Full Fat)", ["cottage cheese"], "dairy", "pan-india", 1, "cup", 100, 296, 18, 3, 24, 0, "", "IFCT-2017", "high"),
    ("paneer-low-fat", "Paneer (Low Fat)", ["skim milk paneer"], "dairy", "pan-india", 1, "cup", 100, 120, 15, 4, 5, 0, "", "IFCT-2017", "medium"),
    ("curd", "Curd (Dahi)", ["yogurt"], "dairy", "pan-india", 1, "bowl", 150, 98, 3.4, 4.7, 3.3, 0, "", "USDA", "high"),
    ("milk-full-cream", "Milk (Full Cream)", ["buffalo milk", "whole milk"], "dairy", "pan-india", 1, "glass", 250, 61, 3.2, 4.8, 3.3, 0, "", "USDA", "high"),
    ("milk-toned", "Milk (Toned)", ["cow milk", "skim milk"], "dairy", "pan-india", 1, "glass", 250, 42, 3.4, 5, 1, 0, "", "USDA", "high"),
    ("buttermilk", "Buttermilk (Chaas)", ["mattha", "neer mor"], "dairy", "pan-india", 1, "glass", 250, 40, 3.3, 4.8, 0.9, 0, "", "USDA", "high"),
    ("ghee", "Ghee (Clarified Butter)", ["desi ghee"], "dairy", "pan-india", 1, "tablespoon", 15, 900, 0, 0, 100, 0, "", "USDA", "high"),
    ("butter", "Butter", ["makhan"], "dairy", "pan-india", 1, "tablespoon", 14, 717, 0.9, 0.1, 81, 0, "", "USDA", "high"),
    ("cheese", "Cheese (Processed)", ["cheese slice", "amul cheese"], "dairy", "pan-india", 1, "piece", 20, 350, 20, 2, 30, 0, "", "IFCT-2017", "high"),
    ("cream", "Fresh Cream", ["malai"], "dairy", "pan-india", 1, "tablespoon", 15, 340, 2.5, 3.5, 35, 0, "", "USDA", "high"),
    ("lassi-sweet", "Sweet Lassi", ["meethi lassi"], "dairy", "north", 1, "glass", 250, 80, 2, 12, 2.5, 0, "", "IFCT-2017", "medium"),

    # EGGS & MEAT (~8)
    ("boiled-egg", "Boiled Egg", ["anda"], "eggs_meat", "pan-india", 1, "piece", 50, 155, 12.6, 1.1, 10.6, 0, "boiled", "USDA", "high"),
    ("omelette", "Omelette (2 eggs)", ["masala omelette"], "eggs_meat", "pan-india", 1, "serving", 120, 180, 11, 2, 14, 0, "pan-fried", "USDA", "high"),
    ("scrambled-egg", "Scrambled Egg (Bhurji)", ["anda bhurji"], "eggs_meat", "pan-india", 1, "serving", 120, 190, 12, 3, 15, 0, "pan-fried", "IFCT-2017", "medium"),
    ("chicken-breast", "Chicken Breast (Raw)", ["boneless chicken"], "eggs_meat", "pan-india", 1, "piece", 150, 120, 22.5, 0, 2.6, 0, "", "USDA", "high"),
    ("chicken-curry", "Chicken Curry", ["murgh gravy"], "eggs_meat", "pan-india", 1, "bowl", 200, 160, 14, 6, 9, 1, "boiled", "IFCT-2017", "medium"),
    ("mutton-curry", "Mutton Curry", ["lamb curry", "meat curry"], "eggs_meat", "pan-india", 1, "bowl", 200, 210, 16, 5, 14, 1, "boiled", "IFCT-2017", "medium"),
    ("fish-curry", "Fish Curry", ["machli curry", "meen kuzhambu"], "eggs_meat", "pan-india", 1, "bowl", 200, 140, 12, 4, 8, 1, "boiled", "IFCT-2017", "medium"),
    ("tandoori-chicken", "Tandoori Chicken", ["roasted chicken"], "eggs_meat", "north", 1, "piece", 150, 180, 22, 3, 9, 0.5, "tandoor", "IFCT-2017", "medium"),

    # FRIED SNACKS (~8)
    ("samosa", "Samosa", ["aloo samosa"], "snacks_fried", "pan-india", 1, "piece", 60, 308, 4, 32, 18, 3, "deep-fried", "IFCT-2017", "high"),
    ("kachori", "Kachori", ["khasta kachori"], "snacks_fried", "north", 1, "piece", 50, 410, 8, 45, 23, 4, "deep-fried", "IFCT-2017", "medium"),
    ("pakora", "Pakora (Veg/Onion)", ["bhajiya", "fritters"], "snacks_fried", "pan-india", 1, "serving", 50, 280, 6, 25, 18, 3, "deep-fried", "IFCT-2017", "medium"),
    ("aloo-tikki", "Aloo Tikki", ["potato patty"], "snacks_fried", "north", 1, "piece", 50, 220, 3, 28, 11, 3, "pan-fried", "IFCT-2017", "medium"),
    ("medu-vada", "Medu Vada", ["uzhunnu vada"], "snacks_fried", "south", 1, "piece", 40, 330, 9, 35, 18, 4, "deep-fried", "IFCT-2017", "medium"),
    ("batata-vada", "Batata Vada", ["aloo bonda"], "snacks_fried", "west", 1, "piece", 50, 250, 4, 25, 15, 3, "deep-fried", "IFCT-2017", "medium"),
    ("bhel-puri", "Bhel Puri", ["bhelpuri"], "snacks_fried", "west", 1, "plate", 100, 170, 4, 30, 4, 3, "mixed", "IFCT-2017", "medium"),
    ("sev-puri", "Sev Puri", ["chaat"], "snacks_fried", "west", 1, "plate", 100, 220, 5, 28, 10, 4, "mixed", "IFCT-2017", "medium"),

    # HEALTHY SNACKS (~8)
    ("dhokla", "Khaman Dhokla", ["besan dhokla"], "snacks_healthy", "west", 1, "piece", 50, 150, 5, 20, 5, 2, "steamed", "IFCT-2017", "medium"),
    ("makhana", "Roasted Makhana", ["fox nuts"], "snacks_healthy", "pan-india", 1, "cup", 30, 350, 10, 77, 0.1, 15, "roasted", "IFCT-2017", "high"),
    ("roasted-chana", "Roasted Chana", ["bhuna chana"], "snacks_healthy", "pan-india", 1, "cup", 30, 370, 20, 60, 5, 16, "roasted", "IFCT-2017", "high"),
    ("murmura", "Murmura (Puffed Rice)", ["kurmura", "mamra"], "snacks_healthy", "pan-india", 1, "cup", 20, 400, 7, 90, 0.5, 2, "roasted", "IFCT-2017", "high"),
    ("dry-fruits-mix", "Dry Fruits & Nuts Mix", ["trail mix"], "snacks_healthy", "pan-india", 1, "cup", 30, 500, 15, 35, 40, 8, "", "USDA", "medium"),
    ("almonds", "Almonds", ["badam"], "snacks_healthy", "pan-india", 1, "cup", 30, 579, 21.2, 21.6, 49.9, 12.5, "", "USDA", "high"),
    ("peanuts", "Peanuts (Roasted)", ["moongfali", "singdana"], "snacks_healthy", "pan-india", 1, "cup", 30, 567, 25.8, 16.1, 49.2, 8.5, "roasted", "USDA", "high"),
    ("popcorn", "Popcorn (Air Popped)", ["makkai"], "snacks_healthy", "pan-india", 1, "cup", 20, 387, 13, 78, 4.5, 14.5, "roasted", "USDA", "high"),

    # SOUTH INDIAN (~8)
    ("idli", "Idli", ["steamed rice cake"], "south_indian", "south", 1, "piece", 50, 140, 4, 30, 0.5, 2, "steamed", "IFCT-2017", "high"),
    ("dosa-plain", "Plain Dosa", ["dosai"], "south_indian", "south", 1, "piece", 80, 220, 5, 35, 6, 2, "pan-fried", "IFCT-2017", "medium"),
    ("masala-dosa", "Masala Dosa", ["potato stuffed dosa"], "south_indian", "south", 1, "piece", 150, 260, 6, 40, 9, 4, "pan-fried", "IFCT-2017", "medium"),
    ("upma", "Upma", ["sooji upma", "uppittu"], "south_indian", "south", 1, "bowl", 150, 170, 4, 25, 6, 2, "boiled", "IFCT-2017", "medium"),
    ("uttapam", "Uttapam", ["oothappam"], "south_indian", "south", 1, "piece", 100, 200, 5, 32, 6, 3, "pan-fried", "IFCT-2017", "medium"),
    ("pongal", "Ven Pongal", ["khara pongal"], "south_indian", "south", 1, "bowl", 150, 210, 6, 28, 8, 3, "boiled", "IFCT-2017", "medium"),
    ("rava-dosa", "Rava Dosa", ["crispy semolina dosa"], "south_indian", "south", 1, "piece", 100, 250, 6, 38, 8, 2, "pan-fried", "IFCT-2017", "medium"),
    ("poha", "Kanda Poha", ["onion poha"], "south_indian", "west", 1, "bowl", 150, 180, 4, 30, 5, 2, "steamed", "IFCT-2017", "medium"),

    # SWEETS (~10)
    ("gulab-jamun", "Gulab Jamun", ["jamun"], "sweets", "pan-india", 1, "piece", 40, 300, 5, 45, 12, 0.5, "deep-fried", "IFCT-2017", "high"),
    ("jalebi", "Jalebi", ["imarti"], "sweets", "pan-india", 1, "piece", 30, 330, 3, 60, 9, 0.5, "deep-fried", "IFCT-2017", "high"),
    ("rasgulla", "Rasgulla", ["roshogolla"], "sweets", "east", 1, "piece", 50, 180, 6, 35, 1, 0, "boiled", "IFCT-2017", "high"),
    ("besan-ladoo", "Besan Ladoo", ["laddu"], "sweets", "pan-india", 1, "piece", 40, 450, 10, 55, 22, 4, "", "IFCT-2017", "high"),
    ("motichoor-ladoo", "Motichoor Ladoo", ["boondi laddu"], "sweets", "pan-india", 1, "piece", 40, 400, 5, 60, 16, 2, "deep-fried", "IFCT-2017", "high"),
    ("modak", "Modak (Ukadiche)", ["steamed modak"], "sweets", "west", 1, "piece", 40, 220, 2, 40, 6, 2, "steamed", "IFCT-2017", "medium"),
    ("sooji-halwa", "Sooji Halwa", ["sheera", "kesari bath"], "sweets", "pan-india", 1, "bowl", 100, 320, 4, 45, 14, 1, "boiled", "IFCT-2017", "medium"),
    ("kaju-barfi", "Kaju Katli", ["kaju barfi"], "sweets", "pan-india", 1, "piece", 20, 450, 12, 50, 23, 2, "", "IFCT-2017", "high"),
    ("kheer", "Rice Kheer", ["payasam"], "sweets", "pan-india", 1, "bowl", 150, 140, 4, 22, 4, 0.5, "boiled", "IFCT-2017", "medium"),
    ("gajar-halwa", "Gajar Halwa", ["carrot pudding"], "sweets", "north", 1, "bowl", 150, 220, 4, 30, 10, 3, "boiled", "IFCT-2017", "medium"),

    # BEVERAGES (~8)
    ("chai", "Masala Chai (With Milk & Sugar)", ["tea"], "beverages", "pan-india", 1, "cup", 150, 60, 2, 10, 2, 0, "boiled", "IFCT-2017", "high"),
    ("black-coffee", "Black Coffee", ["espresso"], "beverages", "pan-india", 1, "cup", 150, 2, 0.2, 0, 0, 0, "boiled", "USDA", "high"),
    ("filter-coffee", "Filter Coffee (With Milk & Sugar)", ["south indian coffee"], "beverages", "south", 1, "cup", 150, 70, 2, 12, 2, 0, "boiled", "IFCT-2017", "high"),
    ("lime-water", "Nimbu Pani (Sweetened)", ["lemonade", "shikanji"], "beverages", "pan-india", 1, "glass", 250, 40, 0, 10, 0, 0, "", "IFCT-2017", "medium"),
    ("coconut-water", "Coconut Water", ["nariyal pani"], "beverages", "pan-india", 1, "glass", 250, 19, 0.7, 3.7, 0.2, 1.1, "", "USDA", "high"),
    ("mango-lassi", "Mango Lassi", ["aam lassi"], "beverages", "north", 1, "glass", 250, 90, 3, 16, 2, 1, "", "IFCT-2017", "medium"),
    ("banana-shake", "Banana Milkshake", ["kele ka shake"], "beverages", "pan-india", 1, "glass", 250, 85, 3, 15, 1.5, 1.5, "", "IFCT-2017", "medium"),
    ("green-tea", "Green Tea (No Sugar)", ["herbal tea"], "beverages", "pan-india", 1, "cup", 150, 1, 0, 0, 0, 0, "boiled", "USDA", "high"),

    # FRUITS (~12)
    ("banana", "Banana", ["kela"], "fruits", "pan-india", 1, "piece", 120, 89, 1.1, 22.8, 0.3, 2.6, "", "USDA", "high"),
    ("apple", "Apple", ["seb"], "fruits", "pan-india", 1, "piece", 150, 52, 0.3, 13.8, 0.2, 2.4, "", "USDA", "high"),
    ("mango", "Mango", ["aam"], "fruits", "pan-india", 1, "piece", 200, 60, 0.8, 15, 0.4, 1.6, "", "USDA", "high"),
    ("papaya", "Papaya", ["papita"], "fruits", "pan-india", 1, "bowl", 150, 43, 0.5, 10.8, 0.1, 1.7, "", "USDA", "high"),
    ("guava", "Guava", ["amrood"], "fruits", "pan-india", 1, "piece", 150, 68, 2.6, 14.3, 0.9, 5.4, "", "USDA", "high"),
    ("watermelon", "Watermelon", ["tarbooz"], "fruits", "pan-india", 1, "bowl", 200, 30, 0.6, 7.6, 0.2, 0.4, "", "USDA", "high"),
    ("orange", "Orange", ["santra"], "fruits", "pan-india", 1, "piece", 130, 47, 0.9, 11.8, 0.1, 2.4, "", "USDA", "high"),
    ("grapes", "Grapes", ["angoor"], "fruits", "pan-india", 1, "bowl", 100, 69, 0.7, 18.1, 0.2, 0.9, "", "USDA", "high"),
    ("chikoo", "Chikoo (Sapodilla)", ["sapota"], "fruits", "pan-india", 1, "piece", 100, 83, 0.4, 20, 1.1, 5.3, "", "USDA", "high"),
    ("pomegranate", "Pomegranate", ["anaar"], "fruits", "pan-india", 1, "bowl", 100, 83, 1.7, 18.7, 1.2, 4, "", "USDA", "high"),
    ("pineapple", "Pineapple", ["ananas"], "fruits", "pan-india", 1, "bowl", 100, 50, 0.5, 13.1, 0.1, 1.4, "", "USDA", "high"),
    ("strawberry", "Strawberry", ["berries"], "fruits", "pan-india", 1, "bowl", 100, 32, 0.7, 7.7, 0.3, 2, "", "USDA", "high"),

    # PREPARED (~15)
    ("paneer-butter-masala", "Paneer Butter Masala", ["paneer makhani"], "prepared", "north", 1, "bowl", 200, 210, 7, 10, 16, 2, "boiled", "IFCT-2017", "medium"),
    ("palak-paneer", "Palak Paneer", ["spinach paneer"], "prepared", "north", 1, "bowl", 200, 160, 8, 8, 12, 3, "boiled", "IFCT-2017", "medium"),
    ("aloo-gobi", "Aloo Gobi", ["potato cauliflower curry"], "prepared", "north", 1, "bowl", 150, 110, 3, 15, 5, 4, "pan-fried", "IFCT-2017", "medium"),
    ("chana-masala", "Chana Masala", ["chole bhature sabzi"], "prepared", "north", 1, "bowl", 150, 140, 6, 18, 5, 6, "boiled", "IFCT-2017", "medium"),
    ("mixed-veg", "Mixed Vegetable Curry", ["veg kadhai"], "prepared", "pan-india", 1, "bowl", 150, 100, 3, 12, 5, 4, "pan-fried", "IFCT-2017", "medium"),
    ("baingan-bharta", "Baingan Bharta", ["mashed eggplant"], "prepared", "north", 1, "bowl", 150, 90, 2, 10, 5, 4, "roasted", "IFCT-2017", "medium"),
    ("aloo-matar", "Aloo Matar", ["potato peas curry"], "prepared", "north", 1, "bowl", 150, 120, 3, 18, 4, 3, "boiled", "IFCT-2017", "medium"),
    ("egg-curry", "Egg Curry", ["anda masala"], "prepared", "pan-india", 1, "bowl", 200, 140, 9, 8, 9, 2, "boiled", "IFCT-2017", "medium"),
    ("butter-chicken", "Butter Chicken", ["murgh makhani"], "prepared", "north", 1, "bowl", 200, 220, 12, 8, 16, 1, "boiled", "IFCT-2017", "medium"),
    ("paneer-bhurji", "Paneer Bhurji", ["scrambled paneer"], "prepared", "north", 1, "bowl", 150, 190, 12, 6, 14, 1, "pan-fried", "IFCT-2017", "medium"),
    ("kadhi-pakora", "Kadhi Pakora", ["yogurt curry with fritters"], "prepared", "north", 1, "bowl", 200, 130, 4, 12, 8, 2, "boiled", "IFCT-2017", "medium"),
    ("pav-bhaji", "Pav Bhaji (Bhaji only)", ["mashed veg gravy"], "prepared", "west", 1, "bowl", 150, 140, 3, 18, 7, 5, "boiled", "IFCT-2017", "medium"),
    ("misal-pav", "Misal (Sprouts Curry)", ["usal"], "prepared", "west", 1, "bowl", 150, 180, 6, 20, 9, 6, "boiled", "IFCT-2017", "medium"),
    ("veg-kofta", "Veg Kofta Curry", ["malai kofta"], "prepared", "north", 1, "bowl", 200, 200, 4, 15, 14, 3, "boiled", "IFCT-2017", "medium"),
    ("rajma-chawal", "Rajma Chawal (Combined)", ["kidney beans rice"], "prepared", "north", 1, "plate", 300, 140, 5, 25, 2, 4, "boiled", "IFCT-2017", "medium"),

    # PACKAGED (~6)
    ("maggi-noodles", "Maggi 2-Minute Noodles", ["instant noodles", "yippee"], "packaged", "pan-india", 1, "piece", 70, 430, 8, 62, 16, 2, "boiled", "IFCT-2017", "high"),
    ("marie-biscuit", "Marie Biscuit", ["tea biscuit"], "packaged", "pan-india", 1, "piece", 5, 450, 8, 75, 12, 2, "baked", "IFCT-2017", "high"),
    ("cream-biscuit", "Cream Biscuit", ["bourbon", "oreo"], "packaged", "pan-india", 1, "piece", 15, 480, 5, 70, 20, 1, "baked", "IFCT-2017", "high"),
    ("namkeen", "Bhujia / Namkeen Mixture", ["aloo bhujia", "mixtrue"], "packaged", "pan-india", 1, "cup", 30, 550, 12, 45, 35, 4, "deep-fried", "IFCT-2017", "high"),
    ("potato-chips", "Potato Chips", ["lays", "wafers"], "packaged", "pan-india", 1, "piece", 30, 536, 7, 53, 35, 4, "deep-fried", "USDA", "high"),
    ("brown-bread", "Brown Bread", ["whole wheat bread"], "packaged", "pan-india", 1, "slice", 25, 250, 10, 45, 4, 6, "baked", "USDA", "high"),

    # CONDIMENTS (~7)
    ("cooking-oil", "Cooking Oil (Sunflower/Mustard)", ["tel", "refined oil"], "condiments", "pan-india", 1, "tablespoon", 15, 900, 0, 0, 100, 0, "", "USDA", "high"),
    ("sugar", "White Sugar", ["cheeni", "shakkar"], "condiments", "pan-india", 1, "teaspoon", 5, 387, 0, 100, 0, 0, "", "USDA", "high"),
    ("honey", "Honey", ["shahad", "madhu", "शहद"], "condiments", "pan-india", 1, "teaspoon", 7, 304, 0.3, 82.4, 0, 0.2, "", "USDA", "high"),
    ("green-chutney", "Green Chutney", ["pudina chutney", "mint coriander chutney"], "condiments", "pan-india", 1, "tablespoon", 15, 40, 2, 6, 1, 2, "", "IFCT-2017", "medium"),
    ("tamarind-chutney", "Tamarind Chutney", ["imli chutney", "meethi chutney"], "condiments", "pan-india", 1, "tablespoon", 15, 180, 1, 45, 0, 2, "", "IFCT-2017", "medium"),
    ("pickle", "Mango Pickle", ["aam ka achar", "mixed pickle"], "condiments", "pan-india", 1, "tablespoon", 15, 150, 1, 10, 12, 2, "", "IFCT-2017", "medium"),
    ("jaggery", "Jaggery", ["gud", "gur"], "condiments", "pan-india", 1, "teaspoon", 5, 383, 0.4, 98, 0.1, 0, "", "IFCT-2017", "high"),
    ("tofu", "Tofu (Soy Paneer)", ["soya paneer"], "condiments", "pan-india", 1, "cup", 100, 144, 15.7, 2.8, 8.7, 2.3, "", "USDA", "high")
]

FOODS = []
for row in foods_data:
    item = {
        "id": row[0],
        "name": row[1],
        "aliases": row[2] if isinstance(row[2], list) else [row[2]],
        "category": row[3],
        "region": row[4],
        "serving_size": row[5],
        "serving_unit": row[6],
        "grams_per_serving": row[7],
        "calories_per_100g": float(row[8]),
        "protein_per_100g": float(row[9]),
        "carbs_per_100g": float(row[10]),
        "fat_per_100g": float(row[11]),
        "fiber_per_100g": float(row[12]),
        "source": row[14],
        "confidence": row[15]
    }
    if row[13]:
        item["cooking_method"] = row[13]
    FOODS.append(item)

def search_foods(query: str = '', category: str = None, limit: int = 50) -> list:
    """Search foods by name or alias, with optional category filter."""
    query = (query or '').lower().strip()
    results = []
    for food in FOODS:
        if category and food.get('category') != category:
            continue
        if not query:
            results.append(food)
        elif query in food['name'].lower():
            results.append(food)
        else:
            for alias in food.get('aliases', []):
                if query in alias.lower():
                    results.append(food)
                    break
        if len(results) >= limit:
            break
    return results

def get_food_by_id(food_id: str) -> dict | None:
    """Get a single food by ID."""
    for food in FOODS:
        if food['id'] == food_id:
            return food
    return None

def get_food_by_name(name: str) -> dict | None:
    """Fuzzy match food by name or alias."""
    name_lower = name.lower().strip()
    for food in FOODS:
        if food['name'].lower() == name_lower:
            return food
        for alias in food['aliases']:
            if alias.lower() == name_lower:
                return food
    return None

