from flask import Flask, request,jsonify, url_for
from flask_cors import CORS
import pymysql
import json
from exp_db import create_job 
from flask import jsonify
import os
from werkzeug.utils import secure_filename
import mysql.connector

from core.extractor import extract_pdf_text
from core.clean_json import clean_json_response
from llm.gemini_llm import call_gemini


from pathlib import Path

import hashlib
import uuid
import re
import secrets
import random
import string


app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500"]) # IP of Device A (frontend)

UPLOAD_FOLDER = 'static/resumes'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility: Database connection
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        db='job_portal',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def response(
    statusCode=200,
    message="Data fetched successfully!",
    result={},
    success=True,
    error="",
):
    if not success:
        print("Error:", error)
    return jsonify({
        "statusCode": statusCode,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        },
        "body": {
                "success": success,
                "message": message,
                "result": result,
                "status": statusCode,
            },

    })


# Create Job by Job Provider
@app.route('/createJob/<int:provider_id>', methods=['POST'])
def job(provider_id):
    data = request.get_json()
    provider_id = data["provider_id"]
    print("Received data for job creation:", data)
    print("Provider ID:", provider_id)
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        task_id = create_job(cursor, data)
        conn.commit()
        return response(message="Job added", result={"id": task_id})
    except KeyError as e:
        conn.rollback()
        return response(
            statusCode=422,
            message=f"Unprocessable Entity: {str(e)} not found",
            success=False,
        )
    except pymysql.IntegrityError as e:
        conn.rollback()
        if e.args[0] == 1062:
            statusCode = 409
            message = "Duplicate entry!"
        elif e.args[0] == 1452:
            statusCode = 409
            message = "Foreign key constraint fails!"
        else:
            statusCode = 403
            message = "Integrity error!"
        return response(statusCode=statusCode, message=message, success=False, error=e)
    except Exception as e:
        conn.rollback()
        return response(
            statusCode=500, 
            message="Internal server error: " + str(e), 
            success=False,
            error=str(e)
        )
    finally:
        cursor.close()
        conn.close()




# view select job 
@app.route("/get_job_by_id/<int:job_id>", methods=["GET"])
def get_job_by_id(job_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT job_id, title, job_description FROM job WHERE job_id = %s", (job_id,))
    job = cursor.fetchone()
    cursor.close()
    conn.close()
    if job:
        return jsonify(job)
    else:
        return jsonify({"error": "Job not found"}), 404


# Utility: Generate secret code (alphanumeric, based on details)
def generate_secret_code(company_name, email, name, phone):
    base_str = f"{company_name}-{email}-{name}-{phone}-{random.randint(1000, 9999)}"
    hash_digest = hashlib.sha256(base_str.encode()).hexdigest()
    short_code = ''.join(random.choices(string.ascii_uppercase, k=3)) + hash_digest[:5].upper()
    return short_code + 'SUGAR'

# Job Provider Registration Endpoint
@app.route("/register", methods=["POST"])
def register_job_provider():
    data = request.get_json()
    print(" Received Registration Data:", data)

    company_name = data.get("company_name", "").strip()
    email = data.get("email", "").strip()
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()

    # Validate required fields
    if not all([company_name, email, name, phone]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                #  Step 1: Check if provider already exists (by email)
                check_sql = """
                    SELECT  secret_code FROM job_provider_profile
                    WHERE email = %s 
                """
                cursor.execute(check_sql, (email,))
                existing = cursor.fetchone()
                print(" Existing Provider:", existing)

                # If provider exists
                if existing:
                    # If same email → return existing secret
                    return jsonify({
                        "message":  "You already created your profile use your secret code to login."
                    })
                
                else:
                    # Step 2: If new provider → insert
                    new_secret_code = generate_secret_code(company_name, email, name, phone)
                    insert_sql = """
                        INSERT INTO job_provider_profile (
                            company_name, email, name, phone,
                            secret_code, created_by
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(insert_sql, (company_name, email, name, phone, new_secret_code, name))
                    conn.commit()

    except Exception as e:
        print(" Registration Error:", str(e))
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "message": "Registration successful",
        "secret_code": new_secret_code
    }), 201


#job_provider_dashboard............
@app.route("/providerdashboard", methods=["POST"])
def provider_dashboard():
    data = request.get_json()
    print(data)
    secret_code = data.get("secret_code")

    if not secret_code:
        return jsonify({"error": "Secret code required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Get provider profile
        provider_sql = "SELECT * FROM job_provider_profile WHERE secret_code = %s"
        cursor.execute(provider_sql, (secret_code,))
        provider = cursor.fetchone()
        

        if not provider:
            return jsonify({"error": "Invalid secret code"}), 404
        print(provider)
        job_provider_id = provider["provider_id"]
        print(job_provider_id)

        # Get all jobs posted by provider
        job_sql = "SELECT * FROM job WHERE provider_id = %s"
        cursor.execute(job_sql, (job_provider_id,))
        jobs = cursor.fetchall()

        return jsonify({
            "provider": provider,
            "job_posts": jobs
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

#  Get Applicants for a specific Job ID
@app.route("/jobapplications", methods=["POST","GET"])
def job_applications():
    data = request.get_json()
    job_id = data.get("job_id")

    if not job_id:
        return jsonify({"error": "Job ID required"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        sql = "SELECT * FROM job_seeker_applications WHERE job_id = %s"
        cursor.execute(sql, (job_id,))
        applications = cursor.fetchall()

        return jsonify({"applications": applications})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

#-----------------------------------------------------------------------
# JOB SEEKER - Register
@app.route("/jobseekerregister", methods=["POST"])
def register_job_seeker():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    resume_file = request.files.get("resume")

    if not all([name, email, phone, resume_file]):
            return jsonify({"error": "All fields are required"}), 400


  
    filename = secure_filename(resume_file.filename)
    name_part, file_ext = os.path.splitext(filename)  
    unique_name = f"{name_part}--{uuid.uuid4().hex}{file_ext}"
    print("Unique Resume Name:", unique_name)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    resume_file.save(file_path)


    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                #  Step 1: Check if seeker already exists (by email)
                check_sql = """
                    SELECT  secret_code FROM job_seekers
                    WHERE email = %s 
                """
                cursor.execute(check_sql, (email,))
                existing = cursor.fetchone()
                # print(" Existing Provider:", existing)

                # If seeker exists
                if existing:
                    # If same email → return existing secret
                    return jsonify({
                        "message": "You already created your profile use your secret code to login.",
                    })
                else: 
                    # Step 2: If new seeker → insert
                    secret_code = generate_secret_code(name, email, file_path, phone)
                    cursor.execute("""
                        INSERT INTO job_seekers (name, email, resume_path , phone , secret_code)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (name, email, file_path, phone, secret_code))
                    conn.commit()
                    return jsonify({"message": "Registered successfully", "secret_code": secret_code})
                
    except Exception as e:
        return jsonify({"error": str(e)})



# JOB SEEKER - Dashboard
@app.route("/jobseekerdashboard", methods=["POST"])
def job_seeker_dashboard():
    data = request.get_json()
    print("Job Seeker Dashboard Data:", data)
    secret_code = secret_code = data.get("secret_code", "").strip()
    print("Secret Code:", secret_code)

    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Get the job seeker
        cursor.execute("SELECT * FROM job_seekers WHERE secret_code=%s", (secret_code,))
        seeker = cursor.fetchone()
        print("Seeker Data:", seeker)
        if not seeker:
            return jsonify({"error": "Invalid secret code"})

        # Get jobs applied by seeker with company name
        cursor.execute("""
            SELECT 
                j.*, 
                p.company_name 
            FROM 
                job_seeker_applications a
            JOIN 
                job j ON a.job_id = j.job_id
            JOIN 
                job_provider_profile p ON j.provider_id = p.provider_id
            WHERE 
                a.job_seeker_id = %s
        """, (seeker['id'],))
        results = cursor.fetchall()
        print("Applications with company:", results)

        return jsonify({
            "seeker": seeker,
            "applications": results
        })
    except Exception as e:
        return jsonify({"error": str(e)})
    finally:
        conn.close()



@app.route('/getresumes/<seeker_id>', methods=['GET'])
def get_resumes(seeker_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute("SELECT resume_path FROM job_seekers WHERE id = %s", (seeker_id,))
        result = cursor.fetchone()

        if not result or not result["resume_path"]:
            return jsonify({"error": "Resume not found"}), 404

        # Extract file name from the path stored
        filename = os.path.basename(result["resume_path"])
        
        # Convert to public URL
        resume_url = url_for('static', filename=f"resumes/{filename}", _external=True)
        print("Resume URL:", resume_url)

        cursor.close()
        conn.close()
        
        return jsonify(resume_url)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# JOB SEEKER - Apply for a Job
@app.route("/jobseekerapply", methods=["POST"])
def apply_for_job():
    data = request.get_json()
    print("Received application data:", data)

    job_seeker_id = data.get("seeker_id")
    job_id = data.get("job_id")

    full_resume_url = data.get("resume_path", "").strip()
    resume_path = full_resume_url.split("/static/")[-1]
    resume_path = os.path.join("static", resume_path)
    print("Cleaned resume path:", resume_path)

    if not job_seeker_id or not job_id:
        return jsonify({"error": "job_seeker_id and job_id required"}), 400

    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # Step 1: Check if seeker has already applied for this job
                cursor.execute("""
                    SELECT * FROM job_seeker_applications   WHERE job_seeker_id = %s AND job_id = %s
                """, (job_seeker_id, job_id))
                existing_application = cursor.fetchone()
                if existing_application:
                    return jsonify({"error": "You have already applied for this job"}), 409
                
                # Step 2: Insert new application
                cursor.execute("SELECT name FROM job_seekers WHERE id = %s", (job_seeker_id,))
                name_result = cursor.fetchone()
                if not name_result:
                    return jsonify({"error": "Invalid job_seeker_id"}), 404
                name = name_result['name']

                cursor.execute("""
                    INSERT INTO job_seeker_applications (job_seeker_id, job_id, name, resume_path)
                    VALUES (%s, %s, %s, %s)
                """, (job_seeker_id, job_id, name, resume_path))
                conn.commit()
                return jsonify({"message": "Applied successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})

 
# JOB SEEKER - View All Jobs with Shortened Job Descriptions
@app.route("/jobs", methods=["GET"])
def view_all_jobs():
    try:
        conn = get_db_connection()
        with conn:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM job WHERE active = 'Y'")
                jobs = cursor.fetchall()

                # Shorten job_description for each job
                for job in jobs:
                    full_jd = job.get("job_description", "")
                    short_jd = full_jd[:200].rsplit(" ", 1)[0] + "..." if len(full_jd) > 200 else full_jd
                    job["job_description"] = short_jd

                print("Jobs fetched:", jobs)
                return jsonify(jobs)

    except Exception as e:
        return jsonify({"error": str(e)})



 
# @app.route("/resumescreening/<int:job_id>", methods=["GET"])
# def resume_screening(job_id):
#     print("Job ID for screening:", job_id)
#     try:
#         if not job_id:
#             return jsonify({"error": "Missing job_id parameter"}), 400

#         conn = get_db_connection()
#         cursor = conn.cursor(pymysql.cursors.DictCursor)

#         cursor.execute("SELECT resume_path FROM job_seeker_applications WHERE job_id = %s", (job_id,))
#         resumes = cursor.fetchall()

#         cursor.execute("SELECT job_description FROM job WHERE job_id = %s", (job_id,))
#         job_description_row = cursor.fetchone()
#         if not job_description_row:
#             return jsonify({"error": "Job description not found"}), 404

#         job_description = job_description_row["job_description"]
#         resume_pdf = [resume['resume_path'] for resume in resumes]
#         print("Resumes to process:", resume_pdf)
#         print("Job Description:", job_description)

#         all_resumes_text = []
#         file_info_map = {}
#         results = []

#         for file_path in resume_pdf:
#             file_path = Path(file_path)
#             resume_text = extract_pdf_text(file_path)
#             filename = file_path.name
#             all_resumes_text.append({"filename": filename, "text": resume_text})
#             file_info_map[filename] = {"save_path": file_path, "filename": filename}

#         try:
#             combined_response_raw = call_gemini(job_description, all_resumes_text)
#             llm_response = clean_json_response(combined_response_raw)
#         except Exception as e:
#             return jsonify({"error": f"LLM failed: {str(e)}"}), 500

#         for llm_json in llm_response:
#             try:
#                 if isinstance(llm_json, str):
#                     llm_json = json.loads(llm_json)

#                 filename = llm_json.get("filename")
#                 if filename not in file_info_map:
#                     continue

#                 # Create public resume URL
#                 llm_json['resume_link'] = url_for('static', filename=f'resumes/{filename}', _external=True)

#                 sql = """
#                     INSERT INTO resume (
#                         filename,
#                         name,
#                         degree,
#                         experience_year,
#                         experience_detail,
#                         location,
#                         jdmatch,
#                         match_skills,
#                         overall_score,
#                         resume_link,
#                         job_id
#                     ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s ,%s ,%s)
#                 """
#                 candidate_row = [
#                     str(filename),
#                     str(llm_json.get("name", "")),
#                     str(llm_json.get("degree", "")),
#                     int(llm_json.get("experience_year", 0)),
#                     str(llm_json.get("experience_details", "")),
#                     str(llm_json.get("location", "")),
#                     int(round(float(llm_json.get('JDMatch', "0").replace('%', '')))),
#                     json.dumps(llm_json.get("MatchingKeywords", {})),
#                     int(round(float(llm_json.get('overall_score', "0").replace('%', '')))),
#                     str(llm_json.get("resume_link", "")),
#                     int(job_id)
#                 ]
#                 cursor.execute(sql, candidate_row)
#                 results.append(llm_json)

#             except Exception as e:
#                 results.append({"file": filename, "error": f"DB insert failed: {str(e)}"})

#         conn.commit()
#         cursor.close()
#         conn.close()

#         return jsonify(results)

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

@app.route("/resumescreening/<int:job_id>", methods=["GET"])
def resume_screening(job_id):
    print("Job ID for screening:", job_id)
    try:
        if not job_id:
            return jsonify({"error": "Missing job_id parameter"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)

        # Get all resumes applied for the job
        cursor.execute("SELECT resume_path FROM job_seeker_applications WHERE job_id = %s", (job_id,))
        applied_resumes = cursor.fetchall()

        # Get job description
        cursor.execute("SELECT job_description FROM job WHERE job_id = %s", (job_id,))
        job_description_row = cursor.fetchone()
        if not job_description_row:
            return jsonify({"error": "Job description not found"}), 404

        job_description = job_description_row["job_description"]
        all_resumes_text = []
        file_info_map = {}
        results = []

        for resume in applied_resumes:
            file_path = Path(resume['resume_path'])
            filename = file_path.name

            #  Step 1: Check if already processed
            cursor.execute("SELECT * FROM resume WHERE filename = %s AND job_id = %s", (filename, job_id))
            existing_result = cursor.fetchone()

            if existing_result:
                print(f"Skipping {filename}, already processed.")
                # Reformat for response
                existing_result["resume_link"] = url_for('static', filename=f'resumes/{filename}', _external=True)
                results.append(existing_result)
                continue

            # Step 2: Extract and prepare for LLM
            resume_text = extract_pdf_text(file_path)
            all_resumes_text.append({"filename": filename, "text": resume_text})
            file_info_map[filename] = {"save_path": file_path, "filename": filename}

        # Step 3: If all resumes are already processed
        if not all_resumes_text:
            cursor.close()
            conn.close()
            return jsonify(results)

        # Step 4: Call LLM for only new resumes
        try:
            combined_response_raw = call_gemini(job_description, all_resumes_text)
            llm_response = clean_json_response(combined_response_raw)
        except Exception as e:
            return jsonify({"error": f"LLM failed: {str(e)}"}), 500

        for llm_json in llm_response:
            try:
                if isinstance(llm_json, str):
                    llm_json = json.loads(llm_json)

                filename = llm_json.get("filename")
                if filename not in file_info_map:
                    continue

                llm_json['resume_link'] = url_for('static', filename=f'resumes/{filename}', _external=True)

                sql = """
                    INSERT INTO resume (
                        filename,
                        name,
                        degree,
                        experience_year,
                        experience_detail,
                        location,
                        jdmatch,
                        match_skills,
                        overall_score,
                        resume_link,
                        job_id
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s ,%s ,%s)
                """
                candidate_row = [
                    str(filename),
                    str(llm_json.get("name", "")),
                    str(llm_json.get("degree", "")),
                    int(llm_json.get("experience_year", 0)),
                    str(llm_json.get("experience_details", "")),
                    str(llm_json.get("location", "")),
                    int(round(float(llm_json.get('JDMatch', "0").replace('%', '')))),
                    json.dumps(llm_json.get("MatchingKeywords", {})),
                    int(round(float(llm_json.get('overall_score', "0").replace('%', '')))),
                    str(llm_json.get("resume_link", "")),
                    int(job_id)
                ]
                cursor.execute(sql, candidate_row)
                results.append(llm_json)

            except Exception as e:
                results.append({"file": filename, "error": f"DB insert failed: {str(e)}"})

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify(results)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 5000, debug = True)

