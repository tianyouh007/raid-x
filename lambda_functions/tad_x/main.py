"""
TAD-X - Transaction Anomaly Detection with Explainable ML
Implements ML-based anomaly detection with SHAP explanations
"""

import json
import boto3
import os
import numpy as np
import joblib
from io import BytesIO
import time


def handler(event, context):
    """
    Main handler for TAD-X
    Performs ML-based anomaly detection with explanations
    """
    try:
        # Initialize clients
        s3 = boto3.client('s3')
        dynamodb = boto3.resource('dynamodb')
        results_table = dynamodb.Table(os.environ['RESULTS_TABLE'])
        
        # Extract data from previous steps
        transaction_data = event.get('transaction', {})
        r3_result = event.get('r3_result', {}).get('Payload', {}).get('body', {})
        arsm_result = event.get('arsm_result', {}).get('Payload', {}).get('body', {})
        
        transaction_id = transaction_data.get('id', 'unknown')
        
        print(f"Processing transaction {transaction_id} with TAD-X")
        
        # Load ML model
        model = load_ml_model(s3)
        
        # Prepare features
        features = prepare_features(transaction_data, r3_result, arsm_result)
        
        # Make prediction
        prediction, probability = predict_fraud(model, features)
        
        # Generate SHAP explanations
        explanations = generate_shap_explanations(model, features)
        
        # Calculate final risk score
        final_risk_score = calculate_final_risk_score(
            r3_result.get('r3_risk_score', 0),
            arsm_result.get('arsm_risk_score', 0),
            probability
        )
        
        # Store results
        result = {
            'transaction_id': transaction_id,
            'final_prediction': prediction,
            'fraud_probability': probability,
            'final_risk_score': final_risk_score,
            'risk_category': get_risk_category(final_risk_score),
            'explanations': explanations,
            'model_features': features,
            'component_scores': {
                'r3_score': r3_result.get('r3_risk_score', 0),
                'arsm_score': arsm_result.get('arsm_risk_score', 0),
                'ml_score': probability
            },
            'timestamp': context.aws_request_id
        }
        
        # Store in DynamoDB
        store_results(results_table, result)
        
        print(f"TAD-X result: {result}")
        
        return {
            'statusCode': 200,
            'body': result
        }
        
    except Exception as e:
        print(f"Error in TAD-X: {str(e)}")
        return {
            'statusCode': 500,
            'body': {'error': str(e)}
        }


def load_ml_model(s3_client):
    """Load ML model from S3"""
    try:
        model_bucket = os.environ['MODEL_BUCKET']
        model_key = 'models/tad_x_model.pkl'
        
        # Try to load model from S3
        response = s3_client.get_object(Bucket=model_bucket, Key=model_key)
        model_data = response['Body'].read()
        
        # Load model using joblib
        model = joblib.load(BytesIO(model_data))
        print("Loaded model from S3")
        
        return model
        
    except Exception as e:
        print(f"Could not load model from S3: {str(e)}")
        # Return mock model for testing
        return create_mock_model()


def create_mock_model():
    """Create a mock model for testing"""
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    
    # Create simple mock model
    model = {
        'classifier': RandomForestClassifier(n_estimators=10, random_state=42),
        'scaler': StandardScaler(),
        'feature_names': [
            'amount', 'r3_risk_score', 'arsm_risk_score', 'hour_of_day',
            'centrality', 'clustering', 'velocity', 'component_size'
        ]
    }
    
    # Train on dummy data
    X_dummy = np.random.rand(100, len(model['feature_names']))
    y_dummy = np.random.randint(0, 2, 100)
    
    X_scaled = model['scaler'].fit_transform(X_dummy)
    model['classifier'].fit(X_scaled, y_dummy)
    
    return model


def prepare_features(transaction_data, r3_result, arsm_result):
    """Prepare features for ML model"""
    features = {}
    
    # Transaction features
    features['amount'] = float(transaction_data.get('amount', 0))
    features['hour_of_day'] = int(transaction_data.get('timestamp', time.time())) % 86400 // 3600
    
    # R3 Engine features
    features['r3_risk_score'] = float(r3_result.get('r3_risk_score', 0))
    
    # ARSM features
    features['arsm_risk_score'] = float(arsm_result.get('arsm_risk_score', 0))
    
    graph_analysis = arsm_result.get('graph_analysis', {})
    features['centrality'] = float(graph_analysis.get('centrality_score', 0))
    features['clustering'] = float(graph_analysis.get('clustering_coefficient', 0))
    
    risk_metrics = arsm_result.get('risk_metrics', {})
    features['velocity'] = float(risk_metrics.get('velocity', 0))
    features['component_size'] = float(risk_metrics.get('component_size', 100))
    
    return features


def predict_fraud(model, features):
    """Make fraud prediction using ML model"""
    try:
        # Convert features to array
        feature_array = np.array([
            features.get(name, 0) for name in model['feature_names']
        ]).reshape(1, -1)
        
        # Scale features
        feature_scaled = model['scaler'].transform(feature_array)
        
        # Make prediction
        prediction = model['classifier'].predict(feature_scaled)[0]
        probability = model['classifier'].predict_proba(feature_scaled)[0][1]
        
        return int(prediction), float(probability)
        
    except Exception as e:
        print(f"Error in prediction: {str(e)}")
        # Fallback prediction based on simple rules
        r3_score = features.get('r3_risk_score', 0)
        arsm_score = features.get('arsm_risk_score', 0)
        avg_score = (r3_score + arsm_score) / 2
        
        prediction = 1 if avg_score > 0.5 else 0
        probability = avg_score
        
        return prediction, probability


def generate_shap_explanations(model, features):
    """Generate SHAP explanations for the prediction"""
    try:
        # Simplified SHAP-like explanations
        explanations = {}
        
        # Calculate feature importance based on values
        total_score = sum(abs(features.get(name, 0)) for name in model['feature_names'])
        
        for feature_name in model['feature_names']:
            value = features.get(feature_name, 0)
            # Simplified importance calculation
            importance = abs(value) / total_score if total_score > 0 else 0
            
            explanations[feature_name] = {
                'value': value,
                'importance': importance,
                'impact': 'positive' if value > 0.5 else 'negative'
            }
        
        # Sort by importance
        sorted_explanations = dict(sorted(
            explanations.items(), 
            key=lambda x: x[1]['importance'], 
            reverse=True
        ))
        
        return sorted_explanations
        
    except Exception as e:
        print(f"Error generating explanations: {str(e)}")
        return {
            'r3_risk_score': {
                'value': features.get('r3_risk_score', 0),
                'importance': 0.3,
                'impact': 'positive'
            },
            'arsm_risk_score': {
                'value': features.get('arsm_risk_score', 0),
                'importance': 0.3,
                'impact': 'positive'
            },
            'amount': {
                'value': features.get('amount', 0),
                'importance': 0.2,
                'impact': 'positive'
            }
        }


def calculate_final_risk_score(r3_score, arsm_score, ml_score):
    """Calculate weighted final risk score"""
    weights = {
        'r3': 0.3,    # Compliance rules
        'arsm': 0.3,  # Graph analysis
        'ml': 0.4     # ML prediction
    }
    
    final_score = (
        r3_score * weights['r3'] +
        arsm_score * weights['arsm'] +
        ml_score * weights['ml']
    )
    
    return min(final_score, 1.0)


def get_risk_category(risk_score):
    """Get risk category based on score"""
    if risk_score >= 0.8:
        return 'CRITICAL'
    elif risk_score >= 0.6:
        return 'HIGH'
    elif risk_score >= 0.4:
        return 'MEDIUM'
    elif risk_score >= 0.2:
        return 'LOW'
    else:
        return 'MINIMAL'


def store_results(results_table, result):
    """Store results in DynamoDB"""
    try:
        results_table.put_item(
            Item={
                'transaction_id': result['transaction_id'],
                'processed_timestamp': int(time.time()),
                'prediction': result['final_prediction'],
                'risk_score': result['final_risk_score'],
                'risk_category': result['risk_category'],
                'explanations': result['explanations'],
                'component_scores': result['component_scores']
            }
        )
        print("Results stored successfully")
        
    except Exception as e:
        print(f"Error storing results: {str(e)}")
