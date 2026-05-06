import sys
sys.path.insert(0, 'E:/pypackages')

from flask import Flask, render_template, jsonify, request
from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_question', methods=['POST'])
def get_question():
    data = request.json
    role = data.get('role')
    level = data.get('level')
    asked = data.get('asked_questions', [])

    prompt = f"""You are an expert technical interviewer for {role} roles at {level} level.

Generate ONE interview question that has NOT been asked before.
Previously asked: {asked}

Return only valid JSON like this:
{{
  "question": "Your interview question here",
  "category": "Technical/Behavioral/System Design",
  "difficulty": "Easy/Medium/Hard",
  "hint": "A small hint if they get stuck"
}}

No markdown, no backticks, just JSON."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    result = json.loads(response.choices[0].message.content)
    return jsonify(result)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    data = request.json
    question = data.get('question')
    answer = data.get('answer')
    role = data.get('role')
    level = data.get('level')

    prompt = f"""You are an expert technical interviewer evaluating a {role} candidate at {level} level.

Question: {question}
Candidate Answer: {answer}

Evaluate the answer and return only valid JSON:
{{
  "score": 8,
  "max_score": 10,
  "verdict": "Good/Excellent/Needs Improvement/Poor",
  "strengths": ["strength 1", "strength 2"],
  "improvements": ["improvement 1", "improvement 2"],
  "ideal_answer": "A brief ideal answer in 2-3 sentences",
  "feedback": "Overall feedback in one paragraph"
}}

Be honest but constructive. No markdown, no backticks, just JSON."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    result = json.loads(response.choices[0].message.content)
    return jsonify(result)

@app.route('/final_report', methods=['POST'])
def final_report():
    data = request.json
    role = data.get('role')
    level = data.get('level')
    results = data.get('results', [])

    total_score = sum(r['score'] for r in results)
    max_score = sum(r['max_score'] for r in results)
    percentage = round((total_score / max_score) * 100) if max_score > 0 else 0

    prompt = f"""You are an expert interviewer. A {role} candidate at {level} level just completed an interview.

Results summary:
- Total Score: {total_score}/{max_score} ({percentage}%)
- Questions answered: {len(results)}

Give a final assessment. Return only valid JSON:
{{
  "overall_rating": "Strong/Good/Average/Needs Work",
  "hire_recommendation": "Strong Hire/Hire/Maybe/No Hire",
  "top_strengths": ["strength 1", "strength 2", "strength 3"],
  "key_improvements": ["area 1", "area 2", "area 3"],
  "study_topics": ["topic 1", "topic 2", "topic 3"],
  "motivational_message": "An encouraging closing message"
}}

No markdown, no backticks, just JSON."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    result = json.loads(response.choices[0].message.content)
    result['percentage'] = percentage
    result['total_score'] = total_score
    result['max_score'] = max_score
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)