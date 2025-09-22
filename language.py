
from flask import Flask, render_template, request
from deep_translator import GoogleTranslator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import requests
import base64

app = Flask(__name__)

# Replace this with your actual Plant.id API key
PLANT_ID_API_KEY = "GzFVMVsMcr20krspg2RHcuZfZT4Sufs7luXeyk4O10xwBWdT9C"

@app.route('/')
def home():
    return render_template('homepagemain.html')


@app.route('/about')
def about():
    return render_template('aboutpage.html')


@app.route('/contact')
def contact():
    return render_template('contactpage.html')


@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Fake user auth for now (replace with real logic later)
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        # Example condition (replace with DB check)
        if email == "test@example.com" and password == "password":
            return {"message": "Login successful!"}, 200
        else:
            return {"message": "Invalid credentials."}, 401

    # GET request → render the login page
    return render_template('signin.html')


@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/reco')
def reco():
    return render_template('reco.html')


@app.route('/plantinfo')
def plantinfo():
    return render_template('plantinfo.html')

@app.route('/plantinfohindi')
def plantinfohindi():
    return render_template()

@app.route('/plantremedies')
def plantremedies():
    return render_template('plantremedies.html')


@app.route('/plantremedieshindi')
def plantremedieshindi():
    return render_template('plantremedieshindi.html')

@app.route('/identify', methods=['POST'])
def identify():
    if 'image' not in request.files:
        return "No image uploaded", 400

    language = request.form.get('language', 'en')
    image = request.files['image']
    image_bytes = image.read()
    base64_image = base64.b64encode(image_bytes).decode("utf-8")

    url = "https://api.plant.id/v2/identify"
    headers = {"Content-Type": "application/json"}
    data = {
        "api_key": PLANT_ID_API_KEY,
        "images": [base64_image],
        "modifiers": ["crops_fast", "similar_images"],
        "plant_language": "en",
        "plant_details": ["common_names", "url", "wiki_description"]
    }

    response = requests.post(url, json=data, headers=headers)
    result = response.json()

    if "suggestions" not in result or not result["suggestions"]:
        return "Could not identify the plant", 400

    plant = result["suggestions"][0]
    name_en = plant["plant_name"]
    common_names_list = plant.get("plant_details", {}).get("common_names", [])
    common_names_en = ", ".join(common_names_list)
    description_en = plant.get("plant_details", {}).get("wiki_description", {}).get("value", "No description available.")

    # Default values
    name_hi = None
    common_names_hi = None
    description_hi = None

    if language == 'hi':
        try:
            # Translate scientific name and common names to Hindi
            name_hi = GoogleTranslator(source='auto', target='hi').translate(name_en)
            common_names_hi = GoogleTranslator(source='auto', target='hi').translate(common_names_en)
            description_hi = GoogleTranslator(source='auto', target='hi').translate(description_en)
        except Exception as e:
            name_hi = name_en
            common_names_hi = common_names_en
            description_hi = "अनुवाद विफल रहा।"

    return render_template("recoresuult.html",
      name=name_en if language == 'en' else name_hi,
      common_names_en=common_names_en if language == 'en' else None,
      common_names_hi=common_names_hi if language == 'hi' else None,
      description_en=description_en if language == 'en' else None,
      description_hi=description_hi if language == 'hi' else None
    )

if __name__ == '__main__':
    app.run(debug=True)