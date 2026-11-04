import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def apply_page_borders(section):
    sectPr = section._sectPr
    # Remove existing pgBorders if any
    for child in sectPr.findall(qn('w:pgBorders')):
        sectPr.remove(child)
    pgBorders = OxmlElement('w:pgBorders')
    pgBorders.set(qn('w:offsetFrom'), 'page')
    for border_name in ['top', 'left', 'bottom', 'right']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '8')      # 1 pt border
        border.set(qn('w:space'), '20')   # 20 pt margin from page boundary
        border.set(qn('w:color'), '000000')
        pgBorders.append(border)
    sectPr.append(pgBorders)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def style_table(table, col_widths, col_alignments, header_bg="E6E6E6"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="888888"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="888888"/>'
        '</w:tblBorders>'
    )
    tblPr.append(tblBorders)
    
    for row_idx, row in enumerate(table.rows):
        is_header = (row_idx == 0)
        # Prevent row split across pages
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement('w:cantSplit'))
        if is_header:
            trPr.append(OxmlElement('w:tblHeader'))
            
        for c_idx, cell in enumerate(row.cells):
            cell.width = Inches(col_widths[c_idx])
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            if is_header:
                set_cell_background(cell, header_bg)
            for p in cell.paragraphs:
                p.alignment = col_alignments[c_idx]
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                for run in p.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(10.5 if not is_header else 11)
                    if is_header:
                        run.font.bold = True

def add_footer_page_number(section, text_pattern):
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.text = text_pattern
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in p.runs:
        run.font.name = 'Times New Roman'
        run.font.size = Pt(10)
        run.font.color.rgb = RGBColor(80, 80, 80)

def main():
    doc = docx.Document()
    
    # Base Document Style
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)
    
    # ---------------------------------------------------------------------------
    # PAGE 1: TITLE / COVER PAGE
    # ---------------------------------------------------------------------------
    sec_cover = doc.sections[0]
    sec_cover.top_margin = Inches(0.8)
    sec_cover.bottom_margin = Inches(0.8)
    sec_cover.left_margin = Inches(1.0)
    sec_cover.right_margin = Inches(1.0)
    apply_page_borders(sec_cover)
    # No footer on cover page
    sec_cover.footer.paragraphs[0].text = ""
    
    logo_path = r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\kpriet_logo.png"
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(10)
        p_logo.paragraph_format.space_after = Pt(0)
        run_logo = p_logo.add_run()
        run_logo.add_picture(logo_path, width=Inches(1.8))
        
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(4)
    p_inst.paragraph_format.space_after = Pt(2)
    r = p_inst.add_run("KPR INSTITUTE OF ENGINEERING AND TECHNOLOGY\n")
    r.font.bold = True
    r.font.size = Pt(13)
    r2 = p_inst.add_run("(Autonomous Institution)")
    r2.font.bold = True
    r2.font.size = Pt(10.5)
    
    p_space1 = doc.add_paragraph()
    p_space1.paragraph_format.space_before = Pt(28)
    p_space1.paragraph_format.space_after = Pt(0)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(0)
    p_title.paragraph_format.line_spacing = 1.25
    r = p_title.add_run("VEHICLE SERVICE MANAGEMENT SYSTEM\n")
    r.font.bold = True
    r.font.size = Pt(16)
    r2 = p_title.add_run("SMART AUTOMOTIVE SERVICE AND FLEET CARE PORTAL")
    r2.font.bold = True
    r2.font.size = Pt(13)
    
    p_space2 = doc.add_paragraph()
    p_space2.paragraph_format.space_before = Pt(36)
    p_space2.paragraph_format.space_after = Pt(0)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(0)
    r = p_sub.add_run("A MINI PROJECT REPORT")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p_space3 = doc.add_paragraph()
    p_space3.paragraph_format.space_before = Pt(30)
    p_space3.paragraph_format.space_after = Pt(0)
    
    p_subm = doc.add_paragraph()
    p_subm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_subm.paragraph_format.space_before = Pt(0)
    p_subm.paragraph_format.space_after = Pt(6)
    r = p_subm.add_run("Submitted by\n")
    r.font.italic = True
    r.font.size = Pt(11)
    r2 = p_subm.add_run("ROHITH KANNAN (24CS150)")
    r2.font.bold = True
    r2.font.size = Pt(12)
    
    p_space4 = doc.add_paragraph()
    p_space4.paragraph_format.space_before = Pt(28)
    p_space4.paragraph_format.space_after = Pt(0)
    
    p_dept = doc.add_paragraph()
    p_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_dept.paragraph_format.space_before = Pt(0)
    p_dept.paragraph_format.space_after = Pt(0)
    p_dept.paragraph_format.line_spacing = 1.25
    r = p_dept.add_run("U21CS503 - Web Technology\n\n")
    r.font.bold = True
    r.font.size = Pt(11)
    r_in = p_dept.add_run("in\n\n")
    r_in.font.italic = True
    r_in.font.size = Pt(10)
    r2 = p_dept.add_run("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING\n")
    r2.font.bold = True
    r2.font.size = Pt(11.5)
    r3 = p_dept.add_run("KPRIET\n\n")
    r3.font.bold = True
    r3.font.size = Pt(11.5)
    r4 = p_dept.add_run("ARASUR, COIMBATORE - 641 407\nNOVEMBER 2026")
    r4.font.bold = True
    r4.font.size = Pt(11)
    
    # ---------------------------------------------------------------------------
    # PAGE 2: BONAFIDE CERTIFICATE
    # ---------------------------------------------------------------------------
    sec_cert = doc.add_section()
    sec_cert.top_margin = Inches(1.0)
    sec_cert.bottom_margin = Inches(1.0)
    sec_cert.left_margin = Inches(1.0)
    sec_cert.right_margin = Inches(1.0)
    apply_page_borders(sec_cert)
    add_footer_page_number(sec_cert, "~ 1 ~")
    
    p_c_title = doc.add_paragraph()
    p_c_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_title.paragraph_format.space_before = Pt(20)
    p_c_title.paragraph_format.space_after = Pt(36)
    r = p_c_title.add_run("BONAFIDE CERTIFICATE")
    r.font.bold = True
    r.font.size = Pt(14)
    
    p_c_body = doc.add_paragraph()
    p_c_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_c_body.paragraph_format.line_spacing = 1.25
    p_c_body.paragraph_format.space_after = Pt(50)
    p_c_body.add_run("Certified that this project report ")
    r = p_c_body.add_run("“VEHICLE SERVICE MANAGEMENT SYSTEM – SMART AUTOMOTIVE SERVICE AND FLEET CARE PORTAL”")
    r.font.bold = True
    p_c_body.add_run(" is the bonafide work of ")
    r2 = p_c_body.add_run("“ROHITH KANNAN (24CS150)”")
    r2.font.bold = True
    p_c_body.add_run(" who carried out the project work under my supervision.")
    
    # Table of Signatures (HOD & Supervisor)
    t_sig = doc.add_table(rows=2, cols=2)
    t_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r in t_sig.rows:
        for c in r.cells:
            c.width = Inches(3.2)
    
    p1 = t_sig.rows[0].cells[0].paragraphs[0]
    p1.add_run("_________________________\n").font.bold = True
    r = p1.add_run("Dr. MIRUNA JOE AMALI\n")
    r.font.bold = True
    p1.add_run("HEAD OF THE DEPARTMENT\nProfessor\nComputer Science and Engineering\nKPR Institute of Engineering and Technology\nArasur, Coimbatore – 641407")
    p1.paragraph_format.line_spacing = 1.15
    
    p2 = t_sig.rows[0].cells[1].paragraphs[0]
    p2.add_run("_________________________\n").font.bold = True
    r = p2.add_run("RAJESHKUMAR S\n")
    r.font.bold = True
    p2.add_run("SUPERVISOR,\nAssistant professor III\nComputer Science and Engineering\nKPR Institute of Engineering and Technology\nArasur, Coimbatore – 641407")
    p2.paragraph_format.line_spacing = 1.15
    
    p_viva = doc.add_paragraph()
    p_viva.paragraph_format.space_before = Pt(65)
    p_viva.paragraph_format.space_after = Pt(45)
    r = p_viva.add_run("Submitted for the University Mini project Viva – Voce held on _______________")
    r.font.bold = True
    
    t_exam = doc.add_table(rows=1, cols=2)
    t_exam.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c in t_exam.rows[0].cells:
        c.width = Inches(3.2)
    p_ex1 = t_exam.rows[0].cells[0].paragraphs[0]
    p_ex1.add_run("___________________________\n").font.bold = True
    p_ex1.add_run("INTERNAL EXAMINER").font.bold = True
    
    p_ex2 = t_exam.rows[0].cells[1].paragraphs[0]
    p_ex2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_ex2.add_run("___________________________\n").font.bold = True
    p_ex2.add_run("EXTERNAL EXAMINER").font.bold = True

    # ---------------------------------------------------------------------------
    # PAGE 3: TABLE OF CONTENTS (- i -)
    # ---------------------------------------------------------------------------
    sec_toc = doc.add_section()
    sec_toc.top_margin = Inches(1.0)
    sec_toc.bottom_margin = Inches(1.0)
    sec_toc.left_margin = Inches(1.0)
    sec_toc.right_margin = Inches(1.0)
    apply_page_borders(sec_toc)
    add_footer_page_number(sec_toc, "- i -")
    
    p_toc_t = doc.add_paragraph()
    p_toc_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_t.paragraph_format.space_before = Pt(10)
    p_toc_t.paragraph_format.space_after = Pt(18)
    r = p_toc_t.add_run("TABLE OF CONTENTS")
    r.font.bold = True
    r.font.size = Pt(13)
    
    toc_data = [
        ("CHAPTER\nNO", "TITLE", "PAGE NO"),
        ("", "LIST OF FIGURES", "iii"),
        ("", "LIST OF ABBREVIATIONS", "iv"),
        ("1", "ABSTRACT", "1"),
        ("2", "INTRODUCTION", "2"),
        ("", "2.1 Background and Need for the Project", "2"),
        ("", "2.2 Objectives", "3"),
        ("", "2.3 Scope", "3"),
        ("", "2.4 Development Plan", "3"),
        ("3", "IMPLEMENTATION", "5"),
        ("", "3.1 Tech Stack", "5"),
        ("", "3.2 Modules", "7"),
        ("", "     3.2.1 Database Module", "7"),
        ("", "     3.2.2 Registration and Login Module", "9"),
        ("", "     3.2.3 Customer Dashboard Module", "9"),
        ("", "     3.2.4 Vehicle Fleet Management Module", "9"),
        ("", "     3.2.5 Service Booking and Estimation Module", "10"),
        ("", "     3.2.6 Service History and Tracking Module", "11"),
        ("", "     3.2.7 Admin Overview Dashboard Module", "11"),
        ("", "     3.2.8 Service Request Queue and Dispatch Module", "11"),
        ("", "     3.2.9 Customer Directory and Fleet Module", "12"),
        ("", "     3.2.10 Security and Access Control Module", "12"),
        ("4", "OUTCOME", "13"),
        ("", "4.1 Implementation Outcome", "13"),
        ("", "4.2 Module-wise Outcome with Screenshots", "13"),
        ("", "4.3 Comparison with Existing Methods", "18"),
        ("", "4.4 Discussion and Limitations", "19"),
        ("5", "CONCLUSION", "20"),
        ("", "5.1 Future Scope", "20"),
        ("", "REFERENCES", "21"),
    ]
    
    t_toc = doc.add_table(rows=len(toc_data), cols=3)
    for r_idx, row in enumerate(toc_data):
        for c_idx, val in enumerate(row):
            t_toc.rows[r_idx].cells[c_idx].paragraphs[0].text = val
            if r_idx in [1, 2, 3, 4, 9, 22, 27, 29] or c_idx == 0:
                for run in t_toc.rows[r_idx].cells[c_idx].paragraphs[0].runs:
                    run.font.bold = True
    style_table(t_toc, [1.0, 4.4, 1.0], [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER])

    # ---------------------------------------------------------------------------
    # PAGE 4: LIST OF FIGURES (- ii -)
    # ---------------------------------------------------------------------------
    sec_lof = doc.add_section()
    sec_lof.top_margin = Inches(1.0)
    sec_lof.bottom_margin = Inches(1.0)
    sec_lof.left_margin = Inches(1.0)
    sec_lof.right_margin = Inches(1.0)
    apply_page_borders(sec_lof)
    add_footer_page_number(sec_lof, "- ii -")
    
    p_lof_t = doc.add_paragraph()
    p_lof_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof_t.paragraph_format.space_before = Pt(10)
    p_lof_t.paragraph_format.space_after = Pt(18)
    r = p_lof_t.add_run("LIST OF FIGURES")
    r.font.bold = True
    r.font.size = Pt(13)
    
    lof_data = [
        ("FIGURE\nNO", "FIGURE NAME", "PAGE NO"),
        ("3.1", "SYSTEM ARCHITECTURE OF VEHICLE SERVICE MANAGEMENT SYSTEM", "5"),
        ("3.2", "ENTITY RELATIONSHIP DIAGRAM OF THE DATABASE", "8"),
        ("3.3", "FLOWCHART OF THE SERVICE BOOKING AND DISPATCH ALGORITHM", "10"),
        ("3.4", "TYPICAL WORKFLOW OF VSM PRO", "11"),
        ("4.1", "PUBLIC LANDING PAGE MODULE", "13"),
        ("4.2", "LOGIN MODULE", "13"),
        ("4.3", "CUSTOMER DASHBOARD MODULE", "14"),
        ("4.4", "VEHICLE FLEET MANAGEMENT MODULE", "14"),
        ("4.5", "SERVICE BOOKING APPOINTMENT MODULE", "15"),
        ("4.6", "SERVICE REQUEST HISTORY MODULE", "15"),
        ("4.7", "ADMIN DASHBOARD OVERVIEW MODULE", "16"),
        ("4.8", "ADMIN SERVICE REQUEST QUEUE MODULE", "16"),
        ("4.9", "ADMIN CUSTOMER DIRECTORY & FLEET MODULE", "17"),
    ]
    t_lof = doc.add_table(rows=len(lof_data), cols=3)
    for r_idx, row in enumerate(lof_data):
        for c_idx, val in enumerate(row):
            t_lof.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t_lof, [1.0, 4.4, 1.0], [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER])

    # ---------------------------------------------------------------------------
    # PAGE 5: LIST OF ABBREVIATIONS (- iii -)
    # ---------------------------------------------------------------------------
    sec_loa = doc.add_section()
    sec_loa.top_margin = Inches(1.0)
    sec_loa.bottom_margin = Inches(1.0)
    sec_loa.left_margin = Inches(1.0)
    sec_loa.right_margin = Inches(1.0)
    apply_page_borders(sec_loa)
    add_footer_page_number(sec_loa, "- iii -")
    
    p_loa_t = doc.add_paragraph()
    p_loa_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loa_t.paragraph_format.space_before = Pt(10)
    p_loa_t.paragraph_format.space_after = Pt(22)
    r = p_loa_t.add_run("LIST OF ABBREVIATIONS")
    r.font.bold = True
    r.font.size = Pt(13)
    
    abbr_data = [
        ("API", "APPLICATION PROGRAMMING INTERFACE"),
        ("CRUD", "CREATE, READ, UPDATE, DELETE"),
        ("CSRF", "CROSS-SITE REQUEST FORGERY"),
        ("CSS", "CASCADING STYLE SHEETS"),
        ("DOM", "DOCUMENT OBJECT MODEL"),
        ("ER", "ENTITY RELATIONSHIP"),
        ("FK", "FOREIGN KEY"),
        ("HTML", "HYPERTEXT MARKUP LANGUAGE"),
        ("HTTP", "HYPERTEXT TRANSFER PROTOCOL"),
        ("IDE", "INTEGRATED DEVELOPMENT ENVIRONMENT"),
        ("JS", "JAVASCRIPT"),
        ("JSON", "JAVASCRIPT OBJECT NOTATION"),
        ("MVC", "MODEL VIEW CONTROLLER"),
        ("OWASP", "OPEN WORLD WIDE APPLICATION SECURITY PROJECT"),
        ("PDO", "PHP DATA OBJECTS"),
        ("PHP", "PHP: HYPERTEXT PREPROCESSOR"),
        ("PK", "PRIMARY KEY"),
        ("RBAC", "ROLE-BASED ACCESS CONTROL"),
        ("SQL", "STRUCTURED QUERY LANGUAGE"),
        ("UI", "USER INTERFACE"),
        ("URL", "UNIFORM RESOURCE LOCATOR"),
        ("VSM", "VEHICLE SERVICE MANAGEMENT"),
        ("XAMPP", "CROSS-PLATFORM, APACHE, MARIADB, PHP AND PERL"),
        ("XSS", "CROSS-SITE SCRIPTING"),
    ]
    
    t_loa = doc.add_table(rows=len(abbr_data), cols=2)
    t_loa.alignment = WD_TABLE_ALIGNMENT.CENTER
    for r_idx, (a, full) in enumerate(abbr_data):
        cell_a = t_loa.rows[r_idx].cells[0]
        cell_f = t_loa.rows[r_idx].cells[1]
        cell_a.width = Inches(1.8)
        cell_f.width = Inches(4.6)
        p_a = cell_a.paragraphs[0]
        p_a.text = a
        p_a.runs[0].font.bold = True
        p_a.runs[0].font.name = 'Times New Roman'
        p_a.paragraph_format.space_before = Pt(3)
        p_a.paragraph_format.space_after = Pt(3)
        
        p_f = cell_f.paragraphs[0]
        p_f.text = full
        p_f.runs[0].font.name = 'Times New Roman'
        p_f.paragraph_format.space_before = Pt(3)
        p_f.paragraph_format.space_after = Pt(3)

    # ---------------------------------------------------------------------------
    # CHAPTER 1: ABSTRACT (Page - 1 -)
    # ---------------------------------------------------------------------------
    sec_ch1 = doc.add_section()
    sec_ch1.top_margin = Inches(1.0)
    sec_ch1.bottom_margin = Inches(1.0)
    sec_ch1.left_margin = Inches(1.25)
    sec_ch1.right_margin = Inches(1.0)
    apply_page_borders(sec_ch1)
    add_footer_page_number(sec_ch1, "- 1 -")
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run("CHAPTER - 1\nABSTRACT")
    r.font.bold = True
    r.font.size = Pt(13)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(12)
    p.add_run(
        "Vehicle Service Management System (VSM Pro) is a full-stack, web-based automotive service management platform "
        "developed using HTML5, CSS3, Bootstrap 5, vanilla JavaScript, PHP 8, and MySQL to streamline maintenance operations, "
        "vehicle fleet tracking, appointment booking, and workshop administration. Traditional automotive repair centers rely on "
        "manual paper job cards, scattered physical registers, and uncoordinated telephone communications, causing record losses, "
        "prolonged turnaround times, and lack of billing transparency. VSM Pro addresses these inefficiencies by establishing a "
        "centralized digital ecosystem connecting vehicle owners directly with workshop service administrators."
    )
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(12)
    p.add_run(
        "The application provides two distinct, role-based environments. The Customer Suite enables vehicle owners to register, log in, "
        "manage a personalized multi-vehicle fleet (cars, motorcycles, electric vehicles) with comprehensive technical specifications, "
        "schedule certified service appointments with live base-rate pricing estimation, and monitor real-time repair progress across four standardized "
        "status states (Pending, In Progress, Completed, Cancelled). Customers can review technician diagnostics, inspect itemized costs, and cancel "
        "pending requests directly. The Admin Management Console equips workshop managers with an interactive operations dashboard featuring "
        "live fleet metrics, revenue calculations, a searchable and filterable service ticket dispatch queue, diagnostic remark authoring, "
        "cost finalization modals, and a customer fleet directory."
    )
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(12)
    p.add_run(
        "Security and software architectural integrity are implemented in adherence to Open Web Application Security Project (OWASP) guidelines. "
        "All database transactions utilize PHP Data Objects (PDO) with strict prepared statements and parameter binding to neutralize SQL injection. "
        "Authentication relies on cryptographic salted hashing via PHP's native password_hash() and password_verify() functions alongside session "
        "regeneration and strict Role-Based Access Control (RBAC). User interfaces feature sanitized output escaping to counter Cross-Site Scripting (XSS) "
        "and dual-tier client/server input validation. The platform was developed and comprehensively tested within a local XAMPP environment on Google Chrome, "
        "validating robust asynchronous client interactivity, relational database integrity with cascading foreign keys, and responsive UI performance."
    )

    # ---------------------------------------------------------------------------
    # CHAPTER 2: INTRODUCTION (Page - 2 - to - 4 -)
    # ---------------------------------------------------------------------------
    sec_ch2 = doc.add_section()
    sec_ch2.top_margin = Inches(1.0)
    sec_ch2.bottom_margin = Inches(1.0)
    sec_ch2.left_margin = Inches(1.25)
    sec_ch2.right_margin = Inches(1.0)
    apply_page_borders(sec_ch2)
    add_footer_page_number(sec_ch2, "- 2 -")
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run("CHAPTER - 2\nINTRODUCTION")
    r.font.bold = True
    r.font.size = Pt(13)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("2.1 Background and Need for the Project")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "In modern urban centers and transportation ecosystems, personal mobility is indispensable. Vehicle owners regularly require routine servicing, "
        "preventative fluid changes, brake inspections, engine diagnostics, cosmetic detailing, and emergency mechanical overhauls. However, the majority "
        "of automotive service workshops and local garages continue to manage daily intake and vehicle maintenance workflows through antiquated manual procedures, "
        "including handwritten paper registers, physical job cards, whiteboard dispatch schedules, and verbal phone consultations. "
        "These methods introduce operational friction, human error, and substantial customer dissatisfaction."
    )
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "Physical job cards are prone to being misplaced, torn, or illegibly annotated, causing technicians to duplicate diagnostic procedures or overlook "
        "critical customer requests. Customers possess no transparent window into their vehicle's servicing stage, forcing them into repeated telephone inquiries "
        "that distract service managers and workshop mechanics. Furthermore, manual invoicing frequently suffers from ambiguity, arbitrary pricing estimates, and "
        "lack of historical records, inhibiting long-term vehicle health monitoring. A comparative evaluation of traditional maintenance practices is synthesized in Table 2.1."
    )
    
    p_tcap = doc.add_paragraph()
    p_tcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap.paragraph_format.space_before = Pt(8)
    p_tcap.paragraph_format.space_after = Pt(4)
    r = p_tcap.add_run("Table 2.1 PROBLEMS IN THE EXISTING METHODS OF VEHICLE SERVICE MANAGEMENT")
    r.font.bold = True
    r.font.size = Pt(10.5)
    
    t21_data = [
        ("Problem", "Description", "Impact"),
        ("Scattered Records", "Maintenance logs, vehicle specs, and bills are kept in paper files and manual binders.", "High risk of record loss, damage, and inability to trace past vehicle repair history."),
        ("No Online Booking", "Service appointments are scheduled via ad-hoc phone calls or physical walk-ins.", "Unpredictable workshop bay congestion, long customer queues, and missed appointments."),
        ("Opaque Pricing", "Estimated repair costs are communicated verbally without baseline transparent packages.", "Frequent customer mistrust, bill disputes, and unexpected post-repair price shocks."),
        ("No Live Tracking", "Customers have no visibility into vehicle service status (Pending, In Progress, Ready).", "Frustrated customers, excessive inquiry phone calls, and disrupted workshop workflows."),
        ("Limited Admin Oversight", "Service managers lack aggregated digital metrics on fleet size, queue bottlenecks, and revenue.", "Poor technician allocation, inventory miscalculations, and low administrative productivity.")
    ]
    t21 = doc.add_table(rows=len(t21_data), cols=3)
    for r_idx, row in enumerate(t21_data):
        for c_idx, val in enumerate(row):
            t21.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t21, [1.4, 2.8, 2.2], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(14)
    p.add_run(
        "Problem Statement: How can a secure, responsive, and database-driven web application empower vehicle owners to manage vehicle fleets, "
        "book certified service packages with transparent cost estimation, track repair lifecycles in real time, and enable workshop administrators "
        "to efficiently dispatch mechanics, update progress, and inspect customer fleet metrics?"
    )
    
    # 2.2 Objectives & 2.3 Scope (Page - 3 -)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("2.2 Objectives")
    r.font.bold = True
    r.font.size = Pt(12)
    
    objectives = [
        "To develop an intuitive, responsive web portal where vehicle owners can register, log in, and securely manage multiple vehicles across diverse categories (Cars, Motorcycles, EVs).",
        "To engineer a normalized MySQL relational database utilizing PDO prepared statements to maintain users, vehicles, certified service offerings, and repair tickets with full referential integrity.",
        "To provide a streamlined service booking engine featuring automated base pricing previews, preferred appointment dates, and custom maintenance notes.",
        "To implement a real-time service tracking module allowing customers to monitor status transitions (Pending, In Progress, Completed, Cancelled) with cancellation capabilities for pending tickets.",
        "To build an administrative operations console with aggregated metric cards (total customers, fleet size, active service queues, and collected revenue).",
        "To design an interactive service dispatch queue enabling administrators to filter by status, search tickets, assign diagnostic remarks, and record finalized repair costs.",
        "To implement strict application security adhering to OWASP principles, incorporating bcrypt password hashing, session regeneration, role-based access control, and output sanitization."
    ]
    for obj in objectives:
        p_obj = doc.add_paragraph(style='List Bullet')
        p_obj.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_obj.paragraph_format.line_spacing = 1.2
        p_obj.paragraph_format.space_before = Pt(2)
        p_obj.paragraph_format.space_after = Pt(3)
        r = p_obj.add_run(obj)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("2.3 Scope")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(12)
    p.add_run(
        "The scope of Vehicle Service Management System (VSM Pro) encompasses full lifecycle digital management of automotive servicing within single or multi-bay "
        "workshops. Functional boundaries cover secure customer registration and authentication, vehicle fleet CRUD (Create, Read, Update, Delete) management, "
        "service appointment scheduling, transparent base-rate pricing calculation, real-time ticket state tracking, admin queue management, and customer fleet directory search. "
        "The current implementation is optimized for local browser deployment over Apache and MySQL via XAMPP. External third-party payment gateway gateways, automated SMS/email gateways, "
        "and GPS hardware vehicle telematics are deliberately excluded from this version and cataloged as prospective enhancements in Chapter 5."
    )

    # 2.4 Development Plan (Page - 4 -)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("2.4 Development Plan")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "The development of VSM Pro was structured across six systematic engineering phases, transitioning from requirement analysis and architectural design "
        "to full-stack implementation, security hardening, and exhaustive browser testing. Each phase yielded well-defined deliverables as summarized in Table 2.2."
    )
    
    p_tcap2 = doc.add_paragraph()
    p_tcap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap2.paragraph_format.space_before = Pt(6)
    p_tcap2.paragraph_format.space_after = Pt(4)
    r = p_tcap2.add_run("Table 2.2 DEVELOPMENT PLAN OF VSM PRO")
    r.font.bold = True
    r.font.size = Pt(10.5)
    
    t22_data = [
        ("S.No", "Phase", "Activities", "Output"),
        ("1", "Requirement Analysis", "Identified core functional workflows: fleet registration, service booking, status tracking, queue dispatch, and admin revenue oversight. Divided system into Customer and Admin roles.", "Functional specification document and role access matrix."),
        ("2", "System & UI Design", "Drafted three-tier system architecture, designed normalized ER schema with 4 relational tables, and conceptualized UI mockups with a modern dark-sidebar dashboard and blue theme.", "System architecture diagram, ER schema, and responsive UI wireframes."),
        ("3", "Front-End Development", "Engineered responsive HTML5 views, custom CSS3 styling, Bootstrap 5 grid layout, and vanilla JavaScript routines for live base price estimates, client validation, and search filters.", "Responsive, modular presentation layer."),
        ("4", "Back-End & Database", "Created vehicle_service_db schema in MySQL with seed accounts and services. Programmed PHP 8 scripts utilizing PDO for secure CRUD operations, session auth, and data retrieval.", "Operational full-stack web application with live database connectivity."),
        ("5", "Security Hardening", "Enforced bcrypt password hashing, prepared statement parameterization, HTML output sanitization, CSRF tokens, and session-based Role-Based Access Control guards on all protected scripts.", "Robust, OWASP-compliant secure web application."),
        ("6", "Testing & Quality Assurance", "Conducted end-to-end integration testing in local XAMPP Apache environment using Google Chrome across user registration, fleet creation, booking dispatch, and status updates.", "Verified zero-defect operational system with test verification logs.")
    ]
    t22 = doc.add_table(rows=len(t22_data), cols=4)
    for r_idx, row in enumerate(t22_data):
        for c_idx, val in enumerate(row):
            t22.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t22, [0.6, 1.4, 2.9, 1.5], [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])

    # ---------------------------------------------------------------------------
    # CHAPTER 3: IMPLEMENTATION (Page - 5 - to - 12 -)
    # ---------------------------------------------------------------------------
    sec_ch3 = doc.add_section()
    sec_ch3.top_margin = Inches(1.0)
    sec_ch3.bottom_margin = Inches(1.0)
    sec_ch3.left_margin = Inches(1.25)
    sec_ch3.right_margin = Inches(1.0)
    apply_page_borders(sec_ch3)
    add_footer_page_number(sec_ch3, "- 5 -")
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run("CHAPTER - 3\nIMPLEMENTATION")
    r.font.bold = True
    r.font.size = Pt(13)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "Vehicle Service Management System follows an enterprise-standard three-layer client-server software architecture. "
        "The presentation layer operates inside modern web browsers (such as Google Chrome, Microsoft Edge, and Mozilla Firefox), "
        "delivering a responsive graphical interface rendered with HTML5, CSS3, Bootstrap 5, and interactive vanilla JavaScript. "
        "The application layer executes on an Apache HTTP server powered by PHP 8, executing authentication routines, role access validation, "
        "fleet processing, and service booking dispatch algorithms. The data storage layer is managed by the MySQL relational database engine (vehicle_service_db), "
        "which enforces referential constraints and foreign key relationships. Communication between PHP and MySQL is mediated via PHP Data Objects (PDO) "
        "with strictly parameterized prepared statements to prevent security vulnerabilities. The end-to-end multi-tier architecture is illustrated in Fig 3.1."
    )
    
    # Figure 3.1
    p_f31 = doc.add_paragraph()
    p_f31.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f31.paragraph_format.space_before = Pt(8)
    p_f31.paragraph_format.space_after = Pt(4)
    fig31_path = r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_3_1_system_architecture.png"
    if os.path.exists(fig31_path):
        p_f31.add_run().add_picture(fig31_path, width=Inches(5.4))
    p_c31 = doc.add_paragraph()
    p_c31.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c31.paragraph_format.space_before = Pt(2)
    p_c31.paragraph_format.space_after = Pt(14)
    r = p_c31.add_run("Fig 3.1 SYSTEM ARCHITECTURE OF VEHICLE SERVICE MANAGEMENT SYSTEM")
    r.font.bold = True
    r.font.size = Pt(10)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("3.1 Tech Stack")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "The technologies comprising VSM Pro were chosen for their proven reliability, open-source availability, high execution speed, "
        "and extensive enterprise community support. The primary software components are detailed below and tabulated in Table 3.1."
    )
    
    tech_descriptions = [
        ("3.1.1 HTML5", "HyperText Markup Language 5 serves as the structural foundation for all application pages, modal dialogues, and data grids. Semantic tags (<header>, <nav>, <main>, <section>, <article>) ensure high structural readability and accessibility, while modern form controls (type='email', type='date', type='tel') enable intuitive browser-level validation prior to form submission."),
        ("3.1.2 CSS3 & Bootstrap 5", "Cascading Style Sheets 3 together with Bootstrap 5 provides a unified, professional visual theme. The layout combines a deep slate-navy sidebar (#0f172a), high-contrast cards, and vibrant blue primary elements (#2563eb). Responsive flexbox containers, CSS grid systems, and adaptive media queries guarantee seamless rendering across mobile screens, tablets, laptops, and ultra-wide desktop monitors."),
        ("3.1.3 JavaScript (Vanilla ES6)", "Client-side interactivity is implemented using lightweight, native JavaScript without external framework overhead. JavaScript powers instant base price previews when selecting service options, real-time table filtering, interactive delete confirmation modals, and dual-layer form input validation."),
        ("3.1.4 PHP 8 & PDO", "PHP 8 serves as the robust server-side engine. Utilizing object-oriented PHP Data Objects (PDO) with prepared statements, the backend safely negotiates all SQL operations. Built-in session security, cryptographic password verification functions, and modular file routing ensure high maintainability and security."),
        ("3.1.5 MySQL & phpMyAdmin", "MySQL 8 / MariaDB provides ACID-compliant relational data management. Foreign key constraints with ON DELETE CASCADE ensure referential integrity across users, vehicles, and service tickets. Indexes on email, registration numbers, user IDs, and status columns provide sub-millisecond query performance."),
        ("3.1.6 Development and Testing Tools", "Development was conducted in Visual Studio Code with Git version control. Local deployment was managed via XAMPP (Apache HTTP Server and MySQL). Testing and DOM debugging were performed using Google Chrome DevTools.")
    ]
    for h_txt, b_txt in tech_descriptions:
        p_h = doc.add_paragraph()
        p_h.paragraph_format.space_before = Pt(6)
        p_h.paragraph_format.space_after = Pt(2)
        r = p_h.add_run(h_txt)
        r.font.bold = True
        r.font.size = Pt(11)
        
        p_b = doc.add_paragraph()
        p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_b.paragraph_format.line_spacing = 1.2
        p_b.paragraph_format.space_after = Pt(8)
        p_b.add_run(b_txt)
        
    p_tcap3 = doc.add_paragraph()
    p_tcap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap3.paragraph_format.space_before = Pt(8)
    p_tcap3.paragraph_format.space_after = Pt(4)
    r = p_tcap3.add_run("Table 3.1 TECHNOLOGY STACK")
    r.font.bold = True
    r.font.size = Pt(10.5)
    
    t31_data = [
        ("Component", "Role in the Project"),
        ("Visual Studio Code", "Integrated Development Environment for scripting PHP, HTML5, CSS3, and JavaScript."),
        ("HTML5", "Defines the semantic structure of dashboards, registration forms, and tabular queues."),
        ("CSS3 & Bootstrap 5", "Implements responsive navigation, slate-navy sidebar theme, status badges, and cards."),
        ("JavaScript (ES6)", "Provides client form validation, instant price calculation preview, and table search filtering."),
        ("PHP 8", "Executes server-side business logic, session authentication, and role routing."),
        ("PHP Data Objects (PDO)", "Executes parameterized SQL queries with complete injection prevention."),
        ("MySQL / MariaDB", "Relational database storing user profiles, vehicle fleets, service catalog, and tickets."),
        ("phpMyAdmin", "Web interface utilized for schema migration, table indexing, and seed data verification."),
        ("XAMPP (Apache)", "Local multi-platform web server environment executing the PHP backend locally."),
        ("Google Chrome & DevTools", "Primary browser used for responsive viewport inspection, network tracing, and QA.")
    ]
    t31 = doc.add_table(rows=len(t31_data), cols=2)
    for r_idx, row in enumerate(t31_data):
        for c_idx, val in enumerate(row):
            t31.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t31, [2.0, 4.4], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])

    # 3.2 Modules (Page - 7 -)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("3.2 Modules")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "VSM Pro is structured into modular functional subsystems. User modules and administrator modules operate under strict role "
        "separation, unified by centralized database connectivity and comprehensive security controllers."
    )
    
    # 3.2.1 Database Module
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("3.2.1 Database Module")
    r.font.bold = True
    r.font.size = Pt(11.5)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "The relational database schema (vehicle_service_db) is normalized to Third Normal Form (3NF) to eliminate data redundancy. "
        "It consists of four interrelated entities: users, vehicles, services, and service_requests. Foreign keys are constrained with "
        "ON DELETE CASCADE to maintain referential integrity. When a user or vehicle record is removed, all dependent service bookings "
        "are safely purged. Unique indexes enforce distinct user emails and vehicle registration numbers. Core entities are described in Table 3.2, "
        "service request lifecycle states are defined in Table 3.3, and entity relationships are modeled in Fig 3.2."
    )
    
    # Figure 3.2 ER Diagram
    p_f32 = doc.add_paragraph()
    p_f32.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f32.paragraph_format.space_before = Pt(8)
    p_f32.paragraph_format.space_after = Pt(4)
    fig32_path = r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_3_2_er_diagram.png"
    if os.path.exists(fig32_path):
        p_f32.add_run().add_picture(fig32_path, width=Inches(5.4))
    p_c32 = doc.add_paragraph()
    p_c32.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c32.paragraph_format.space_before = Pt(2)
    p_c32.paragraph_format.space_after = Pt(12)
    r = p_c32.add_run("Fig 3.2 ENTITY RELATIONSHIP DIAGRAM OF THE DATABASE")
    r.font.bold = True
    r.font.size = Pt(10)
    
    p_tcap4 = doc.add_paragraph()
    p_tcap4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap4.paragraph_format.space_before = Pt(6)
    p_tcap4.paragraph_format.space_after = Pt(4)
    r = p_tcap4.add_run("Table 3.2 CORE DATA ENTITIES")
    r.font.bold = True
    r.font.size = Pt(10.5)
    
    t32_data = [
        ("Entity", "Information Held"),
        ("users", "User identifier (PK), full name, email address (UNIQUE), 10-digit phone, bcrypt password hash, residential address, system role ('customer' or 'admin'), and creation timestamp."),
        ("vehicles", "Vehicle identifier (PK), user_id (FK to users), vehicle type (Car, Motorcycle, EV, SUV), brand, model, registration number (UNIQUE), manufacture year, fuel type, and registration date."),
        ("services", "Service catalog identifier (PK), service package name, comprehensive maintenance description, and base service price."),
        ("service_requests", "Request identifier (PK), user_id (FK to users), vehicle_id (FK to vehicles), service_id (FK to services), preferred service date, issue description, ticket status, admin remarks, finalized cost, and timestamps.")
    ]
    t32 = doc.add_table(rows=len(t32_data), cols=2)
    for r_idx, row in enumerate(t32_data):
        for c_idx, val in enumerate(row):
            t32.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t32, [1.6, 4.8], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])
    
    p_tcap5 = doc.add_paragraph()
    p_tcap5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap5.paragraph_format.space_before = Pt(10)
    p_tcap5.paragraph_format.space_after = Pt(4)
    r = p_tcap5.add_run("Table 3.3 STATUS VALUES OF SERVICE REQUESTS")
    r.font.bold = True
    r.font.size = Pt(10.5)
    
    t33_data = [
        ("Record", "Status", "Meaning"),
        ("service_requests", "Pending", "The customer has booked the appointment; ticket is awaiting workshop administrator review and bay assignment."),
        ("service_requests", "In Progress", "The vehicle has been admitted to the workshop; mechanics are currently actively servicing or repairing the vehicle."),
        ("service_requests", "Completed", "Maintenance tasks are finished; inspection is complete, final invoice cost is assigned, and vehicle is ready for customer pickup."),
        ("service_requests", "Cancelled", "The booking was cancelled either by the customer prior to technician dispatch or revoked by the administrator.")
    ]
    t33 = doc.add_table(rows=len(t33_data), cols=3)
    for r_idx, row in enumerate(t33_data):
        for c_idx, val in enumerate(row):
            t33.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t33, [1.5, 1.2, 3.7], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])

    # Other Modules
    modules_info = [
        ("3.2.2 Registration and Login Module", "New customers create personal accounts by submitting their full name, valid email address, 10-digit phone number, address, and password. Client-side JavaScript verifies proper formatting while PHP conducts authoritative regex and unique email validation. Passwords are encrypted using PHP's password_hash() with PASSWORD_BCRYPT. Upon logging in, credentials are authenticated using password_verify(). Successful authentication invokes session_regenerate_id() to thwart session fixation attacks, directing users to the customer suite or admin management console based on their stored role."),
        ("3.2.3 Customer Dashboard Module", "The customer home suite displays a personalized greeting banner, rapid action shortcuts ('Add Vehicle', 'Book New Service'), and four real-time metric cards (My Vehicles, Pending Requests, In Progress, Completed Services). An embedded summary table highlights recent service bookings, while a registered fleet roster displays quick cards for each enrolled automobile and motorcycle."),
        ("3.2.4 Vehicle Fleet Management Module", "Empowers vehicle owners to maintain an accurate digital fleet roster. Customers can register new vehicles by specifying type (Car, Motorcycle, Electric, Commercial), make/brand, model designation, unique license registration number, manufacturing year, and fuel type (Petrol, Diesel, Electric, Hybrid). Built-in edit and delete modals allow customers to update vehicle data or retire vehicles with immediate cascading integrity."),
        ("3.2.5 Service Booking and Estimation Module", "The appointment booking interface presents a dynamic scheduling form. The customer selects a registered vehicle from an auto-populated dropdown and chooses a desired service package (General Service, Oil & Filter Change, Brake Repair, Engine Diagnostics, Car Spa & Detailing, Tyre Balancing). A JavaScript event listener immediately updates an 'Estimated Price Preview' card showcasing the service package base cost and inclusions. Customers pick their preferred service calendar date and submit special diagnostic instructions."),
        ("3.2.6 Service History and Tracking Module", "Provides customers with complete chronological transparency over all historic and active service tickets. Each ticket displays scheduled dates, vehicle model, license registration, service package, total finalized cost, and real-time color-coded status badges (Pending: amber, In Progress: blue, Completed: green, Cancelled: red). Customers can inspect detailed technician remarks or cancel bookings that remain in 'Pending' status."),
        ("3.2.7 Admin Overview Dashboard Module", "The workshop management console provides administrators with instantaneous high-level operational intelligence. Key metric cards summarize Total Registered Customers, Total Registered Fleet Size, Active Pending Requests, In-Progress Bay Tickets, Completed Jobs, and Cumulative Revenue ($). A quick-access table lists incoming service tickets with direct shortcuts to ticket management."),
        ("3.2.8 Service Request Queue and Dispatch Module", "An advanced administrative dispatch console that lists all service tickets across the enterprise. Features interactive status filter pills ('All', 'Pending', 'In Progress', 'Completed', 'Cancelled') and a live client-side search bar matching customer names, vehicle models, registration plates, and request IDs. Administrators open a management modal to update ticket status, input diagnostic remarks, and enter finalized repair invoices."),
        ("3.2.9 Customer Directory and Fleet Module", "Enables workshop managers to inspect all verified customer accounts in a clean data table. Displays customer identity, contact telephone, email address, physical location, total fleet count, and aggregate bookings. An interactive 'View Fleet' modal surfaces all registered vehicles owned by a specific customer, facilitating targeted customer service."),
        ("3.2.10 Security Module", "Enterprise web security is embedded into every tier of VSM Pro, adhering to OWASP web application recommendations. Security safeguards protect against SQL injection, Cross-Site Scripting (XSS), Cross-Site Request Forgery (CSRF), and unauthorized privilege escalation as outlined in Table 3.4.")
    ]
    
    for m_title, m_desc in modules_info:
        p_m = doc.add_paragraph()
        p_m.paragraph_format.space_before = Pt(8)
        p_m.paragraph_format.space_after = Pt(3)
        r = p_m.add_run(m_title)
        r.font.bold = True
        r.font.size = Pt(11.5)
        
        p_md = doc.add_paragraph()
        p_md.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_md.paragraph_format.line_spacing = 1.25
        p_md.paragraph_format.space_after = Pt(8)
        p_md.add_run(m_desc)
        
        if "3.2.5" in m_title:
            # Figure 3.3 Flowchart
            p_f33 = doc.add_paragraph()
            p_f33.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_f33.paragraph_format.space_before = Pt(8)
            p_f33.paragraph_format.space_after = Pt(4)
            fig33_path = r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_3_3_flowchart_booking.png"
            if os.path.exists(fig33_path):
                p_f33.add_run().add_picture(fig33_path, width=Inches(4.6))
            p_c33 = doc.add_paragraph()
            p_c33.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_c33.paragraph_format.space_before = Pt(2)
            p_c33.paragraph_format.space_after = Pt(12)
            r = p_c33.add_run("Fig 3.3 FLOWCHART OF THE SERVICE BOOKING AND DISPATCH ALGORITHM")
            r.font.bold = True
            r.font.size = Pt(10)
            
            # Figure 3.4 Workflow
            p_f34 = doc.add_paragraph()
            p_f34.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_f34.paragraph_format.space_before = Pt(8)
            p_f34.paragraph_format.space_after = Pt(4)
            fig34_path = r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_3_4_typical_workflow.png"
            if os.path.exists(fig34_path):
                p_f34.add_run().add_picture(fig34_path, width=Inches(4.6))
            p_c34 = doc.add_paragraph()
            p_c34.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_c34.paragraph_format.space_before = Pt(2)
            p_c34.paragraph_format.space_after = Pt(12)
            r = p_c34.add_run("Fig 3.4 TYPICAL WORKFLOW OF VSM PRO")
            r.font.bold = True
            r.font.size = Pt(10)

    # Table 3.4 Security Controls
    p_tcap6 = doc.add_paragraph()
    p_tcap6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap6.paragraph_format.space_before = Pt(10)
    p_tcap6.paragraph_format.space_after = Pt(4)
    r = p_tcap6.add_run("Table 3.4 SECURITY CONTROLS IMPLEMENTED IN THE APPLICATION")
    r.font.bold = True
    r.font.size = Pt(10.5)
    
    t34_data = [
        ("Security Control", "Implementation in VSM Pro"),
        ("Password Protection", "User passwords are encrypted via bcrypt (password_hash(PASSWORD_BCRYPT)) with automatic salt generation; verified via password_verify()."),
        ("SQL Injection Prevention", "All database operations employ PDO prepared statements with strict parameter binding (:param), ensuring user input is never concatenated into raw SQL."),
        ("Session Management", "Authenticated sessions invoke session_regenerate_id(true) on login. Strict session timeout and session destruction occur on sign out."),
        ("Role-Based Access Control", "Access check middleware (auth_check.php) validates session role; unauthorized customer attempts to access admin scripts trigger immediate redirect."),
        ("Cross-Site Scripting (XSS)", "All dynamic database strings rendered to HTML pass through htmlspecialchars($str, ENT_QUOTES, 'UTF-8') to neutralize injected scripts."),
        ("CSRF Protection", "State-altering POST requests incorporate cryptographic CSRF session tokens verified by server-side endpoints."),
        ("Business Rule Validation", "Customers cannot cancel services once status changes to 'In Progress' or 'Completed'; customers cannot book past dates or duplicate plates.")
    ]
    t34 = doc.add_table(rows=len(t34_data), cols=2)
    for r_idx, row in enumerate(t34_data):
        for c_idx, val in enumerate(row):
            t34.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t34, [2.0, 4.4], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])

    # ---------------------------------------------------------------------------
    # CHAPTER 4: OUTCOME (Page - 13 - to - 19 -)
    # ---------------------------------------------------------------------------
    sec_ch4 = doc.add_section()
    sec_ch4.top_margin = Inches(1.0)
    sec_ch4.bottom_margin = Inches(1.0)
    sec_ch4.left_margin = Inches(1.25)
    sec_ch4.right_margin = Inches(1.0)
    apply_page_borders(sec_ch4)
    add_footer_page_number(sec_ch4, "- 13 -")
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run("CHAPTER - 4\nOUTCOME")
    r.font.bold = True
    r.font.size = Pt(13)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("4.1 Implementation Outcome")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "Vehicle Service Management System (VSM Pro) was successfully engineered, integrated, and verified within a local XAMPP Apache/MySQL environment. "
        "The web application delivers an elegant, high-performance interface with immediate responsiveness across desktop and mobile viewports. "
        "End-to-end user workflows—from initial account onboarding and multi-vehicle fleet registry to service appointment booking with live base estimation, "
        "administrative dispatch queue filtering, status and invoice updates, and real-time customer history tracking—were executed without runtime errors. "
        "Extensive browser testing using Google Chrome confirmed data persistence, referential foreign key cascading, and reliable session authentication."
    )
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("4.2 Module-wise Outcome with Screenshots")
    r.font.bold = True
    r.font.size = Pt(12)
    
    screenshots_info = [
        ("Fig 4.1 PUBLIC LANDING PAGE MODULE", r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_4_1_landing_page.png", 
         "Public Landing Page Module. The application landing page welcomes visitors with a branded top navigation bar (Home, Dashboard, Sign Out), an engaging hero headline 'Smart Vehicle Service, Seamless Management', key value proposition metrics (100% Transparent Pricing, 6+ Certified Services, 24/7 Online Booking), and an interactive 'Live Fleet Tracker' card reflecting active workshop operations (Fig 4.1)."),
        
        ("Fig 4.2 LOGIN MODULE", r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_4_2_login_module.png", 
         "Authentication and Login Module. The login interface features a clean, elevated card with an encrypted security shield icon, input fields for registered email address and password, an interactive 'Sign In to Account' action button, and a registration navigation prompt. Role-based routing automatically evaluates verified credentials and redirects users to their respective workspace (Fig 4.2)."),
         
        ("Fig 4.3 CUSTOMER DASHBOARD MODULE", r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_4_3_customer_dashboard.png", 
         "Customer Dashboard Module. Upon signing in, customers are greeted with a personalized welcome banner and quick-action shortcuts ('Add Vehicle', 'Book New Service'). Four metric cards display counts for My Vehicles (2), Pending Requests (0), In Progress (1), and Completed Services (1). Summary panels provide instant visibility over recent service appointments and enrolled fleet assets (Fig 4.3)."),
         
        ("Fig 4.4 VEHICLE FLEET MANAGEMENT MODULE", r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_4_4_vehicle_fleet.png", 
         "Vehicle Fleet Management Module. The fleet roster displays all registered customer vehicles in a modern data table. Each entry includes vehicle designation (e.g., Yamaha MT-15 V2, Honda Civic EX), vehicle type badge (Motorcycle, Car), unique license plate tag (YAM-7788, ABC-1024), manufacture year, fuel type (Petrol), active service count, and action buttons for booking, editing, or deleting assets (Fig 4.4)."),
         
        ("Fig 4.5 SERVICE BOOKING APPOINTMENT MODULE", r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_4_5_book_service.png", 
         "Service Booking Appointment Module. Provides a streamlined appointment scheduling form. The customer selects an enrolled vehicle and chooses a service package from the catalog. The 'Estimated Price Preview' card automatically computes and renders the baseline cost ($40.00) alongside service package inclusions and physical inspection disclaimers (Fig 4.5)."),
         
        ("Fig 4.6 SERVICE REQUEST HISTORY MODULE", r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_4_6_service_history.png", 
         "Service Request History Module. Customers can track all historical and active maintenance tickets with status filter pills (All Records, Pending, In Progress, Completed, Cancelled). Each row details vehicle information, service package name, scheduled date, total finalized billing amount ($60.00, $135.00), booking timestamp, and detailed view modals (Fig 4.6)."),
         
        ("Fig 4.7 ADMIN DASHBOARD OVERVIEW MODULE", r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_4_7_admin_dashboard.png", 
         "Admin Dashboard Overview Module. The administrative control center provides workshop supervisors with aggregated operational metrics: Total Customers (2), Total Vehicles (4), Pending Tickets (1), In Progress (1), Completed Jobs (1), and Total Revenue ($135.00). An actionable 'Recent Service Requests' grid enables managers to review incoming tickets and dispatch mechanics (Fig 4.7)."),
         
        ("Fig 4.8 ADMIN SERVICE REQUEST QUEUE MODULE", r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_4_8_admin_service_queue.png", 
         "Admin Service Request Queue Module. A comprehensive ticket management console equipped with quick-filter status tabs and a real-time search field. Displays customer contact information, vehicle details, service packages, appointment dates, color-coded status badges, finalized costs, and diagnostic technician remarks (Fig 4.8)."),
         
        ("Fig 4.9 ADMIN CUSTOMER DIRECTORY & FLEET MODULE", r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_4_4_admin_customers_fleet.png" if not os.path.exists(r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_4_9_admin_customers_fleet.png") else r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\fig_4_9_admin_customers_fleet.png", 
         "Admin Customer Directory & Fleet Module. Enables workshop management to browse all registered clients, residential addresses, phone numbers, and associated fleet metrics. An interactive 'View Fleet' modal reveals all vehicles owned by a specific customer, assisting workshop personnel in providing personalized automotive care (Fig 4.9).")
    ]
    
    for cap, img_path, narrative in screenshots_info:
        p_n = doc.add_paragraph()
        p_n.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_n.paragraph_format.line_spacing = 1.25
        p_n.paragraph_format.space_before = Pt(8)
        p_n.paragraph_format.space_after = Pt(6)
        p_n.add_run(narrative)
        
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(4)
            p_img.paragraph_format.space_after = Pt(2)
            p_img.add_run().add_picture(img_path, width=Inches(5.4))
            
            p_c = doc.add_paragraph()
            p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_c.paragraph_format.space_before = Pt(2)
            p_c.paragraph_format.space_after = Pt(12)
            r = p_c.add_run(cap)
            r.font.bold = True
            r.font.size = Pt(10)

    # 4.3 Comparison with Existing Methods (Page - 18 -)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("4.3 Comparison with Existing Methods")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "A rigorous comparative evaluation between traditional manual workshop management techniques and VSM Pro demonstrates "
        "substantial improvements across data integrity, workflow automation, cost transparency, and customer satisfaction, as presented in Table 4.1."
    )
    
    p_tcap7 = doc.add_paragraph()
    p_tcap7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap7.paragraph_format.space_before = Pt(6)
    p_tcap7.paragraph_format.space_after = Pt(4)
    r = p_tcap7.add_run("Table 4.1 EXISTING METHODS VERSUS VSM PRO")
    r.font.bold = True
    r.font.size = Pt(10.5)
    
    t41_data = [
        ("Aspect", "Existing Manual Methods", "VSM Pro System"),
        ("Record Storage", "Physical paper logbooks, receipt slips, and filing folders.", "Centralized MySQL relational database with ACID compliance and backups."),
        ("Appointment Booking", "Ad-hoc telephone calls or walk-ins causing shop floor crowding.", "24/7 web booking portal with preferred dates and instant base estimates."),
        ("Pricing Transparency", "Verbal estimates quoted after repairs; prone to hidden charges.", "Standardized baseline pricing catalog with itemized repair billing."),
        ("Fleet Oversight", "Vehicle specs must be re-collected manually on every workshop visit.", "Permanent multi-vehicle registry per customer profile with full specs."),
        ("Status Tracking", "Customer must place repeated phone inquiries to obtain repair progress.", "Instant real-time status badges (Pending, In Progress, Completed, Cancelled)."),
        ("Administrative Control", "No consolidated metrics; manual end-of-month revenue reconciliation.", "Real-time management console tracking fleet size, active queues, and revenue."),
        ("Security & Privacy", "Physical books accessible to anyone; unencrypted customer details.", "Bcrypt salted hashing, PDO injection protection, and strict session RBAC.")
    ]
    t41 = doc.add_table(rows=len(t41_data), cols=3)
    for r_idx, row in enumerate(t41_data):
        for c_idx, val in enumerate(row):
            t41.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t41, [1.4, 2.5, 2.5], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT])

    # 4.4 Discussion and Limitations (Page - 19 -)
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("4.4 Discussion and Limitations")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p_tcap8 = doc.add_paragraph()
    p_tcap8.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap8.paragraph_format.space_before = Pt(6)
    p_tcap8.paragraph_format.space_after = Pt(4)
    r = p_tcap8.add_run("Table 4.2 KEY OUTCOMES OF VSM PRO")
    r.font.bold = True
    r.font.size = Pt(10.5)
    
    t42_data = [
        ("Outcome", "Value", "Meaning"),
        ("Centralized Fleet", "Achieved", "All vehicle profiles and service tickets consolidated into a normalized database."),
        ("Pricing Transparency", "Supported", "Instant service package estimates provided upon booking selection."),
        ("Real-Time Tracking", "Available", "Four clear status states with live workshop diagnostic updates."),
        ("Access Control", "Role-Based", "Strict separation between Customer Suite and Admin Management Console."),
        ("Application Security", "Hardened", "Full protection against SQL injection, XSS attacks, and unauthorized access."),
        ("UI Responsiveness", "Verified", "Adaptive desktop and mobile layout powered by Bootstrap 5 and custom CSS3.")
    ]
    t42 = doc.add_table(rows=len(t42_data), cols=3)
    for r_idx, row in enumerate(t42_data):
        for c_idx, val in enumerate(row):
            t42.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t42, [1.6, 1.2, 3.6], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT])
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "The experimental validation and local deployment results establish that VSM Pro successfully eliminates traditional automotive service friction. "
        "By consolidating customer vehicles, standardized service offerings, and workshop dispatch queues into an integrated relational database, "
        "the application significantly reduces administrative turnaround times, prevents misplaced maintenance records, and builds trust through upfront pricing."
    )
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(12)
    p.add_run(
        "However, certain technical constraints exist within the current architecture. The system currently executes in a local XAMPP Apache development environment "
        "and requires migration to cloud hosting (e.g., AWS, DigitalOcean) for wide internet deployment. Real-time customer communication relies on portal visits rather "
        "than automated SMS or WhatsApp dispatch notifications, and payments are recorded administratively rather than processed through online payment gateways. "
        "These constraints present valuable opportunities for future engineering iterations."
    )

    # ---------------------------------------------------------------------------
    # CHAPTER 5: CONCLUSION (Page - 20 -)
    # ---------------------------------------------------------------------------
    sec_ch5 = doc.add_section()
    sec_ch5.top_margin = Inches(1.0)
    sec_ch5.bottom_margin = Inches(1.0)
    sec_ch5.left_margin = Inches(1.25)
    sec_ch5.right_margin = Inches(1.0)
    apply_page_borders(sec_ch5)
    add_footer_page_number(sec_ch5, "- 20 -")
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run("CHAPTER - 5\nCONCLUSION")
    r.font.bold = True
    r.font.size = Pt(13)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "Vehicle Service Management System (VSM Pro) was conceived, engineered, and verified as a modern, responsive, and secure full-stack web application "
        "designed to digitize automotive maintenance operations. By pairing an intuitive HTML5, CSS3, Bootstrap 5, and vanilla JavaScript front-end with a robust "
        "PHP 8 and MySQL relational backend, the system delivers an end-to-end operational platform bridging vehicle owners and workshop administrators. "
        "Customers benefit from effortless fleet enrollment, transparent service booking with automated cost estimation, and live ticket tracking. "
        "Workshop supervisors gain deep administrative oversight through real-time operational analytics, interactive dispatch queues, and customer directories."
    )
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.space_after = Pt(12)
    p.add_run(
        "The project provided rigorous hands-on exposure to full-stack software development principles, including modular file architectures, relational database "
        "normalization (3NF), foreign key cascading, secure session management, and OWASP-recommended security practices (PDO prepared statements, bcrypt hashing, "
        "and HTML escaping). Comprehensive local testing across diverse user roles confirmed that VSM Pro effectively solves the communication breakdowns, lost job cards, "
        "and billing disputes endemic to conventional automotive garages."
    )
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("5.1 Future Scope")
    r.font.bold = True
    r.font.size = Pt(12)
    
    future_items = [
        "Automated Multi-Channel Notifications: Integrating Twilio SMS, WhatsApp Business API, and SendGrid email notifications to alert customers instantly when their vehicle service status transitions to 'In Progress' or 'Completed'.",
        "Online Payment Gateway Integration: Incorporating secure payment gateways (Stripe, Razorpay, or PayPal) allowing customers to pay finalized repair invoices digitally via credit cards, UPI, or net banking.",
        "IoT Telematics & OBD-II Diagnostics: Connecting vehicle onboard diagnostic (OBD-II) hardware readers to automatically upload real-time odometer readings, engine trouble codes (DTC), and fluid levels into the vehicle profile.",
        "Intelligent Mechanic & Bay Dispatching: Developing an automated heuristic scheduling algorithm to allocate service bays and certified mechanics based on skill specialization and shop floor availability.",
        "Multi-Branch Workshop Network: Scaling the database architecture to support multi-franchise automobile service centers across multiple geographic cities with unified customer profiles.",
        "Dedicated Mobile Application: Developing native iOS and Android companion applications using Flutter or React Native to support camera barcode scanning of vehicle VIN plates and push notifications."
    ]
    for item in future_items:
        p_f = doc.add_paragraph(style='List Bullet')
        p_f.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_f.paragraph_format.line_spacing = 1.2
        p_f.paragraph_format.space_before = Pt(2)
        p_f.paragraph_format.space_after = Pt(4)
        r = p_f.add_run(item)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)

    # ---------------------------------------------------------------------------
    # REFERENCES (Page - 21 -)
    # ---------------------------------------------------------------------------
    sec_ref = doc.add_section()
    sec_ref.top_margin = Inches(1.0)
    sec_ref.bottom_margin = Inches(1.0)
    sec_ref.left_margin = Inches(1.25)
    sec_ref.right_margin = Inches(1.0)
    apply_page_borders(sec_ref)
    add_footer_page_number(sec_ref, "- 21 -")
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(20)
    r = p.add_run("REFERENCES")
    r.font.bold = True
    r.font.size = Pt(13)
    
    references = [
        "PHP Documentation Group. PHP Manual: Language Reference & Features. Available at: https://www.php.net/manual/en/",
        "PHP Documentation Group. PHP Data Objects (PDO) and Prepared Statements. Available at: https://www.php.net/manual/en/book.pdo.php",
        "Oracle Corporation. MySQL 8.0 Reference Manual: Relational Database Architecture. Available at: https://dev.mysql.com/doc/refman/8.0/en/",
        "Apache Friends. XAMPP Apache + MariaDB + PHP + Perl Distribution. Available at: https://www.apachefriends.org/",
        "Bootstrap Core Team. Bootstrap 5.3 Documentation: Responsive Grid and Components. Available at: https://getbootstrap.com/docs/5.3/",
        "Mozilla Developer Network (MDN). HTML5: HyperText Markup Language Semantic Specifications. Available at: https://developer.mozilla.org/en-US/docs/Web/HTML",
        "Mozilla Developer Network (MDN). CSS3: Cascading Style Sheets Layout and Flexbox. Available at: https://developer.mozilla.org/en-US/docs/Web/CSS",
        "Mozilla Developer Network (MDN). JavaScript ES6 Guide & DOM Manipulation. Available at: https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "Open Web Application Security Project (OWASP). OWASP Top 10 Web Application Security Risks. Available at: https://owasp.org/www-project-top-ten/",
        "OWASP Foundation. SQL Injection Prevention Cheat Sheet & Parameterized Queries. Available at: https://cheatsheetseries.owasp.org/",
        "Microsoft Corporation. Visual Studio Code: Code Editing and Integrated Debugging. Available at: https://code.visualstudio.com/docs",
        "Google Chrome DevTools Team. Chrome DevTools: Diagnostic Network Profiling & DOM Inspection. Available at: https://developer.chrome.com/docs/devtools"
    ]
    
    for idx, ref in enumerate(references, 1):
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.space_before = Pt(3)
        p_ref.paragraph_format.space_after = Pt(5)
        p_ref.paragraph_format.left_indent = Inches(0.35)
        p_ref.paragraph_format.first_line_indent = Inches(-0.35)
        r = p_ref.add_run(f"{idx}.\t{ref}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(11)

    output_path = r"C:\Users\rohit\OneDrive\Desktop\web tech pro\Vehicle_Service_Management_System_Project_Report.docx"
    doc.save(output_path)
    print(f"Report successfully generated at: {output_path}")

if __name__ == '__main__':
    main()
