import pandas as pd
import os
from datetime import datetime

def convert_excel_to_csv():
    """Convert all updated Excel templates to CSV format for analysis"""
    
    # Updated Excel templates in the main folder
    excel_templates = {
        'AI Tutor': 'ai_tutor template updated.xlsx',
        'AI Mentor': 'ai_mentor_template - updated.xlsx', 
        'AI Impact': 'AI-initiatives impact updated.xlsx',
        'AI TKT': 'AI_ TKT _ Template updated.xlsx',
        'Unit Performance': 'unit_performance_template -updated.xlsx',
        'CR (Corporate Relations)': 'CR_template -updated.xlsx',
        'PRP (Placement Readiness Program)': 'PRP_template - updated.xlsx'
    }
    
    print("=" * 80)
    print("CONVERTING UPDATED TEMPLATES TO CSV")
    print("=" * 80)
    print(f"Conversion started at: {datetime.now()}")
    print()
    
    conversion_results = {}
    
    for template_name, excel_file in excel_templates.items():
        if os.path.exists(excel_file):
            try:
                print(f"📄 Processing: {template_name}")
                print(f"   File: {excel_file}")
                
                # Read Excel file
                df = pd.read_excel(excel_file)
                
                # Generate CSV filename
                csv_filename = excel_file.replace('.xlsx', '.csv')
                
                # Save as CSV
                df.to_csv(csv_filename, index=False)
                
                # Store results
                conversion_results[template_name] = {
                    'excel_file': excel_file,
                    'csv_file': csv_filename,
                    'shape': df.shape,
                    'columns': list(df.columns),
                    'status': 'SUCCESS'
                }
                
                print(f"   ✅ Converted to: {csv_filename}")
                print(f"   📊 Shape: {df.shape}")
                print(f"   📋 Columns ({len(df.columns)}): {list(df.columns)}")
                print()
                
                # Display first few rows for verification
                if not df.empty:
                    print("   📝 Sample data:")
                    print(df.head(2).to_string(index=False))
                else:
                    print("   ⚠️ Template is empty (header only)")
                print("-" * 80)
                
            except Exception as e:
                conversion_results[template_name] = {
                    'excel_file': excel_file,
                    'status': 'ERROR',
                    'error': str(e)
                }
                print(f"   ❌ Error converting {excel_file}: {e}")
                print("-" * 80)
        else:
            conversion_results[template_name] = {
                'excel_file': excel_file,
                'status': 'FILE_NOT_FOUND'
            }
            print(f"   ⚠️ File not found: {excel_file}")
            print("-" * 80)
    
    # Summary
    print("\n" + "=" * 80)
    print("CONVERSION SUMMARY")
    print("=" * 80)
    
    successful = sum(1 for r in conversion_results.values() if r['status'] == 'SUCCESS')
    total = len(conversion_results)
    
    print(f"Total templates: {total}")
    print(f"Successfully converted: {successful}")
    print(f"Failed: {total - successful}")
    print()
    
    for name, result in conversion_results.items():
        status_icon = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"{status_icon} {name}: {result['status']}")
    
    print("=" * 80)
    
    return conversion_results

if __name__ == "__main__":
    results = convert_excel_to_csv()
