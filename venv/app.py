
# Event Feedback Analysis: 
# By analyzing the sentiment of feedback for events, Admin Of Elkindy can gauge overall attendee satisfaction and improve future events based on their feedbacks.
# Sentiment Analysis Using TextBlob: This is a form of natural language processing.
# TextBlob uses pre-trained models to assess the polarity (sentiment) of text. 
# While it leverages models that are built using machine learning techniques, 
# Data Normalization and Aggregation: we normalized data from different scales (ratings out of 5 and 10) and combined them to compute an overall sentiment score.

from flask import Flask, jsonify, request
from pymongo import MongoClient
from textblob import TextBlob
app = Flask(__name__)

# Connect to MongoDB
mongo_uri = "mongodb+srv://kindi:123@cluster0.scfokhp.mongodb.net/"  
client = MongoClient(mongo_uri)
db = client['ELKindyDB']

@app.route('/')
def home():
    return "Welcome to my Flask app!"

@app.route('/feedbacks', methods=['GET'])
def get_feedbacks():
    feedbacks = list(db.feedbacks.find())  
    # Convert MongoDB objects to JSON
    for feedback in feedbacks:
        feedback['_id'] = str(feedback['_id'])
    return jsonify(feedbacks)

# @app.route('/analyze', methods=['POST'])
# def analyze_feedback():
#     data = request.get_json()
#     texts = [data.get(field, '') for field in ['bestPart', 'improvements', 'finalComments',  'venueIssues', 'venueFeature']]
#     text_sentiments = [TextBlob(text).sentiment.polarity for text in texts if text]
#     average_text_sentiment = sum(text_sentiments) / len(text_sentiments) if text_sentiments else 0

#     # Numeric ratings on a scale of 1-10
#     numeric_fields = ['entertainmentRating', 'inspirationRating', 'themeRelevance', 'valueForMoney']
#     numeric_ratings = [data.get(field, 0) for field in numeric_fields]
    
#     # Ratings on a scale of 1-5, normalize to scale of 1-10
#     scale_5_fields = ['performersQuality.overallQuality', 'performersQuality.themeAlignment', 'performersQuality.audienceEngagement',
#                       'presentersFeedback.interesting', 'presentersFeedback.relevant', 'presentersFeedback.inspiring']
#     scale_5_ratings = [(data.get(field, 0) * 2) for field in scale_5_fields]  # Multiply by 2 to normalize to 1-10 scale

#     # Combine all ratings
#     all_ratings = numeric_ratings + scale_5_ratings
#     average_numeric_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0
#     normalized_numeric_sentiment = (average_numeric_rating / 10) * 2 - 1  # Normalize to range -1 to 1

#     # Venue satisfaction (Boolean)
#     venue_satisfaction = data.get('venueSatisfaction', False)
#     venue_satisfaction_score = 1 if venue_satisfaction else -1

#     # Combine sentiments
#     overall_sentiment = (average_text_sentiment + normalized_numeric_sentiment + venue_satisfaction_score) / 3
#     return jsonify({'overall_sentiment': overall_sentiment})

@app.route('/analyze', methods=['POST'])
def analyze_feedback():
    data = request.get_json()
    user_response = {}
    admin_statistics = {}

    # Analyzing text fields for sentiment 
    text_fields = ['bestPart', 'improvements', 'finalComments']
    sentiments = {field: TextBlob(data.get(field, '')).sentiment.polarity for field in text_fields if data.get(field, '')}
    overall_sentiment = sum(sentiments.values()) / len(sentiments) if sentiments else 0

    # Generate user-friendly message for users
    if overall_sentiment > 0.1:
        user_response['message'] = "Thank you for your positive feedback!"
    elif overall_sentiment < -0.1:
        user_response['message'] = "We're sorry you had a bad experience, we'll work on improving this."
    else:
        user_response['message'] = "Thank you for your feedback!"

    # Prepare statistics for admin
    admin_statistics['detailed_sentiments'] = {field: {'sentiment': sentiment} for field, sentiment in sentiments.items()}
    admin_statistics['overall_sentiment'] = overall_sentiment

    # Combine results in a single response object
    response = {
        'userResponse': user_response,
        'adminStatistics': admin_statistics
    }
    return jsonify(response)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=True, port=8000)
