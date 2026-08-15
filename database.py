# ==============================================================================
# TASK 5: BACKEND & DATA MODELING ENGINE (Python + SQLite)
# 
# Features Implemented:
# 1. Clean and structured relational datasets (16,000+ total rows across 7 tables)
# 2. Proper joins and foreign key relationships (teachers <-> late_counts, benchmark_scores, etc.)
# 3. Clearly named calculated fields & aggregated metrics (OverallScore, Int/Ext Index, Attrition Rate)
# 4. Comprehensive NULL / NA value handling (SQL COALESCE + Pandas .fillna() & .to_numeric())
# ==============================================================================

import pandas as pd
import numpy as np
import sqlite3
import hashlib
import json
import os

DB_FILE = "school_analytics.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    """
    TASK 5.1 & 5.2: Create clean, structured relational datasets and enforce foreign key relationships.
    Creates 7 normalized tables: users, teachers, late_counts, benchmark_scores, 
    stakeholder_ratings, teacher_details_extra, and attrition.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users table (Authentication & User Roles)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # 2. Teachers table (Master Entity - 1,000 Teacher Profiles)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            dob TEXT,
            qualifications TEXT,
            experience_school INTEGER,
            experience_prev INTEGER,
            section TEXT,
            classes_per_week INTEGER,
            subjects TEXT
        )
    """)

    # 3. Late counts table (Relational Dataset - 12,000+ Monthly Attendance Records)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS late_counts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            month TEXT,
            year INTEGER,
            late_count INTEGER,
            unplanned_leaves INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
        )
    """)

    # 4. Benchmark scores table (Evaluation Metrics & Compliance)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS benchmark_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            int_bm_score REAL,
            ext_bm_score REAL,
            compliance_score REAL,
            training_hours INTEGER,
            assignment_stars INTEGER,
            co_curricular_count INTEGER,
            co_curricular_quality TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
        )
    """)

    # 5. Stakeholder ratings table (Head, Peer, Student, Parent 360 Feedback)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stakeholder_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            head_stars INTEGER,
            peer_stars INTEGER,
            student_stars INTEGER,
            parent_stars INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
        )
    """)

    # 6. Teacher details extra (Qualitative Analysis & Support Parameters)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teacher_details_extra (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            expectations TEXT,
            support_params TEXT,
            int_bm_notes TEXT,
            ext_bm_notes TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
        )
    """)

    # 7. Attrition table (Attrition Score & Risk Classification)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attrition (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            teacher_id INTEGER,
            attrition_score REAL,
            attrition_type TEXT,
            explanation TEXT,
            FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id) ON DELETE CASCADE
        )
    """)

    # Create Foreign Key Indexes for high-performance sub-second joins over 16,000+ rows
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_late_teacher_m ON late_counts(teacher_id, month);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bm_teacher ON benchmark_scores(teacher_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_attr_teacher ON attrition(teacher_id);")

    conn.commit()

    # Seed 10,000+ records if database is empty or requires re-seeding
    cursor.execute("SELECT COUNT(*) FROM late_counts")
    count_late = cursor.fetchone()[0]
    if count_late < 10000:
        seed_large_dataset(conn)

    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def seed_large_dataset(conn):
    """TASK 5.1: Seeds clean, structured 16,000+ record dataset with explicit type safety."""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM late_counts")
    cursor.execute("DELETE FROM benchmark_scores")
    cursor.execute("DELETE FROM stakeholder_ratings")
    cursor.execute("DELETE FROM teacher_details_extra")
    cursor.execute("DELETE FROM attrition")
    cursor.execute("DELETE FROM teachers")
    conn.commit()

    np.random.seed(42)

    # Core Reference Teachers from PDF
    key_teachers = [
        ("Linda Martinez", "10 May 1987", "MA, BEd", 13, 0, "Sec2", 29, "Hindi-VI, VIII-X"),
        ("Aachal Jodhavat", "15 Aug 1990", "MSc, BEd", 8, 4, "Sec1", 26, "Maths-IX-XII"),
        ("Jessica Garcia", "22 Nov 1985", "MA, MEd", 10, 5, "Sec3", 30, "English-X-XII"),
        ("Patricia Taylor", "04 Mar 1992", "BSc, BEd", 5, 2, "Sec2", 28, "Science-VI-VIII"),
        ("Kevin Adams", "18 Jul 1988", "MSc, PhD", 7, 3, "Sec1", 25, "Physics-XI-XII"),
        ("Matthew Young", "30 Jan 1991", "BA, BEd", 6, 1, "Sec3", 27, "Social Studies-VII-IX"),
        ("George Turner", "12 Oct 1989", "MA, BEd", 9, 3, "Sec2", 28, "History-VIII-X"),
        ("Steven Evans", "05 Sep 1986", "MSc, BEd", 11, 2, "Sec1", 26, "Chemistry-XI-XII"),
        ("Michael Ross", "14 Apr 1984", "MA, BEd", 14, 6, "Sec3", 29, "Geography-IX-XII"),
        ("William Davis", "29 Dec 1980", "MA, MEd", 18, 5, "Sec2", 30, "Political Science-XI-XII"),
        ("Rajesh Khanna", "08 Jun 1982", "MCom, BEd", 15, 4, "Sec1", 27, "Economics-XI-XII"),
        ("Sarah Jenkins", "19 Mar 1993", "BA, BEd", 4, 1, "Sec2", 28, "English-VI-VIII"),
        ("David Miller", "25 Feb 1991", "BSc, BEd", 7, 2, "Sec3", 26, "Maths-VI-VIII"),
        ("Emily Watson", "11 Aug 1994", "MA, BEd", 3, 0, "Sec1", 25, "Hindi-VI-VII"),
        ("Robert Brown", "03 Dec 1987", "MSc, BEd", 9, 3, "Sec2", 29, "Biology-IX-XII"),
        ("James Wilson", "17 May 1989", "BA, BEd", 8, 2, "Sec3", 28, "Art & Craft-VI-X")
    ]

    first_names = ["Anita", "Suresh", "Priya", "Rahul", "Deepak", "Ananya", "Meera", "Vikram", "Sunita", "Rohan",
                   "Kavita", "Amit", "Pooja", "Sanjay", "Neha", "Alok", "Swati", "Nitin", "Ritu", "Manish",
                   "Shweta", "Abhishek", "Divya", "Gaurav", "Simran", "Varun", "Archana", "Tarun", "Bhavna", "Karan",
                   "Rachna", "Vivek", "Tanvi", "Harish", "Aarti", "Ashok", "Surbhi", "Dinesh", "Kriti", "Vijay",
                   "Lata", "Ramesh", "Geeta", "Sunil", "Asha", "Pankaj", "Usha", "Vinod", "Rekha", "Manoj"]
    middle_initials = ["A.", "B.", "C.", "D.", "E.", "F.", "G.", "H.", "K.", "L.", "M.", "N.", "P.", "R.", "S.", "T.", "V.", "Y."]
    last_names = ["Sharma", "Verma", "Gupta", "Singh", "Kumar", "Jha", "Patel", "Joshi", "Mehta", "Rao", "Nair", "Iyer", "Chawla", "Deshmukh", "Kulkarni", "Reddy"]

    additional_teachers = []
    seen_names = set(t[0] for t in key_teachers)

    while len(key_teachers) + len(additional_teachers) < 1000:
        fn = str(np.random.choice(first_names))
        ln = str(np.random.choice(last_names))
        mi = str(np.random.choice(middle_initials))
        name = f"{fn} {mi} {ln}"
        if name in seen_names:
            name = f"{fn} {ln}"
            if name in seen_names:
                continue
        seen_names.add(name)
        dob = f"{np.random.randint(1, 28):02d} {np.random.choice(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])} {np.random.randint(1975, 1998)}"
        qual = str(np.random.choice(["MA, BEd", "MSc, BEd", "BA, BEd", "BSc, BEd", "MCom, BEd", "None"]))
        if qual == "None": qual = None
        exp_sch = int(np.random.randint(1, 20))
        exp_prev = int(np.random.choice([0, 1, 2, 3, 4, 5])) if np.random.rand() > 0.15 else None
        sec = str(np.random.choice(["Sec1", "Sec2", "Sec3"]))
        cpw = int(np.random.randint(20, 32))
        sub = str(np.random.choice(["Maths-VI-X", "English-IX-XII", "Science-VI-VIII", "Social Studies-VIII-X", "Hindi-VI-X", "Computer-VI-XII", "None"]))
        if sub == "None": sub = None
        additional_teachers.append((name, dob, qual, exp_sch, exp_prev, sec, cpw, sub))

    all_teachers_list = key_teachers + additional_teachers

    cursor.executemany("""
        INSERT INTO teachers (name, dob, qualifications, experience_school, experience_prev, section, classes_per_week, subjects)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, all_teachers_list)

    cursor.execute("SELECT teacher_id, name FROM teachers")
    teacher_id_map = {name: tid for tid, name in cursor.fetchall()}

    # 1. Attrition Data
    attrition_records = [
        ("Jessica Garcia", 3.00, "Resigned", "Looking for new job"),
        ("Patricia Taylor", 3.00, "High Risk", "Stressed and not happy with peer group"),
        ("Kevin Adams", 3.00, "High Risk", "Teaches PP, Over Qualified. Would look for Opportunities after her mother's condition revives"),
        ("Matthew Young", 2.00, "Medium Risk", "No immediate attrition. But not enjoying teaching"),
        ("George Turner", 2.00, "Medium Risk", "No immediate attrition. But not enjoying teaching"),
        ("Steven Evans", 2.00, "Medium Risk", "No immediate attrition. But not enjoying teaching"),
        ("Michael Ross", 1.00, "Low Risk", "Attitude issue, reluctant to change"),
        ("William Davis", 1.00, "Low Risk", "Senior teacher, does not want to change"),
        ("Rajesh Khanna", 1.00, "Low Risk", "Complacent due to proximity to Principal"),
    ]
    attr_dict = {r[0]: (float(r[1]), str(r[2]), str(r[3])) for r in attrition_records}

    attrition_inserts = []
    for name, tid in teacher_id_map.items():
        if name in attr_dict:
            attrition_inserts.append((int(tid), attr_dict[name][0], attr_dict[name][1], attr_dict[name][2]))
        else:
            rand_val = float(np.random.rand())
            if rand_val < 0.03:
                attrition_inserts.append((int(tid), 3.00, "High Risk", "Looking for career growth"))
            elif rand_val < 0.08:
                attrition_inserts.append((int(tid), 2.00, "Medium Risk", "Workload stress"))
            elif rand_val < 0.15:
                attrition_inserts.append((int(tid), 1.00, "Low Risk", "Personal commitments"))
            else:
                attrition_inserts.append((int(tid), 0.00, "No Risk", "Part of previous year program"))

    cursor.executemany("""
        INSERT INTO attrition (teacher_id, attrition_score, attrition_type, explanation)
        VALUES (?, ?, ?, ?)
    """, attrition_inserts)

    # 2. Benchmark Scores
    benchmark_inserts = []
    for name, tid in teacher_id_map.items():
        if name == "Linda Martinez":
            benchmark_inserts.append((int(tid), 74.0, 65.0, 5.5, 11, 3, 8, "Good"))
        elif name == "Aachal Jodhavat":
            benchmark_inserts.append((int(tid), 68.5, 60.0, 5.8, 15, 3, 7, "Good"))
        else:
            int_score = float(round(float(np.random.normal(62.8, 6.0)), 1))
            ext_score = float(round(float(np.random.normal(57.3, 5.5)), 1))
            comp_score = float(round(float(np.random.normal(5.6, 1.0)), 1))
            int_score = max(30.0, min(95.0, int_score))
            ext_score = max(30.0, min(90.0, ext_score))
            comp_score = max(1.0, min(10.0, comp_score))
            training = int(np.random.randint(5, 45))
            assign_stars = int(np.random.randint(1, 4))
            cca_cnt = int(np.random.randint(4, 12))
            cca_qual = str(np.random.choice(["Needs Improvement", "Good", "Excellent", "None"]))
            if cca_qual == "None": cca_qual = None
            benchmark_inserts.append((int(tid), int_score, ext_score, comp_score, training, assign_stars, cca_cnt, cca_qual))

    cursor.executemany("""
        INSERT INTO benchmark_scores (teacher_id, int_bm_score, ext_bm_score, compliance_score, training_hours, assignment_stars, co_curricular_count, co_curricular_quality)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, benchmark_inserts)

    # 3. Late Counts (12,000+ Records)
    months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar"]
    late_inserts = []
    dec_late_counts = np.random.multinomial(137, [1.0/1000]*1000)

    for i, (name, tid) in enumerate(teacher_id_map.items()):
        for m in months:
            if m == "Dec":
                lc = int(dec_late_counts[i])
                unplanned = 0 if name == "Linda Martinez" else int(np.random.randint(0, 2))
            else:
                if name == "Aachal Jodhavat":
                    wave_dict = {"Apr": 0, "May": 4, "Jun": 3, "Jul": 2, "Aug": 3, "Sep": 1, "Oct": 2, "Nov": 1, "Dec": 2, "Jan": 0, "Feb": 1, "Mar": 0}
                    lc = int(wave_dict.get(m, 1))
                elif name == "Linda Martinez":
                    lc = 0
                else:
                    val = np.random.choice([0, 0, 1, 1, 2, 3])
                    lc = int(val) if float(np.random.rand()) > 0.05 else None
                unplanned = int(np.random.randint(0, 3))
            yr = 2025 if m in ["Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"] else 2026
            late_inserts.append((int(tid), str(m), int(yr), lc, unplanned))

    cursor.executemany("""
        INSERT INTO late_counts (teacher_id, month, year, late_count, unplanned_leaves)
        VALUES (?, ?, ?, ?, ?)
    """, late_inserts)

    # 4. Stakeholder Ratings
    stakeholder_inserts = []
    for name, tid in teacher_id_map.items():
        stakeholder_inserts.append((int(tid), int(np.random.randint(2, 4)), int(np.random.randint(2, 4)), int(np.random.randint(2, 4)), int(np.random.randint(2, 4))))

    cursor.executemany("""
        INSERT INTO stakeholder_ratings (teacher_id, head_stars, peer_stars, student_stars, parent_stars)
        VALUES (?, ?, ?, ?, ?)
    """, stakeholder_inserts)

    # 5. Teacher Details Extra
    extra_inserts = []
    for name, tid in teacher_id_map.items():
        if name == "Linda Martinez":
            exp = json.dumps(["Adopt activity-based learning", "Improve assessment design", "Maintain accurate records", "Actively seek professional development opportunities"])
            sup = json.dumps(["Academic board duties: Contributed", "Examination portfolio: Contributed", "Admission-related duties: Contributed", "School affiliation: Contributed"])
            int_notes = json.dumps(["Lesson plan: Well-structured", "Worksheet: Effective", "Time Management: Managed well", "Pedagogical Planning: Requires slight follow-up"])
            ext_notes = json.dumps(["Lesson plan: Clear LOs, needs to improve assessment", "Worksheet: Purposefully designed, HODs to be included", "Time Management: Efficient, well-executed", "Pedagogical Planning: Student-centered strategies seen"])
        else:
            exp = json.dumps(["Enhance digital classroom integration", "Provide timely student feedback"])
            sup = json.dumps(["Academic board duties: Contributed"])
            int_notes = json.dumps(["Lesson plan: Satisfactory", "Worksheet: Standard"])
            ext_notes = json.dumps(["Lesson plan: Aligned with curriculum", "Worksheet: Good depth"])
        extra_inserts.append((int(tid), exp, sup, int_notes, ext_notes))

    cursor.executemany("""
        INSERT INTO teacher_details_extra (teacher_id, expectations, support_params, int_bm_notes, ext_bm_notes)
        VALUES (?, ?, ?, ?, ?)
    """, extra_inserts)

    conn.commit()

# ==============================================================================
# TASK 5.2, 5.3 & 5.4: RELATIONAL JOINS, CALCULATED METRICS & NULL HANDLING
# ==============================================================================

def fetch_attrition_risk_summary(section_filter: str = "All Sections"):
    conn = get_connection()
    sec_where = "" if section_filter == "All Sections" else f" WHERE t.section = '{section_filter}'"
    query = f"""
        SELECT
            CASE
                WHEN COALESCE(a.attrition_score, 0.0) >= 3.0 THEN 'High Risk'
                WHEN COALESCE(a.attrition_score, 0.0) = 2.0 THEN 'Medium Risk'
                WHEN COALESCE(a.attrition_score, 0.0) = 1.0 THEN 'Low Risk'
                ELSE 'No Risk'
            END as RiskLevel,
            COUNT(*) as Count
        FROM attrition a
        JOIN teachers t ON a.teacher_id = t.teacher_id
        {sec_where}
        GROUP BY RiskLevel
        ORDER BY RiskLevel ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def fetch_top_attrition_reasons(limit: int = 5, section_filter: str = "All Sections"):
    """
    TASK 5.3 & 5.4: Aggregates qualitative attrition risk reasons with SQL COALESCE.
    """
    conn = get_connection()
    sec_where = "" if section_filter == "All Sections" else f" AND t.section = '{section_filter}'"
    query = f"""
        SELECT
            COALESCE(a.explanation, 'No specific reason') as Reason,
            COUNT(*) as Count
        FROM attrition a
        JOIN teachers t ON a.teacher_id = t.teacher_id
        WHERE COALESCE(a.attrition_score, 0.0) > 0
        {sec_where}
        GROUP BY Reason
        ORDER BY Count DESC
        LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def fetch_dashboard_kpis(section_filter: str = "All Sections"):
    """
    TASK 5.2, 5.3 & 5.4:
    - Proper SQL INNER JOINs between teachers, late_counts, benchmark_scores, and attrition.
    - Clearly named calculated metrics (total_teachers, attrition_risk, avg_int_bm, avg_ext_bm).
    - Robust NULL handling using SQL COALESCE(val, fallback).
    """
    conn = get_connection()
    sec_where = "" if section_filter == "All Sections" else f" WHERE section = '{section_filter}'"

    # Total Teachers Count
    df_teachers = pd.read_sql_query(f"SELECT COUNT(*) as total_teachers FROM teachers {sec_where}", conn)
    total_teachers = int(df_teachers.iloc[0]['total_teachers'])

    # Attrition Risk Count (JOIN teachers <-> attrition)
    attr_query = f"""
        SELECT COUNT(*) as attr_risk FROM attrition a
        JOIN teachers t ON a.teacher_id = t.teacher_id
        WHERE COALESCE(a.attrition_score, 0) > 0 {("AND t.section = '" + section_filter + "'") if section_filter != "All Sections" else ""}
    """
    df_attrition = pd.read_sql_query(attr_query, conn)
    attrition_risk = int(df_attrition.iloc[0]['attr_risk'])

    # Total Late Count Instances (JOIN teachers <-> late_counts)
    late_query = f"""
        SELECT SUM(COALESCE(l.late_count, 0)) as total_late FROM late_counts l
        JOIN teachers t ON l.teacher_id = t.teacher_id
        WHERE l.month = 'Dec' {("AND t.section = '" + section_filter + "'") if section_filter != "All Sections" else ""}
    """
    df_late = pd.read_sql_query(late_query, conn)
    late_count_instances = int(df_late.iloc[0]['total_late']) if pd.notnull(df_late.iloc[0]['total_late']) else 0

    # Benchmark & Compliance Averages (JOIN teachers <-> benchmark_scores)
    bm_query = f"""
        SELECT
            AVG(COALESCE(b.int_bm_score, 60.0)) as avg_int_bm,
            AVG(COALESCE(b.ext_bm_score, 55.0)) as avg_ext_bm,
            AVG(COALESCE(b.compliance_score, 5.0)) as avg_compliance,
            AVG(COALESCE(b.co_curricular_count, 6)) as avg_cca
        FROM benchmark_scores b
        JOIN teachers t ON b.teacher_id = t.teacher_id
        {sec_where}
    """
    df_benchmarks = pd.read_sql_query(bm_query, conn)

    avg_int_bm = round(float(df_benchmarks.iloc[0]['avg_int_bm']), 1)
    avg_ext_bm = round(float(df_benchmarks.iloc[0]['avg_ext_bm']), 1)
    avg_compliance = round(float(df_benchmarks.iloc[0]['avg_compliance']), 1)
    avg_cca = round(float(df_benchmarks.iloc[0]['avg_cca'] / 12.0 * 10.0), 1)

    conn.close()

    return {
        "total_teachers": total_teachers,
        "attrition_risk": attrition_risk,
        "late_count_instances": late_count_instances,
        "avg_int_bm": avg_int_bm,
        "avg_ext_bm": avg_ext_bm,
        "avg_compliance": avg_compliance,
        "avg_cca": avg_cca
    }

def fetch_section_column_chart():
    """TASK 5.2 & 5.3: Section-wise benchmark score aggregations with SQL JOIN."""
    conn = get_connection()
    query = """
        SELECT
            t.section as Section,
            ROUND(AVG(COALESCE(b.int_bm_score, 60.0)), 1) as "Int BM",
            ROUND(AVG(COALESCE(b.ext_bm_score, 55.0)), 1) as "Ext BM",
            ROUND(AVG(COALESCE(b.compliance_score, 5.0)) * 10, 1) as "Compliance Score (x10)"
        FROM teachers t
        JOIN benchmark_scores b ON t.teacher_id = b.teacher_id
        GROUP BY t.section
        ORDER BY t.section ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def fetch_top_teacher_rankings(limit: int = 10, section_filter: str = "All Sections"):
    """
    TASK 5.3: Calculated Field 'OverallScore' = (Int BM + Ext BM + Compliance*10) / 3.0 with optional section slicer.
    """
    conn = get_connection()
    sec_where = "" if section_filter == "All Sections" else f" WHERE t.section = '{section_filter}'"
    query = f"""
        SELECT
            t.name as Teacher,
            COALESCE(t.section, 'Sec1') as Section,
            ROUND((COALESCE(b.int_bm_score, 60) + COALESCE(b.ext_bm_score, 55) + (COALESCE(b.compliance_score, 5)*10)) / 3.0, 1) as OverallScore
        FROM teachers t
        JOIN benchmark_scores b ON t.teacher_id = b.teacher_id
        {sec_where}
        ORDER BY OverallScore DESC
        LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def fetch_conditionally_formatted_teachers(section_filter: str = "All Sections", limit: int = 25):
    """
    TASK 5.2, 5.3 & 5.4: Relational JOIN across 3 tables (teachers, benchmark_scores, attrition) 
    with SQL COALESCE fallback for missing scores.
    """
    conn = get_connection()
    sec_where = "" if section_filter == "All Sections" else f" WHERE t.section = '{section_filter}'"
    query = f"""
        SELECT
            t.name as "Teacher Name",
            COALESCE(t.section, 'Sec1') as "Section",
            COALESCE(t.subjects, 'General') as "Subjects",
            COALESCE(b.int_bm_score, 60.0) as "Int BM Score",
            COALESCE(b.ext_bm_score, 55.0) as "Ext BM Score",
            COALESCE(b.compliance_score, 5.0) as "Compliance Score",
            COALESCE(a.attrition_score, 0.0) as "Risk Score"
        FROM teachers t
        JOIN benchmark_scores b ON t.teacher_id = b.teacher_id
        JOIN attrition a ON t.teacher_id = a.teacher_id
        {sec_where}
        ORDER BY b.int_bm_score DESC
        LIMIT {limit}
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def fetch_performance_landscape():
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    scores = [42, 45, 48, 52, 50, 56, 61, 65, 68, 72, 75, 78]
    return pd.DataFrame({"Month": months, "Performance Score": scores})

def fetch_teacher_full_profile(teacher_name: str):
    """
    TASK 5.2, 5.3 & 5.4: Relational JOIN across 5 tables (teachers, benchmark_scores, 
    stakeholder_ratings, teacher_details_extra, attrition) with zero-crash NULL handling.
    """
    conn = get_connection()
    query = """
        SELECT
            t.teacher_id, t.name,
            COALESCE(t.dob, 'N/A') as dob,
            COALESCE(t.qualifications, 'Not Specified') as qualifications,
            COALESCE(t.experience_school, 0) as experience_school,
            COALESCE(t.experience_prev, 0) as experience_prev,
            COALESCE(t.section, 'General') as section,
            COALESCE(t.classes_per_week, 24) as classes_per_week,
            COALESCE(t.subjects, 'General Subjects') as subjects,
            COALESCE(b.int_bm_score, 60.0) as int_bm_score,
            COALESCE(b.ext_bm_score, 55.0) as ext_bm_score,
            COALESCE(b.compliance_score, 5.0) as compliance_score,
            COALESCE(b.training_hours, 10) as training_hours,
            COALESCE(b.assignment_stars, 3) as assignment_stars,
            COALESCE(b.co_curricular_count, 6) as co_curricular_count,
            COALESCE(b.co_curricular_quality, 'Good') as co_curricular_quality,
            COALESCE(s.head_stars, 3) as head_stars,
            COALESCE(s.peer_stars, 3) as peer_stars,
            COALESCE(s.student_stars, 3) as student_stars,
            COALESCE(s.parent_stars, 3) as parent_stars,
            e.expectations, e.support_params, e.int_bm_notes, e.ext_bm_notes,
            COALESCE(a.attrition_score, 0.0) as attrition_score,
            COALESCE(a.attrition_type, 'No Risk') as attrition_type,
            COALESCE(a.explanation, 'No active risk recorded.') as explanation
        FROM teachers t
        LEFT JOIN benchmark_scores b ON t.teacher_id = b.teacher_id
        LEFT JOIN stakeholder_ratings s ON t.teacher_id = s.teacher_id
        LEFT JOIN teacher_details_extra e ON t.teacher_id = e.teacher_id
        LEFT JOIN attrition a ON t.teacher_id = a.teacher_id
        WHERE t.name = ?
    """
    df = pd.read_sql_query(query, conn, params=[teacher_name])

    df_late = pd.read_sql_query("""
        SELECT COALESCE(late_count, 0) as late_count, COALESCE(unplanned_leaves, 0) as unplanned_leaves
        FROM late_counts
        WHERE teacher_id = (SELECT teacher_id FROM teachers WHERE name = ?) AND month = 'Dec'
    """, conn, params=[teacher_name])

    conn.close()

    if df.empty:
        return None

    row = df.iloc[0].to_dict()
    row['late_current_month'] = int(df_late.iloc[0]['late_count']) if not df_late.empty else 0
    row['unplanned_leaves'] = int(df_late.iloc[0]['unplanned_leaves']) if not df_late.empty else 0
    row['expectations'] = json.loads(row['expectations']) if row['expectations'] else ["Maintain high teaching standards"]
    row['support_params'] = json.loads(row['support_params']) if row['support_params'] else ["Academic board duties: Contributed"]
    row['int_bm_notes'] = json.loads(row['int_bm_notes']) if row['int_bm_notes'] else ["Lesson plan: Satisfactory"]
    row['ext_bm_notes'] = json.loads(row['ext_bm_notes']) if row['ext_bm_notes'] else ["Lesson plan: Aligned"]

    return row

def fetch_late_arrival_trend(teacher_name: str = None):
    """
    TASK 5.2, 5.3 & 5.4: Fetches late arrival trend joining teachers and late_counts.
    Calculates average late counts across teachers when no specific teacher is selected.
    """
    conn = get_connection()
    if teacher_name:
        query = """
            SELECT l.month, CAST(COALESCE(l.late_count, 0) AS REAL) as late_count
            FROM late_counts l
            JOIN teachers t ON l.teacher_id = t.teacher_id
            WHERE t.name = ?
            ORDER BY l.id
        """
        df = pd.read_sql_query(query, conn, params=[teacher_name])
    else:
        query = """
            SELECT l.month, CAST(AVG(COALESCE(l.late_count, 0)) AS REAL) as late_count
            FROM late_counts l
            GROUP BY l.month
            ORDER BY l.id
        """
        df = pd.read_sql_query(query, conn)
    conn.close()

    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)
    df = df.sort_values('month').reset_index(drop=True)
    return df

def fetch_attrition_table(attrition_type: str = "All", section_filter: str = "All Sections"):
    """
    TASK 5.2, 5.3 & 5.4: Relational JOIN between attrition and teachers.
    Includes Pandas-level .fillna() for explicit missing value handling.
    """
    conn = get_connection()
    query = """
        SELECT
            t.name as "Teacher Name",
            COALESCE(t.section, 'Sec1') as "Section",
            COALESCE(a.attrition_score, 0.0) as "Attr. Score",
            COALESCE(a.explanation, 'No active risk recorded.') as "Attrition Explanation",
            COALESCE(a.attrition_type, 'No Risk') as attrition_type
        FROM attrition a
        JOIN teachers t ON a.teacher_id = t.teacher_id
        WHERE 1=1
    """
    if section_filter != "All Sections":
        query += f" AND t.section = '{section_filter}'"

    if attrition_type != "All":
        if attrition_type == "High Risk (>2.0)":
            query += " AND COALESCE(a.attrition_score, 0.0) >= 3.0"
        elif attrition_type == "Medium Risk (1.0 - 2.0)":
            query += " AND COALESCE(a.attrition_score, 0.0) = 2.0"
        elif attrition_type == "Low Risk (0.0 - 1.0)":
            query += " AND COALESCE(a.attrition_score, 0.0) = 1.0"
        elif attrition_type == "No Risk (0.0)":
            query += " AND COALESCE(a.attrition_score, 0.0) = 0.0"

    query += " ORDER BY a.attrition_score DESC, t.name ASC"
    df = pd.read_sql_query(query, conn)

    # TASK 5.4: Pandas fillna fallback
    df = df.fillna({
        "Teacher Name": "Unknown",
        "Section": "General",
        "Attr. Score": 0.0,
        "Attrition Explanation": "No active risk recorded.",
        "attrition_type": "No Risk"
    })

    conn.close()
    return df

def get_all_teacher_names(section_filter: str = "All Sections"):
    conn = get_connection()
    sec_where = "" if section_filter == "All Sections" else f" WHERE section = '{section_filter}'"
    df = pd.read_sql_query(f"SELECT name FROM teachers {sec_where} ORDER BY name ASC", conn)
    conn.close()
    return df['name'].tolist()


def add_new_teacher(name, dob, qualifications, experience_school, experience_prev,
                    section, classes_per_week, subjects):
    """Admin function: inserts a new teacher and seeds default evaluation records."""
    import json as _json
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO teachers (name, dob, qualifications, experience_school,
                                  experience_prev, section, classes_per_week, subjects)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, dob, qualifications, experience_school, experience_prev,
              section, classes_per_week, subjects))
        tid = cursor.lastrowid

        cursor.execute("""
            INSERT INTO benchmark_scores
                (teacher_id, int_bm_score, ext_bm_score, compliance_score,
                 training_hours, assignment_stars, co_curricular_count, co_curricular_quality)
            VALUES (?, 60.0, 55.0, 5.0, 10, 3, 6, 'Good')
        """, (tid,))

        cursor.execute("""
            INSERT INTO stakeholder_ratings (teacher_id, head_stars, peer_stars, student_stars, parent_stars)
            VALUES (?, 3, 3, 3, 3)
        """, (tid,))

        cursor.execute("""
            INSERT INTO attrition (teacher_id, attrition_score, attrition_type, explanation)
            VALUES (?, 0.0, 'No Risk', 'Newly added teacher')
        """, (tid,))

        exp   = _json.dumps(["Maintain high teaching standards", "Engage students effectively"])
        sup   = _json.dumps(["Academic board duties: Contributed"])
        i_n   = _json.dumps(["Lesson plan: Satisfactory", "Worksheet: Standard"])
        e_n   = _json.dumps(["Lesson plan: Aligned with curriculum", "Worksheet: Good depth"])
        cursor.execute("""
            INSERT INTO teacher_details_extra
                (teacher_id, expectations, support_params, int_bm_notes, ext_bm_notes)
            VALUES (?, ?, ?, ?, ?)
        """, (tid, exp, sup, i_n, e_n))

        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        for m in months:
            cursor.execute("""
                INSERT INTO late_counts (teacher_id, month, year, late_count, unplanned_leaves)
                VALUES (?, ?, 2026, 0, 0)
            """, (tid, m))

        conn.commit()
        conn.close()
        return True, "Teacher added successfully."
    except sqlite3.IntegrityError:
        conn.close()
        return False, f"A teacher named '{name}' already exists in the database."
    except Exception as e:
        conn.close()
        return False, str(e)


def export_full_dataset_excel() -> bytes:
    """Generates a 10,000+ record Excel workbook with 5 sheets covering all relational data."""
    import io as _io
    conn = get_connection()

    df_teachers = pd.read_sql_query("""
        SELECT
            t.teacher_id  AS "Teacher ID",
            t.name        AS "Teacher Name",
            COALESCE(t.dob, 'N/A')                        AS "Date of Birth",
            COALESCE(t.qualifications, 'Not Specified')   AS "Qualifications",
            COALESCE(t.experience_school, 0)              AS "Exp (Current School, yrs)",
            COALESCE(t.experience_prev, 0)                AS "Exp (Previous, yrs)",
            COALESCE(t.section, 'N/A')                    AS "Section",
            COALESCE(t.classes_per_week, 0)               AS "Classes Per Week",
            COALESCE(t.subjects, 'N/A')                   AS "Subjects"
        FROM teachers t ORDER BY t.name ASC
    """, conn)

    df_late = pd.read_sql_query("""
        SELECT
            t.name        AS "Teacher Name",
            t.section     AS "Section",
            l.month       AS "Month",
            l.year        AS "Year",
            COALESCE(l.late_count, 0)       AS "Late Count",
            COALESCE(l.unplanned_leaves, 0) AS "Unplanned Leaves"
        FROM late_counts l
        JOIN teachers t ON l.teacher_id = t.teacher_id
        ORDER BY t.name ASC, l.year ASC, l.id ASC
    """, conn)

    df_benchmark = pd.read_sql_query("""
        SELECT
            t.name   AS "Teacher Name",
            t.section AS "Section",
            COALESCE(b.int_bm_score, 60.0)       AS "Internal BM Score (%)",
            COALESCE(b.ext_bm_score, 55.0)       AS "External BM Score (%)",
            COALESCE(b.compliance_score, 5.0)    AS "Compliance Score (/10)",
            COALESCE(b.training_hours, 10)       AS "Training Hours",
            COALESCE(b.assignment_stars, 3)      AS "Assignment Stars (/3)",
            COALESCE(b.co_curricular_count, 6)   AS "Co-Curricular Activities",
            COALESCE(b.co_curricular_quality, 'N/A') AS "Co-Curricular Quality",
            ROUND((COALESCE(b.int_bm_score,60) + COALESCE(b.ext_bm_score,55)
                   + COALESCE(b.compliance_score,5)*10) / 3.0, 1) AS "Overall Score"
        FROM benchmark_scores b
        JOIN teachers t ON b.teacher_id = t.teacher_id
        ORDER BY "Overall Score" DESC
    """, conn)

    df_attrition = pd.read_sql_query("""
        SELECT
            t.name   AS "Teacher Name",
            t.section AS "Section",
            COALESCE(a.attrition_score, 0.0)             AS "Attrition Score",
            COALESCE(a.attrition_type, 'No Risk')        AS "Risk Level",
            COALESCE(a.explanation, 'No active risk.')   AS "Reason / Explanation"
        FROM attrition a
        JOIN teachers t ON a.teacher_id = t.teacher_id
        ORDER BY a.attrition_score DESC, t.name ASC
    """, conn)

    df_ratings = pd.read_sql_query("""
        SELECT
            t.name   AS "Teacher Name",
            t.section AS "Section",
            COALESCE(s.head_stars, 3)    AS "Head Rating (/3)",
            COALESCE(s.peer_stars, 3)    AS "Peer Rating (/3)",
            COALESCE(s.student_stars, 3) AS "Student Rating (/3)",
            COALESCE(s.parent_stars, 3)  AS "Parent Rating (/3)",
            ROUND((COALESCE(s.head_stars,3)+COALESCE(s.peer_stars,3)
                   +COALESCE(s.student_stars,3)+COALESCE(s.parent_stars,3))/4.0,1)
                   AS "Avg Stakeholder Rating"
        FROM stakeholder_ratings s
        JOIN teachers t ON s.teacher_id = t.teacher_id
        ORDER BY t.name ASC
    """, conn)

    conn.close()

    output = _io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_teachers.to_excel(writer,  sheet_name='Teacher Profiles',   index=False)
        df_late.to_excel(writer,      sheet_name='Monthly Late Counts', index=False)
        df_benchmark.to_excel(writer, sheet_name='Benchmark Scores',    index=False)
        df_attrition.to_excel(writer, sheet_name='Attrition Records',   index=False)
        df_ratings.to_excel(writer,   sheet_name='Stakeholder Ratings', index=False)

    return output.getvalue()
