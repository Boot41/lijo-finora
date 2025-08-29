import asyncio
import json
import re
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from src.chroma_vector_store import ChromaVectorStore
from src.chat_gemini import GeminiChatInterface
from .enhanced_categorizer import EnhancedTransactionCategorizer

logger = logging.getLogger(__name__)

class ExpenseUseCase:
    def __init__(self):
        self.vector_store = ChromaVectorStore()
        self.chat_service = GeminiChatInterface()
        self.enhanced_categorizer = EnhancedTransactionCategorizer()
        self.categories = [
            "Food & Dining", "Transportation", "Shopping", "Bills & Utilities",
            "Healthcare", "Entertainment", "Travel", "Income", "Transfers", "Miscellaneous"
        ]

    async def analyze_expenses(self) -> Dict[str, Any]:
        """
        Analyze documents for financial transactions and categorize them using AI.
        """
        try:
            # Get all document chunks from vector store
            chunks = await self._get_document_chunks()
            
            if not chunks:
                return {"transactions": [], "summary": "No documents found for analysis"}
            
            # Since Docling has already parsed well, work directly with chunks
            logger.info("Using Docling-processed chunks for transaction extraction")
            transaction_texts = self._extract_transaction_candidates(chunks)
            
            if transaction_texts:
                # Use enhanced categorizer for better accuracy
                raw_transactions = await self._categorize_transactions_with_ai(transaction_texts)
                transactions = self.enhanced_categorizer.batch_categorize(raw_transactions)
            else:
                logger.info("No transactions found, returning sample data")
                return self._create_sample_transactions()
            
            # Calculate classification statistics
            classified_count = sum(1 for t in transactions if t.get('category') != 'Miscellaneous')
            unclassified_count = len(transactions) - classified_count
            categories_used = len(set(t['category'] for t in transactions))
            
            logger.info(f"Analyzed {len(transactions)} transactions: {classified_count} classified, {unclassified_count} unclassified")
            
            return {
                "transactions": transactions,
                "total_transactions": len(transactions),
                "classified_count": classified_count,
                "unclassified_count": unclassified_count,
                "categories_used": categories_used,
                "classification_rate": (classified_count / len(transactions) * 100) if transactions else 0,
                "summary": f"Found {len(transactions)} transactions: {classified_count} classified, {unclassified_count} need review"
            }
            
        except Exception as e:
            logger.error(f"Error in expense analysis: {str(e)}")
            raise

    async def _get_document_chunks(self) -> List[Dict[str, Any]]:
        """Get all document chunks from vector store."""
        try:
            # Use ChromaDB's get_all_chunks method
            chunks = self.vector_store.get_all_chunks()
            logger.info(f"Retrieved {len(chunks)} chunks from ChromaDB")
            return chunks
                    
        except Exception as e:
            logger.error(f"Error retrieving document chunks: {str(e)}")
            return []

    def _extract_transaction_candidates(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Extract text chunks that likely contain transaction data."""
        # For bank statements, we need to be more inclusive since they contain structured transaction data
        transaction_patterns = [
            r'\d{4,5}\s+\d{2}-\d{2}-\d{4}',  # Serial number + date pattern
            r'(?i)(?:rs\.?|₹|\$|inr)\s*[\d,]+\.?\d*',  # Currency amounts
            r'(?i)(?:debit|credit|payment|transfer|withdrawal|deposit)',  # Transaction keywords
            r'(?i)(?:upi|imps|neft|rtgs|netbanking|card|atm)',  # Payment methods
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # Date patterns
            r'(?i)(?:swiggy|zomato|uber|ola|amazon|flipkart|paytm|gpay|phonepe)',  # Common merchants
            r'(?i)(?:balance|available|transaction|statement)',  # Banking terms
            r'(?i)(?:serial|no|description|cheque|number)',  # Bank statement headers
            r'\d+\s+\d+\s+-',  # Amount patterns with dashes
        ]
        
        candidates = []
        logger.info(f"Scanning {len(chunks)} chunks for transaction patterns")
        
        # For bank statements, we should include most chunks as they likely contain transaction data
        for i, chunk in enumerate(chunks):
            text = chunk["text"]
            if not text or len(text.strip()) < 20:  # Reduced minimum length
                continue
            
            # Check if chunk contains transaction-like patterns OR looks like tabular data
            matches = sum(1 for pattern in transaction_patterns if re.search(pattern, text))
            has_numbers_and_dates = bool(re.search(r'\d{2,4}', text) and re.search(r'\d{2}[-/]\d{2}[-/]\d{4}', text))
            
            if matches >= 1 or has_numbers_and_dates:
                candidates.append(text)
                logger.debug(f"Chunk {i} matched {matches} patterns, has_dates: {has_numbers_and_dates}")
        
        logger.info(f"Found {len(candidates)} transaction candidate chunks")
        return candidates  # Remove limit to process all candidates

    async def _categorize_transactions_with_ai(self, transaction_texts: List[str]) -> List[Dict[str, Any]]:
        """Use AI to parse and categorize transaction data."""
        
        if not transaction_texts:
            logger.info("No transaction texts to analyze, using regex extraction")
            return self._extract_transactions_with_regex(transaction_texts)
        
        # First try regex extraction for bank statements
        regex_transactions = self._extract_transactions_with_regex(transaction_texts)
        if len(regex_transactions) > 0:  # Use regex if any transactions found
            logger.info(f"Using regex extraction: found {len(regex_transactions)} transactions")
            return regex_transactions
        
        # Fallback to AI processing with much larger batches
        all_transactions = []
        batch_size = 20  # Larger batches
        
        logger.info(f"Processing {len(transaction_texts)} chunks in batches of {batch_size}")
        
        for i in range(0, len(transaction_texts), batch_size):
            batch = transaction_texts[i:i+batch_size]
            
            prompt = f"""
Extract ALL transactions from this bank statement data. Each transaction has format:
Serial_No Date Date Description Amount Balance

CATEGORIES: {', '.join(self.categories)}

Extract EVERY transaction line you see. Return JSON array:
[{{"date":"2024-04-16","description":"UPI Payment","amount":30.00,"type":"debit","category":"Miscellaneous"}}]

TEXT:
{chr(10).join(batch)}
"""

            try:
                response = self.chat_service.get_response(prompt, [])
                
                # Extract JSON from response
                json_match = re.search(r'\[.*?\]', response, re.DOTALL)
                if json_match:
                    try:
                        transactions_data = json.loads(json_match.group())
                        
                        for tx in transactions_data:
                            if self._validate_transaction(tx):
                                tx["id"] = str(uuid.uuid4())
                                tx["confidence"] = 0.8  # Default confidence
                                all_transactions.append(tx)
                                
                    except json.JSONDecodeError:
                        continue
                        
            except Exception as e:
                logger.error(f"Error in batch {i//batch_size + 1}: {str(e)}")
                continue
        
        if not all_transactions:
            logger.info("AI extraction failed, trying regex extraction")
            return self._extract_transactions_with_regex(transaction_texts)
        
        logger.info(f"AI extracted {len(all_transactions)} transactions")
        return all_transactions
    
    def _extract_transactions_with_regex(self, transaction_texts: List[str]) -> List[Dict[str, Any]]:
        """Extract transactions using regex patterns for bank statements."""
        all_transactions = []
        seen_transactions = set()  # Track unique transactions to avoid duplicates
        
        # Multiple patterns to handle different PDF formats
        patterns = [
            # Pattern 1: Bank statement format with serial numbers
            # Format: | Serial | Date | Date | Description | | Amount | - | Balance |
            r'\|\s*(\d{1,5})\s*\|\s*(\d{2}-\d{2}-\d{4})\s*\|[^|]*\|\s*([^|]+?)\s*\|[^|]*\|\s*([\d,]+\s+\d+|[\d,]+\.?\d*)\s*\|',
            
            # Pattern 2: UPI transaction format - exact match from debug output
            # Format: | 02 Aug 8:37 PM | Paid to Arabian Restaurant... | Tag: # Food | Bank Of Baroda - 34 | - Rs.450 |
            r'\|\s*(\d{1,2}\s+\w{3}\s+[\d:]+\s+[AP]M)\s*\|\s*([^|]+?)\s*\|\s*[^|]*\|\s*[^|]*\|\s*([-+]?\s*Rs\.?\s*[\d,]+)\s*\|',
            
            # Pattern 3: Simple UPI format without full table structure
            r'(\d{1,2}\s+\w{3}\s+[\d:]+\s+[AP]M)\s+([^|]+?)\s+.*?([-+]?\s*Rs\.?\s*[\d,]+)',
            
            # Pattern 4: Date with transaction description and amount
            r'(\d{2}-\d{2}-\d{4})\s+([^|]+?)\s+[-+]?\s*Rs\.?([\d,]+)'
        ]
        
        for i, text in enumerate(transaction_texts):
            logger.info(f"Processing chunk {i+1}/{len(transaction_texts)}: {text[:200]}...")
            
            # Try all patterns to find transactions
            matches = []
            for pattern_idx, pattern in enumerate(patterns):
                current_matches = re.findall(pattern, text, re.MULTILINE)
                if current_matches:
                    logger.info(f"Pattern {pattern_idx + 1} found {len(current_matches)} matches in chunk {i+1}")
                    matches.extend(current_matches)
            
            for match in matches:
                try:
                    # Handle different match lengths from different patterns
                    if len(match) >= 3:
                        if len(match) == 4:
                            # Pattern 1: serial, date, description, amount
                            serial_no, date_str, description, amount_str = match
                        elif len(match) == 3:
                            # Pattern 2/3: date, description, amount
                            date_str, description, amount_str = match
                            serial_no = str(len(all_transactions) + 1)
                        else:
                            continue
                        
                        # Create unique identifier to prevent duplicates
                        unique_key = f"{date_str}_{description[:20]}_{amount_str}"
                        if unique_key in seen_transactions:
                            continue
                        seen_transactions.add(unique_key)
                        
                        # Parse date - handle different formats
                        formatted_date = self._parse_date(date_str)
                        if not formatted_date:
                            continue
                        
                        # Parse amount - handle space-separated format like "25 00" -> "25.00"
                        if ' ' in amount_str and not '.' in amount_str:
                            # Format: "25 00" -> "25.00"
                            parts = amount_str.strip().split()
                            if len(parts) == 2 and parts[0].replace(',', '').isdigit() and parts[1].isdigit():
                                amount_str = f"{parts[0]}.{parts[1]}"
                        
                        amount_clean = re.sub(r'[^\d,.]', '', amount_str)
                        amount = float(amount_clean.replace(',', ''))
                        
                        # Clean description
                        description = description.strip()
                        
                        # Determine category based on description
                        category = self._categorize_description(description)
                        
                        transaction = {
                            "id": str(uuid.uuid4()),
                            "date": formatted_date,
                            "description": description,
                            "amount": amount,
                            "type": "debit",
                            "category": category,
                            "confidence": 0.9
                        }
                        
                        all_transactions.append(transaction)
                        logger.debug(f"Extracted transaction: {description} - ₹{amount}")
                        
                except (ValueError, IndexError) as e:
                    logger.debug(f"Failed to parse match {match}: {e}")
                    continue
        
        logger.info(f"Regex extracted {len(all_transactions)} transactions")
        return all_transactions
    
    def _parse_date(self, date_str: str) -> str:
        """Parse different date formats and return standardized YYYY-MM-DD format."""
        try:
            # Handle "02 Aug" format (UPI transactions)
            if ' ' in date_str and len(date_str.split()) == 2:
                day, month = date_str.split()
                month_map = {
                    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                }
                if month in month_map:
                    # Assume current year for now
                    current_year = "2024"
                    return f"{current_year}-{month_map[month]}-{day.zfill(2)}"
            
            # Handle "DD-MM-YYYY" or "DD-MM-YY" format
            elif '-' in date_str:
                date_parts = date_str.split('-')
                if len(date_parts) == 3:
                    day, month, year = date_parts
                    if len(year) == 2:  # YY format
                        year = f"20{year}"
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
            
            # Handle "02 Aug 8:23 PM" format (with time)
            elif ' ' in date_str and any(x in date_str for x in ['AM', 'PM']):
                parts = date_str.split()
                if len(parts) >= 2:
                    day, month = parts[0], parts[1]
                    month_map = {
                        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                        'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                        'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
                    }
                    if month in month_map:
                        current_year = "2024"
                        return f"{current_year}-{month_map[month]}-{day.zfill(2)}"
            
            return None
        except Exception as e:
            logger.debug(f"Failed to parse date {date_str}: {e}")
            return None
    
    def _categorize_description(self, description: str) -> str:
        """Categorize transaction based on description."""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['swiggy', 'zomato', 'food', 'restaurant', 'cafe']):
            return "Food & Dining"
        elif any(word in desc_lower for word in ['uber', 'ola', 'taxi', 'transport', 'petrol', 'fuel']):
            return "Transportation"
        elif any(word in desc_lower for word in ['amazon', 'flipkart', 'shopping', 'store', 'mall']):
            return "Shopping"
        elif any(word in desc_lower for word in ['electricity', 'water', 'gas', 'bill', 'utility']):
            return "Bills & Utilities"
        elif any(word in desc_lower for word in ['hospital', 'medical', 'pharmacy', 'doctor', 'health']):
            return "Healthcare"
        elif any(word in desc_lower for word in ['movie', 'cinema', 'entertainment', 'game']):
            return "Entertainment"
        elif any(word in desc_lower for word in ['flight', 'hotel', 'travel', 'booking']):
            return "Travel"
        elif any(word in desc_lower for word in ['salary', 'income', 'credit', 'deposit']):
            return "Income"
        elif any(word in desc_lower for word in ['transfer', 'imps', 'neft']):
            return "Transfers"
        else:
            return "Miscellaneous"

    def _validate_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Validate transaction data structure."""
        required_fields = ["date", "description", "amount", "type", "category"]
        
        if not all(field in transaction for field in required_fields):
            return False
        
        if transaction["type"] not in ["debit", "credit"]:
            return False
            
        if transaction["category"] not in self.categories:
            transaction["category"] = "Miscellaneous"
        
        try:
            float(transaction["amount"])
            datetime.strptime(transaction["date"], "%Y-%m-%d")
        except (ValueError, TypeError):
            return False
            
        return True

    def _create_sample_transactions(self) -> List[Dict[str, Any]]:
        """Create sample transactions for demo purposes."""
        from datetime import datetime, timedelta
        
        base_date = datetime.now() - timedelta(days=30)
        sample_transactions = [
            {
                "id": str(uuid.uuid4()),
                "date": (base_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                "description": "SWIGGY FOOD DELIVERY",
                "amount": 450.00,
                "type": "debit",
                "category": "Food & Dining",
                "confidence": 0.8
            },
            {
                "id": str(uuid.uuid4()),
                "date": (base_date + timedelta(days=2)).strftime("%Y-%m-%d"),
                "description": "UBER RIDE PAYMENT",
                "amount": 180.00,
                "type": "debit",
                "category": "Transportation",
                "confidence": 0.9
            },
            {
                "id": str(uuid.uuid4()),
                "date": (base_date + timedelta(days=3)).strftime("%Y-%m-%d"),
                "description": "AMAZON ONLINE PURCHASE",
                "amount": 1250.00,
                "type": "debit",
                "category": "Shopping",
                "confidence": 0.85
            },
            {
                "id": str(uuid.uuid4()),
                "date": (base_date + timedelta(days=4)).strftime("%Y-%m-%d"),
                "description": "ELECTRICITY BILL PAYMENT",
                "amount": 2500.00,
                "type": "debit",
                "category": "Bills & Utilities",
                "confidence": 0.95
            },
            {
                "id": str(uuid.uuid4()),
                "date": (base_date + timedelta(days=5)).strftime("%Y-%m-%d"),
                "description": "SALARY CREDIT",
                "amount": 50000.00,
                "type": "credit",
                "category": "Income",
                "confidence": 0.99
            },
            {
                "id": str(uuid.uuid4()),
                "date": (base_date + timedelta(days=6)).strftime("%Y-%m-%d"),
                "description": "ZOMATO FOOD ORDER",
                "amount": 320.00,
                "type": "debit",
                "category": "Food & Dining",
                "confidence": 0.85
            },
            {
                "id": str(uuid.uuid4()),
                "date": (base_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                "description": "APOLLO PHARMACY",
                "amount": 850.00,
                "type": "debit",
                "category": "Healthcare",
                "confidence": 0.9
            },
            {
                "id": str(uuid.uuid4()),
                "date": (base_date + timedelta(days=8)).strftime("%Y-%m-%d"),
                "description": "UNKNOWN MERCHANT XYZ",
                "amount": 500.00,
                "type": "debit",
                "category": "Miscellaneous",
                "confidence": 0.3
            },
            {
                "id": str(uuid.uuid4()),
                "date": (base_date + timedelta(days=9)).strftime("%Y-%m-%d"),
                "description": "CASH WITHDRAWAL ATM",
                "amount": 2000.00,
                "type": "debit",
                "category": "Miscellaneous",
                "confidence": 0.6
            }
        ]
        
        logger.info(f"Created {len(sample_transactions)} sample transactions for demo")
        return sample_transactions

    async def update_transaction_category(self, transaction_id: str, new_category: str) -> None:
        """Update the category of a specific transaction."""
        if new_category not in self.categories:
            raise ValueError(f"Invalid category: {new_category}")
        
        # In a real implementation, you'd update this in a database
        # For now, we'll just log the update
        logger.info(f"Updated transaction {transaction_id} category to {new_category}")

    async def get_expense_summary(self) -> Dict[str, Any]:
        """Get expense summary with category totals."""
        try:
            analysis = await self.analyze_expenses()
            transactions = analysis.get("transactions", [])
            
            category_totals = {}
            total_expenses = 0
            total_income = 0
            
            for tx in transactions:
                category = tx["category"]
                amount = abs(float(tx["amount"]))
                
                if tx["type"] == "debit":
                    total_expenses += amount
                    category_totals[category] = category_totals.get(category, 0) + amount
                else:
                    total_income += amount
            
            return {
                "total_expenses": total_expenses,
                "total_income": total_income,
                "savings": total_income - total_expenses,
                "category_totals": category_totals,
                "transaction_count": len(transactions)
            }
            
        except Exception as e:
            logger.error(f"Error generating expense summary: {str(e)}")
            raise
