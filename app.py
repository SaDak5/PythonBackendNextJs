from flask import Flask, request, jsonify
from flask_cors import CORS
from faq_data import find_faq, get_random_response, get_suggestions, faq_questions
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Autorise les requêtes depuis Next.js

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({"error": "Le message est requis"}), 400

        # 1. Chercher dans les FAQ
        faq_results = find_faq(message)
        
        if faq_results:
            faq_match = faq_results[0]
            return jsonify({ 
                "response": get_random_response(faq_match["responses"]),
                "source": "faq",
                "allResponses": faq_match["responses"],
                "question": faq_match["question"],
                "confidence": "high"
            })

        # 2. Si pas trouvé, chercher des suggestions
        suggestions = get_suggestions(message)
        
        if suggestions:
            suggestions_text = "\n".join([f"• {s}" for s in suggestions])
            return jsonify({ 
                "response": f"Je n'ai pas trouvé de réponse exacte, mais voici des suggestions :\n\n{suggestions_text}",
                "source": "suggestions",
                "suggestions": suggestions,
                "confidence": "medium"
            })

        # 3. Réponse par défaut
        return jsonify({ 
            "response": "Je n'ai pas trouvé d'information sur ce sujet dans notre base. Contactez le support RH pour plus d'aide.",
            "source": "default",
            "confidence": "low",
            "contact": "rh@entreprise.com - Poste 4567"
        })

    except Exception as e:
        print(f"Erreur API Chat: {e}")
        return jsonify({"error": "Erreur serveur interne"}), 500

@app.route('/api/chat/questions', methods=['GET'])
def get_questions():
    all_questions = []
    for category in faq_questions:
        for question in category["questions"]:
            all_questions.append({
                "question": question["question"],
                "category": category["category"],
                "tags": question["tags"]
            })
    
    return jsonify({ 
        "questions": all_questions,
        "total": len(all_questions) 
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "OK", "service": "ChatBot API Python"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)