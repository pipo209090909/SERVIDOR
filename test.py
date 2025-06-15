import mysql.connector
import os 


db_config={
    'user':'ABfoGMxni1GpTcX.root',
    'password': '4KYTJVK19PQOcK54',
    'host': 'gateway01.us-east-1.prod.aws.tidbcloud.com',
    'port': 4000,
    'database': 'test'
}


try: 
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT 2")

    result = cursor.fetchone()

    print("Conexio exitosa a la base de datos. Resultados de la consulta:", result)

except mysql.connector.Error as err:
    print("Error al conectarse a la base de datos:", err)


finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Conexion cerrada.")