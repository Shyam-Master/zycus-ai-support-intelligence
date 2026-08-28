import logging
from fastapi import FastAPI, HTTPException
from app.schemas.triage import TriageRequest, TriageResponse
from app.schemas.tam import TamBriefResponse
from app.services.triage_service import TriageService
from app.services.tam_service import TamService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title='Zycus AI Support')

triage_svc = TriageService()
tam_svc = TamService()

@app.get('/')
async def root():
    return {
        "message": "Zycus AI Support Intelligence API",
        "status": "running"
    }

@app.get('/health')
async def health_check():
    return {"status": "healthy"}

@app.post('/triage', response_model=TriageResponse)
async def triage_ticket(request: TriageRequest):
    try:
        return triage_svc.triage_ticket(request)
    except ValueError as ve:
        logger.warning(f'Validation Error: {ve}')
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f'Error triaging ticket: {e}')
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/account/{account_id}/brief', response_model=TamBriefResponse)
async def get_tam_brief(account_id: str):
    try:
        return tam_svc.generate_brief(account_id)
    except ValueError as ve:
        logger.warning(f'Not Found: {ve}')
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error(f'Error generating brief: {e}')
        raise HTTPException(status_code=500, detail=str(e))
