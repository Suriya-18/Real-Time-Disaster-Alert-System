import requests
from twilio.rest import Client
from flask import Flask, request, jsonify

# Twilio Configuration
TWILIO_ACCOUNT_SID = "your_twilio_account_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"
TO_PHONE_NUMBER = "recipient_phone_number"

# OpenWeather API Configuration
OPENWEATHER_API_KEY = "your_openweather_api_key"
LOCATION = "Chennai,IN"  # Example location (city, country code)

# Flask App
app = Flask(__name__)

def get_weather_data():
    """Fetch weather data from OpenWeather API."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={LOCATION}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def check_disaster_conditions(weather_data):
    """Check for disaster conditions like storms, extreme weather, etc."""
    weather_main = weather_data["weather"][0]["main"]
    weather_description = weather_data["weather"][0]["description"]
    if weather_main in ["Rain", "Thunderstorm", "Snow"] or "extreme" in weather_description:
        return True, f"Alert: {weather_main} - {weather_description.capitalize()} detected in {LOCATION}."
    return False, "Weather is normal."

def send_sms_alert(message):
    """Send SMS alert using Twilio."""
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=TWILIO_PHONE_NUMBER,
        to=TO_PHONE_NUMBER
    )

@app.route('/check_disaster', methods=['GET'])
def check_disaster():
    """API endpoint to check for disasters and send alerts."""
    weather_data = get_weather_data()
    if not weather_data:
        return jsonify({"error": "Failed to fetch weather data"}), 500

    is_disaster, alert_message = check_disaster_conditions(weather_data)
    if is_disaster:
        send_sms_alert(alert_message)
        return jsonify({"status": "Disaster detected", "message": alert_message})
    else:
        return jsonify({"status": "No disaster", "message": "Weather is normal."})

if __name__ == '__main__':
    app.run(debug=True)
