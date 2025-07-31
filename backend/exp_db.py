import pymysql

from datetime import datetime


# To change datatime %YY-%MM-%DD
def convert_date(date_str):
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
    except:
        return date_str  
    
    

# query for create the job by provider
def create_job(cursor, data):
    try:
        # Fetch job provider name
        query = "SELECT name AS provider_name FROM job_provider_profile WHERE provider_id = %s"
        cursor.execute(query, (data["provider_id"],))
        result = cursor.fetchone()
        print("Provider name fetched:", result)

        sql = """
        INSERT INTO job (
            provider_id,
            title,
            job_description,
            experience_level,
            job_type,
            category,
            location,
            application_deadline,
            created_by
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        bindData = [
            data['provider_id'],
            data['title'],
            data['job_description'],
            data['experience'],
            data['job_type'],
            data['category'],
            data['location'],
            data['application_deadline'],
            result['provider_name']
        ]

        cursor.execute(sql, bindData)
        return cursor.lastrowid
    except pymysql.IntegrityError as e:
        raise e
    except Exception as e:
        raise e




def select_all_tasks(cursor):
    print("Selecting all tasks")
    try:
        sql = "SELECT * FROM job"
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        raise e
    
def job_provider_profile(cursor,data):
    print("Creating job provider profile with data:", data)
    try:
        sql = """
        INSERT INTO job_provider_profile (company_id, name, email, password_hash, phone)
        VALUES (%s, %s, %s, %s, %s)
        """
        bindData = [
            data['company'],
            data['name'],
            data['email'],
            data['password'],
            data['phone']
        ]
        cursor.execute(sql, bindData)
        return cursor.lastrowid
    except pymysql.IntegrityError as e:
        raise e
    except Exception as e:
        raise e


