import io
import pandas as pd
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from ..database import query_db

def get_attendance_summary(start_date, end_date, class_id=None):
    """Mengambil data mentah absensi berdasarkan filter."""
    query = '''
        SELECT a.date, a.time_in, a.status, a.note, 
               s.nis, s.full_name, c.name as class_name
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        JOIN classes c ON s.class_id = c.id
        WHERE a.date BETWEEN ? AND ?
    '''
    params = [start_date, end_date]
    
    if class_id:
        query += " AND s.class_id = ?"
        params.append(class_id)
        
    query += " ORDER BY a.date DESC, c.name ASC, s.full_name ASC"
    
    return query_db(query, params)

def generate_excel_report(records, start_date, end_date):
    """Membuat file Excel yang terformat rapi dari data absensi."""
    df = pd.DataFrame(records)
    
    if df.empty:
        df = pd.DataFrame(columns=['Tanggal', 'Waktu', 'NIS', 'Nama Siswa', 'Kelas', 'Status', 'Keterangan'])
    else:
        df.columns = ['Tanggal', 'Waktu', 'NIS', 'Nama Siswa', 'Kelas', 'Status', 'Keterangan']
        
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Tulis DataFrame ke sheet
        df.to_excel(writer, index=False, sheet_name='Rekap Absensi')
        
        # Akses workbook dan worksheet untuk formatting
        workbook = writer.book
        worksheet = writer.sheets['Rekap Absensi']
        
        # Definisi Style
        header_fill = PatternFill(start_color="064E3B", end_color="064E3B", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True, size=11, name='Calibri')
        border = Border(
            left=Side(style='thin'), right=Side(style='thin'),
            top=Side(style='thin'), bottom=Side(style='thin')
        )
        center_align = Alignment(horizontal='center', vertical='center')
        
        # Format Header
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align
            cell.border = border
            
        # Format Body & Auto-width
        for col in worksheet.columns:
            max_length = 0
            column = col[0].column_letter # Get column letter
            for cell in col:
                cell.border = border
                cell.alignment = Alignment(vertical='center', wrap_text=True)
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            adjusted_width = (max_length + 2) * 1.2
            worksheet.column_dimensions[column].width = adjusted_width
            
        # Freeze Top Row
        worksheet.freeze_panes = 'A2'
        
    output.seek(0)
    return output