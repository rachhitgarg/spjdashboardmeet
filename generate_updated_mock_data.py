import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_ai_tutor_mock_data():
    """Generate mock data for AI Tutor template"""
    print("Generating AI Tutor mock data...")
    
    # Sample data based on the template structure with MBA subjects
    campuses = ['SG', 'MUM', 'SYD', 'DXB']
    courses = ['GCGM', 'MGB', 'GMBA']
    cohorts = ['Jan-22', 'Jul-22', 'Jan-23', 'Jul-23', 'Jan-24', 'Jul-24']
    # MBA Subject Names (replacing Unit 1, Unit 2, etc.)
    mba_subjects = [
        'Corporate Finance', 'Digital Marketing', 'Business Analytics', 'Strategic Management',
        'Operations Management', 'Human Resource Management', 'International Business',
        'Financial Accounting', 'Organizational Behavior', 'Supply Chain Management',
        'Investment Banking', 'Consumer Behavior', 'Data Science', 'Leadership & Change',
        'Project Management', 'Business Law', 'Global Economics', 'Marketing Research',
        'Financial Markets', 'Business Intelligence', 'Innovation Management', 'Risk Management'
    ]
    
    # Faculty names (avoiding Jain)
    faculty_names = ['Smith', 'Johnson', 'Brown', 'Davis', 'Wilson', 'Miller', 'Jones', 'Garcia', 
                    'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Jackson', 'White', 'Harris', 'Martin']
    
    data = []
    for i in range(200):  # Generate 200 records
        campus = random.choice(campuses)
        course = random.choice(courses)
        cohort = random.choice(cohorts)
        subject = random.choice(mba_subjects)
        
        # Generate realistic data with proper scaling
        batch_size = random.randint(20, 50)
        sessions_created = random.randint(5, 25)
        # Fix adoption rate calculation - students participated should be <= batch_size
        students_participated = random.randint(int(batch_size * 0.6), batch_size)
        students_attempted_quiz = random.randint(int(students_participated * 0.7), students_participated)
        # Quiz scores out of 10 (not 100)
        avg_quiz_score = random.uniform(6.0, 10.0)
        students_feedback = random.randint(int(students_participated * 0.8), students_participated)
        faculty_rating = random.uniform(6.0, 10.0)  # Faculty rating out of 10
        ai_quality_score = random.uniform(6.0, 10.0)  # AI quality score out of 10
        ai_impact_score = random.uniform(6.0, 10.0)   # AI impact score out of 10
        avg_rating = random.uniform(7.0, 10.0)        # Average rating out of 10
        # Sensible quiz count between 2-12 (as per business rule)
        quizzes_conducted = random.randint(2, 12)
        # Quiz score out of 10
        avg_quiz_score_final = random.uniform(6.5, 10.0)
        
        data.append({
            'Campus (SG/MUM/SYD/DXB)': campus,
            'Course(GCGM/MGM/GMBA)': course,
            'Cohort': cohort,
            'Unit_Name': subject,
            'Batch_size(number should come from student feedback form)': batch_size,
            'Faculty Name': f'Prof_{random.choice(faculty_names)}',
            'Faculty_Email_ID': f'prof_{random.randint(1, 100)}@spjain.edu',
            'Unit_Commencement_date': (datetime.now() - timedelta(days=random.randint(30, 365))).strftime('%d-%b-%Y'),
            'Unit_End_Date': (datetime.now() - timedelta(days=random.randint(1, 30))).strftime('%d-%b-%Y'),
            'No_of_Session_IDs_created': sessions_created,
            'Total_Students_Participated_watched videos': students_participated,
            'Total_Students_Attempted_AI Tutor Platform Quiz': students_attempted_quiz,
            'Average Score of AI Tutor Platform Quiz': round(avg_quiz_score, 1),
            'No_of_students_who_filled_student feedback form': students_feedback,
            'Faculty_Rating_provide by students': round(faculty_rating, 2),
            'AI_Tutor_quality_score': round(ai_quality_score, 2),
            'AI_Tutor_impact_score': round(ai_impact_score, 2),
            'Avg_Rating_for_AI_Tutor_Tool': round(avg_rating, 2),
            'Faculty_Implemented_AI_Tutor_efficiently(Yes/No)': random.choice(['Yes', 'No']),
            'No. of Quizzes_conducted': quizzes_conducted,
            'AI_Quizzes_used_for_grading': random.choice(['Yes', 'No']),
            'Average_ Quiz_Score': round(avg_quiz_score_final, 1),
            'Faculty_Feedback': random.choice(['Very Positive', 'Positive', 'Neutral', 'Negative'])
        })
    
    df = pd.DataFrame(data)
    df.to_csv('ai_tutor template updated.csv', index=False)
    print(f"✅ Generated {len(df)} AI Tutor records")
    return df

def generate_ai_mentor_mock_data():
    """Generate mock data for AI Mentor template"""
    print("Generating AI Mentor mock data...")
    
    courses = ['GCGM', 'MGB', 'GMBA']
    cohorts = ['Jan-22', 'Jul-22', 'Jan-23', 'Jul-23', 'Jan-24', 'Jul-24']
    terms = ['Term 1', 'Term 2', 'Term 3', 'Term 4']
    project_types = ['ARP', 'IBR 1', 'IBR 2', 'Industry Project']
    
    # Academic manager names (avoiding Jain)
    manager_names = ['Singh', 'Patel', 'Sharma', 'Kumar', 'Gupta', 'Agarwal', 'Verma', 'Lee',
                    'Chen', 'Wong', 'Tan', 'Lim', 'Rao', 'Nair', 'Reddy', 'Iyer']
    
    data = []
    for i in range(150):  # Generate 150 records
        data.append({
            'Academic_Manager_Name': f'AM_{random.choice(manager_names)}',
            'Course': random.choice(courses),
            'Cohort': random.choice(cohorts),
            'Term': random.choice(terms),
            'Project Type (ARP, IBR 1, IBR 2, Industry Project)': random.choice(project_types),
            'Total Number of students/teams  mentoring/mentored': random.randint(5, 25),
            "Q1_Are Students_motivated to use AI Mentor? (Yes/No, as they don't find it useful)": random.choice(['Yes', 'No']),
            'Q2_Are students using AI Mentor effectively ? (Yes/No)': random.choice(['Yes', 'No']),
            'Q3_Have you mandated students to meet you only after obtaining suggestions from AI Mentor? (Yes/No)': random.choice(['Yes', 'No']),
            "Q4_Improvement_observed in student's logical thinking, Presentation & Report Structure with the use of AI Mentor (Yes/No)": random.choice(['Yes', 'No']),
            'Approx. percentage of students under your guidance who levelled up using AI Mentor.': random.randint(20, 90)
        })
    
    df = pd.DataFrame(data)
    df.to_csv('ai_mentor_template - updated.csv', index=False)
    print(f"✅ Generated {len(df)} AI Mentor records")
    return df

def generate_ai_impact_mock_data():
    """Generate mock data for AI Impact template"""
    print("Generating AI Impact mock data...")
    
    courses = ['GCGM', 'MGB', 'GMBA']
    cohorts = ['Jan-22', 'Jul-22', 'Jan-23', 'Jul-23', 'Jan-24', 'Jul-24']
    usage_levels = ['None', 'Low', 'Medium', 'High']
    
    data = []
    for i in range(500):  # Generate 500 records
        data.append({
            'Student Name': f'Student_{i+1}_{random.choice(cohorts)}',
            'Student _mail id': f'student{i+1}@{random.choice(cohorts).lower()}.spjain.edu',
            'Course': random.choice(courses),
            'Cohort': random.choice(cohorts),
            'Placed/Not Placed': random.choice(['Placed', 'Not Placed']),
            'CGPA': round(random.uniform(2.5, 4.0), 2),
            'AI Tutor Usage': random.choice(usage_levels),
            'AI Mentor Usage': random.choice(usage_levels),
            'JPT Usage': random.choice(usage_levels),
            'Yoodli Usage': random.choice(usage_levels)
        })
    
    df = pd.DataFrame(data)
    df.to_csv('AI-initiatives impact updated.csv', index=False)
    print(f"✅ Generated {len(df)} AI Impact records")
    return df

def generate_ai_tkt_mock_data():
    """Generate mock data for AI TKT template"""
    print("Generating AI TKT mock data...")
    
    # MBA Subject Names (replacing Unit 1, Unit 2, etc.)
    mba_subjects = [
        'Corporate Finance', 'Digital Marketing', 'Business Analytics', 'Strategic Management',
        'Operations Management', 'Human Resource Management', 'International Business',
        'Financial Accounting', 'Organizational Behavior', 'Supply Chain Management',
        'Investment Banking', 'Consumer Behavior', 'Data Science', 'Leadership & Change'
    ]
    courses = ['GCGM', 'MGB', 'GMBA']
    
    data = []
    for i in range(100):  # Generate 100 records
        subject = random.choice(mba_subjects)
        course = random.choice(courses)
        before_score = random.uniform(60, 80)
        after_score = before_score + random.uniform(5, 20)  # Improvement after AI TKT
        improvement = ((after_score - before_score) / before_score) * 100
        
        data.append({
            'Unit': subject,
            'Course': course,
            'Average Grades Before AI for TKT': round(before_score, 1),
            'Avergae Grades After AI for TKT': round(after_score, 1),
            'Improvement%': round(improvement, 1)
        })
    
    df = pd.DataFrame(data)
    df.to_csv('AI_ TKT _ Template updated.csv', index=False)
    print(f"✅ Generated {len(df)} AI TKT records")
    return df

def generate_unit_performance_mock_data():
    """Generate mock data for Unit Performance template"""
    print("Generating Unit Performance mock data...")
    
    courses = ['GCGM', 'MGB', 'GMBA']
    cohorts = ['Jan-22', 'Jul-22', 'Jan-23', 'Jul-23', 'Jan-24', 'Jul-24']
    years = [2022, 2023, 2024]
    # MBA Subject Names (replacing Unit 1, Unit 2, etc.)
    mba_subjects = [
        'Corporate Finance', 'Digital Marketing', 'Business Analytics', 'Strategic Management',
        'Operations Management', 'Human Resource Management', 'International Business',
        'Financial Accounting', 'Organizational Behavior', 'Supply Chain Management'
    ]
    
    data = []
    for i in range(200):  # Generate 200 records
        course = random.choice(courses)
        cohort = random.choice(cohorts)
        year = random.choice(years)
        subject = random.choice(mba_subjects)
        ai_tutor_status = random.choice(['Before', 'After'])
        
        # Before AI tutor: lower scores, After AI tutor: higher scores
        if ai_tutor_status == 'Before':
            total_score = random.uniform(65, 80)
        else:
            total_score = random.uniform(75, 90)
        
        data.append({
            'Course': course,
            'Cohort': cohort,
            'Year': year,
            'Unit_Name': subject,
            'AI Tutor (Before/After)': ai_tutor_status,
            'Total_Avg_score': round(total_score, 1)
        })
    
    df = pd.DataFrame(data)
    df.to_csv('unit_performance_template -updated.csv', index=False)
    print(f"✅ Generated {len(df)} Unit Performance records")
    return df

def generate_cr_mock_data():
    """Generate mock data for CR (Corporate Relations) template with JPT impact correlation"""
    print("Generating CR mock data...")
    
    courses = ['GCGM', 'MGB', 'GMBA']
    cohorts = ['Jan-22', 'Jul-22', 'Jan-23', 'Jul-23', 'Jan-24', 'Jul-24']
    years = [2022, 2023, 2024]
    industries = ['Technology', 'Finance', 'Consulting', 'Healthcare', 'Manufacturing', 'Retail', 'Education']
    companies = ['Microsoft', 'Google', 'Amazon', 'TCS', 'Infosys', 'Accenture', 'Deloitte', 'PwC', 'EY', 'KPMG']
    tiers = ['Tier 1', 'Tier 2', 'Tier 3']
    locations = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune', 'Kolkata']
    
    data = []
    for i in range(300):  # Generate 300 records
        company = random.choice(companies)
        industry = random.choice(industries)
        tier = random.choice(tiers)
        location = random.choice(locations)
        course = random.choice(courses)
        cohort = random.choice(cohorts)
        year = random.choice(years)
        
        vacancies = random.randint(2, 15)
        eligible = random.randint(20, 50)
        applied = random.randint(int(eligible * 0.6), eligible)
        interviewed = random.randint(int(applied * 0.7), applied)
        
        # JPT usage affects conversion rates
        jpt_used = random.choice(['Yes', 'No'])
        
        # Higher conversion rates for JPT users
        if jpt_used == 'Yes':
            conversion_rate = random.uniform(0.4, 0.7)  # 40-70% for JPT users
            avg_ctc_base = random.uniform(12, 30)  # Higher packages for JPT users
        else:
            conversion_rate = random.uniform(0.2, 0.5)  # 20-50% for non-JPT users
            avg_ctc_base = random.uniform(8, 20)   # Lower packages for non-JPT users
        
        selected = max(1, int(interviewed * conversion_rate))
        selected = min(selected, vacancies)  # Can't select more than vacancies
        
        # CTC varies by tier and JPT usage
        if tier == 'Tier 1':
            avg_ctc = avg_ctc_base * random.uniform(1.2, 1.5)
        elif tier == 'Tier 2':
            avg_ctc = avg_ctc_base * random.uniform(1.0, 1.2)
        else:  # Tier 3
            avg_ctc = avg_ctc_base * random.uniform(0.8, 1.0)
        
        highest_ctc = avg_ctc + random.uniform(2, 8)
        
        data.append({
            'Course': course,
            'Cohort': cohort,
            'Year': year,
            'Industry_Sector': industry,
            'Company Name': company,
            'Company_Tier': tier,
            'Job_role': f'{industry} {random.choice(["Analyst", "Consultant", "Manager", "Specialist", "Lead"])}',
            'Location': location,
            'No. of Vacancies_Offered': vacancies,
            'Date of first interview(mm/dd/yyyy)': (datetime.now() - timedelta(days=random.randint(1, 180))).strftime('%m/%d/%Y'),
            'No. of Students_Eligible': eligible,
            'No. of students applied': applied,
            'No. of Students_Interviewed': interviewed,
            'Students_Selected': selected,
            'Avg_CTC(in USD)': round(avg_ctc, 1),
            'Highest_CTC(in USD)': round(highest_ctc, 1),
            'Students used JPT(Yes/No)': jpt_used
        })
    
    df = pd.DataFrame(data)
    df.to_csv('CR_template -updated.csv', index=False)
    print(f"✅ Generated {len(df)} CR records with JPT impact correlation")
    return df

def generate_prp_mock_data():
    """Generate mock data for PRP (Placement Readiness Program) template with JPT correlation"""
    print("Generating PRP mock data...")
    
    courses = ['GCGM', 'MGB', 'GMBA']
    cohorts = ['Jan-22', 'Jul-22', 'Jan-23', 'Jul-23', 'Jan-24', 'Jul-24']
    years = [2022, 2023, 2024]
    categories = ['Outstanding', 'Good', 'Average', 'Needs Handholding']
    
    data = []
    for i in range(400):  # Generate 400 records
        course = random.choice(courses)
        cohort = random.choice(cohorts)
        year = random.choice(years)
        
        # Generate term-wise scores (out of 100)
        term1_score = random.uniform(70, 95)
        term2_score = random.uniform(70, 95)
        term3_score = random.uniform(70, 95)
        avg_term_score = (term1_score + term2_score + term3_score) / 3
        
        # Generate JPT mock interview attempts with correlation to performance
        # Better students tend to have more high-scoring JPT attempts
        if avg_term_score >= 85:
            jpt_attempts_above_80 = random.randint(3, 8)  # High performers
        elif avg_term_score >= 75:
            jpt_attempts_above_80 = random.randint(1, 5)  # Medium performers
        else:
            jpt_attempts_above_80 = random.randint(0, 3)  # Lower performers
        
        # Generate area head mock interview scores with correlation to term scores
        area_head_score = avg_term_score + random.uniform(-10, 10)
        area_head_score = max(60, min(100, area_head_score))  # Keep within bounds
        
        # Generate allocated interview attempts
        allocated_attempts = random.randint(3, 8)
        
        # Generate overall categorization based on performance
        if avg_term_score >= 90 and jpt_attempts_above_80 >= 3:
            category = 'Outstanding'
            placement_probability = 0.8
        elif avg_term_score >= 80 and jpt_attempts_above_80 >= 2:
            category = 'Good'
            placement_probability = 0.6
        elif avg_term_score >= 70 and jpt_attempts_above_80 >= 1:
            category = 'Average'
            placement_probability = 0.4
        else:
            category = 'Needs Handholding'
            placement_probability = 0.2
        
        # Generate placement status with correlation to performance and JPT usage
        placed = 'Placed' if random.random() < placement_probability else 'Not Placed'
        if placed == 'Placed':
            attempts_for_placement = random.randint(1, min(allocated_attempts, 5))
        else:
            attempts_for_placement = 0
        
        data.append({
            'Student Roll No.': f'SPJ{year}{random.randint(1000, 9999)}',
            'Student Name': f'Student_{i+1}_{cohort}',
            'Email id': f'student{i+1}@{cohort.lower()}.spjain.edu',
            'Course': course,
            'Cohort': cohort,
            'Year': year,
            'Term-1': round(term1_score, 1),
            'Term-2': round(term2_score, 1),
            'Term-3': round(term3_score, 1),
            'No. of JPT Mock Interviews attempted and scored equal or above 80%': jpt_attempts_above_80,
            'Area Head Mock Interview Score': round(area_head_score, 1),
            'No. of Allocated Interview Attempts': allocated_attempts,
            'Categorise student overall (Outstanding, Good, Average, Needs Handholding)': category,
            'Placed/Not Placed': placed,
            'If placed, no. of interview attempts required for placement': attempts_for_placement
        })
    
    df = pd.DataFrame(data)
    df.to_csv('PRP_template - updated.csv', index=False)
    print(f"✅ Generated {len(df)} PRP records with JPT correlation")
    return df

def main():
    """Generate all mock data"""
    print("=" * 80)
    print("GENERATING MOCK DATA FOR ALL TEMPLATES")
    print("=" * 80)
    print(f"Generation started at: {datetime.now()}")
    print()
    
    # Set random seed for reproducibility
    random.seed(42)
    np.random.seed(42)
    
    try:
        # Generate mock data for all templates
        ai_tutor_df = generate_ai_tutor_mock_data()
        ai_mentor_df = generate_ai_mentor_mock_data()
        ai_impact_df = generate_ai_impact_mock_data()
        ai_tkt_df = generate_ai_tkt_mock_data()
        unit_performance_df = generate_unit_performance_mock_data()
        cr_df = generate_cr_mock_data()
        prp_df = generate_prp_mock_data()
        
        print("\n" + "=" * 80)
        print("MOCK DATA GENERATION SUMMARY")
        print("=" * 80)
        
        total_records = (len(ai_tutor_df) + len(ai_mentor_df) + len(ai_impact_df) + 
                        len(ai_tkt_df) + len(unit_performance_df) + len(cr_df) + len(prp_df))
        
        print(f"Total records generated: {total_records:,}")
        print()
        print("✅ AI Tutor:", len(ai_tutor_df), "records")
        print("✅ AI Mentor:", len(ai_mentor_df), "records")
        print("✅ AI Impact:", len(ai_impact_df), "records")
        print("✅ AI TKT:", len(ai_tkt_df), "records")
        print("✅ Unit Performance:", len(unit_performance_df), "records")
        print("✅ CR (Corporate Relations):", len(cr_df), "records")
        print("✅ PRP (Placement Readiness Program):", len(prp_df), "records")
        
        print("\n" + "=" * 80)
        print("All mock data files have been generated successfully!")
        print("You can now run the dashboard with realistic data for testing.")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error generating mock data: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()
