from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from mysql_connection import get_connection
from mysql.connector import Error
from datetime import datetime
import boto3
from config import Config

class PostingResource(Resource) :
    # 포스팅 작성 API
    @jwt_required()
    def post(slef) :

        user_id = get_jwt_identity()
        
        # from=data
        # photo : file
        # content : text

        # 둘중 하나라도 없으면 안됨 세이프 코딩
        if 'photo' not in request.files or 'content' not in request.form :
            return {'error' : '데이터를 정확히 보내세요'}, 400
        
        file = request.files['photo']
        content = request.form['content']

        # 이미지 데이터만 받게 세이프 코딩
        if 'image' not in file.content_type :
            return {'error' : '이미지 파일이 아닙니다.'}

        # 사진명을 유니크하게 변경해서 S3에 업로드
        current_time = datetime.now()
        new_file_name = current_time.isoformat().replace(':', '_') + '.' + file.content_type.split('/')[-1]
        file.filename = new_file_name
        client =  boto3.client('s3', aws_access_key_id= Config.ACCESS_KEY, aws_secret_access_key= Config.SECRET_ACCESS)

        try :
            client.upload_fileobj(file, Config.S3_BUCKET, new_file_name, ExtraArgs= {'ACL' : 'public-read', 'ContentType' : file.content_type})
        
        except Exception as e :
            return {"error" : str(e)}, 500

        # 저장된 사진의 imgUrl
        imgUrl = Config.S3_LOCATION + new_file_name

        # DB에 저장
        try :
            connection = get_connection()

            query = '''insert into content
                    (userId, content, imgUrl)
                    values (%s, %s, %s);'''

            record = (user_id, content, imgUrl)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success"}, 200

    # 전체 포스팅 리스트 가져오는 API
    def get(slef) :
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select *
                    from content
                    limit ''' + offset + ''' , ''' + limit + ''' ; '''
                    
            cursor = connection.cursor(dictionary= True)

            cursor.execute(query, )

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['createdAt'] = row['createdAt'].isoformat()
                result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success", "items" : result_list, "count" : len(result_list)}, 200

class MyPostingResource(Resource) :
    # 내 포스팅 리스트만 가져오는 API
    @jwt_required()
    def get(slef) :
        user_id = get_jwt_identity()
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select *
                    from content
                    where userId = %s
                    limit ''' + offset + ''' , ''' + limit + ''' ; '''

            record = (user_id, )

            cursor = connection.cursor(dictionary= True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['createdAt'] = row['createdAt'].isoformat()
                result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success", "items" : result_list, "count" : len(result_list)}, 200

class ModifyPostingResource(Resource) :
    # 포스팅 수정 API
    @jwt_required()
    def post(slef, content_id) :

        user_id = get_jwt_identity()
        
        # from=data
        # photo : file
        # content : text

        # 둘중 하나라도 없으면 안됨 세이프 코딩
        if 'photo' not in request.files or 'content' not in request.form :
            return {'error' : '데이터를 정확히 보내세요'}, 400
        
        file = request.files['photo']
        content = request.form['content']

        # 이미지 데이터만 받게 세이프 코딩
        if 'image' not in file.content_type :
            return {'error' : '이미지 파일이 아닙니다.'}

        # 사진명을 유니크하게 변경해서 S3에 업로드
        current_time = datetime.now()
        new_file_name = current_time.isoformat().replace(':', '_') + '.' + file.content_type.split('/')[-1]
        file.filename = new_file_name
        client =  boto3.client('s3', aws_access_key_id= Config.ACCESS_KEY, aws_secret_access_key= Config.SECRET_ACCESS)

        try :
            client.upload_fileobj(file, Config.S3_BUCKET, new_file_name, ExtraArgs= {'ACL' : 'public-read', 'ContentType' : file.content_type})
        
        except Exception as e :
            return {"error" : str(e)}, 500

        # 저장된 사진의 imgUrl
        imgUrl = Config.S3_LOCATION + new_file_name

        # DB에 저장되어있는 포스팅정보 수정
        try :
            connection = get_connection()

            query = '''update content
                    set
                    content = %s,
                    imgUrl = %s
                    where id = %s and userId = %s;'''

            record = (content, imgUrl, content_id, user_id)

            cursor = connection.cursor()

            cursor.execute(query, record)

            connection.commit()

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success"}, 200

    # 포스팅 삭제 API
    @jwt_required()
    def delete(slef, content_id) :

        user_id = get_jwt_identity()

        try :
            connection = get_connection()

            query = ''' delete from content
                    where id = %s and userId = %s ; '''
            
            record = (content_id, user_id)

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

class followeePostingResource(Resource) :
    # 친구들 포스팅 리스트만 가져오는 API
    @jwt_required()
    def get(slef) :
        user_id = get_jwt_identity()
        offset = request.args.get('offset')
        limit = request.args.get('limit')

        try :
            connection = get_connection()

            query = '''select c.id, c.imgUrl, c.content, u.id, u.email, c.updatedAt
                    from follow f
                    left join content c on f.followeeId = c.userId
                    left join user u on f.followeeId = u.id
                    where f.followerId = %s
                    limit ''' + offset + ''' , ''' + limit + ''' ; '''

            record = (user_id, )

            cursor = connection.cursor(dictionary= True)

            cursor.execute(query, record)

            result_list = cursor.fetchall()

            i = 0
            for row in result_list :
                result_list[i]['updatedAt'] = row['updatedAt'].isoformat()
                i = i + 1

            cursor.close()
            connection.close()

        except Error as e :
            print(e)
            cursor.close()
            connection.close()

            return {"error" : str(e)}, 500

        return {"result" : "success", "items" : result_list, "count" : len(result_list)}, 200
