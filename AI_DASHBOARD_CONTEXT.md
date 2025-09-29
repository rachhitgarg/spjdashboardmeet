# AI Initiatives Dashboard - Context & Configuration

## Project Overview
**Project**: AI Initiatives Impact Dashboard for SP Jain School of Global Management
**Purpose**: Centralized dashboard for stakeholders to view all AI initiatives and allow departments to upload data
**Target Users**: Academic teams, Placement teams, Management, Students

## Current Application Structure

### Main Components
1. **ai_initiatives_dashboard.py** - Main dashboard application
2. **data_manager.py** - Data management and upload system
3. **Updated Templates** - New data formats with validation

### Programs & Campuses
- **Programs**: MGB, GMBA, GCGM (newly added)
- **Campuses**: SG, DXB, MUM, SYD (newly added - mainly for AI tutor)

## AI Initiatives Covered

### 1. AI Tutor (Updated Version)
- **Purpose**: Student learning assistance
- **New Features**: Enhanced with more columns, better tracking
- **Campus**: Mainly SYD, but all campuses
- **Analysis**: Before/After AI implementation effectiveness
- **Columns**: 23 columns including enhanced tracking

### 2. AI Mentor
- **Purpose**: Academic manager feedback system
- **Analysis**: Improvement observation, student motivation, effectiveness
- **Columns**: 11 columns including project types and mentoring metrics

### 3. AI TKT (Technical Knowledge Test) - Updated
- **Purpose**: Measure technical knowledge improvement
- **Analysis**: Before/After AI_TKT tool usage score comparison
- **Key Metric**: Unit score improvement after AI_TKT practice
- **Columns**: 5 columns for before/after analysis

### 4. JPT (Job Preparation Tool)
- **Purpose**: Placement preparation and tracking
- **Analysis**: Placement rates, CTC analysis, company data

### 5. CR (Corporate Relations) - Updated Format
- **Purpose**: Placement-related data management
- **Responsibility**: Placement team
- **Link**: Connected to overall placement process
- **Columns**: 17 columns for comprehensive placement tracking

### 6. PRP (Placement Readiness Program) - Updated Format
- **Purpose**: Student placement preparation evaluation
- **Features**: Mock interview performance, tool evaluation
- **Link**: Connected to JPT for comprehensive placement readiness
- **Columns**: 18 columns for detailed evaluation

### 7. Unit Performance - Modified
- **Purpose**: Academic performance tracking
- **Key Feature**: Cohort average final scores
- **Analysis**: Before/After AI tutor implementation comparison
- **Metric**: Effectiveness of AI tutor on overall cohort performance
- **Columns**: 6 columns for before/after tracking

## Data Structure Philosophy
- **Unit** = Subject (e.g., Unit 1, Unit 2)
- **Course** = Program (GCGM/MGB/GMBA)
- **Campus** = Location (SYD/SG/MUM/DXB)
- **Cohort** = Student batch/intake

## Dashboard Features Required
1. **Multi-level Filtering**: Year, Program, Campus, Tools
2. **Before/After Analysis**: AI tool effectiveness measurement
3. **Cross-Initiative Analysis**: How different AI tools impact overall outcomes
4. **Placement Correlation**: AI tool usage vs placement success
5. **Academic Performance**: Unit scores vs AI tool implementation
6. **Data Management**: Upload, download, merge, validate data

## Key Analysis Requirements

### AI TKT Analysis
- Before/After score comparison per unit per course
- Improvement measurement after AI_TKT tool practice
- Effectiveness tracking across programs and campuses

### AI Tutor Effectiveness
- Unit performance before/after AI tutor implementation
- Cohort average final score improvements
- Campus-wise and program-wise effectiveness

### Placement Readiness Integration
- PRP evaluation scores
- JPT mock interview performance
- CR placement data correlation
- Overall placement success prediction

## Technical Requirements
- **Framework**: Streamlit
- **Data Format**: CSV (converted from Excel templates)
- **Visualization**: Plotly
- **Data Management**: Pandas with validation
- **Logging**: Operation audit trail

## Updated Templates Structure
All templates now include enhanced validation and additional columns for better tracking and analysis.

## Template Column Details

### AI Tutor Template (23 columns)
- Campus, Course, Cohort, Unit_Name, Batch_size, Faculty details
- Session tracking, student participation, quiz scores
- Faculty ratings, AI tutor quality/impact scores
- Implementation efficiency, quiz usage for grading

### AI Mentor Template (11 columns)
- Academic manager details, project types (ARP, IBR 1, IBR 2, Industry Project)
- Student motivation, effectiveness, mandated usage
- Improvement observation, percentage of students who leveled up

### AI TKT Template (5 columns)
- Unit, Course, Average Grades Before/After AI TKT, Improvement%

### Unit Performance Template (6 columns)
- Course, Cohort, Year, Unit_Name, AI Tutor (Before/After), Total_Avg_score

### CR Template (17 columns)
- Course, Cohort, Year, Industry details, Company information
- Vacancies, interview details, student metrics, CTC information
- JPT usage tracking

### PRP Template (18 columns)
- Student details, course information, term-wise scores
- JPT mock interview attempts, area head mock interview scores
- Overall categorization, placement status

### AI Impact Template (10 columns)
- Student details, placement status, CGPA
- Usage levels for AI Tutor, AI Mentor, JPT, Yoodli

---
*Last Updated: September 25, 2025*
*Context maintained for AI Initiatives Dashboard development*
