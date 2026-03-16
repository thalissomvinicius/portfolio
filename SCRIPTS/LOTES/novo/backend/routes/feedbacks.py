from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
import uuid

router = APIRouter()

DATA_FILE = os.path.join("data", "feedbacks.json")

# Ensure data directory exists
os.makedirs("data", exist_ok=True)
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

class Feedback(BaseModel):
    id: Optional[str] = None
    autor: str
    mensagem: str
    data: Optional[str] = None
    tipo: str = "Sugestão"

def load_feedbacks():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_feedbacks(feedbacks):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, ensure_ascii=False, indent=2)

@router.get("/feedbacks", response_model=List[Feedback])
async def get_feedbacks():
    return load_feedbacks()

@router.post("/feedbacks")
async def create_feedback(feedback: Feedback):
    try:
        feedbacks = load_feedbacks()
        
        novo_feedback = feedback.dict()
        novo_feedback["id"] = str(uuid.uuid4())
        novo_feedback["data"] = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        # Add to beginning of list
        feedbacks.insert(0, novo_feedback)
        save_feedbacks(feedbacks)
            
        return {"message": "Feedback salvo com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/feedbacks/{feedback_id}")
async def delete_feedback(feedback_id: str):
    try:
        feedbacks = load_feedbacks()
        # Filtrar removendo o item com o ID correspondente
        novos_feedbacks = [f for f in feedbacks if f.get("id") != feedback_id]
        
        if len(novos_feedbacks) == len(feedbacks):
            raise HTTPException(status_code=404, detail="Feedback não encontrado")
            
        save_feedbacks(novos_feedbacks)
        return {"message": "Feedback removido com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/feedbacks/{feedback_id}")
async def update_feedback(feedback_id: str, feedback: Feedback):
    try:
        feedbacks = load_feedbacks()
        encontrado = False
        
        for i, item in enumerate(feedbacks):
            if item.get("id") == feedback_id:
                # Manter dados originais que não devem mudar (id, data se não for atualizar)
                feedbacks[i]["autor"] = feedback.autor
                feedbacks[i]["mensagem"] = feedback.mensagem
                feedbacks[i]["tipo"] = feedback.tipo
                encontrado = True
                break
        
        if not encontrado:
            raise HTTPException(status_code=404, detail="Feedback não encontrado")
            
        save_feedbacks(feedbacks)
        return {"message": "Feedback atualizado com sucesso"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
