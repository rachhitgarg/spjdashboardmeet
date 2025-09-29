import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
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
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .tool-toggle {
        background-color: #e1f5fe;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
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

def calculate_conversion_rate(selected, applied):
    """Calculate conversion rate with error handling"""
    if applied == 0:
        return 0
    return (selected / applied) * 100

def calculate_improvement_percentage(before, after):
    """Calculate improvement percentage"""
    if before == 0:
        return 0
    return ((after - before) / before) * 100

def data_management_page():
    """Enhanced Data Management Page for uploading, downloading, and managing data"""
    st.markdown('<h1 class="main-header">📊 Data Management Center</h1>', unsafe_allow_html=True)
    st.markdown("### Upload, Download, and Manage AI Initiatives Data")
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Create tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["📥 Download Templates", "📤 Upload Data", "🗂️ Data Summary", "📋 Operation Logs"])
    
    with tab1:
        st.subheader("📥 Download Data Templates")
        st.write("Download empty templates to fill with your data:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Individual template downloads
            st.write("**Individual Templates:**")
            for data_type in data_manager.templates.keys():
                template_data = data_manager.download_template(data_type)
                if template_data:
                    template_info = data_manager.get_template_info(data_type)
                    st.download_button(
                        label=f"📄 Download {data_type} Template",
                        data=template_data,
                        file_name=data_manager.templates[data_type]['filename'],
                        mime='text/csv',
                        key=f"download_{data_type.replace(' ', '_')}",
                        help=f"{template_info['description'] if template_info else ''}"
                    )
        
        with col2:
            # All templates download
            st.write("**All Templates (ZIP):**")
            all_templates = data_manager.download_all_templates()
            st.download_button(
                label="📦 Download All Templates (ZIP)",
                data=all_templates,
                file_name="ai_initiatives_templates_updated.zip",
                mime='application/zip'
            )
            
            st.info("""
            **Instructions:**
            1. Download the template(s) you need
            2. Fill in your data following the column structure
            3. Save as CSV format
            4. Upload using the 'Upload Data' tab
            """)
    
    with tab2:
        st.subheader("📤 Upload Data")
        
        # User information
        col1, col2 = st.columns(2)
        with col1:
            user_name = st.text_input("Your Name", placeholder="Enter your name for logging")
        with col2:
            user_team = st.text_input("Team/Department", placeholder="e.g., Academic Team, Placement Team")
        
        user_info = f"{user_name} ({user_team})" if user_name and user_team else "Anonymous User"
        
        # Data type selection
        data_type = st.selectbox("Select Data Type", list(data_manager.templates.keys()))
        
        # Show template info
        template_info = data_manager.get_template_info(data_type)
        if template_info:
            st.info(f"**{data_type}**: {template_info['description']} ({template_info['column_count']} columns)")
        
        # File upload
        uploaded_file = st.file_uploader(
            f"Upload {data_type} Data",
            type=['csv'],
            help=f"Upload CSV file with {data_type} data"
        )
        
        if uploaded_file is not None:
            try:
                # Read uploaded file
                uploaded_df = pd.read_csv(uploaded_file)
                
                st.write("**Preview of uploaded data:**")
                st.dataframe(uploaded_df.head())
                
                # Validate data structure
                is_valid, message = data_manager.validate_uploaded_data(uploaded_df, data_type)
                
                if is_valid:
                    st.success(f"✅ {message}")
                    
                    # Load existing data
                    existing_df = data_manager.load_existing_data(data_type)
                    
                    st.write(f"**Current data:** {len(existing_df)} records")
                    st.write(f"**New data:** {len(uploaded_df)} records")
                    
                    # Operation selection
                    operation = st.radio(
                        "Choose operation:",
                        ["Merge with existing data", "Replace all existing data"],
                        help="Merge: Add new data to existing data. Replace: Delete all existing data and use only new data."
                    )
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("🚀 Execute Upload", type="primary"):
                            if operation == "Merge with existing data":
                                result_df, success, msg = data_manager.merge_data(existing_df, uploaded_df, data_type, user_info)
                            else:
                                result_df, success, msg = data_manager.replace_data(uploaded_df, data_type, user_info)
                            
                            if success:
                                # Save the data
                                save_success, save_msg = data_manager.save_data(result_df, data_type)
                                if save_success:
                                    st.success(f"✅ {msg}")
                                    st.success(f"✅ {save_msg}")
                                    st.balloons()
                                    
                                    # Clear cache to reload data
                                    st.cache_data.clear()
                                else:
                                    st.error(f"❌ {save_msg}")
                            else:
                                st.error(f"❌ {msg}")
                    
                    with col2:
                        if st.button("🗑️ Delete All Data", help="This will delete all existing data for this type"):
                            if st.checkbox("I confirm I want to delete all data", key="delete_confirm"):
                                success, msg = data_manager.delete_data(data_type, user_info)
                                if success:
                                    st.success(f"✅ {msg}")
                                    st.cache_data.clear()
                                else:
                                    st.error(f"❌ {msg}")
                
                else:
                    st.error(f"❌ {message}")
                    if template_info:
                        st.write("**Expected columns:**")
                        st.write(template_info['columns'])
                    
            except Exception as e:
                st.error(f"❌ Error reading uploaded file: {e}")
    
    with tab3:
        st.subheader("🗂️ Data Summary")
        
        summary = data_manager.get_data_summary()
        
        # Display as cards
        cols = st.columns(2)
        for i, (data_type, info) in enumerate(summary.items()):
            with cols[i % 2]:
                if 'error' in info:
                    st.error(f"**{data_type}**\n\nError: {info['error']}")
                elif 'status' in info:
                    st.warning(f"**{data_type}**\n\n{info['status']}")
                else:
                    st.info(f"""
                    **{data_type}**
                    
                    📊 Records: {info['records']:,}
                    📅 Last Modified: {info['last_modified']}
                    💾 File Size: {info['file_size']}
                    📝 Description: {info.get('description', 'N/A')}
                    """)
        
        # Refresh button
        if st.button("🔄 Refresh Summary"):
            st.cache_data.clear()
            st.experimental_rerun()
    
    with tab4:
        st.subheader("📋 Operation Logs")
        
        if 'operation_logs' in st.session_state and st.session_state.operation_logs:
            # Display recent logs
            st.write("**Recent Operations:**")
            logs_df = pd.DataFrame(st.session_state.operation_logs)
            
            # Sort by timestamp (most recent first)
            logs_df = logs_df.sort_values('timestamp', ascending=False)
            
            # Display as table
            st.dataframe(
                logs_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Clear logs button
            if st.button("🗑️ Clear Logs"):
                st.session_state.operation_logs = []
                st.experimental_rerun()
                
        else:
            st.info("No operations logged yet.")
        
        # Download full log file
        if os.path.exists('data_operations.log'):
            with open('data_operations.log', 'r') as f:
                log_content = f.read()
            
            st.download_button(
                label="📄 Download Full Log File",
                data=log_content,
                file_name=f"data_operations_log_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
                mime='text/plain'
            )

def ai_tkt_analysis(data):
    """AI TKT (Technical Knowledge Test) Analysis Section"""
    st.markdown('<h2 class="section-header">🧠 AI TKT (Technical Knowledge Test) Analysis</h2>', unsafe_allow_html=True)
    
    ai_tkt_data = data.get('AI TKT', pd.DataFrame())
    
    if ai_tkt_data.empty:
        st.warning("No AI TKT data available. Please upload data using the Data Management page.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tests = len(ai_tkt_data)
        st.metric("Total Tests Conducted", f"{total_tests:,}")
    
    with col2:
        if 'Average Grades Before AI for TKT' in ai_tkt_data.columns:
            avg_before = ai_tkt_data['Average Grades Before AI for TKT'].mean()
            st.metric("Average Before Score", f"{avg_before:.1f}")
    
    with col3:
        if 'Avergae Grades After AI for TKT' in ai_tkt_data.columns:
            avg_after = ai_tkt_data['Avergae Grades After AI for TKT'].mean()
            st.metric("Average After Score", f"{avg_after:.1f}")
    
    with col4:
        if 'Improvement%' in ai_tkt_data.columns:
            avg_improvement = ai_tkt_data['Improvement%'].mean()
            st.metric("Average Improvement", f"{avg_improvement:.1f}%")
    
    # Before/After Analysis
    if 'Average Grades Before AI for TKT' in ai_tkt_data.columns and 'Avergae Grades After AI for TKT' in ai_tkt_data.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Score distribution comparison
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=ai_tkt_data['Average Grades Before AI for TKT'], name='Before AI TKT', opacity=0.7))
            fig.add_trace(go.Histogram(x=ai_tkt_data['Avergae Grades After AI for TKT'], name='After AI TKT', opacity=0.7))
            fig.update_layout(title='Score Distribution: Before vs After AI TKT', barmode='overlay')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Improvement by unit/course
            if 'Unit' in ai_tkt_data.columns and 'Course' in ai_tkt_data.columns:
                improvement_data = ai_tkt_data.copy()
                
                unit_improvement = improvement_data.groupby(['Course', 'Unit'])['Improvement%'].mean().reset_index()
                
                fig = px.bar(unit_improvement, x='Unit', y='Improvement%', color='Course',
                            title='Average Improvement by Unit and Course',
                            labels={'Improvement%': 'Improvement (%)'})
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

def cr_analysis(data):
    """Corporate Relations Analysis Section"""
    st.markdown('<h2 class="section-header">🏢 Corporate Relations (CR) Analysis</h2>', unsafe_allow_html=True)
    
    cr_data = data.get('CR (Corporate Relations)', pd.DataFrame())
    
    if cr_data.empty:
        st.warning("No Corporate Relations data available. Please upload data using the Data Management page.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_companies = len(cr_data['Company Name'].unique()) if 'Company Name' in cr_data.columns else 0
        st.metric("Total Companies Engaged", f"{total_companies:,}")
    
    with col2:
        total_placements = cr_data['Students_Selected'].sum() if 'Students_Selected' in cr_data.columns else 0
        st.metric("Total Students Placed", f"{total_placements:,}")
    
    with col3:
        avg_ctc = cr_data['Avg_CTC(in USD)'].mean() if 'Avg_CTC(in USD)' in cr_data.columns else 0
        st.metric("Average CTC", f"${avg_ctc:,.0f}")
    
    with col4:
        if 'Year' in cr_data.columns:
            current_year_placements = cr_data[cr_data['Year'] == cr_data['Year'].max()]['Students_Selected'].sum() if 'Students_Selected' in cr_data.columns else 0
            st.metric("Current Year Placements", f"{current_year_placements:,}")
    
    # Analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Placements by industry
        if 'Industry_Sector' in cr_data.columns and 'Students_Selected' in cr_data.columns:
            industry_placements = cr_data.groupby('Industry_Sector')['Students_Selected'].sum().reset_index()
            fig = px.pie(industry_placements, values='Students_Selected', names='Industry_Sector',
                        title='Placements by Industry Sector')
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # CTC distribution
        if 'Avg_CTC(in USD)' in cr_data.columns:
            fig = px.histogram(cr_data, x='Avg_CTC(in USD)', title='CTC Distribution',
                              labels={'Avg_CTC(in USD)': 'Average CTC (USD)', 'count': 'Number of Companies'})
            st.plotly_chart(fig, use_container_width=True)

def prp_analysis(data):
    """Placement Readiness Program Analysis Section"""
    st.markdown('<h2 class="section-header">🎯 Placement Readiness Program (PRP) Analysis</h2>', unsafe_allow_html=True)
    
    prp_data = data.get('PRP (Placement Readiness Program)', pd.DataFrame())
    
    if prp_data.empty:
        st.warning("No PRP data available. Please upload data using the Data Management page.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_students = len(prp_data)
        st.metric("Total Students Evaluated", f"{total_students:,}")
    
    with col2:
        # Calculate average of term scores
        term_columns = ['Term-1', 'Term-2', 'Term-3']
        available_terms = [col for col in term_columns if col in prp_data.columns]
        if available_terms:
            avg_score = prp_data[available_terms].mean(axis=1).mean()
            st.metric("Average Overall Score", f"{avg_score:.1f}")
    
    with col3:
        if 'No. of JPT Mock Interviews attempted and scored equal or above 80%' in prp_data.columns:
            avg_jpt = prp_data['No. of JPT Mock Interviews attempted and scored equal or above 80%'].mean()
            st.metric("Average JPT High Scores", f"{avg_jpt:.1f}")
    
    with col4:
        if 'Area Head Mock Interview Score' in prp_data.columns:
            avg_mock = prp_data['Area Head Mock Interview Score'].mean()
            st.metric("Average Mock Interview Score", f"{avg_mock:.1f}")
    
    # Analysis charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Score distribution
        if 'Term-1' in prp_data.columns:
            fig = px.histogram(prp_data, x='Term-1', title='Term-1 Score Distribution',
                              labels={'Term-1': 'Term-1 Score', 'count': 'Number of Students'})
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Placement status
        if 'Placed/Not Placed' in prp_data.columns:
            placement_counts = prp_data['Placed/Not Placed'].value_counts()
            fig = px.pie(values=placement_counts.values, names=placement_counts.index,
                        title='Placement Status Distribution')
            st.plotly_chart(fig, use_container_width=True)

def enhanced_ai_tutor_analysis(data):
    """Enhanced AI Tutor Analysis with new features"""
    st.markdown('<h2 class="section-header">📚 Enhanced AI Tutor Analysis</h2>', unsafe_allow_html=True)
    
    ai_tutor_data = data.get('AI Tutor', pd.DataFrame())
    
    if ai_tutor_data.empty:
        st.warning("No AI Tutor data available. Please upload data using the Data Management page.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'Total_Students_Participated_watched videos' in ai_tutor_data.columns and 'Batch_size(number should come from student feedback form)' in ai_tutor_data.columns:
            total_participated = ai_tutor_data['Total_Students_Participated_watched videos'].sum()
            total_batch = ai_tutor_data['Batch_size(number should come from student feedback form)'].sum()
            adoption_rate = (total_participated / total_batch * 100) if total_batch > 0 else 0
            st.metric("Overall Adoption Rate", f"{adoption_rate:.1f}%")
    
    with col2:
        if 'Avg_Rating_for_AI_Tutor_Tool' in ai_tutor_data.columns:
            avg_rating = ai_tutor_data['Avg_Rating_for_AI_Tutor_Tool'].mean()
            st.metric("Avg AI Tutor Rating", f"{avg_rating:.2f}/5.0")
    
    with col3:
        if 'No_of_Session_IDs_created' in ai_tutor_data.columns:
            total_sessions = ai_tutor_data['No_of_Session_IDs_created'].sum()
            st.metric("Total Sessions Created", f"{total_sessions:,}")
    
    with col4:
        if 'Total_Students_Participated_watched videos' in ai_tutor_data.columns:
            total_participants = ai_tutor_data['Total_Students_Participated_watched videos'].sum()
            st.metric("Total Students Participated", f"{total_participants:,}")
    
    # Campus-wise analysis (including SYD)
    if 'Campus (SG/MUM/SYD/DXB)' in ai_tutor_data.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate adoption rate by campus
            campus_data = ai_tutor_data.groupby('Campus (SG/MUM/SYD/DXB)').agg({
                'Total_Students_Participated_watched videos': 'sum',
                'Batch_size(number should come from student feedback form)': 'sum'
            }).reset_index()
            campus_data['Adoption_Rate'] = (campus_data['Total_Students_Participated_watched videos'] / 
                                          campus_data['Batch_size(number should come from student feedback form)'] * 100)
            
            fig = px.bar(campus_data, x='Campus (SG/MUM/SYD/DXB)', y='Adoption_Rate',
                        title='Student Adoption Rate by Campus',
                        labels={'Adoption_Rate': 'Adoption Rate (%)'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Rating by campus
            if 'Avg_Rating_for_AI_Tutor_Tool' in ai_tutor_data.columns:
                campus_rating = ai_tutor_data.groupby('Campus (SG/MUM/SYD/DXB)')['Avg_Rating_for_AI_Tutor_Tool'].mean().reset_index()
                fig = px.bar(campus_rating, x='Campus (SG/MUM/SYD/DXB)', y='Avg_Rating_for_AI_Tutor_Tool',
                            title='AI Tutor Rating by Campus',
                            labels={'Avg_Rating_for_AI_Tutor_Tool': 'Average Rating'})
                st.plotly_chart(fig, use_container_width=True)

def enhanced_unit_performance_analysis(data):
    """Enhanced Unit Performance Analysis with AI Tutor effectiveness"""
    st.markdown('<h2 class="section-header">📈 Enhanced Unit Performance Analysis</h2>', unsafe_allow_html=True)
    
    unit_data = data.get('Unit Performance', pd.DataFrame())
    
    if unit_data.empty:
        st.warning("No Unit Performance data available. Please upload data using the Data Management page.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_units = len(unit_data['Unit_Name'].unique()) if 'Unit_Name' in unit_data.columns else 0
        st.metric("Total Units Tracked", f"{total_units:,}")
    
    with col2:
        if 'Total_Avg_score' in unit_data.columns:
            avg_score = unit_data['Total_Avg_score'].mean()
            st.metric("Average Unit Score", f"{avg_score:.1f}")
    
    with col3:
        if 'AI Tutor (Before/After)' in unit_data.columns:
            ai_implemented = (unit_data['AI Tutor (Before/After)'] == 'After').sum()
            st.metric("Units with AI Tutor", f"{ai_implemented:,}")
    
    with col4:
        if 'AI Tutor (Before/After)' in unit_data.columns and 'Total_Avg_score' in unit_data.columns:
            before_ai = unit_data[unit_data['AI Tutor (Before/After)'] == 'Before']['Total_Avg_score'].mean()
            after_ai = unit_data[unit_data['AI Tutor (Before/After)'] == 'After']['Total_Avg_score'].mean()
            improvement = calculate_improvement_percentage(before_ai, after_ai)
            st.metric("AI Tutor Impact", f"{improvement:.1f}%")
    
    # Before/After AI Tutor Analysis
    if 'AI Tutor (Before/After)' in unit_data.columns and 'Total_Avg_score' in unit_data.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Score comparison
            before_scores = unit_data[unit_data['AI Tutor (Before/After)'] == 'Before']['Total_Avg_score']
            after_scores = unit_data[unit_data['AI Tutor (Before/After)'] == 'After']['Total_Avg_score']
            
            fig = go.Figure()
            fig.add_trace(go.Box(y=before_scores, name='Before AI Tutor', boxpoints='all'))
            fig.add_trace(go.Box(y=after_scores, name='After AI Tutor', boxpoints='all'))
            fig.update_layout(title='Unit Scores: Before vs After AI Tutor Implementation')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Program-wise analysis
            if 'Course' in unit_data.columns:
                program_analysis = unit_data.groupby(['Course', 'AI Tutor (Before/After)'])['Total_Avg_score'].mean().reset_index()
                fig = px.bar(program_analysis, x='Course', y='Total_Avg_score', color='AI Tutor (Before/After)',
                            title='Average Unit Scores by Program and AI Tutor Status',
                            labels={'Total_Avg_score': 'Average Score'})
                st.plotly_chart(fig, use_container_width=True)

def main():
    # Sidebar navigation
    st.sidebar.title("🚀 Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📈 Dashboard", "📊 Data Management"]
    )
    
    if page == "📊 Data Management":
        data_management_page()
        return
    
    # Header
    st.markdown('<h1 class="main-header">🚀 AI Initiatives Impact Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("### SP Jain School of Global Management - MGB, GMBA & GCGM Programs")
    
    # Load data
    data = load_data()
    
    if not data:
        st.error("Failed to load data. Please check if all CSV files are present.")
        return
    
    # Sidebar for filters
    st.sidebar.header("📊 Dashboard Filters")
    
    # Get unique values for filtering
    all_years = []
    all_programs = []
    all_campuses = []
    
    for df in data.values():
        if not df.empty:
            if 'Year' in df.columns:
                all_years.extend(df['Year'].unique())
            if 'Program' in df.columns:
                all_programs.extend(df['Program'].unique())
            elif 'Course' in df.columns:
                all_programs.extend(df['Course'].unique())
            elif 'Course(GCGM/MGM/GMBA)' in df.columns:
                all_programs.extend(df['Course(GCGM/MGM/GMBA)'].unique())
            if 'Campus' in df.columns:
                all_campuses.extend(df['Campus'].unique())
            elif 'Campus (SG/MUM/SYD/DXB)' in df.columns:
                all_campuses.extend(df['Campus (SG/MUM/SYD/DXB)'].unique())
    
    # Remove duplicates and sort
    years = sorted(list(set(all_years))) if all_years else [2022, 2023, 2024]
    programs = sorted(list(set(all_programs))) if all_programs else ['MGB', 'GMBA', 'GCGM']
    campuses = sorted(list(set(all_campuses))) if all_campuses else ['SG', 'DXB', 'MUM', 'SYD']
    
    # Year filter
    with st.sidebar.container():
        st.write("**📅 Year Selection:**")
        year_options = ["All Years"] + [str(year) for year in years]
        selected_year_option = st.selectbox("Choose Years", year_options, index=0)
        
        if selected_year_option == "All Years":
            selected_years = years
        else:
            selected_years = [int(selected_year_option)]
    
    # Program filter (including GCGM)
    with st.sidebar.container():
        st.write("**🎓 Program Selection:**")
        program_options = ["All Programs"] + programs
        selected_program_option = st.selectbox("Choose Programs", program_options, index=0)
        
        if selected_program_option == "All Programs":
            selected_programs = programs
        else:
            selected_programs = [selected_program_option]
    
    # Campus filter (including SYD)
    with st.sidebar.container():
        st.write("**🏫 Campus Selection:**")
        campus_options = ["All Campuses"] + campuses
        selected_campus_option = st.selectbox("Choose Campuses", campus_options, index=0)
        
        if selected_campus_option == "All Campuses":
            selected_campuses = campuses
        else:
            selected_campuses = [selected_campus_option]
    
    # Tool selection
    st.sidebar.header("🛠️ AI Tools Analysis")
    with st.sidebar.container():
        tool_options = ["All Tools", "AI Tutor", "AI Mentor", "AI TKT", "CR", "PRP", "Unit Performance"]
        selected_tool_option = st.selectbox("Choose AI Tools", tool_options, index=0)
        
        if selected_tool_option == "All Tools":
            selected_tools = ["AI Tutor", "AI Mentor", "AI TKT", "CR", "PRP", "Unit Performance"]
        else:
            selected_tools = [selected_tool_option]
    
    # Filter summary
    st.sidebar.markdown("---")
    st.sidebar.write("**🔍 Current Filters:**")
    st.sidebar.write(f"📅 Years: {len(selected_years)} selected")
    st.sidebar.write(f"🎓 Programs: {len(selected_programs)} selected") 
    st.sidebar.write(f"🏫 Campuses: {len(selected_campuses)} selected")
    st.sidebar.write(f"🛠️ Tools: {len(selected_tools)} selected")
    
    # Reset filters button
    if st.sidebar.button("🔄 Reset All Filters"):
        st.experimental_rerun()
    
    # Apply filters to data
    filtered_data = {}
    for data_type, df in data.items():
        if df.empty:
            filtered_data[data_type] = df
            continue
            
        filtered_df = df.copy()
        
        # Apply year filter
        if selected_years and 'Year' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Year'].isin(selected_years)]
        
        # Apply program filter
        if selected_programs:
            if 'Program' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Program'].isin(selected_programs)]
            elif 'Course' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Course'].isin(selected_programs)]
            elif 'Course(GCGM/MGM/GMBA)' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Course(GCGM/MGM/GMBA)'].isin(selected_programs)]
        
        # Apply campus filter
        if selected_campuses:
            if 'Campus' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Campus'].isin(selected_campuses)]
            elif 'Campus (SG/MUM/SYD/DXB)' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Campus (SG/MUM/SYD/DXB)'].isin(selected_campuses)]
        
        filtered_data[data_type] = filtered_df
    
    # Display analysis sections based on selected tools
    if "All Tools" in selected_tools or "AI Tutor" in selected_tools:
        enhanced_ai_tutor_analysis(filtered_data)
    
    if "All Tools" in selected_tools or "AI Mentor" in selected_tools:
        # AI Mentor analysis
        st.markdown('<h2 class="section-header">🤖 AI Mentor Impact Analysis</h2>', unsafe_allow_html=True)
        
        ai_mentor_data = filtered_data.get('AI Mentor', pd.DataFrame())
        if not ai_mentor_data.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_managers = len(ai_mentor_data)
                st.metric("Total Academic Managers", total_managers)
            
            with col2:
                if "Q1_Are Students_motivated to use AI Mentor? (Yes/No, as they don't find it useful)" in ai_mentor_data.columns:
                    motivation_rate = (ai_mentor_data["Q1_Are Students_motivated to use AI Mentor? (Yes/No, as they don't find it useful)"] == 'Yes').sum() / len(ai_mentor_data) * 100
                    st.metric("Student Motivation Rate", f"{motivation_rate:.1f}%")
            
            with col3:
                if "Q2_Are students using AI Mentor effectively ? (Yes/No)" in ai_mentor_data.columns:
                    effectiveness_rate = (ai_mentor_data["Q2_Are students using AI Mentor effectively ? (Yes/No)"] == 'Yes').sum() / len(ai_mentor_data) * 100
                    st.metric("Effectiveness Rate", f"{effectiveness_rate:.1f}%")
            
            with col4:
                if "Q4_Improvement_observed in student's logical thinking, Presentation & Report Structure with the use of AI Mentor (Yes/No)" in ai_mentor_data.columns:
                    improvement_rate = (ai_mentor_data["Q4_Improvement_observed in student's logical thinking, Presentation & Report Structure with the use of AI Mentor (Yes/No)"] == 'Yes').sum() / len(ai_mentor_data) * 100
                    st.metric("Improvement Observed Rate", f"{improvement_rate:.1f}%")
    
    if "All Tools" in selected_tools or "AI TKT" in selected_tools:
        ai_tkt_analysis(filtered_data)
    
    if "All Tools" in selected_tools or "CR" in selected_tools:
        cr_analysis(filtered_data)
    
    if "All Tools" in selected_tools or "PRP" in selected_tools:
        prp_analysis(filtered_data)
    
    if "All Tools" in selected_tools or "Unit Performance" in selected_tools:
        enhanced_unit_performance_analysis(filtered_data)
    
    # Overall AI Impact Analysis
    st.markdown('<h2 class="section-header">🎯 Overall AI Initiatives Impact</h2>', unsafe_allow_html=True)
    
    ai_impact_data = filtered_data.get('AI Impact', pd.DataFrame())
    if not ai_impact_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # AI tool usage impact on placement
            if 'AI Tutor Usage' in ai_impact_data.columns and 'Placed/Not Placed' in ai_impact_data.columns:
                placement_by_ai_usage = ai_impact_data.groupby(['AI Tutor Usage', 'Placed/Not Placed']).size().unstack(fill_value=0)
                placement_by_ai_usage['Total'] = placement_by_ai_usage.sum(axis=1)
                placement_by_ai_usage['Placement_Rate'] = (placement_by_ai_usage['Placed'] / placement_by_ai_usage['Total'] * 100).round(1)
                
                fig = px.bar(placement_by_ai_usage.reset_index(), x='AI Tutor Usage', y='Placement_Rate',
                            title='Placement Rate by AI Tutor Usage Level',
                            labels={'Placement_Rate': 'Placement Rate (%)'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # CGPA vs AI tool usage
            if 'AI Tutor Usage' in ai_impact_data.columns and 'CGPA' in ai_impact_data.columns:
                cgpa_by_ai_usage = ai_impact_data.groupby('AI Tutor Usage')['CGPA'].mean().reset_index()
                fig = px.bar(cgpa_by_ai_usage, x='AI Tutor Usage', y='CGPA',
                            title='Average CGPA by AI Tutor Usage Level',
                            labels={'CGPA': 'Average CGPA'})
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    # Data summary
    st.markdown('<h2 class="section-header">📋 Data Summary</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_records = sum(len(df) for df in filtered_data.values() if not df.empty)
        st.metric("Total Records Analyzed", f"{total_records:,}")
    
    with col2:
        ai_tutor_records = len(filtered_data.get('AI Tutor', pd.DataFrame()))
        st.metric("AI Tutor Records", f"{ai_tutor_records:,}")
    
    with col3:
        cr_records = len(filtered_data.get('CR (Corporate Relations)', pd.DataFrame()))
        st.metric("CR Placement Records", f"{cr_records:,}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🚀 AI Initiatives Dashboard | SP Jain School of Global Management</p>
        <p>Data covers MGB, GMBA & GCGM programs across SG, DXB, MUM, and SYD campuses</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
