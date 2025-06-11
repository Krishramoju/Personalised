from flask import Flask, request, jsonify
from collections import defaultdict

app = Flask(__name__)

user_histories = defaultdict(list)
user_profiles = defaultdict(lambda: {
    "likes": [],
    "name": None,
    "last_topic": None,
    "knowledge": []
})

def update_user_profile(user_id, message):
    message_lower = message.lower()

    if "my name is" in message_lower:
        name = message.split("my name is")[-1].strip().split()[0].capitalize()
        user_profiles[user_id]["name"] = name

    if "i like" in message_lower:
        interest = message.split("i like")[-1].strip().split('.')[0]
        user_profiles[user_id]["likes"].append(interest)

    user_profiles[user_id]["last_topic"] = message.strip()

    if any(kw in message_lower for kw in ["i am", "i have", "i know", "i want"]):
        user_profiles[user_id]["knowledge"].append(message.strip())

def generate_response(user_id, message, context):
    profile = user_profiles[user_id]
    name = profile.get("name")
    likes = profile.get("likes")
    last_topic = profile.get("last_topic")
    knowledge = profile.get("knowledge")

    base_response = f"That's interesting."

    if name:
        base_response = f"Hey {name}, that’s interesting."

    if likes:
        base_response += f" Since you like {likes[-1]}, you might find this relevant."

    if last_topic and last_topic != message:
        base_response += f" Also, earlier you talked about '{last_topic}'."

    if knowledge:
        recent_facts = "; ".join(knowledge[-2:])
        base_response += f" I remember you also told me: {recent_facts}."

    return base_response + " Let's explore that further."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_id = data.get('user_id')
    message = data.get('message')

    if not user_id or not message:
        return jsonify({"error": "user_id and message are required"}), 400

    update_user_profile(user_id, message)
    user_histories[user_id].append({"role": "user", "content": message})

    context = user_histories[user_id][-10:]

    response_text = generate_response(user_id, message, context)

    user_histories[user_id].append({"role": "bot", "content": response_text})

    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(debug=True)
