from fastapi import APIRouter, Request, HTTPException
from setting import *
from utility import *
from pydantic import BaseModel
from typing import Optional
from datetime import date
from enum import Enum, IntEnum
import uuid

router=APIRouter(tags=["consult"])


#validation
#1 status:type
class status_type(str, Enum):
    open='open'
    succesfully_closed='succesfully_closed'
    unsuccesfully_closed ='unsuccesfully_closed'

#scehema
#1 followup
class followup(BaseModel):
    patient_id:int
    created_by:Optional[int]=0
    status:status_type
    next_followup_at:Optional[datetime] = None
    closed_at:Optional[date] = None
    data:dict


#scehema
#1 consult
class consult(BaseModel):
    patient_id:int
    created_by:Optional[int]=0
    why_reason:Optional[str]=None
    symtoms:Optional[str]=None
    general:Optional[str]=None


#scehema
# meeting
class meeting(BaseModel):
    doctor_id:int
    patient_id:int
    meeting_link:str
    payment_link:str
    date_time:datetime
    created_by:Optional[int]=0
    type:Optional[str]=None
    data:dict


# meeting
class meeting_filter(BaseModel):
    doctor_id:Optional[int]=0
    patient_id:Optional[int]=0
    date_time:Optional[datetime]
    created_by:Optional[int]=0
    type:Optional[str]=None


   


#1 followup create
@router.post("/followup")
async def followup_create(request:Request,payload:followup):
    #prework
    user_id = request.state.user_id
    payload=payload.dict()
    #admin user check
    response = await is_admin(user_id)
    if response['status'] != "true":
        raise HTTPException(status_code=400,detail=response)
    
    #query set
    query="""insert into followup (created_by,patient_id,status,next_followup_at,closed_at,data)
        values (:created_by,:patient_id,:status,:next_followup_at,:closed_at,:data)
        returning *"""
    values={"created_by":user_id,"patient_id":payload['patient_id'],"status":payload['status'],"next_followup_at":payload['next_followup_at'],"closed_at":payload['closed_at'],"data":json.dumps(payload['data'])}
    
    #query run
    response = await database_execute(query,values)
    if response["status"]=="false":
        raise HTTPException(status_code=400,detail=response)

    return response


#2 followup filter
@router.post("/followup/filter")
async def followup_filter(request:Request,payload:followup):
    #query set
    query="select * from followup where is_active='true'"
    if payload['patient_id']:
        query = query + " and patient_id=:patient_id"
    if payload['closed_at']:
        query = query + " and closed_at=:closed_at"
    if payload['next_followup_at']:
        query = query + " and next_followup_at=:next_followup_at"
    if payload['status']:
        query = query + " and status=:status"
    if payload['created_by']:
        query = query + " and created_by=:created_by"
        
    values={"created_by":payload['created_by'],"patient_id":payload['patient_id'],"status":payload['status'],"next_followup_at":payload['next_followup_at'],"closed_at":payload['closed_at']}
    #query run
    response=await database_fetch_all(query,values)
    if response["status"]=="false":
        raise HTTPException(status_code=400,detail=response)
    row=response["message"]
    #finally
    response=row
    return response




#----------------------------------------------------------------------------------------


#1 consult create
@router.post("/consult")
async def consult_create(request:Request,payload:consult):
    #prework
    user_id = request.state.user_id
    payload=payload.dict()
    #admin user check
    response = await is_admin(user_id)
    if response['status'] != "true":
        raise HTTPException(status_code=400,detail=response)
    payload['data'] = json.dumps({"symtoms":payload['symtoms'],"why_reason":payload['why_reason'],"general":payload['general']})
    #query set
    query="""insert into consult (created_by,patient_id,data)
        values (:created_by,:patient_id,:data)
        returning *"""
    values={"created_by":user_id,"patient_id":payload['patient_id'],"data":payload['data']}
    
    #query run
    response = await database_execute(query,values)
    if response["status"]=="false":
        raise HTTPException(status_code=400,detail=response)

    return response


#2 consult filter
@router.post("/consult/filter")
async def followup_filter(request:Request,payload:consult):
    #query set
    query="select * from consult where is_active='true'"
    if payload['patient_id']:
        query = query + " and patient_id=:patient_id"
    if payload['created_by']:
        query = query + " and created_by=:created_by"
        
    values={"created_by":payload['created_by'],"patient_id":payload['patient_id']}
    #query run
    response=await database_fetch_all(query,values)
    if response["status"]=="false":
        raise HTTPException(status_code=400,detail=response)
    row=response["message"]
    #finally
    response=row
    return response



#----------------------------------------------------------------------------------------


#1 meeting create
@router.post("/meeting")
async def meeting_create(request:Request,payload:meeting):
    #prework
    user_id = request.state.user_id
    payload=payload.dict()
    #admin user check
    response = await is_admin(user_id)
    if response['status'] != "true":
        raise HTTPException(status_code=400,detail=response)
    
    #query set
    query="""insert into meeting (created_by, patient_id, doctor_id, type, meeting_link,        payment_link, date_time, data )
    values (:created_by, :patient_id, :doctor_id, :type, :meeting_link, :payment_link, :date_time, :data )
    returning *"""
    values={"created_by":user_id,"patient_id":payload['patient_id'],"doctor_id":payload['doctor_id'],"type":payload['type'],"meeting_link":payload['meeting_link'],"payment_link":payload['payment_link'],"date_time":payload['date_time'],"data":json.dumps(payload['data'])}
    
    #query run
    response = await database_execute(query,values)
    if response["status"]=="false":
        raise HTTPException(status_code=400,detail=response)

    return response


#2 meeting filter
@router.post("/meeting/filter")
async def meeting_filter(request:Request,payload:meeting_filter):
    #query set
    query="select * from meeting where is_active='true'"
    if payload['patient_id']:
        query = query + " and patient_id=:patient_id"
    if payload['created_by']:
        query = query + " and created_by=:created_by"
    if payload['doctor_id']:
        query = query + " and doctor_id=:doctor_id"
        
    values={"created_by":payload['created_by'],"patient_id":payload['patient_id'],"doctor_id":payload['doctor_id']}
    #query run
    response=await database_fetch_all(query,values)
    if response["status"]=="false":
        raise HTTPException(status_code=400,detail=response)
    row=response["message"]
    #finally
    response=row
    return response


