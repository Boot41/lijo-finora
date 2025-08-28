from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from usecases.expense_usecase import ExpenseUseCase
from middleware.auth import get_current_user_optional

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/expenses", tags=["expenses"])

class CategoryUpdateRequest(BaseModel):
    category: str

@router.get("/analyze")
async def analyze_expenses(current_user=Depends(get_current_user_optional)) -> Dict[str, Any]:
    """
    Analyze uploaded documents for expense transactions and categorize them using AI.
    """
    try:
        expense_usecase = ExpenseUseCase()
        result = await expense_usecase.analyze_expenses()
        return result
    except Exception as e:
        logger.error(f"Error analyzing expenses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing expenses: {str(e)}")

@router.put("/transactions/{transaction_id}/category")
async def update_transaction_category(
    transaction_id: str, 
    request: CategoryUpdateRequest,
    current_user=Depends(get_current_user_optional)
) -> Dict[str, str]:
    """
    Update the category of a specific transaction.
    """
    try:
        expense_usecase = ExpenseUseCase()
        await expense_usecase.update_transaction_category(transaction_id, request.category)
        return {"message": "Transaction category updated successfully"}
    except Exception as e:
        logger.error(f"Error updating transaction category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating transaction category: {str(e)}")

@router.get("/summary")
async def get_expense_summary(current_user=Depends(get_current_user_optional)) -> Dict[str, Any]:
    """
    Get expense summary with category totals and insights.
    """
    try:
        expense_usecase = ExpenseUseCase()
        result = await expense_usecase.get_expense_summary()
        return result
    except Exception as e:
        logger.error(f"Error getting expense summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting expense summary: {str(e)}")

@router.get("/debug/chunks")
async def debug_chunks(current_user=Depends(get_current_user_optional)) -> Dict[str, Any]:
    """
    Debug endpoint to check document chunks retrieval.
    """
    try:
        expense_usecase = ExpenseUseCase()
        chunks = await expense_usecase._get_document_chunks()
        candidates = expense_usecase._extract_transaction_candidates(chunks)
        
        return {
            "total_chunks": len(chunks),
            "transaction_candidates": len(candidates),
            "sample_chunks": chunks[:3] if chunks else [],
            "sample_candidates": candidates[:3] if candidates else []
        }
    except Exception as e:
        logger.error(f"Error in debug chunks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in debug chunks: {str(e)}")
