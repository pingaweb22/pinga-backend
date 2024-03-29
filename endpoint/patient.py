from fastapi import APIRouter, Request, HTTPException
from sqlalchemy.sql.elements import Null
from setting import *
from utility import *
from pydantic import BaseModel
from datetime import date
from typing import Optional, List
from enum import Enum, IntEnum
import random
import uuid
from sms import *

router=APIRouter(tags=["patient"])

#validation
#1 user:type
class user_type(str, Enum):
    admin='admin'
    worker='worker'
    fellow="fellow"
    user="patient"
#2 gender
class gender(str, Enum):
   male='male'
   female='female'
   # gender_expansive='Gender expansive'
   # intersex='Intersex'
   # non_binary='Non binary'
   # trans_female='Trans female'
   # trans_male='Trans male'
   # prefer_not_to_say='Prefer not to say'
  

#scehema
#1 user:login
class user_login(BaseModel):
   mobile:str
   password:str
class user_login_google_auth(BaseModel):
   google_auth:str
   google_auth_token:str
   email:str

class user_login_mobile_otp_auth(BaseModel):
   mobile:str
   otp:Optional[str]=None

class verify_reset_login_otp(BaseModel):
   otp:str
   password:str
   email:Optional[str]=None
   mobile:Optional[str]=None
class reset_login_otp(BaseModel):
   email:Optional[str]=None
   mobile:Optional[str]=None

#2 user update:profile
class user_profile(BaseModel):
   name:str
   email:str
   gender:gender
   dob:date
   profile_pic_url:str
   height:str
   weight:str
   tnc_accepted:bool
#3 user:create
class user_create(BaseModel):
   name:str
   gender:str
   dob:str
   height:str
   mobile:str
   email:str
   weight:str
   bmi:str
   type:user_type
#4 extra:interest
class interest(BaseModel):
   interest:list

class user_filter(BaseModel):
   mobile:Optional[str]=None
   name:Optional[str]=None

#endpoint
#3 user profile update:self
@router.put("/patient/profile-update-self")
async def patient_update_profile_self(request:Request,payload:user_profile):
   #prework
   user_id = request.state.user_id
   payload=payload.dict()   
   #query set
   query="""update patient set name=:name,email=:email,gender=:gender,dob=:dob,profile_pic_url=:profile_pic_url,weight=:weight,height=:height,tnc_accepted=:tnc_accepted where id=:id"""
   values={"name":payload['name'],"email":payload['email'],"gender":payload['gender'],"dob":payload['dob'], "profile_pic_url":payload['profile_pic_url'],"weight":payload['weight'],"height":payload['height'],"tnc_accepted":payload["tnc_accepted"],"id":user_id}
   #query run
   response=await database_execute(query,values)
   if response["status"]=="false":
      raise HTTPException(status_code=400,detail=response)
   #finally
   return response




#4 user read:self
@router.get("/patient/read-self")
async def patient_read_self(request:Request):
   #prework
   user_id = request.state.user_id
   #query set
   query="""select * from patient where id=:id"""
   values={"id":user_id}
   #query run
   response=await database_fetch_all(query,values)
   if response["status"]=="false":
      raise HTTPException(status_code=400,detail=response)
   row=response["message"][0]
   if row['password']:
      row['password'] = "already set"
   else:
      row['password'] = "not set"
   #finally
   response=row
   return response


#4 user read:admin
@router.get("/patient/{user_id}/read-single-by-admin/")
async def patient_read_single_by_admin(request:Request, user_id:int):
   #prework
   admin_user_id = request.state.user_id
   # admin user check
   response = await is_admin(admin_user_id)
   if response['status'] != "true":
      raise HTTPException(status_code=401,detail=response)
   #query set
   query="""select * from "patient" where id=:id"""
   values={"id":user_id}
   #query run
   response=await database_fetch_all(query,values)
   if response["status"]=="false":
      raise HTTPException(status_code=400,detail=response)
   row=response["message"][0]
   row=response["message"][0]
   if row['password']:
      row['password'] = "already set"
   else:
      row['password'] = "not set"
   #finally
   response=row
   return response



#6 user read all: by admin
@router.get("/patient/read-all-by-admin/")
async def patient_read_all_by_admin(request:Request,offset:int):
   #prework
   user_id = request.state.user_id
   # admin user check
   response = await is_admin(user_id)
   if response['status'] != "true":
      raise HTTPException(status_code=401,detail=response)
   #query set
   query="""select * from patient order by created_at desc limit 10 offset :offset"""
   values={"offset":offset}
   #query run
   response=await database_fetch_all(query,values)
   if response["status"]=="false":
      raise HTTPException(status_code=400,detail=response)
   row=response["message"]
   #finally
   response=row
   return response


#7 user create: by admin
@router.post("/patient/create-by-admin")
async def patient_create_by_admin(request:Request,payload:user_create):
   #prework
   user_id = request.state.user_id
   payload=payload.dict()
   payload['password'] = '123456'
   password_hash=password_hash_create(payload['password'])
   # admin user check
   response = await is_admin(user_id)
   if response['status'] != "true":
      raise HTTPException(status_code=401,detail=response) 
   #query set
   query="""insert into patient (name,gender,dob,height,mobile,email,weight,data,password,type,created_by) values (:name,:gender,:dob,:height,:mobile,:email,:weight,:data,:password,:type,:created_by) returning *"""
   values={"name":payload['name'],"gender":payload['gender'],"dob":payload['dob'],"height":payload['height'],"mobile":payload['mobile'],"email":payload['email'],"weight":payload["weight"],"data":'{"bmi":"'+payload["bmi"]+'"}',"password":password_hash,"type":payload['type'],"created_by":user_id}
   #query run
   response=await database_execute(query,values)
   if response["status"]=="false":
      raise HTTPException(status_code=400,detail=response)
   #finally
   return response
   

#8 user read single by admin
@router.get("/patient/{id}")
async def patient_get_single(request:Request,id:int):
   #prework
   user_id=request.state.user_id
   #query set
   query="""select * from patient where id=:id"""
   values={"id":id}
   #query run
   response=await database_fetch_all(query,values)
   if response["status"]=="false":
      raise HTTPException(status_code=400,detail=response)
   row=response["message"]
   #finally
   response=row
   return response 
  

  
#9 user search by mobile: by admin
@router.get("/patient/filter/{search}")
async def patient_filter(request:Request,search:str):
   #prework
   user_id=request.state.user_id
   #query set
   query="""select id,mobile,name,email,gender,dob ,profile_pic_url,weight,height,created_at ,is_active ,created_by , type,role from patient where is_active='true' """
   
   query = query+" and mobile like '%"+search+"%' or name like '%"+search+"%'"

   values={}
   print(query)
   #query run
   response=await database_fetch_all(query,values)
   if response["status"]=="false":
      raise HTTPException(status_code=400,detail=response)
   row=response["message"]
   # if row['password']:
   #    row['password'] = "already set"
   # else:
   #    row['password'] = "not set"
   #finally
   response=row
   return response



#10 user create: by self
@router.post("/patient/signup-normal")
async def public_user_signup_normal(request:Request,payload:user_login):
   #prework
   payload=payload.dict()
   payload["mobile"]=payload["mobile"].lower()
   payload["password"]=hashlib.md5(payload['password'].encode()).hexdigest()
   #check null value
   if '' in list(payload.values()) or any(' ' in ele for ele in list(payload.values())):
      raise HTTPException(status_code=400,detail="null or white space not allowed")
   
   #query set
   query="""insert into patient (created_by,type,mobile,password) values (:created_by,:type,:mobile,:password) returning *;"""
   values={"created_by":1,"type":"normal","mobile":payload['mobile'],"password":payload['password']}
   #query run
   response=await database_execute(query,values)
   #query fail
   if response["status"]=="false":
      raise HTTPException(status_code=400,detail=response)
   #finally
   response["next"]="login-non-admin"
   return response
   


#10 user create: by self
@router.post("/patient/signup-google")
async def public_user_signup_google(request:Request,payload:user_login_google_auth):
   #prework
   payload=payload.dict()

   # check google verification
   google_auth_verify = await google_auth_verification(payload['google_auth_token'],payload['email'])
   if google_auth_verify['status'] == 'false':
      raise HTTPException(status_code=400,detail="Email Not Match!")

   #check null value
   if '' in list(payload.values()) or any(' ' in ele for ele in list(payload.values())):
      raise HTTPException(status_code=400,detail="null or white space not allowed")
   mobile = null
   password = str(random.randrange(20, 50, 3)) + "test"
   print(mobile)
   #query set
   query="""insert into patient (created_by,type,mobile,password,google_auth,email) values (:created_by,:type,:mobile,:password,:google_auth,:email) returning *;"""
   values={"created_by":1,"type":"normal","mobile":mobile,"password":password,"google_auth":payload['google_auth'],"email":payload['email']}
   #query run
   response=await database_execute(query,values)
   #query fail
   if response["status"]=="false":
      raise HTTPException(status_code=400,detail=response)
   #finally
   response["next"]="login-non-admin-google-auth"
   return response


@router.post("/patient/create-login-otp")
async def user_login_otp_create(request:Request,payload:user_login_mobile_otp_auth):
   #prework
   payload=payload.dict()
   
   new_otp = str(random.randint(1111,9999))
   sms_text = 'PINGA login OTP is '+new_otp
      
   try:
      sms_response=await sendSMS(payload['mobile'], sms_text)
      sms_response=dict(json.loads(sms_response.decode()))
      if sms_response['status'] != 'success':
         response = {"status":"failed", "message":"otp not sent!"}
         raise HTTPException(status_code=400,detail=response)
   except:
      response = {"status":"false", "message":"otp not sent!"}
      raise HTTPException(status_code=400,detail=response)
   
   #query set
   query="""insert into otp (mobile,otp) values (:mobile,:otp);"""
   values={"mobile":payload['mobile'],"otp":new_otp}
   #query run
   response=await database_execute(query,values)
   #query fail
   if response["status"]=="false":
      raise HTTPException(status_code=400,detail=response)
   #finally
   response = {"status":"success", "message":"otp sent!","next":"login-mobile-otp"}
   return response
   
   


@router.post("/patient/create-password-reset-otp")
async def user_password_reset_create(request:Request,payload:reset_login_otp):
   #prework
   payload=payload.dict()
   
   new_otp = str(random.randint(1111,9999))
   sms_text = "OTP for PINGA password reset is "+new_otp+". Do not share it with anyone."
   try:
      sms_response=await sendSMS(payload['mobile'], sms_text)
      sms_response=dict(json.loads(sms_response.decode()))
      if sms_response['status'] != 'success':
         response = {"status":"failed", "message":"otp not sent!"}
         raise HTTPException(status_code=400,detail=response)
      #query set
      query="""insert into otp (mobile,email,otp) values (:mobile,:email,:otp);"""
      values={"mobile":payload['mobile'],"email":payload['email'],"otp":new_otp}
      #query run
      response=await database_execute(query,values)
      #query fail
      if response["status"]=="false":
         raise HTTPException(status_code=400,detail=response)
      #finally
      response = {"status":"success", "message":"otp sent!","next":"verify-password-reset-otp"}
      return response
   except:
      response = {"status":"false", "message":"otp not sent!"}
      raise HTTPException(status_code=400,detail=response)
   


@router.post("/patient/verify-password-reset-otp")
async def user_password_reset_create(request:Request,payload:verify_reset_login_otp):
   #prework
   payload=payload.dict()
   #query set
   query="""select  AGE(NOW(),created_at)::text AS difference  from otp where mobile=:mobile and otp=:otp order by id desc limit 1"""
   values={"mobile":payload['mobile'],"otp":payload['otp']}
   
   #query run
   response=await database_fetch_all(query,values)

   if response["message"] == []:
      response = {"status":"false", "message":"otp not verified!"}
      raise HTTPException(status_code=400,detail=response)
   
   diffrence = response["message"][0]['difference'].split(':')
   if int(diffrence[1])>=50:
      response = {"status":"false", "message":"otp expired!"}
      raise HTTPException(status_code=400,detail=response)

   password_hash=password_hash_create(payload['password'])
   query="""update patient set password=:password where mobile=:mobile"""
   values={"password":password_hash,"mobile":payload['mobile']}
   #query run
   response=await database_execute(query,values)
   if response["status"]=="false":
      raise HTTPException(status_code=400,detail=response)
   #finally
   response = {"status":"success", "message":"password reset succesfully!"}
   return response
