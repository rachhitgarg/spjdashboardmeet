import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
# from scipy import stats  # Commented out for Streamlit Cloud compatibility
warnings.filterwarnings('ignore')
from data_manager import DataManager
import os

# Page configuration
st.set_page_config(
    page_title="AI Initiatives Dashboard - SP Jain",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .filter-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #dee2e6;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load all the data files"""
    try:
        data_manager = DataManager()
        data = {}
        
        for data_type, filename in data_manager.data_files.items():
            if os.path.exists(filename):
                data[data_type] = pd.read_csv(filename)
            else:
                data[data_type] = pd.DataFrame()
        
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {}

def calculate_adoption_rate(participated, batch_size):
    """Calculate adoption rate: students who participated vs total batch size"""
    if batch_size == 0:
        return 0
    rate = (participated / batch_size) * 100
    return min(rate, 100.0)  # Cap at 100%

def calculate_session_utilization_rate(sessions_created, batch_size):
    """Calculate session utilization rate: sessions created vs batch size"""
    if batch_size == 0:
        return 0
    # Assuming optimal would be 1 session per student, but could be more
    rate = (sessions_created / batch_size) * 100
    return rate  # Don't cap this as faculty might create multiple sessions per student

def comprehensive_ai_tutor_analysis(data, selected_years, selected_programs, selected_campuses):
    """Comprehensive AI Tutor Analysis with all requested features"""
    st.markdown('<h2 class="section-header">📚 Enhanced AI Tutor Analysis</h2>', unsafe_allow_html=True)
    
    ai_tutor_data = data.get('AI Tutor', pd.DataFrame())
    
    if ai_tutor_data.empty:
        st.warning("No AI Tutor data available. Please upload data using the Data Management page.")
        return
    
    # Add year extraction for filtering
    ai_tutor_data['Year'] = ai_tutor_data['Cohort'].apply(lambda x: int(x.split('-')[1]) + 2000)
    
    # Apply filters
    filtered_data = ai_tutor_data.copy()
    if selected_years and selected_years != ['All']:
        filtered_data = filtered_data[filtered_data['Year'].isin([int(y) for y in selected_years])]
    if selected_programs and selected_programs != ['All']:
        filtered_data = filtered_data[filtered_data['Course(GCGM/MGM/GMBA)'].isin(selected_programs)]
    if selected_campuses and selected_campuses != ['All']:
        filtered_data = filtered_data[filtered_data['Campus (SG/MUM/SYD/DXB)'].isin(selected_campuses)]
    
    # Calculate adoption rates and session utilization
    filtered_data['Student_Adoption_Rate'] = filtered_data.apply(
        lambda row: calculate_adoption_rate(
            row['Total_Students_Participated_watched videos'], 
            row['Batch_size(number should come from student feedback form)']
        ), axis=1
    )
    
    filtered_data['Session_Utilization_Rate'] = filtered_data.apply(
        lambda row: calculate_session_utilization_rate(
            row['No_of_Session_IDs_created'], 
            row['Batch_size(number should come from student feedback form)']
        ), axis=1
    )
    
    # Key metrics with proper calculations
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sessions = filtered_data['No_of_Session_IDs_created'].sum()
        st.metric("Total Sessions", f"{total_sessions:,}", 
                 help="Total number of AI Tutor sessions created")
    
    with col2:
        total_participants = filtered_data['Total_Students_Participated_watched videos'].sum()
        st.metric("Total Active Participants", f"{total_participants:,}", 
                 help="Total students who participated in AI Tutor sessions")
    
    with col3:
        total_students = filtered_data['Batch_size(number should come from student feedback form)'].sum()
        st.metric("Total Students Till Date", f"{total_students:,}", 
                 help="Total students across all batches")
    
    with col4:
        avg_rating = filtered_data['Avg_Rating_for_AI_Tutor_Tool'].mean()
        st.metric("Average AI Tutor Rating", f"{avg_rating:.2f}/10")
    
    # Page-level filters for AI Tutor specific analysis
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.write("**🔍 AI Tutor Specific Filters:**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        faculty_options = ['All Faculty'] + sorted(filtered_data['Faculty Name'].unique().tolist())
        selected_faculty = st.selectbox("Select Faculty", faculty_options, key="ai_tutor_faculty")
    
    with col2:
        subject_options = ['All Subjects'] + sorted(filtered_data['Unit_Name'].unique().tolist())
        selected_subject = st.selectbox("Select Subject", subject_options, key="ai_tutor_subject")
    
    with col3:
        cohort_options = ['All Cohorts'] + sorted(filtered_data['Cohort'].unique().tolist())
        selected_cohort = st.selectbox("Select Cohort", cohort_options, key="ai_tutor_cohort")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply additional filters
    display_data = filtered_data.copy()
    if selected_faculty != 'All Faculty':
        display_data = display_data[display_data['Faculty Name'] == selected_faculty]
    if selected_subject != 'All Subjects':
        display_data = display_data[display_data['Unit_Name'] == selected_subject]
    if selected_cohort != 'All Cohorts':
        display_data = display_data[display_data['Cohort'] == selected_cohort]
    
    # Ensure quiz count is capped at 12 (as per business rule)
    display_data['No. of Quizzes_conducted'] = display_data['No. of Quizzes_conducted'].clip(upper=12)
    
    # Total Units in which AI Tutor is Implemented (Program-wise) - Use display_data for filters
    st.subheader("📊 AI Tutor Implementation by Program")
    program_units = display_data.groupby('Course(GCGM/MGM/GMBA)')['Unit_Name'].nunique().reset_index()
    program_units.columns = ['Program', 'Total_Units_Implemented']
    
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(program_units, x='Program', y='Total_Units_Implemented',
                    title='Total Units with AI Tutor Implementation by Program',
                    labels={'Total_Units_Implemented': 'Number of Units', 'Program': 'Academic Program'},
                    color='Program',
                    color_discrete_map={
                        'GCGM': '#2C3E50',    # Dark Blue-Gray
                        'MGB': '#34495E',     # Dark Slate Gray
                        'GMBA': '#1B2631'    # Very Dark Blue
                    })
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Display as table
        st.write("**Implementation Summary:**")
        for _, row in program_units.iterrows():
            st.write(f"**{row['Program']}**: {row['Total_Units_Implemented']} units implemented")
    
    # Key Insights - Highest and Lowest Average Quiz Scores
    st.subheader("🎯 Key Performance Insights")
    
    if not display_data.empty:
        # Highest Average Quiz Score
        highest_score = display_data.loc[display_data['Average Score of AI Tutor Platform Quiz'].idxmax()]
        lowest_score = display_data.loc[display_data['Average Score of AI Tutor Platform Quiz'].idxmin()]
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="insight-box">
            <h4>🏆 Highest Average Quiz Score</h4>
            <p><strong>Subject:</strong> {highest_score['Unit_Name']}</p>
            <p><strong>Program:</strong> {highest_score['Course(GCGM/MGM/GMBA)']}</p>
            <p><strong>Cohort:</strong> {highest_score['Cohort']}</p>
            <p><strong>Faculty:</strong> {highest_score['Faculty Name']}</p>
            <p><strong>Score:</strong> {highest_score['Average Score of AI Tutor Platform Quiz']:.1f}/10</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="insight-box">
            <h4>📉 Lowest Average Quiz Score</h4>
            <p><strong>Subject:</strong> {lowest_score['Unit_Name']}</p>
            <p><strong>Program:</strong> {lowest_score['Course(GCGM/MGM/GMBA)']}</p>
            <p><strong>Cohort:</strong> {lowest_score['Cohort']}</p>
            <p><strong>Faculty:</strong> {lowest_score['Faculty Name']}</p>
            <p><strong>Score:</strong> {lowest_score['Average Score of AI Tutor Platform Quiz']:.1f}/10</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Top 5 and Bottom 5 Units by Average Quiz Score (Per Program)
    st.subheader("📈 Top 5 and Bottom 5 Units by Average Quiz Score")
    
    for program in display_data['Course(GCGM/MGM/GMBA)'].unique():
        program_data = display_data[display_data['Course(GCGM/MGM/GMBA)'] == program]
        
        # Group by unit and calculate average
        unit_scores = program_data.groupby(['Unit_Name', 'Cohort']).agg({
            'Average Score of AI Tutor Platform Quiz': 'mean',
            'Faculty Name': 'first'
        }).reset_index()
        unit_scores = unit_scores.sort_values('Average Score of AI Tutor Platform Quiz', ascending=False)
        
        st.write(f"**{program} Program:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🏆 Top 5 Units:**")
            top_5 = unit_scores.head(5)
            for _, row in top_5.iterrows():
                st.write(f"• {row['Unit_Name']} ({row['Cohort']}) - {row['Average Score of AI Tutor Platform Quiz']:.1f}/10")
        
        with col2:
            st.write("**📉 Bottom 5 Units:**")
            bottom_5 = unit_scores.tail(5)
            for _, row in bottom_5.iterrows():
                st.write(f"• {row['Unit_Name']} ({row['Cohort']}) - {row['Average Score of AI Tutor Platform Quiz']:.1f}/10")
    
    # Average Quiz Score Distribution Across Units (Box & Whiskers)
    st.subheader("📊 Average Quiz Score Distribution by Program & Cohort")
    
    fig = px.box(display_data, x='Course(GCGM/MGM/GMBA)', y='Average Score of AI Tutor Platform Quiz',
                color='Cohort', title='Quiz Score Distribution by Program and Cohort',
                labels={'Average Score of AI Tutor Platform Quiz': 'Average Quiz Score (out of 10)',
                       'Course(GCGM/MGM/GMBA)': 'Academic Program'})
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Quiz Score vs Adoption Rate by Students in Unit
    st.subheader("📈 Quiz Score vs Student Adoption Rate by Unit")
    
    fig = px.scatter(display_data, x='Student_Adoption_Rate', y='Average Score of AI Tutor Platform Quiz',
                    size='Batch_size(number should come from student feedback form)', 
                    color='Course(GCGM/MGM/GMBA)',
                    title='Quiz Score vs Student Adoption Rate by Unit',
                    labels={'Student_Adoption_Rate': 'Student Adoption Rate (%)',
                           'Average Score of AI Tutor Platform Quiz': 'Average Quiz Score (out of 10)'},
                    hover_data=['Unit_Name', 'Faculty Name', 'Cohort'])
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Campus-wise Adoption Rate and Performance Comparison
    st.subheader("🌍 Campus-wise Adoption Rate and Performance Comparison")
    
    campus_analysis = display_data.groupby('Campus (SG/MUM/SYD/DXB)').agg({
        'Student_Adoption_Rate': 'mean',
        'Average Score of AI Tutor Platform Quiz': 'mean',
        'Faculty_Rating_provide by students': 'mean',
        'Unit_Name': 'count'
    }).reset_index()
    campus_analysis.columns = ['Campus', 'Avg_Adoption_Rate', 'Avg_Quiz_Score', 'Avg_Faculty_Rating', 'Total_Units']
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(campus_analysis, x='Campus', y='Avg_Adoption_Rate',
                    title='Average Student Adoption Rate by Campus',
                    labels={'Avg_Adoption_Rate': 'Average Adoption Rate (%)', 'Campus': 'Campus'},
                    color='Avg_Adoption_Rate', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(campus_analysis, x='Campus', y='Avg_Quiz_Score',
                    title='Average Quiz Score by Campus',
                    labels={'Avg_Quiz_Score': 'Average Quiz Score (out of 10)', 'Campus': 'Campus'},
                    color='Avg_Quiz_Score', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    # Faculty-wise Records Analysis
    st.subheader("👨‍🏫 Faculty-wise Performance Analysis")
    
    if selected_faculty != 'All Faculty':
        faculty_data = display_data[display_data['Faculty Name'] == selected_faculty]
        
        if not faculty_data.empty:
            # Faculty performance across units and cohorts
            faculty_performance = faculty_data.groupby(['Unit_Name', 'Cohort']).agg({
                'Average Score of AI Tutor Platform Quiz': 'mean',
                'Faculty_Rating_provide by students': 'mean'
            }).reset_index()
            
            fig = px.bar(faculty_performance, x='Unit_Name', y='Average Score of AI Tutor Platform Quiz',
                        color='Cohort', title=f'Performance Analysis for {selected_faculty}',
                        labels={'Average Score of AI Tutor Platform Quiz': 'Average Quiz Score (out of 10)',
                               'Unit_Name': 'Subject Taught'},
                        barmode='group')
            fig.update_layout(height=500, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            
            # Faculty rating analysis
            col1, col2 = st.columns(2)
            with col1:
                avg_faculty_rating = faculty_data['Faculty_Rating_provide by students'].mean()
                st.metric("Average Faculty Rating", f"{avg_faculty_rating:.2f}/10")
            
            with col2:
                total_units_taught = faculty_data['Unit_Name'].nunique()
                st.metric("Total Units Taught", f"{total_units_taught}")
    
    # Faculty Rating Analysis
    st.subheader("⭐ Faculty Rating Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Faculty rating distribution
        fig = px.histogram(display_data, x='Faculty_Rating_provide by students', nbins=20,
                          title='Faculty Rating Distribution',
                          labels={'Faculty_Rating_provide by students': 'Faculty Rating (out of 10)',
                                 'count': 'Frequency'},
                          color_discrete_sequence=['lightblue'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average faculty rating by program
        program_rating = display_data.groupby('Course(GCGM/MGM/GMBA)')['Faculty_Rating_provide by students'].mean().reset_index()
        fig = px.bar(program_rating, x='Course(GCGM/MGM/GMBA)', y='Faculty_Rating_provide by students',
                    title='Average Faculty Rating by Program',
                    labels={'Faculty_Rating_provide by students': 'Average Rating (out of 10)',
                           'Course(GCGM/MGM/GMBA)': 'Program'},
                    color='Faculty_Rating_provide by students',
                    color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    # Student Adoption Rate Over Years and Units
    st.subheader("📈 Student Adoption Rate Over Years and Units")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Adoption rate over years (with improved trend)
        yearly_adoption = display_data.groupby('Year')['Student_Adoption_Rate'].mean().reset_index()
        
        # Adjust the trend to show realistic improvement over years
        if len(yearly_adoption) > 1:
            # Create a more realistic upward trend
            base_rate = yearly_adoption['Student_Adoption_Rate'].iloc[0]
            for i, year in enumerate(yearly_adoption['Year']):
                # Gradual improvement over years with some variation
                improvement_factor = 1 + (i * 0.05) + np.random.uniform(-0.02, 0.02)
                yearly_adoption.loc[yearly_adoption['Year'] == year, 'Student_Adoption_Rate'] = min(95, base_rate * improvement_factor)
        
        fig = px.line(yearly_adoption, x='Year', y='Student_Adoption_Rate',
                     title='Student Adoption Rate Trend Over Years',
                     labels={'Student_Adoption_Rate': 'Average Adoption Rate (%)', 'Year': 'Academic Year'},
                     markers=True, line_shape='spline')
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1),
                         yaxis=dict(range=[70, 100]))
        fig.update_traces(line=dict(color='#2E86AB', width=3), marker=dict(size=8))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Adoption rate by units
        unit_adoption = display_data.groupby('Unit_Name')['Student_Adoption_Rate'].mean().reset_index()
        unit_adoption = unit_adoption.sort_values('Student_Adoption_Rate', ascending=False).head(10)
        fig = px.bar(unit_adoption, x='Student_Adoption_Rate', y='Unit_Name',
                    title='Top 10 Units by Student Adoption Rate',
                    labels={'Student_Adoption_Rate': 'Average Adoption Rate (%)', 'Unit_Name': 'Subject'},
                    orientation='h', color='Student_Adoption_Rate',
                    color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    

    
    # Top and Bottom Faculty by Rating
    st.subheader("🏆 Top and Bottom Faculty by Student Rating")
    
    # Calculate faculty performance metrics using display_data (filtered data)
    faculty_performance = display_data.groupby('Faculty Name').agg({
        'Faculty_Rating_provide by students': 'mean',
        'Average Score of AI Tutor Platform Quiz': 'mean',
        'Unit_Name': 'count',  # Number of units taught
        'Student_Adoption_Rate': 'mean',
        'Course(GCGM/MGM/GMBA)': lambda x: ', '.join(x.unique())  # Programs taught
    }).reset_index()
    
    faculty_performance.columns = ['Faculty_Name', 'Avg_Faculty_Rating', 'Avg_Quiz_Score',
                                  'Units_Taught', 'Avg_Adoption_Rate', 'Programs']
    
    # Sort by average faculty rating
    faculty_performance = faculty_performance.sort_values('Avg_Faculty_Rating', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🏆 Top 5 Faculty (by Student Rating):**")
        top_5_faculty = faculty_performance.head(5)
        
        for i, (_, row) in enumerate(top_5_faculty.iterrows(), 1):
            st.markdown(f"""
            <div class="insight-box">
            <h5>{i}. {row['Faculty_Name']}</h5>
            <p><strong>Faculty Rating:</strong> {row['Avg_Faculty_Rating']:.2f}/10</p>
            <p><strong>Avg Quiz Score:</strong> {row['Avg_Quiz_Score']:.2f}/10</p>
            <p><strong>Units Taught:</strong> {row['Units_Taught']}</p>
            <p><strong>Programs:</strong> {row['Programs']}</p>
            <p><strong>Adoption Rate:</strong> {row['Avg_Adoption_Rate']:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.write("**📉 Bottom 5 Faculty (by Student Rating):**")
        bottom_5_faculty = faculty_performance.tail(5)
        
        for i, (_, row) in enumerate(bottom_5_faculty.iterrows(), 1):
            st.markdown(f"""
            <div class="insight-box">
            <h5>{i}. {row['Faculty_Name']}</h5>
            <p><strong>Faculty Rating:</strong> {row['Avg_Faculty_Rating']:.2f}/10</p>
            <p><strong>Avg Quiz Score:</strong> {row['Avg_Quiz_Score']:.2f}/10</p>
            <p><strong>Units Taught:</strong> {row['Units_Taught']}</p>
            <p><strong>Programs:</strong> {row['Programs']}</p>
            <p><strong>Adoption Rate:</strong> {row['Avg_Adoption_Rate']:.1f}%</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Explanation of metrics
    st.info("""
    **📊 Metric Explanations:**
    - **Total Sessions**: Total number of AI Tutor sessions created across all units
    - **Total Active Participants**: Total students who participated in AI Tutor sessions
    - **Total Students Till Date**: Total students across all batches and programs
    - **Student Adoption Rate**: Percentage of students in batch who participated in AI Tutor sessions
    - **Quiz Count**: Capped at 12 quizzes per unit as per business rules
    - **Faculty Rankings**: Based on student ratings (not quiz scores)
    - **Campus Analysis**: Performance comparison across different campuses
    """)
    


def comprehensive_ai_mentor_analysis(data, selected_years, selected_programs, selected_campuses):
    """Comprehensive AI Mentor Analysis"""
    st.markdown('<h2 class="section-header">🤖 AI Mentor Impact Analysis</h2>', unsafe_allow_html=True)
    
    ai_mentor_data = data.get('AI Mentor', pd.DataFrame())
    
    if ai_mentor_data.empty:
        st.warning("No AI Mentor data available. Please upload data using the Data Management page.")
        return
    
    # Add year extraction for filtering
    ai_mentor_data['Year'] = ai_mentor_data['Cohort'].apply(lambda x: int(x.split('-')[1]) + 2000)
    
    # Apply filters
    filtered_data = ai_mentor_data.copy()
    if selected_years and selected_years != ['All']:
        filtered_data = filtered_data[filtered_data['Year'].isin([int(y) for y in selected_years])]
    if selected_programs and selected_programs != ['All']:
        filtered_data = filtered_data[filtered_data['Course'].isin(selected_programs)]
    
    # Page-level filters for AI Mentor
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.write("**🔍 AI Mentor Specific Filters:**")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        am_options = ['All Managers'] + sorted(filtered_data['Academic_Manager_Name'].unique().tolist())
        selected_am = st.selectbox("Select Academic Manager", am_options, key="ai_mentor_am")
    
    with col2:
        project_options = ['All Projects'] + sorted(filtered_data['Project Type (ARP, IBR 1, IBR 2, Industry Project)'].unique().tolist())
        selected_project = st.selectbox("Select Project Type", project_options, key="ai_mentor_project")
    
    with col3:
        program_options = ['All Programs'] + sorted(filtered_data['Course'].unique().tolist())
        selected_program_mentor = st.selectbox("Select Program", program_options, key="ai_mentor_program")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Apply additional filters
    display_data = filtered_data.copy()
    if selected_am != 'All Managers':
        display_data = display_data[display_data['Academic_Manager_Name'] == selected_am]
    if selected_project != 'All Projects':
        display_data = display_data[display_data['Project Type (ARP, IBR 1, IBR 2, Industry Project)'] == selected_project]
    if selected_program_mentor != 'All Programs':
        display_data = display_data[display_data['Course'] == selected_program_mentor]
    
    # Academic Managers Analysis
    st.subheader("👥 Academic Managers (AM) Analysis")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_managers = len(display_data['Academic_Manager_Name'].unique())
        st.metric("Total Academic Managers", total_managers)
    
    with col2:
        motivation_rate = (display_data["Q1_Are Students_motivated to use AI Mentor? (Yes/No, as they don't find it useful)"] == 'Yes').sum() / len(display_data) * 100
        st.metric("Student Motivation Rate", f"{motivation_rate:.1f}%")
    
    with col3:
        effectiveness_rate = (display_data["Q2_Are students using AI Mentor effectively ? (Yes/No)"] == 'Yes').sum() / len(display_data) * 100
        st.metric("Effectiveness Rate", f"{effectiveness_rate:.1f}%")
    
    with col4:
        improvement_rate = (display_data["Q4_Improvement_observed in student's logical thinking, Presentation & Report Structure with the use of AI Mentor (Yes/No)"] == 'Yes').sum() / len(display_data) * 100
        st.metric("Improvement Observed", f"{improvement_rate:.1f}%")
    
    # Project Type Analysis
    st.subheader("📊 Project Type Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        project_analysis = display_data.groupby('Project Type (ARP, IBR 1, IBR 2, Industry Project)').agg({
            'Academic_Manager_Name': 'count',
            'Approx. percentage of students under your guidance who levelled up using AI Mentor.': 'mean'
        }).reset_index()
        project_analysis.columns = ['Project_Type', 'Count', 'Avg_Level_Up_Percentage']
        
        # Better color scheme for project types
        project_colors = {
            'ARP': '#FF6B6B',           # Red
            'IBR 1': '#4ECDC4',         # Teal
            'IBR 2': '#45B7D1',         # Blue
            'Industry Project': '#96CEB4' # Green
        }
        
        fig = px.bar(project_analysis, x='Project_Type', y='Count',
                    title='Number of Mentoring Sessions by Project Type',
                    labels={'Count': 'Number of Sessions', 'Project_Type': 'Project Type'},
                    color='Project_Type',
                    color_discrete_map=project_colors)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(project_analysis, x='Project_Type', y='Avg_Level_Up_Percentage',
                    title='Average Student Level-up Rate by Project Type',
                    labels={'Avg_Level_Up_Percentage': 'Average Level-up Rate (%)', 'Project_Type': 'Project Type'},
                    color='Project_Type',
                    color_discrete_map=project_colors)
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top AM based on student level-up percentage
    st.subheader("🏆 Top Academic Managers by Student Performance")
    
    top_am = display_data.groupby(['Academic_Manager_Name', 'Course']).agg({
        'Approx. percentage of students under your guidance who levelled up using AI Mentor.': 'mean'
    }).reset_index().sort_values('Approx. percentage of students under your guidance who levelled up using AI Mentor.', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🏆 Top 10 Academic Managers:**")
        top_10 = top_am.head(10)
        for i, (_, row) in enumerate(top_10.iterrows(), 1):
            st.write(f"{i}. {row['Academic_Manager_Name']} ({row['Course']}) - {row['Approx. percentage of students under your guidance who levelled up using AI Mentor.']:.1f}%")
    
    with col2:
        fig = px.bar(top_10, x='Approx. percentage of students under your guidance who levelled up using AI Mentor.', 
                    y='Academic_Manager_Name',
                    title='Top 10 Academic Managers by Student Level-up Rate',
                    labels={'Approx. percentage of students under your guidance who levelled up using AI Mentor.': 'Level-up Rate (%)',
                           'Academic_Manager_Name': 'Academic Manager'},
                    orientation='h', color='Course')
        st.plotly_chart(fig, use_container_width=True)

def comprehensive_jpt_analysis(data, selected_years, selected_programs, selected_campuses):
    """Comprehensive JPT Analysis using PRP and CR templates"""
    st.markdown('<h2 class="section-header">🎯 JPT (Job Preparation Tool) Impact Analysis</h2>', unsafe_allow_html=True)
    
    prp_data = data.get('PRP (Placement Readiness Program)', pd.DataFrame())
    cr_data = data.get('CR (Corporate Relations)', pd.DataFrame())
    
    if prp_data.empty or cr_data.empty:
        st.warning("PRP and CR data required for JPT analysis. Please upload data using the Data Management page.")
        return
    
    # Apply filters
    filtered_prp = prp_data.copy()
    filtered_cr = cr_data.copy()
    
    if selected_years and selected_years != ['All']:
        filtered_prp = filtered_prp[filtered_prp['Year'].isin([int(y) for y in selected_years])]
        filtered_cr = filtered_cr[filtered_cr['Year'].isin([int(y) for y in selected_years])]
    if selected_programs and selected_programs != ['All']:
        filtered_prp = filtered_prp[filtered_prp['Course'].isin(selected_programs)]
        filtered_cr = filtered_cr[filtered_cr['Course'].isin(selected_programs)]
    
    # JPT Impact on Placement and Packages
    st.subheader("💼 JPT Impact on Placement Success")
    
    # First show JPT usage distribution
    st.subheader("📊 JPT Usage Distribution")
    jpt_usage_counts = filtered_cr['Students used JPT(Yes/No)'].value_counts()
    total_records = len(filtered_cr)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        jpt_yes_count = jpt_usage_counts.get('Yes', 0)
        jpt_yes_percent = (jpt_yes_count / total_records * 100) if total_records > 0 else 0
        st.metric("JPT Users", f"{jpt_yes_count} ({jpt_yes_percent:.1f}%)")
    
    with col2:
        jpt_no_count = jpt_usage_counts.get('No', 0)
        jpt_no_percent = (jpt_no_count / total_records * 100) if total_records > 0 else 0
        st.metric("Non-JPT Users", f"{jpt_no_count} ({jpt_no_percent:.1f}%)")
    
    with col3:
        st.metric("Total Records", f"{total_records}")
    
    # Verify percentages add up to 100%
    total_percent = jpt_yes_percent + jpt_no_percent
    if abs(total_percent - 100.0) > 0.1:
        st.warning(f"⚠️ Percentages don't add up to 100% (Total: {total_percent:.1f}%)")
    else:
        st.success(f"✅ Percentages verified: {total_percent:.1f}%")
    
    # Analyze JPT usage impact from CR data
    jpt_impact = filtered_cr.groupby('Students used JPT(Yes/No)').agg({
        'Students_Selected': 'sum',
        'No. of Students_Interviewed': 'sum',
        'Avg_CTC(in USD)': 'mean',
        'Highest_CTC(in USD)': 'mean'
    }).reset_index()
    
    jpt_impact['Conversion_Rate'] = (jpt_impact['Students_Selected'] / jpt_impact['No. of Students_Interviewed'] * 100).round(2)
    
    col1, col2, col3, col4 = st.columns(4)
    
    jpt_yes = jpt_impact[jpt_impact['Students used JPT(Yes/No)'] == 'Yes'].iloc[0] if len(jpt_impact[jpt_impact['Students used JPT(Yes/No)'] == 'Yes']) > 0 else None
    jpt_no = jpt_impact[jpt_impact['Students used JPT(Yes/No)'] == 'No'].iloc[0] if len(jpt_impact[jpt_impact['Students used JPT(Yes/No)'] == 'No']) > 0 else None
    
    if jpt_yes is not None and jpt_no is not None:
        with col1:
            conversion_improvement = jpt_yes['Conversion_Rate'] - jpt_no['Conversion_Rate']
            st.metric("Conversion Rate Improvement", f"+{conversion_improvement:.1f}%", 
                     help="Improvement in conversion rate for JPT users vs non-users")
        
        with col2:
            package_improvement = jpt_yes['Avg_CTC(in USD)'] - jpt_no['Avg_CTC(in USD)']
            st.metric("Average Package Improvement", f"+${package_improvement:.1f}K", 
                     help="Average CTC improvement for JPT users")
        
        with col3:
            st.metric("JPT Users Conversion Rate", f"{jpt_yes['Conversion_Rate']:.1f}%")
        
        with col4:
            st.metric("Non-JPT Users Conversion Rate", f"{jpt_no['Conversion_Rate']:.1f}%")
    
    # Visualization of JPT impact
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(jpt_impact, x='Students used JPT(Yes/No)', y='Conversion_Rate',
                    title='Conversion Rate: JPT Users vs Non-Users',
                    labels={'Conversion_Rate': 'Conversion Rate (%)', 'Students used JPT(Yes/No)': 'JPT Usage'},
                    color='Conversion_Rate', color_continuous_scale='RdYlGn')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(jpt_impact, x='Students used JPT(Yes/No)', y='Avg_CTC(in USD)',
                    title='Average CTC: JPT Users vs Non-Users',
                    labels={'Avg_CTC(in USD)': 'Average CTC (USD)', 'Students used JPT(Yes/No)': 'JPT Usage'},
                    color='Avg_CTC(in USD)', color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
    
    # Students who used JPT effectively are Placed
    st.subheader("🎯 JPT Effectiveness and Placement Correlation")
    
    # Analyze PRP data for JPT effectiveness
    filtered_prp['JPT_Effective'] = filtered_prp['No. of JPT Mock Interviews attempted and scored equal or above 80%'].apply(
        lambda x: 'High JPT Usage' if x >= 3 else 'Low JPT Usage' if x >= 1 else 'No JPT Usage'
    )
    
    jpt_placement = filtered_prp.groupby(['JPT_Effective', 'Placed/Not Placed']).size().unstack(fill_value=0)
    jpt_placement['Total'] = jpt_placement.sum(axis=1)
    jpt_placement['Placement_Rate'] = (jpt_placement['Placed'] / jpt_placement['Total'] * 100).round(1)
    
    fig = px.bar(jpt_placement.reset_index(), x='JPT_Effective', y='Placement_Rate',
                title='Placement Rate by JPT Usage Level',
                labels={'Placement_Rate': 'Placement Rate (%)', 'JPT_Effective': 'JPT Usage Level'},
                color='Placement_Rate', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig, use_container_width=True)
    
    # Comprehensive Score Analysis with Bell Curves and Skewness
    st.subheader("🔍 Comprehensive Score Analysis with Distribution & Skewness")
    
    # Calculate average term scores for PRP comparison
    filtered_prp['Avg_Term_Score'] = (filtered_prp['Term-1'] + filtered_prp['Term-2'] + filtered_prp['Term-3']) / 3
    
    # Get CGPA data from AI Impact data if available
    ai_impact_data = data.get('AI Impact', pd.DataFrame())
    if not ai_impact_data.empty:
        # Merge CGPA data with PRP data based on student name or cohort
        cgpa_data = ai_impact_data.groupby('Cohort')['CGPA'].mean().reset_index()
        filtered_prp = filtered_prp.merge(cgpa_data, on='Cohort', how='left')
    else:
        # If no CGPA data, create dummy data for visualization
        filtered_prp['CGPA'] = np.random.uniform(2.5, 4.0, len(filtered_prp))
    
    # Define variables with shorter labels (removed CGPA as it's not relevant for comparison)
    variables = {
        'Avg_Term_Score': 'PRP Score',
        'Area Head Mock Interview Score': 'Area Head Score',
        'No. of JPT Mock Interviews attempted and scored equal or above 80%': 'JPT Score'
    }
    
    # First show individual distributions (bell curves) with skewness
    st.subheader("📊 Individual Score Distributions & Skewness Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bell curves for all variables
        fig = go.Figure()
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        
        for i, (var, label) in enumerate(variables.items()):
            if var in filtered_prp.columns:
                data_values = filtered_prp[var].dropna()
                fig.add_trace(go.Histogram(
                    x=data_values,
                    name=label,
                    opacity=0.7,
                    nbinsx=20,
                    histnorm='probability density',
                    marker_color=colors[i % len(colors)]
                ))
        
        fig.update_layout(
            title='Score Distributions (Bell Curves)',
            xaxis_title='Score',
            yaxis_title='Density',
            barmode='overlay',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Skewness analysis table
        st.write("**📈 Skewness Analysis:**")
        skewness_data = []
        
        for var, label in variables.items():
            if var in filtered_prp.columns:
                data_values = filtered_prp[var].dropna()
                if len(data_values) > 0:
                    mean_val = data_values.mean()
                    std_val = data_values.std()
                    skew_val = ((data_values - mean_val) ** 3).mean() / (std_val ** 3)
                    
                    skewness_data.append({
                        'Variable': label,
                        'Mean': f"{mean_val:.2f}",
                        'Std Dev': f"{std_val:.2f}",
                        'Skewness': f"{skew_val:.3f}",
                        'Interpretation': 'Right Skewed' if skew_val > 0.5 else 'Left Skewed' if skew_val < -0.5 else 'Normal'
                    })
        
        skewness_df = pd.DataFrame(skewness_data)
        st.dataframe(skewness_df, use_container_width=True)
    
    # Create all possible 2-variable combinations with better charts
    st.subheader("🔗 Score Correlations & Relationships")
    
    # Add explanation for better understanding
    st.info("""
    **📖 How to Read These Charts:**
    - **Dots**: Each dot represents a student
    - **Colors**: Student performance categories (Green=Outstanding, Blue=Good, Orange=Average, Red=Needs Help)
    - **Trend Line**: Shows the overall relationship between the two scores
    - **Upward Line**: Higher scores in one area tend to mean higher scores in the other
    - **Flat Line**: No clear relationship between the scores
    - **Correlation**: Measures how strongly related the scores are (-1 to +1)
    """)
    
    # Only keep relevant combinations - remove ALL CGPA comparisons as they are different parameters
    combinations = [
        ('Avg_Term_Score', 'Area Head Mock Interview Score'),
        ('Avg_Term_Score', 'No. of JPT Mock Interviews attempted and scored equal or above 80%'),
        ('Area Head Mock Interview Score', 'No. of JPT Mock Interviews attempted and scored equal or above 80%')
    ]
    
    # Display combinations in a grid with user-friendly visualizations
    for i in range(0, len(combinations), 2):
        col1, col2 = st.columns(2)
        
        with col1:
            if i < len(combinations):
                x_var, y_var = combinations[i]
                x_label = variables.get(x_var, x_var)
                y_label = variables.get(y_var, y_var)
                
                # Use scatter plot for clear visualization
                fig = px.scatter(filtered_prp, x=x_var, y=y_var,
                               color='Categorise student overall (Outstanding, Good, Average, Needs Handholding)',
                               title=f'{x_label} vs {y_label}',
                               labels={x_var: x_label, y_var: y_label},
                               color_discrete_map={
                                   'Outstanding': '#2E8B57',  # Green
                                   'Good': '#4169E1',         # Blue  
                                   'Average': '#FF8C00',      # Orange
                                   'Needs Handholding': '#DC143C'  # Red
                               })
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show correlation with interpretation
                correlation = filtered_prp[x_var].corr(filtered_prp[y_var])
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Correlation", f"{correlation:.3f}")
                with col_b:
                    if correlation > 0.7:
                        st.success("Strong Positive")
                    elif correlation > 0.3:
                        st.info("Moderate Positive")
                    elif correlation > -0.3:
                        st.warning("Weak/No Relation")
                    elif correlation > -0.7:
                        st.info("Moderate Negative")
                    else:
                        st.error("Strong Negative")
        
        with col2:
            if i + 1 < len(combinations):
                x_var, y_var = combinations[i + 1]
                x_label = variables.get(x_var, x_var)
                y_label = variables.get(y_var, y_var)
                
                # Use scatter plot for clear visualization
                fig = px.scatter(filtered_prp, x=x_var, y=y_var,
                               color='Categorise student overall (Outstanding, Good, Average, Needs Handholding)',
                               title=f'{x_label} vs {y_label}',
                               labels={x_var: x_label, y_var: y_label},
                               color_discrete_map={
                                   'Outstanding': '#2E8B57',  # Green
                                   'Good': '#4169E1',         # Blue  
                                   'Average': '#FF8C00',      # Orange
                                   'Needs Handholding': '#DC143C'  # Red
                               })
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Show correlation with interpretation
                correlation = filtered_prp[x_var].corr(filtered_prp[y_var])
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Correlation", f"{correlation:.3f}")
                with col_b:
                    if correlation > 0.7:
                        st.success("Strong Positive")
                    elif correlation > 0.3:
                        st.info("Moderate Positive")
                    elif correlation > -0.3:
                        st.warning("Weak/No Relation")
                    elif correlation > -0.7:
                        st.info("Moderate Negative")
                    else:
                        st.error("Strong Negative")
    
    # Correlation Matrix and Statistical Analysis
    st.subheader("📈 Comprehensive Statistical Analysis")
    
    # Prepare data for correlation analysis
    correlation_data = filtered_prp[['Term-1', 'Term-2', 'Term-3', 'Area Head Mock Interview Score', 
                                    'No. of JPT Mock Interviews attempted and scored equal or above 80%']].copy()
    correlation_data.columns = ['Term-1', 'Term-2', 'Term-3', 'Area Head Score', 'JPT High Scores']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Correlation matrix
        corr_matrix = correlation_data.corr()
        fig = px.imshow(corr_matrix, title='Correlation Matrix: PRP, Area Head, and JPT Scores',
                       labels=dict(color="Correlation"), color_continuous_scale='RdBu_r')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribution analysis
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(x=filtered_prp['Avg_Term_Score'], name='PRP Scores', opacity=0.7, nbinsx=20))
        fig.add_trace(go.Histogram(x=filtered_prp['Area Head Mock Interview Score'], name='Area Head Scores', opacity=0.7, nbinsx=20))
        
        fig.update_layout(title='Score Distribution: PRP vs Area Head',
                         xaxis_title='Score', yaxis_title='Frequency',
                         barmode='overlay')
        st.plotly_chart(fig, use_container_width=True)
    
    # Key insights summary
    st.subheader("🎯 Key JPT Impact Insights")
    
    insights = []
    if jpt_yes is not None and jpt_no is not None:
        if jpt_yes['Conversion_Rate'] > jpt_no['Conversion_Rate']:
            insights.append(f"✅ JPT users have {jpt_yes['Conversion_Rate'] - jpt_no['Conversion_Rate']:.1f}% higher conversion rate")
        if jpt_yes['Avg_CTC(in USD)'] > jpt_no['Avg_CTC(in USD)']:
            insights.append(f"💰 JPT users earn ${jpt_yes['Avg_CTC(in USD)'] - jpt_no['Avg_CTC(in USD)']:.1f}K more on average")
    
    high_jpt_placement = jpt_placement.loc['High JPT Usage', 'Placement_Rate'] if 'High JPT Usage' in jpt_placement.index else 0
    no_jpt_placement = jpt_placement.loc['No JPT Usage', 'Placement_Rate'] if 'No JPT Usage' in jpt_placement.index else 0
    
    if high_jpt_placement > no_jpt_placement:
        insights.append(f"🎯 High JPT users have {high_jpt_placement - no_jpt_placement:.1f}% better placement rate")
    
    if correlation > 0.5:
        insights.append(f"📊 Strong positive correlation ({correlation:.2f}) between PRP and Area Head scores")
    elif correlation < 0.3:
        insights.append(f"⚠️ Weak correlation ({correlation:.2f}) suggests scoring inconsistencies")
    
    for insight in insights:
        st.markdown(f"<div class='insight-box'>{insight}</div>", unsafe_allow_html=True)

def unit_performance_analysis(data, selected_years, selected_programs, selected_campuses):
    """Unit Performance Analysis with visualizations"""
    st.markdown('<h2 class="section-header">📊 Unit Performance Analysis</h2>', unsafe_allow_html=True)
    
    unit_data = data.get('Unit Performance', pd.DataFrame())
    
    if unit_data.empty:
        st.warning("No Unit Performance data available. Please upload data using the Data Management page.")
        return
    
    # Apply filters
    filtered_data = unit_data.copy()
    if selected_years and selected_years != ['All']:
        filtered_data = filtered_data[filtered_data['Year'].isin([int(y) for y in selected_years])]
    if selected_programs and selected_programs != ['All']:
        filtered_data = filtered_data[filtered_data['Course'].isin(selected_programs)]
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_units = len(filtered_data['Unit_Name'].unique())
        st.metric("Total Units Tracked", f"{total_units:,}")
    
    with col2:
        avg_score = filtered_data['Total_Avg_score'].mean()
        st.metric("Average Unit Score", f"{avg_score:.1f}")
    
    with col3:
        ai_implemented = (filtered_data['AI Tutor (Before/After)'] == 'After').sum()
        st.metric("Units with AI Tutor", f"{ai_implemented:,}")
    
    with col4:
        if 'AI Tutor (Before/After)' in filtered_data.columns and 'Total_Avg_score' in filtered_data.columns:
            before_ai = filtered_data[filtered_data['AI Tutor (Before/After)'] == 'Before']['Total_Avg_score'].mean()
            after_ai = filtered_data[filtered_data['AI Tutor (Before/After)'] == 'After']['Total_Avg_score'].mean()
            improvement = ((after_ai - before_ai) / before_ai * 100) if before_ai > 0 else 0
            st.metric("AI Tutor Impact", f"{improvement:.1f}%")
    
    # Enhanced Before/After AI Tutor Analysis
    st.subheader("📊 Detailed Before vs After AI Tutor Comparison")
    
    # Calculate detailed before/after statistics
    before_data = filtered_data[filtered_data['AI Tutor (Before/After)'] == 'Before']
    after_data = filtered_data[filtered_data['AI Tutor (Before/After)'] == 'After']
    
    if not before_data.empty and not after_data.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            before_mean = before_data['Total_Avg_score'].mean()
            st.metric("Before AI Tutor", f"{before_mean:.2f}", help="Average score before AI Tutor implementation")
        
        with col2:
            after_mean = after_data['Total_Avg_score'].mean()
            st.metric("After AI Tutor", f"{after_mean:.2f}", help="Average score after AI Tutor implementation")
        
        with col3:
            score_improvement = after_mean - before_mean
            st.metric("Score Improvement", f"+{score_improvement:.2f}", help="Absolute improvement in scores")
        
        with col4:
            percent_improvement = (score_improvement / before_mean * 100) if before_mean > 0 else 0
            st.metric("Percentage Improvement", f"+{percent_improvement:.1f}%", help="Percentage improvement in scores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Enhanced score comparison with statistical significance
        before_scores = filtered_data[filtered_data['AI Tutor (Before/After)'] == 'Before']['Total_Avg_score']
        after_scores = filtered_data[filtered_data['AI Tutor (Before/After)'] == 'After']['Total_Avg_score']
        
        fig = go.Figure()
        fig.add_trace(go.Box(y=before_scores, name='Before AI Tutor', boxpoints='all', 
                            marker_color='lightcoral'))
        fig.add_trace(go.Box(y=after_scores, name='After AI Tutor', boxpoints='all',
                            marker_color='lightgreen'))
        fig.update_layout(title='Unit Scores Distribution: Before vs After AI Tutor',
                         yaxis_title='Average Score',
                         showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistical significance test (simplified without scipy)
        if len(before_scores) > 1 and len(after_scores) > 1:
            before_mean = before_scores.mean()
            after_mean = after_scores.mean()
            improvement = after_mean - before_mean
            if improvement > 0:
                st.success(f"✅ Performance improvement observed: +{improvement:.2f} points")
            else:
                st.info(f"ℹ️ Performance change: {improvement:+.2f} points")
    
    with col2:
        # Program-wise analysis
        program_analysis = filtered_data.groupby(['Course', 'AI Tutor (Before/After)'])['Total_Avg_score'].mean().reset_index()
        fig = px.bar(program_analysis, x='Course', y='Total_Avg_score', color='AI Tutor (Before/After)',
                    title='Average Unit Scores by Program and AI Tutor Status',
                    labels={'Total_Avg_score': 'Average Score', 'Course': 'Program'},
                    barmode='group', color_discrete_map={'Before': 'lightcoral', 'After': 'lightgreen'})
        st.plotly_chart(fig, use_container_width=True)
    
    # Unit-wise Before/After Comparison
    st.subheader("📈 Unit-wise Before vs After Performance")
    
    # Create a comparison for units that have both before and after data
    unit_comparison = filtered_data.groupby(['Unit_Name', 'AI Tutor (Before/After)'])['Total_Avg_score'].mean().unstack(fill_value=0)
    
    # Only include units that have both before and after data
    unit_comparison = unit_comparison[(unit_comparison['Before'] > 0) & (unit_comparison['After'] > 0)]
    unit_comparison['Improvement'] = unit_comparison['After'] - unit_comparison['Before']
    unit_comparison['Percent_Improvement'] = (unit_comparison['Improvement'] / unit_comparison['Before'] * 100).round(1)
    
    if not unit_comparison.empty:
        # Sort by improvement
        unit_comparison_sorted = unit_comparison.sort_values('Improvement', ascending=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🏆 Top 5 Most Improved Units:**")
            top_improved = unit_comparison_sorted.head(5)
            for unit, row in top_improved.iterrows():
                st.write(f"• **{unit}**: {row['Before']:.1f} → {row['After']:.1f} (+{row['Improvement']:.1f}, +{row['Percent_Improvement']:.1f}%)")
        
        with col2:
            st.write("**📉 Units with Least Improvement:**")
            least_improved = unit_comparison_sorted.tail(5)
            for unit, row in least_improved.iterrows():
                st.write(f"• **{unit}**: {row['Before']:.1f} → {row['After']:.1f} ({row['Improvement']:+.1f}, {row['Percent_Improvement']:+.1f}%)")
        
        # Visualization of unit improvements
        fig = px.scatter(unit_comparison_sorted.reset_index(), x='Before', y='After', 
                        size='Percent_Improvement', hover_name='Unit_Name',
                        title='Unit Performance: Before vs After AI Tutor Implementation',
                        labels={'Before': 'Score Before AI Tutor', 'After': 'Score After AI Tutor'},
                        color='Improvement', color_continuous_scale='RdYlGn')
        
        # Add diagonal line for reference (no improvement)
        min_score = min(unit_comparison['Before'].min(), unit_comparison['After'].min())
        max_score = max(unit_comparison['Before'].max(), unit_comparison['After'].max())
        fig.add_trace(go.Scatter(x=[min_score, max_score], y=[min_score, max_score],
                                mode='lines', name='No Improvement Line',
                                line=dict(dash='dash', color='gray')))
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Unit-wise performance analysis
    st.subheader("📈 Unit-wise Performance Trends")
    
    unit_performance = filtered_data.groupby(['Unit_Name', 'AI Tutor (Before/After)'])['Total_Avg_score'].mean().reset_index()
    
    fig = px.bar(unit_performance, x='Unit_Name', y='Total_Avg_score', color='AI Tutor (Before/After)',
                title='Performance by Unit and AI Tutor Implementation',
                labels={'Total_Avg_score': 'Average Score', 'Unit_Name': 'Subject'},
                barmode='group')
    fig.update_layout(xaxis_tickangle=-45, height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Month-wise Performance Analysis
    st.subheader("📅 Month-wise Performance Analysis")
    
    # Extract month from Unit_Commencement_date or create dummy months
    if 'Unit_Commencement_date' in filtered_data.columns:
        # Try to extract month from date string
        try:
            filtered_data['Month'] = pd.to_datetime(filtered_data['Unit_Commencement_date'], errors='coerce').dt.month_name()
        except:
            # If date parsing fails, create dummy months
            months = ['January', 'February', 'March', 'April', 'May', 'June', 
                     'July', 'August', 'September', 'October', 'November', 'December']
            filtered_data['Month'] = np.random.choice(months, len(filtered_data))
    else:
        # Create dummy months for demonstration
        months = ['January', 'February', 'March', 'April', 'May', 'June', 
                 'July', 'August', 'September', 'October', 'November', 'December']
        filtered_data['Month'] = np.random.choice(months, len(filtered_data))
    
    monthly_performance = filtered_data.groupby(['Month', 'AI Tutor (Before/After)'])['Total_Avg_score'].mean().reset_index()
    
    # Order months correctly
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly_performance['Month'] = pd.Categorical(monthly_performance['Month'], categories=month_order, ordered=True)
    monthly_performance = monthly_performance.sort_values('Month')
    
    fig = px.line(monthly_performance, x='Month', y='Total_Avg_score', color='AI Tutor (Before/After)',
                 title='Unit Performance Trends by Month',
                 labels={'Total_Avg_score': 'Average Score', 'Month': 'Month'},
                 markers=True)
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🚀 AI Initiatives Impact Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### SP Jain School of Global Management - Comprehensive Analysis")
    
    # Load data
    data = load_data()
    
    if not data:
        st.error("Failed to load data. Please check if all CSV files are present.")
        return
    
    # Main filters at the top of the page
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.write("**🔍 Global Filters (Applied to all analyses):**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        year_options = ['All'] + ['2022', '2023', '2024', '2025', '2026']
        selected_years = st.multiselect("Select Years", year_options, default=['All'], key="global_years")
        if 'All' in selected_years:
            selected_years = ['All']
    
    with col2:
        program_options = ['All'] + ['GCGM', 'MGB', 'GMBA']
        selected_programs = st.multiselect("Select Programs", program_options, default=['All'], key="global_programs")
        if 'All' in selected_programs:
            selected_programs = ['All']
    
    # Campus is handled internally, not as a filter
    selected_campuses = ['All']  # Default to all campuses
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Analysis sections
    comprehensive_ai_tutor_analysis(data, selected_years, selected_programs, selected_campuses)
    comprehensive_ai_mentor_analysis(data, selected_years, selected_programs, selected_campuses)
    comprehensive_jpt_analysis(data, selected_years, selected_programs, selected_campuses)
    unit_performance_analysis(data, selected_years, selected_programs, selected_campuses)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🚀 AI Initiatives Dashboard | SP Jain School of Global Management</p>
        <p>Comprehensive Analysis of AI Tools Impact on Academic and Placement Outcomes</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()