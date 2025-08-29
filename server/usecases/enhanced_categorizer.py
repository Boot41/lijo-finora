"""
Enhanced Transaction Categorizer using FinBERT + Custom Rules
Combines ML-based categorization with rule-based fallbacks
"""
import re
import logging
from typing import List, Dict, Tuple, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
import pickle
import os

logger = logging.getLogger(__name__)

class EnhancedTransactionCategorizer:
    def __init__(self):
        self.finbert_classifier = None
        self.custom_model = None
        self.vectorizer = None
        self.categories = [
            'Food & Dining', 'Transportation', 'Shopping', 'Bills & Utilities',
            'Healthcare', 'Entertainment', 'Travel', 'Income', 'Transfers', 'Miscellaneous'
        ]
        
        # Enhanced keyword rules
        self.category_keywords = {
            'Food & Dining': [
                'restaurant', 'cafe', 'food', 'dining', 'pizza', 'burger', 'coffee',
                'starbucks', 'mcdonalds', 'kfc', 'dominos', 'swiggy', 'zomato',
                'grocery', 'supermarket', 'walmart', 'target', 'safeway', 'big bazaar',
                'reliance fresh', 'more', 'dmart', 'bakery', 'bar', 'pub'
            ],
            'Transportation': [
                'uber', 'lyft', 'taxi', 'cab', 'ola', 'rapido', 'metro', 'bus',
                'train', 'flight', 'airline', 'fuel', 'gas', 'petrol', 'diesel',
                'parking', 'toll', 'auto', 'rickshaw', 'bike', 'car rental'
            ],
            'Shopping': [
                'amazon', 'flipkart', 'myntra', 'ajio', 'shopping', 'mall',
                'store', 'retail', 'clothing', 'electronics', 'furniture',
                'home depot', 'ikea', 'costco', 'online', 'ecommerce'
            ],
            'Bills & Utilities': [
                'electricity', 'water', 'gas bill', 'internet', 'phone', 'mobile',
                'broadband', 'wifi', 'utility', 'electric', 'power', 'telecom',
                'airtel', 'jio', 'vodafone', 'bsnl', 'tata sky', 'dish tv'
            ],
            'Healthcare': [
                'hospital', 'doctor', 'medical', 'pharmacy', 'medicine', 'clinic',
                'health', 'dental', 'insurance', 'apollo', 'fortis', 'max',
                'medplus', 'pharmeasy', 'netmeds', 'lab', 'diagnostic'
            ],
            'Entertainment': [
                'movie', 'cinema', 'theater', 'netflix', 'spotify', 'amazon prime',
                'hotstar', 'youtube', 'gaming', 'game', 'entertainment',
                'concert', 'show', 'event', 'ticket', 'bookmyshow'
            ],
            'Travel': [
                'hotel', 'booking', 'travel', 'vacation', 'trip', 'flight',
                'airline', 'makemytrip', 'goibibo', 'cleartrip', 'oyo',
                'airbnb', 'resort', 'tour', 'holiday'
            ],
            'Income': [
                'salary', 'wage', 'income', 'deposit', 'credit', 'refund',
                'cashback', 'bonus', 'dividend', 'interest', 'transfer in'
            ],
            'Transfers': [
                'transfer', 'paytm', 'phonepe', 'googlepay', 'upi', 'neft',
                'rtgs', 'imps', 'wallet', 'payment', 'send money', 'receive'
            ]
        }
        
        self.load_models()
    
    def load_models(self):
        """Load or initialize ML models"""
        try:
            # Try to load FinBERT (fallback to general sentiment if not available)
            try:
                self.finbert_classifier = pipeline(
                    "text-classification",
                    model="ProsusAI/finbert",
                    tokenizer="ProsusAI/finbert"
                )
                logger.info("FinBERT model loaded successfully")
            except Exception as e:
                logger.warning(f"FinBERT not available, using general classifier: {e}")
                self.finbert_classifier = pipeline("text-classification")
            
            # Load custom model if exists
            model_path = "custom_categorizer.pkl"
            vectorizer_path = "tfidf_vectorizer.pkl"
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                with open(model_path, 'rb') as f:
                    self.custom_model = pickle.load(f)
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                logger.info("Custom model loaded successfully")
            else:
                logger.info("No custom model found, will use rule-based categorization")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def categorize_transaction(self, description: str, amount: float = None) -> Tuple[str, float]:
        """
        Categorize a single transaction using multiple methods
        Returns: (category, confidence_score)
        """
        if not description:
            return 'Miscellaneous', 0.0
        
        description_clean = description.lower().strip()
        
        # Method 1: Rule-based categorization (highest priority)
        rule_category, rule_confidence = self._rule_based_categorization(description_clean)
        if rule_confidence > 0.8:
            return rule_category, rule_confidence
        
        # Method 2: Custom ML model (if available)
        if self.custom_model and self.vectorizer:
            ml_category, ml_confidence = self._ml_categorization(description_clean)
            if ml_confidence > 0.7:
                return ml_category, ml_confidence
        
        # Method 3: FinBERT analysis (if available)
        if self.finbert_classifier:
            finbert_category, finbert_confidence = self._finbert_categorization(description_clean)
            if finbert_confidence > 0.6:
                return finbert_category, finbert_confidence
        
        # Method 4: Amount-based heuristics
        amount_category = self._amount_based_categorization(amount)
        if amount_category:
            return amount_category, 0.5
        
        # Fallback: Use rule-based result or Miscellaneous
        return rule_category if rule_confidence > 0.3 else 'Miscellaneous', max(rule_confidence, 0.3)
    
    def _rule_based_categorization(self, description: str) -> Tuple[str, float]:
        """Enhanced rule-based categorization with confidence scoring"""
        best_category = 'Miscellaneous'
        best_score = 0.0
        
        for category, keywords in self.category_keywords.items():
            score = 0.0
            matched_keywords = 0
            
            for keyword in keywords:
                if keyword in description:
                    # Exact match gets higher score
                    if keyword == description:
                        score += 1.0
                    # Partial match
                    elif len(keyword) > 3:  # Avoid short word false positives
                        score += 0.8
                    else:
                        score += 0.6
                    matched_keywords += 1
            
            # Normalize score by number of keywords
            if matched_keywords > 0:
                normalized_score = min(score / len(keywords) * matched_keywords, 1.0)
                if normalized_score > best_score:
                    best_score = normalized_score
                    best_category = category
        
        return best_category, best_score
    
    def _ml_categorization(self, description: str) -> Tuple[str, float]:
        """Use custom trained ML model for categorization"""
        try:
            # Vectorize the description
            description_vector = self.vectorizer.transform([description])
            
            # Get prediction probabilities
            probabilities = self.custom_model.predict_proba(description_vector)[0]
            
            # Get the best prediction
            best_idx = probabilities.argmax()
            confidence = probabilities[best_idx]
            category = self.categories[best_idx]
            
            return category, confidence
            
        except Exception as e:
            logger.error(f"Error in ML categorization: {e}")
            return 'Miscellaneous', 0.0
    
    def _finbert_categorization(self, description: str) -> Tuple[str, float]:
        """Use FinBERT for financial text analysis"""
        try:
            # FinBERT gives sentiment, we need to map to categories
            # This is a simplified approach - you might want to fine-tune FinBERT
            result = self.finbert_classifier(description)
            
            # Map FinBERT sentiment to transaction categories (simplified)
            # In practice, you'd want to fine-tune FinBERT on transaction data
            sentiment = result[0]['label']
            confidence = result[0]['score']
            
            # Simple mapping (you'd want to improve this)
            if 'positive' in sentiment.lower():
                return 'Income', confidence * 0.7  # Reduce confidence for this mapping
            else:
                return 'Miscellaneous', confidence * 0.5
                
        except Exception as e:
            logger.error(f"Error in FinBERT categorization: {e}")
            return 'Miscellaneous', 0.0
    
    def _amount_based_categorization(self, amount: float) -> Optional[str]:
        """Use amount patterns for categorization hints"""
        if amount is None:
            return None
        
        abs_amount = abs(amount)
        
        # Large amounts often indicate transfers or bills
        if abs_amount > 10000:
            return 'Transfers' if amount > 0 else 'Bills & Utilities'
        
        # Small amounts often indicate food or transportation
        if abs_amount < 500:
            return 'Food & Dining'
        
        return None
    
    def train_custom_model(self, training_data: List[Dict]):
        """Train custom ML model on user's transaction data"""
        try:
            # Prepare training data
            descriptions = [item['description'].lower() for item in training_data]
            categories = [item['category'] for item in training_data]
            
            # Create TF-IDF vectorizer
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words='english'
            )
            
            # Vectorize descriptions
            X = self.vectorizer.fit_transform(descriptions)
            y = categories
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train Naive Bayes classifier
            self.custom_model = MultinomialNB()
            self.custom_model.fit(X_train, y_train)
            
            # Evaluate
            accuracy = self.custom_model.score(X_test, y_test)
            logger.info(f"Custom model trained with accuracy: {accuracy:.2f}")
            
            # Save models
            with open("custom_categorizer.pkl", 'wb') as f:
                pickle.dump(self.custom_model, f)
            with open("tfidf_vectorizer.pkl", 'wb') as f:
                pickle.dump(self.vectorizer, f)
            
            return accuracy
            
        except Exception as e:
            logger.error(f"Error training custom model: {e}")
            return 0.0
    
    def batch_categorize(self, transactions: List[Dict]) -> List[Dict]:
        """Categorize multiple transactions efficiently"""
        categorized_transactions = []
        
        for transaction in transactions:
            description = transaction.get('description', '')
            amount = transaction.get('amount', 0)
            
            category, confidence = self.categorize_transaction(description, amount)
            
            transaction_copy = transaction.copy()
            transaction_copy['category'] = category
            transaction_copy['confidence'] = confidence
            
            categorized_transactions.append(transaction_copy)
        
        return categorized_transactions
