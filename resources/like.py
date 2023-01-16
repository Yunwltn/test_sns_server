from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error

class likeResource(Resource) :
    @jwt_required()
    def post(self, content_id) : 
    
        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = '''insert into test_sns_db.like
                    (userId, contentId)
                    values(%s, %s);'''

            record = ( user_id, content_id )

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"result" : "fail", "error" : str(e)}, 500

        return {"result" : "success"}, 200

    @jwt_required()
    def delete(self, content_id) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = ''' delete from test_sns_db.like
                    where userId = %s and contentId = %s ; '''
            
            record = (user_id, content_id)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"result" : "fail", "error" : str(e)}, 500

        return {"result" : "success"}, 200