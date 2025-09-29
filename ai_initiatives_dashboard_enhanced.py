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
    .section-header {
        font-size: 1.8rem;
        color: #2c3e50;
        margin: 2rem 0 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .plotly-graph-div {
        margin-bottom: 1rem;
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

def calculate_adoption_rate(participated, batch_size):
    """Calculate adoption rate ensuring it's never over 100%"""
    if batch_size == 0:
        return 0
    rate = (participated / batch_size) * 100
    return min(rate, 100.0)  # Cap at 100%

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

def enhanced_ai_tutor_analysis(data):
    """Enhanced AI Tutor Analysis with fixed metrics and visualizations"""
    st.markdown('<h2 class="section-header">📚 AI Tutor Impact Analysis</h2>', unsafe_allow_html=True)
    
    ai_tutor_data = data.get('AI Tutor', pd.DataFrame())
    
    if ai_tutor_data.empty:
        st.warning("No AI Tutor data available. Please upload data using the Data Management page.")
        return
    
    # Key metrics with proper calculations
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'Total_Students_Participated_watched videos' in ai_tutor_data.columns and 'Batch_size(number should come from student feedback form)' in ai_tutor_data.columns:
            # Calculate adoption rate properly
            ai_tutor_data['Adoption_Rate'] = ai_tutor_data.apply(
                lambda row: calculate_adoption_rate(
                    row['Total_Students_Participated_watched videos'], 
                    row['Batch_size(number should come from student feedback form)']
                ), axis=1
            )
            avg_adoption_rate = ai_tutor_data['Adoption_Rate'].mean()
            st.metric("Average Adoption Rate", f"{avg_adoption_rate:.1f}%")
    
    with col2:
        if 'Avg_Rating_for_AI_Tutor_Tool' in ai_tutor_data.columns:
            avg_rating = ai_tutor_data['Avg_Rating_for_AI_Tutor_Tool'].mean()
            st.metric("Average AI Tutor Rating", f"{avg_rating:.2f}/5.0")
    
    with col3:
        if 'No_of_Session_IDs_created' in ai_tutor_data.columns:
            total_sessions = ai_tutor_data['No_of_Session_IDs_created'].sum()
            st.metric("Total Sessions Created", f"{total_sessions:,}")
    
    with col4:
        if 'Average Score of AI Tutor Platform Quiz' in ai_tutor_data.columns:
            avg_quiz_score = ai_tutor_data['Average Score of AI Tutor Platform Quiz'].mean()
            st.metric("Average Quiz Score", f"{avg_quiz_score:.1f}/10")
    
    # Visualizations with proper legends and labels
    col1, col2 = st.columns(2)
    
    with col1:
        # Student Adoption Rate Trend by Year (fixed year issue)
        if 'Cohort' in ai_tutor_data.columns and 'Adoption_Rate' in ai_tutor_data.columns:
            # Extract year from cohort
            ai_tutor_data['Year'] = ai_tutor_data['Cohort'].apply(lambda x: int(x.split('-')[1]) + 2000)
            
            yearly_adoption = ai_tutor_data.groupby('Year')['Adoption_Rate'].mean().reset_index()
            
            fig = px.line(yearly_adoption, x='Year', y='Adoption_Rate',
                         title='AI Tutor Student Adoption Rate Trend',
                         labels={'Adoption_Rate': 'Adoption Rate (%)', 'Year': 'Academic Year'},
                         markers=True)
            fig.update_layout(
                xaxis=dict(tickmode='linear', dtick=1),
                yaxis=dict(range=[0, 100]),
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Campus-wise Analysis
        if 'Campus (SG/MUM/SYD/DXB)' in ai_tutor_data.columns and 'Adoption_Rate' in ai_tutor_data.columns:
            campus_adoption = ai_tutor_data.groupby('Campus (SG/MUM/SYD/DXB)')['Adoption_Rate'].mean().reset_index()
            
            fig = px.bar(campus_adoption, x='Campus (SG/MUM/SYD/DXB)', y='Adoption_Rate',
                        title='Student Adoption Rate by Campus',
                        labels={'Adoption_Rate': 'Adoption Rate (%)', 'Campus (SG/MUM/SYD/DXB)': 'Campus'},
                        color='Adoption_Rate',
                        color_continuous_scale='Blues')
            fig.update_layout(
                showlegend=False,
                height=400,
                yaxis=dict(range=[0, 100])
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Faculty Feedback Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Faculty_Feedback' in ai_tutor_data.columns:
            feedback_counts = ai_tutor_data['Faculty_Feedback'].value_counts()
            
            fig = px.pie(values=feedback_counts.values, names=feedback_counts.index,
                        title='Faculty Feedback Distribution',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Quiz Performance by Subject
        if 'Unit_Name' in ai_tutor_data.columns and 'Average Score of AI Tutor Platform Quiz' in ai_tutor_data.columns:
            subject_performance = ai_tutor_data.groupby('Unit_Name')['Average Score of AI Tutor Platform Quiz'].mean().reset_index()
            subject_performance = subject_performance.sort_values('Average Score of AI Tutor Platform Quiz', ascending=True).tail(10)
            
            fig = px.bar(subject_performance, 
                        x='Average Score of AI Tutor Platform Quiz', 
                        y='Unit_Name',
                        title='Top 10 Subjects by Quiz Performance',
                        labels={'Average Score of AI Tutor Platform Quiz': 'Average Quiz Score (out of 10)', 'Unit_Name': 'Subject'},
                        orientation='h',
                        color='Average Score of AI Tutor Platform Quiz',
                        color_continuous_scale='Viridis')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

def enhanced_prp_analysis(data):
    """Enhanced PRP Analysis with proper JPT score handling and filtering"""
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
            st.metric("Average Term Score", f"{avg_score:.1f}/100")
    
    with col3:
        if 'No. of JPT Mock Interviews attempted and scored equal or above 80%' in prp_data.columns:
            avg_jpt = prp_data['No. of JPT Mock Interviews attempted and scored equal or above 80%'].mean()
            st.metric("Avg JPT High Score Attempts", f"{avg_jpt:.1f}")
    
    with col4:
        if 'Area Head Mock Interview Score' in prp_data.columns:
            avg_mock = prp_data['Area Head Mock Interview Score'].mean()
            st.metric("Avg Mock Interview Score", f"{avg_mock:.1f}/100")
    
    # Enhanced visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Term Performance Comparison
        if all(col in prp_data.columns for col in ['Term-1', 'Term-2', 'Term-3']):
            term_avg = {
                'Term-1': prp_data['Term-1'].mean(),
                'Term-2': prp_data['Term-2'].mean(),
                'Term-3': prp_data['Term-3'].mean()
            }
            
            fig = px.bar(x=list(term_avg.keys()), y=list(term_avg.values()),
                        title='Average Performance by Term',
                        labels={'x': 'Academic Term', 'y': 'Average Score (out of 100)'},
                        color=list(term_avg.values()),
                        color_continuous_scale='Blues')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Placement Status Distribution
        if 'Placed/Not Placed' in prp_data.columns:
            placement_counts = prp_data['Placed/Not Placed'].value_counts()
            
            fig = px.pie(values=placement_counts.values, names=placement_counts.index,
                        title='Student Placement Status',
                        color_discrete_sequence=['#2E8B57', '#DC143C'])
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # JPT Performance Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # JPT Attempts Distribution
        if 'No. of JPT Mock Interviews attempted and scored equal or above 80%' in prp_data.columns:
            jpt_distribution = prp_data['No. of JPT Mock Interviews attempted and scored equal or above 80%'].value_counts().sort_index()
            
            fig = px.bar(x=jpt_distribution.index, y=jpt_distribution.values,
                        title='Distribution of JPT High Score Attempts',
                        labels={'x': 'Number of JPT Attempts (Score ≥80%)', 'y': 'Number of Students'},
                        color=jpt_distribution.values,
                        color_continuous_scale='Greens')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Student Category Distribution
        if 'Categorise student overall (Outstanding, Good, Average, Needs Handholding)' in prp_data.columns:
            category_counts = prp_data['Categorise student overall (Outstanding, Good, Average, Needs Handholding)'].value_counts()
            
            fig = px.bar(x=category_counts.index, y=category_counts.values,
                        title='Student Performance Categories',
                        labels={'x': 'Performance Category', 'y': 'Number of Students'},
                        color=category_counts.values,
                        color_continuous_scale='RdYlBu_r')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

def enhanced_ai_impact_analysis(data):
    """Enhanced AI Impact Analysis with intuitive charts"""
    st.markdown('<h2 class="section-header">🎯 Overall AI Initiatives Impact Analysis</h2>', unsafe_allow_html=True)
    
    ai_impact_data = data.get('AI Impact', pd.DataFrame())
    
    if ai_impact_data.empty:
        st.warning("No AI Impact data available. Please upload data using the Data Management page.")
        return
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_students = len(ai_impact_data)
        st.metric("Total Students Analyzed", f"{total_students:,}")
    
    with col2:
        if 'Placed/Not Placed' in ai_impact_data.columns:
            placement_rate = (ai_impact_data['Placed/Not Placed'] == 'Placed').sum() / len(ai_impact_data) * 100
            st.metric("Overall Placement Rate", f"{placement_rate:.1f}%")
    
    with col3:
        if 'CGPA' in ai_impact_data.columns:
            avg_cgpa = ai_impact_data['CGPA'].mean()
            st.metric("Average CGPA", f"{avg_cgpa:.2f}/4.0")
    
    with col4:
        # High AI usage students (using multiple tools)
        ai_tools = ['AI Tutor Usage', 'AI Mentor Usage', 'JPT Usage', 'Yoodli Usage']
        available_tools = [col for col in ai_tools if col in ai_impact_data.columns]
        if available_tools:
            high_usage_count = 0
            for _, row in ai_impact_data.iterrows():
                high_usage_tools = sum(1 for tool in available_tools if row[tool] in ['High', 'Medium'])
                if high_usage_tools >= 2:
                    high_usage_count += 1
            high_usage_rate = (high_usage_count / len(ai_impact_data)) * 100
            st.metric("Multi-Tool Users", f"{high_usage_rate:.1f}%")
    
    # Enhanced visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # AI Tool Usage Impact on Placement
        if 'AI Tutor Usage' in ai_impact_data.columns and 'Placed/Not Placed' in ai_impact_data.columns:
            # Create placement rate by AI usage level
            placement_analysis = ai_impact_data.groupby('AI Tutor Usage').agg({
                'Placed/Not Placed': lambda x: (x == 'Placed').sum() / len(x) * 100
            }).reset_index()
            placement_analysis.columns = ['AI_Usage_Level', 'Placement_Rate']
            
            # Order usage levels logically
            usage_order = ['None', 'Low', 'Medium', 'High']
            placement_analysis['AI_Usage_Level'] = pd.Categorical(placement_analysis['AI_Usage_Level'], categories=usage_order, ordered=True)
            placement_analysis = placement_analysis.sort_values('AI_Usage_Level')
            
            fig = px.bar(placement_analysis, x='AI_Usage_Level', y='Placement_Rate',
                        title='Placement Success by AI Tutor Usage Level',
                        labels={'AI_Usage_Level': 'AI Tutor Usage Level', 'Placement_Rate': 'Placement Rate (%)'},
                        color='Placement_Rate',
                        color_continuous_scale='RdYlGn',
                        text='Placement_Rate')
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # CGPA Distribution by AI Usage
        if 'AI Tutor Usage' in ai_impact_data.columns and 'CGPA' in ai_impact_data.columns:
            fig = px.box(ai_impact_data, x='AI Tutor Usage', y='CGPA',
                        title='CGPA Distribution by AI Tutor Usage',
                        labels={'AI_Tutor_Usage': 'AI Tutor Usage Level', 'CGPA': 'CGPA (out of 4.0)'},
                        color='AI Tutor Usage',
                        color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Multi-tool usage analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # AI Tool Usage Heatmap
        ai_tools = ['AI Tutor Usage', 'AI Mentor Usage', 'JPT Usage', 'Yoodli Usage']
        available_tools = [col for col in ai_tools if col in ai_impact_data.columns]
        
        if len(available_tools) >= 2:
            # Create correlation matrix for tool usage
            tool_data = ai_impact_data[available_tools].copy()
            
            # Convert usage levels to numeric
            usage_mapping = {'None': 0, 'Low': 1, 'Medium': 2, 'High': 3}
            for tool in available_tools:
                tool_data[tool] = tool_data[tool].map(usage_mapping)
            
            correlation_matrix = tool_data.corr()
            
            fig = px.imshow(correlation_matrix,
                           title='AI Tool Usage Correlation Matrix',
                           labels=dict(color="Correlation"),
                           color_continuous_scale='RdBu_r',
                           aspect="auto")
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Program-wise AI Impact
        if 'Course' in ai_impact_data.columns and 'Placed/Not Placed' in ai_impact_data.columns:
            program_placement = ai_impact_data.groupby('Course').agg({
                'Placed/Not Placed': lambda x: (x == 'Placed').sum() / len(x) * 100,
                'CGPA': 'mean'
            }).reset_index()
            program_placement.columns = ['Program', 'Placement_Rate', 'Avg_CGPA']
            
            fig = px.scatter(program_placement, x='Avg_CGPA', y='Placement_Rate', 
                           size='Placement_Rate', color='Program',
                           title='Program Performance: CGPA vs Placement Rate',
                           labels={'Avg_CGPA': 'Average CGPA', 'Placement_Rate': 'Placement Rate (%)'},
                           hover_data=['Program'])
            fig.update_layout(height=400)
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
    
    if "All Tools" in selected_tools or "PRP" in selected_tools:
        enhanced_prp_analysis(filtered_data)
    
    if "All Tools" in selected_tools or len([t for t in selected_tools if t in ["AI Impact", "AI Tutor", "AI Mentor", "JPT"]]) > 0:
        enhanced_ai_impact_analysis(filtered_data)
    
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