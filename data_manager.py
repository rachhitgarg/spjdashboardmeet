import pandas as pd
import os
import logging
from datetime import datetime
import streamlit as st
import zipfile
from io import BytesIO

# Configure logging
logging.basicConfig(
    filename='data_operations.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DataManager:
    """Enhanced class to handle data upload, download, merge, and delete operations for all AI initiatives"""
    
    def __init__(self):
        # Updated data files mapping
        self.data_files = {
            'AI Tutor': 'ai_tutor template updated.csv',
            'AI Mentor': 'ai_mentor_template - updated.csv',
            'AI Impact': 'AI-initiatives impact updated.csv',
            'AI TKT': 'AI_ TKT _ Template updated.csv',
            'Unit Performance': 'unit_performance_template -updated.csv',
            'CR (Corporate Relations)': 'CR_template -updated.csv',
            'PRP (Placement Readiness Program)': 'PRP_template - updated.csv'
        }
        
        # Enhanced templates with all new columns (will be updated after conversion)
        self.templates = {
            'AI Tutor': {
                'filename': 'ai_tutor_template_updated.csv',
                'description': 'Enhanced AI Tutor with additional tracking columns',
                'columns': []  # Will be populated after conversion
            },
            'AI Mentor': {
                'filename': 'ai_mentor_template_updated.csv',
                'description': 'AI Mentor feedback and effectiveness tracking',
                'columns': []  # Will be populated after conversion
            },
            'AI Impact': {
                'filename': 'ai_impact_template_updated.csv',
                'description': 'Overall AI initiatives impact on student outcomes',
                'columns': []  # Will be populated after conversion
            },
            'AI TKT': {
                'filename': 'ai_tkt_template_updated.csv',
                'description': 'Technical Knowledge Test before/after analysis',
                'columns': []  # Will be populated after conversion
            },
            'Unit Performance': {
                'filename': 'unit_performance_template_updated.csv',
                'description': 'Unit performance with AI tutor effectiveness tracking',
                'columns': []  # Will be populated after conversion
            },
            'CR (Corporate Relations)': {
                'filename': 'cr_template_updated.csv',
                'description': 'Corporate Relations and placement data',
                'columns': []  # Will be populated after conversion
            },
            'PRP (Placement Readiness Program)': {
                'filename': 'prp_template_updated.csv',
                'description': 'Placement Readiness Program evaluation and JPT integration',
                'columns': []  # Will be populated after conversion
            }
        }
        
        # Initialize column structures after conversion
        self._initialize_column_structures()
    
    def _initialize_column_structures(self):
        """Initialize column structures from converted CSV files"""
        for data_type, filename in self.data_files.items():
            if os.path.exists(filename):
                try:
                    df = pd.read_csv(filename)
                    if data_type in self.templates:
                        self.templates[data_type]['columns'] = list(df.columns)
                except Exception as e:
                    st.warning(f"Could not load columns for {data_type}: {e}")
    
    def log_operation(self, operation, data_type, user_info, details=""):
        """Log data operations for audit trail"""
        log_message = f"Operation: {operation} | Data Type: {data_type} | User: {user_info} | Details: {details}"
        logging.info(log_message)
        
        # Also create a session log for display
        if 'operation_logs' not in st.session_state:
            st.session_state.operation_logs = []
        
        st.session_state.operation_logs.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operation': operation,
            'data_type': data_type,
            'user': user_info,
            'details': details
        })
    
    def create_template(self, data_type):
        """Create empty template for data type"""
        if data_type in self.templates and self.templates[data_type]['columns']:
            template_df = pd.DataFrame(columns=self.templates[data_type]['columns'])
            return template_df
        return None
    
    def download_template(self, data_type):
        """Generate downloadable template"""
        template_df = self.create_template(data_type)
        if template_df is not None:
            csv_buffer = BytesIO()
            template_df.to_csv(csv_buffer, index=False)
            return csv_buffer.getvalue()
        return None
    
    def download_all_templates(self):
        """Create a zip file with all templates"""
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for data_type, template_info in self.templates.items():
                template_df = self.create_template(data_type)
                if template_df is not None:
                    csv_buffer = BytesIO()
                    template_df.to_csv(csv_buffer, index=False)
                    zip_file.writestr(template_info['filename'], csv_buffer.getvalue())
        
        return zip_buffer.getvalue()
    
    def validate_uploaded_data(self, uploaded_df, data_type):
        """Validate uploaded data structure"""
        if data_type not in self.templates:
            return False, "Invalid data type"
        
        if not self.templates[data_type]['columns']:
            return False, "Template structure not initialized. Please run conversion first."
        
        expected_columns = set(self.templates[data_type]['columns'])
        uploaded_columns = set(uploaded_df.columns)
        
        missing_columns = expected_columns - uploaded_columns
        extra_columns = uploaded_columns - expected_columns
        
        if missing_columns:
            return False, f"Missing columns: {', '.join(missing_columns)}"
        
        if extra_columns:
            st.warning(f"Extra columns found (will be ignored): {', '.join(extra_columns)}")
        
        return True, "Valid data structure"
    
    def load_existing_data(self, data_type):
        """Load existing data file"""
        filename = self.data_files.get(data_type)
        if filename and os.path.exists(filename):
            try:
                return pd.read_csv(filename)
            except Exception as e:
                st.error(f"Error loading existing data: {e}")
                return pd.DataFrame()
        return pd.DataFrame()
    
    def merge_data(self, existing_df, new_df, data_type, user_info):
        """Merge new data with existing data"""
        try:
            # Filter new data to only include expected columns
            expected_columns = self.templates[data_type]['columns']
            new_df_filtered = new_df[expected_columns]
            
            if existing_df.empty:
                merged_df = new_df_filtered
            else:
                merged_df = pd.concat([existing_df, new_df_filtered], ignore_index=True)
            
            # Remove duplicates if any
            merged_df = merged_df.drop_duplicates()
            
            self.log_operation("MERGE", data_type, user_info, 
                             f"Added {len(new_df_filtered)} records, Total: {len(merged_df)}")
            
            return merged_df, True, "Data merged successfully"
            
        except Exception as e:
            return existing_df, False, f"Error merging data: {e}"
    
    def replace_data(self, new_df, data_type, user_info):
        """Replace existing data with new data"""
        try:
            # Filter new data to only include expected columns
            expected_columns = self.templates[data_type]['columns']
            new_df_filtered = new_df[expected_columns]
            
            self.log_operation("REPLACE", data_type, user_info, 
                             f"Replaced all data with {len(new_df_filtered)} new records")
            
            return new_df_filtered, True, "Data replaced successfully"
            
        except Exception as e:
            return pd.DataFrame(), False, f"Error replacing data: {e}"
    
    def save_data(self, df, data_type):
        """Save data to file"""
        filename = self.data_files.get(data_type)
        if filename:
            try:
                df.to_csv(filename, index=False)
                return True, "Data saved successfully"
            except Exception as e:
                return False, f"Error saving data: {e}"
        return False, "Invalid data type"
    
    def delete_data(self, data_type, user_info):
        """Delete all data for a specific type"""
        try:
            filename = self.data_files.get(data_type)
            if filename and os.path.exists(filename):
                # Create backup before deletion
                backup_filename = f"{filename}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                df = pd.read_csv(filename)
                df.to_csv(backup_filename, index=False)
                
                # Create empty dataframe with correct structure
                empty_df = self.create_template(data_type)
                empty_df.to_csv(filename, index=False)
                
                self.log_operation("DELETE", data_type, user_info, 
                                 f"All data deleted, backup created: {backup_filename}")
                
                return True, f"Data deleted successfully. Backup created: {backup_filename}"
            else:
                return False, "Data file not found"
                
        except Exception as e:
            return False, f"Error deleting data: {e}"
    
    def get_data_summary(self):
        """Get summary of all data files"""
        summary = {}
        for data_type, filename in self.data_files.items():
            if os.path.exists(filename):
                try:
                    df = pd.read_csv(filename)
                    summary[data_type] = {
                        'records': len(df),
                        'last_modified': datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d %H:%M:%S'),
                        'file_size': f"{os.path.getsize(filename) / 1024:.1f} KB",
                        'description': self.templates[data_type]['description']
                    }
                except Exception as e:
                    summary[data_type] = {'error': str(e)}
            else:
                summary[data_type] = {'records': 0, 'status': 'File not found'}
        
        return summary
    
    def get_template_info(self, data_type):
        """Get detailed template information"""
        if data_type in self.templates:
            return {
                'description': self.templates[data_type]['description'],
                'columns': self.templates[data_type]['columns'],
                'column_count': len(self.templates[data_type]['columns'])
            }
        return None
