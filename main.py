from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware



db_config={
    'user':'ABfoGMxni1GpTcX.root',
    'password': '4KYTJVK19PQOcK54',
    'host': 'gateway01.us-east-1.prod.aws.tidbcloud.com',
    'port': 4000,
    'database': 'test'
}

class LoginRequest(BaseModel):
    email: str
    password : str

class RegisterRequest(BaseModel):
    email: str
    password : str

class UpdateRequest(BaseModel):
    current_email: str
    new_email: str
    new_password : str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    connection= mysql.connector.connect(**db_config)
    return connection

@app.post("/login")
def login(login_request: LoginRequest):
    print(f"Recieved email: {login_request.email}")
    print(f"Recieved password: {login_request.password}")

    connection= get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = "SELECT * FROM login where email = %s AND password = %s"
    cursor.execute(query, (login_request.email, login_request.password))    
    user=cursor.fetchone()
    cursor.close()
    connection.close()

    if user:
        return{"message": "Login successful", "user":user}
    
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/register")
def register(register_request: RegisterRequest):
    print(f"Register attemp with email: {register_request.email}")

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    check_query= "SELECT * FROM login WHERE email = %s"
    cursor.execute(check_query,(register_request.email,))
    existing_user=cursor.fetchone()

    if existing_user:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=800, detail="Email already registered")
    
    insert_query = "INSERT INTO login(email, password) VALUES (%s, %s)"
    cursor.execute(insert_query,(register_request.email, register_request.password))
    connection.commit()

    cursor.execute(check_query,(register_request.email))
    new_user=cursor.fetchone

    cursor.close()
    connection.close()

    if new_user:
        return {"message": "Registration successful", "user": new_user}
    else:
        raise HTTPException(status_code=500, detail="Registration failed")
    

@app.delete("/delete_user/{email}")
def delete_user(email:str):
    print(f"Delete attempt for email: {email}")

    connection = get_db_connection()
    cursor= connection.cursor(dictionary=True)

    check_query= "SELECT * FROM  login WHERE email = %s"
    cursor.execute(check_query, (email,))
    existing_user = cursor.fetchone()

    if not existing_user:
        cursor.close()
        connection.close()
        raise HTTPException(status_code=404, detail="User not found")
    

    delete_query = "DELETE FROM login WHERE email = %s"
    cursor.execute(delete_query, (email,))
    connection.commit()

    affected_rows = cursor.rowcount

    cursor.close()
    connection.close()

    if affected_rows > 0:
        return {"message": f"User {email} deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Delete operation failed")


@app.get("/users")
def get_all_users():
    connection= get_db_connection()
    cursor=connection.cursor(dictionary=True)

    try:
        query="SELECT * FROM login"
        cursor.execute(query)
        users=cursor.fetchall()

        return {"users":users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()
        connection.close()


@app.put("/update_user")
def update_user(update_request: UpdateRequest):
    connection = get_db_connection()
    cursor=connection.cursor(dictionary=True)

    try:
        check_query="SELECT * FROM login WHERE email = %s"
        cursor.execute(check_query, (update_request.current_email,))
        existing_user = cursor.fetchone()

        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if update_request.current_email != update_request.new_email:
            cursor.execute(check_query, (update_request.new_email,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="Email in used")

        update_query = "UPDATE login SET email = %s, password = %s WHERE email = %s"
        cursor.execute(update_query, (
            update_request.new_email,
            update_request.new_password,
            update_request.current_email
        ))
        connection.commit()

        return {"message": "Usuario actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualiizar: {str(e)}")
    finally:
        cursor.close()
        connection.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI TiDB Gateaway"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
