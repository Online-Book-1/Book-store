# routes/user_routes.py
from fastapi import APIRouter, Depends, HTTPException
from schemas.user import UserCreateSchema, UserCreateResponseSchema, UserLoginSchema, VerifyOtpSchema, ResendOtpSchema, ForgotPasswordSchema
from services.user_manager import UserManager
from repositories.user_repository import UserRepository
from database import get_db
from schemas.token import Token
from config import settings
from redis import Redis
from kafka import KafkaProducer
from utils.hashing import get_pass_hash
import json, random
import traceback
import string
import secrets
from schemas.token import Token, RefreshTokenSchema

router = APIRouter()

# ── Redis Connection ──
redis_client = Redis(
    host=settings.REDIS_SERVERS,
    port=int(settings.REDIS_PORT),
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5,
    retry_on_timeout=True
)

# ── Kafka Producer ──
# Update your Kafka Producer initialization in user_routes.py:

producer = KafkaProducer(
    bootstrap_servers=[settings.KAFKA_BOOTSTRAP_SERVERS],
    value_serializer=lambda x: json.dumps(x).encode('utf-8'),
    # --- ADD THESE THREE LINES ---
    max_block_ms=2000,           # Don't hang for more than 2 seconds
    request_timeout_ms=2000,     # Time to wait for a response
    metadata_max_age_ms=30000    # How often to refresh partition info
)

def get_user_manager(db=Depends(get_db)) -> UserManager:
    user_repo = UserRepository(db)
    return UserManager(user_repo)


@router.get("/")
def root():
    return {"status": "Connected"}


# ── STEP 1: Register → store in Redis, send OTP ──
@router.post("/auth/register")
def create_user(user_data: UserCreateSchema, user_manager: UserManager = Depends(get_user_manager)):
    try:
        existing = user_manager.get_user_by_email(user_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        otp = str(random.randint(100000, 999999))
        print(f"OTP:{otp}", flush=True)

        temp_data = {
            "otp":      otp,
            "username": user_data.username,
            "email":    user_data.email,
            "password": get_pass_hash(user_data.password)
        }
        redis_client.set(user_data.email, json.dumps(temp_data), ex=300)

        # ← Kafka wrapped separately — failure won't crash registration
        try:
            producer.send('user_events', value={
                "event_type": "SEND_OTP",
                "data": {
                    "email":    user_data.email,
                    "username": user_data.username,
                    "otp":      otp
                }
            })
        except Exception as kafka_err:
            print(f"⚠️ Kafka unavailable: {kafka_err}", flush=True)
            # continue — OTP is in Redis, user can still verify

        return {"message": "OTP sent successfully. Please check your email."}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# ── RESEND OTP ──
@router.post("/auth/resend-otp")
def resend_otp(payload: ResendOtpSchema):
    # check if user data exists in Redis
    stored_json = redis_client.get(payload.email)
    if not stored_json:
        raise HTTPException(
            status_code=400,
            detail="No pending registration found. Please register again."
        )

    stored_data = json.loads(stored_json)

    # generate new OTP
    new_otp = str(random.randint(100000, 999999))
    print(f"RESEND OTP: {new_otp}", flush=True)

    # update OTP in Redis — keep same user data, reset expiry
    stored_data["otp"] = new_otp
    redis_client.set(payload.email, json.dumps(stored_data), ex=300)

    # push to Kafka
    producer.send('user_events', value={
        "event_type": "SEND_OTP",
        "data": {
            "email":    payload.email,
            "username": stored_data["username"],
            "otp":      new_otp
        }
    })

    return {"message": "OTP resent successfully. Please check your email."}

# ── STEP 2: Verify OTP → create user in DB ──
@router.post("/auth/verify-otp", response_model=UserCreateResponseSchema)
def verify_otp(payload: VerifyOtpSchema, user_manager: UserManager = Depends(get_user_manager)):
    # get temp data from Redis
    stored_json = redis_client.get(payload.email)
    if not stored_json:
        raise HTTPException(status_code=400, detail="OTP expired or invalid")

    stored_data = json.loads(stored_json)

    # verify OTP
    if stored_data["otp"] != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # create user in DB
    user = user_manager.create_verified_user(
        username      = stored_data["username"],
        email         = stored_data["email"],
        hashed_password = stored_data["password"]  # already hashed
    )

    # delete from Redis
    redis_client.delete(payload.email)

    return user


# ── LOGIN ──
@router.post("/auth/login", response_model=Token)
def login(login_data: UserLoginSchema, user_manager: UserManager = Depends(get_user_manager)):
    try:
        token = user_manager.login(login_data.email, login_data.password)
        return token
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=401, detail=str(e))



@router.post("/auth/refresh", response_model=Token)
def refresh_token(payload: RefreshTokenSchema, user_manager: UserManager = Depends(get_user_manager)):
    try:
        return user_manager.refresh_access_token(payload.refresh_token)
    except PermissionError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/auth/forgot_password")
def forgot_password(forgot_details: ForgotPasswordSchema,user_manager: UserManager = Depends(get_user_manager)):
    try:
        existing = user_manager.get_user_by_email(forgot_details.email)
        if not existing:
            raise HTTPException(status_code=404, detail="User not found")

        otp = str(random.randint(100000, 999999))
        print(f"OTP:{otp}", flush=True)

         # Save flattened data
        temp_data = {
        "otp": otp,
         "email": forgot_details.email,
         "username": existing.username
         
         }
        redis_client.set(forgot_details.email, json.dumps(temp_data), ex=300)

        # ← Kafka wrapped separately — failure won't crash registration
        try:
            kafka_payload = {
             "event_type": "FORGOT_PASSWORD",
             "data": temp_data # Router expects 'data' key
           }
            producer.send('user_events', value=kafka_payload)

        except Exception as kafka_err:
            print(f"⚠️ Kafka unavailable: {kafka_err}", flush=True)
            # continue — OTP is in Redis, user can still verify

        return {"message": "OTP sent successfully. Please check your email."}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

      

@router.post("/auth/forgot/verify-otp")
def verify_otp(payload: VerifyOtpSchema,user_manager: UserManager = Depends(get_user_manager)):
    stored_data_json = redis_client.get(payload.email)
    
    if not stored_data_json:
        raise HTTPException(status_code=400, detail="Invalid OTP or Time Expired")
    
    stored_data = json.loads(stored_data_json)
    print(stored_data)

    if stored_data["otp"] != payload.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    
    
    # Generate random password
    alphabet = string.ascii_letters + string.digits
    new_password = ''.join(secrets.choice(alphabet) for i in range(12))
    print(f'New Password is: {new_password}',flush=True)
    
    # FIXED: Update user password in database
    existing = user_manager.get_user_by_email(payload.email)
     
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing.password = get_pass_hash(new_password)
     
    user_manager.save(existing)
     
    
     
     
    redis_client.delete(payload.email)

    # --- FIX 3: Match Topic and Event Type to Router ---
    event_data = {
        "event_type": "NEW_PASSWORD", # Matches Router TEMPLATE_MAP
        "data": {
            "username":  stored_data['username'],
            "email":  stored_data['email'],
            "new_password":new_password
             
        }
    }
    
    # Send to 'user.events' (Router listens here), not 'platform_notifications'
    producer.send('user_events', value=event_data)
     

    return {"Status": "Password updated and Sent"}


   
      