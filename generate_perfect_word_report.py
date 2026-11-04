import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def apply_page_borders(section):
    sectPr = section._sectPr
    for child in list(sectPr):
        if child.tag.endswith('pgBorders'):
            sectPr.remove(child)
    pgBorders = OxmlElement('w:pgBorders')
    pgBorders.set(qn('w:offsetFrom'), 'page')
    for border_name in ['top', 'left', 'bottom', 'right']:
        border = OxmlElement(f'w:{border_name}')
        border.set(qn('w:val'), 'single')
        border.set(qn('w:sz'), '8')       # 1 pt
        border.set(qn('w:space'), '18')    # 18 pt from edge
        border.set(qn('w:color'), '000000')
        pgBorders.append(border)
    sectPr.append(pgBorders)

def set_cell_margins(cell, top=50, bottom=50, left=100, right=100):
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

def style_table(table, col_widths, col_alignments, header_bg="E6E6E6", font_size=10, pad_v=40):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        '<w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:left w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:right w:val="single" w:sz="6" w:space="0" w:color="000000"/>'
        '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="777777"/>'
        '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="777777"/>'
        '</w:tblBorders>'
    )
    tblPr.append(tblBorders)
    
    for row_idx, row in enumerate(table.rows):
        is_header = (row_idx == 0)
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement('w:cantSplit'))
        if is_header:
            trPr.append(OxmlElement('w:tblHeader'))
            
        for c_idx, cell in enumerate(row.cells):
            cell.width = Inches(col_widths[c_idx])
            set_cell_margins(cell, top=pad_v, bottom=pad_v, left=100, right=100)
            if is_header:
                set_cell_background(cell, header_bg)
            for p in cell.paragraphs:
                p.alignment = col_alignments[c_idx]
                p.paragraph_format.line_spacing = 1.05
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
                for run in p.runs:
                    run.font.name = 'Times New Roman'
                    run.font.size = Pt(font_size if not is_header else font_size + 0.5)
                    if is_header:
                        run.font.bold = True

def add_static_footer(section, text_str):
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.text = text_str
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(60, 60, 60)

def main():
    doc = docx.Document()
    
    # Global Font Setup
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0, 0, 0)
    
    # =========================================================================
    # 1. COVER PAGE (Page 1)
    # =========================================================================
    sec_cover = doc.sections[0]
    sec_cover.top_margin = Inches(0.8)
    sec_cover.bottom_margin = Inches(0.8)
    sec_cover.left_margin = Inches(1.0)
    sec_cover.right_margin = Inches(1.0)
    apply_page_borders(sec_cover)
    sec_cover.footer.paragraphs[0].text = ""
    
    logo_path = r"C:\Users\rohit\OneDrive\Desktop\web tech pro\report_assets\kpriet_logo.png"
    if os.path.exists(logo_path):
        p_logo = doc.add_paragraph()
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.paragraph_format.space_before = Pt(6)
        p_logo.paragraph_format.space_after = Pt(0)
        p_logo.add_run().add_picture(logo_path, width=Inches(1.8))
        
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
    
    p_sp1 = doc.add_paragraph()
    p_sp1.paragraph_format.space_before = Pt(26)
    
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.line_spacing = 1.3
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(0)
    r = p_title.add_run("VEHICLE SERVICE MANAGEMENT SYSTEM\n")
    r.font.bold = True
    r.font.size = Pt(16)
    r2 = p_title.add_run("SMART AUTOMOTIVE SERVICE AND FLEET CARE PORTAL")
    r2.font.bold = True
    r2.font.size = Pt(13)
    
    p_sp2 = doc.add_paragraph()
    p_sp2.paragraph_format.space_before = Pt(32)
    
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(0)
    r = p_sub.add_run("A MINI PROJECT REPORT")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p_sp3 = doc.add_paragraph()
    p_sp3.paragraph_format.space_before = Pt(28)
    
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
    
    p_sp4 = doc.add_paragraph()
    p_sp4.paragraph_format.space_before = Pt(26)
    
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
    
    # =========================================================================
    # 2. BONAFIDE CERTIFICATE (Page 2)
    # =========================================================================
    sec_cert = doc.add_section()
    sec_cert.top_margin = Inches(1.0)
    sec_cert.bottom_margin = Inches(1.0)
    sec_cert.left_margin = Inches(1.0)
    sec_cert.right_margin = Inches(1.0)
    apply_page_borders(sec_cert)
    add_static_footer(sec_cert, "~ 1 ~")
    
    p_c_title = doc.add_paragraph()
    p_c_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_title.paragraph_format.space_before = Pt(14)
    p_c_title.paragraph_format.space_after = Pt(28)
    r = p_c_title.add_run("BONAFIDE CERTIFICATE")
    r.font.bold = True
    r.font.size = Pt(13)
    
    p_c_body = doc.add_paragraph()
    p_c_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_c_body.paragraph_format.line_spacing = 1.25
    p_c_body.paragraph_format.space_after = Pt(45)
    p_c_body.add_run("Certified that this project report ")
    r = p_c_body.add_run("“VEHICLE SERVICE MANAGEMENT SYSTEM – SMART AUTOMOTIVE SERVICE AND FLEET CARE PORTAL”")
    r.font.bold = True
    p_c_body.add_run(" is the bonafide work of ")
    r2 = p_c_body.add_run("“ROHITH KANNAN (24CS150)”")
    r2.font.bold = True
    p_c_body.add_run(" who carried out the project work under my supervision.")
    
    t_sig = doc.add_table(rows=1, cols=2)
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
    p_viva.paragraph_format.space_before = Pt(55)
    p_viva.paragraph_format.space_after = Pt(40)
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

    # =========================================================================
    # 3. TABLE OF CONTENTS (Page 3: - i -)
    # =========================================================================
    sec_toc = doc.add_section()
    sec_toc.top_margin = Inches(0.8)
    sec_toc.bottom_margin = Inches(0.8)
    sec_toc.left_margin = Inches(1.0)
    sec_toc.right_margin = Inches(1.0)
    apply_page_borders(sec_toc)
    add_static_footer(sec_toc, "- i -")
    
    p_toc_t = doc.add_paragraph()
    p_toc_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_toc_t.paragraph_format.space_before = Pt(4)
    p_toc_t.paragraph_format.space_after = Pt(8)
    r = p_toc_t.add_run("TABLE OF CONTENTS")
    r.font.bold = True
    r.font.size = Pt(12)
    
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
    # Extra compact to guarantee exactly 1 page
    style_table(t_toc, [0.9, 4.6, 0.9], [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER], font_size=9.2, pad_v=20)

    # =========================================================================
    # 4. LIST OF FIGURES (Page 4: - ii -)
    # =========================================================================
    sec_lof = doc.add_section()
    sec_lof.top_margin = Inches(0.9)
    sec_lof.bottom_margin = Inches(0.9)
    sec_lof.left_margin = Inches(1.0)
    sec_lof.right_margin = Inches(1.0)
    apply_page_borders(sec_lof)
    add_static_footer(sec_lof, "- ii -")
    
    p_lof_t = doc.add_paragraph()
    p_lof_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_lof_t.paragraph_format.space_before = Pt(6)
    p_lof_t.paragraph_format.space_after = Pt(12)
    r = p_lof_t.add_run("LIST OF FIGURES")
    r.font.bold = True
    r.font.size = Pt(12)
    
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
    style_table(t_lof, [0.9, 4.6, 0.9], [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER], font_size=9.5, pad_v=35)

    # =========================================================================
    # 5. LIST OF ABBREVIATIONS (Page 5: - iii -)
    # =========================================================================
    sec_loa = doc.add_section()
    sec_loa.top_margin = Inches(0.9)
    sec_loa.bottom_margin = Inches(0.9)
    sec_loa.left_margin = Inches(1.0)
    sec_loa.right_margin = Inches(1.0)
    apply_page_borders(sec_loa)
    add_static_footer(sec_loa, "- iii -")
    
    p_loa_t = doc.add_paragraph()
    p_loa_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loa_t.paragraph_format.space_before = Pt(6)
    p_loa_t.paragraph_format.space_after = Pt(14)
    r = p_loa_t.add_run("LIST OF ABBREVIATIONS")
    r.font.bold = True
    r.font.size = Pt(12)
    
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
        p_a.runs[0].font.size = Pt(10)
        p_a.paragraph_format.space_before = Pt(1.5)
        p_a.paragraph_format.space_after = Pt(1.5)
        
        p_f = cell_f.paragraphs[0]
        p_f.text = full
        p_f.runs[0].font.name = 'Times New Roman'
        p_f.runs[0].font.size = Pt(10)
        p_f.paragraph_format.space_before = Pt(1.5)
        p_f.paragraph_format.space_after = Pt(1.5)

    # Helper function to create standard chapter page sections
    def create_page_section(footer_str):
        s = doc.add_section()
        s.top_margin = Inches(0.9)
        s.bottom_margin = Inches(0.9)
        s.left_margin = Inches(1.25)
        s.right_margin = Inches(1.0)
        apply_page_borders(s)
        add_static_footer(s, footer_str)
        return s

    # =========================================================================
    # PAGE 6: CHAPTER 1 ABSTRACT (- 1 -)
    # =========================================================================
    create_page_section("- 1 -")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run("CHAPTER - 1\nABSTRACT")
    r.font.bold = True
    r.font.size = Pt(13)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "Vehicle Service Management System (VSM Pro) is a full-stack, web-based automotive service management platform developed using HTML5, CSS3, Bootstrap 5, vanilla JavaScript, PHP 8, and MySQL to streamline maintenance operations, vehicle fleet tracking, appointment booking, and workshop administration. Traditional automotive repair centers rely on manual paper job cards, scattered physical registers, and uncoordinated telephone communications, causing record losses, prolonged turnaround times, and lack of billing transparency. VSM Pro addresses these inefficiencies by establishing a centralized digital ecosystem connecting vehicle owners directly with workshop service administrators."
    )
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "The application provides two distinct, role-based environments. The Customer Suite enables vehicle owners to register, log in, manage a personalized multi-vehicle fleet (cars, motorcycles, electric vehicles) with comprehensive technical specifications, schedule certified service appointments with live base-rate pricing estimation, and monitor real-time repair progress across four standardized status states (Pending, In Progress, Completed, Cancelled). Customers can review technician diagnostics, inspect itemized costs, and cancel pending requests directly. The Admin Management Console equips workshop managers with an interactive operations dashboard featuring live fleet metrics, revenue calculations, a searchable and filterable service ticket dispatch queue, diagnostic remark authoring, cost finalization modals, and a customer fleet directory."
    )
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "Security and software architectural integrity are implemented in adherence to Open Web Application Security Project (OWASP) guidelines. All database transactions utilize PHP Data Objects (PDO) with strict prepared statements and parameter binding to neutralize SQL injection. Authentication relies on cryptographic salted hashing via PHP's native password_hash() and password_verify() functions alongside session regeneration and strict Role-Based Access Control (RBAC). User interfaces feature sanitized output escaping to counter Cross-Site Scripting (XSS) and dual-tier client/server input validation. The platform was developed and comprehensively tested within a local XAMPP environment on Google Chrome, validating robust asynchronous client interactivity, relational database integrity with cascading foreign keys, and responsive UI performance."
    )

    # =========================================================================
    # PAGE 7: CHAPTER 2 INTRODUCTION (- 2 -)
    # =========================================================================
    create_page_section("- 2 -")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(12)
    r = p.add_run("CHAPTER - 2\nINTRODUCTION")
    r.font.bold = True
    r.font.size = Pt(13)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("2.1 Background and Need for the Project")
    r.font.bold = True
    r.font.size = Pt(11.5)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Every day, vehicle owners in modern cities require routine servicing, oil changes, brake repairs, engine diagnostics, and car detailing. In most automotive garages, such maintenance is handled through physical registers, paper job cards, and phone calls. These methods are unreliable: records get lost, there is no shared tracking of vehicle repairs, and pricing quotes lack transparency."
    )
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "A study of the existing practice shows the problems summarised in Table 2.1. There is a clear need for a single, secure and searchable system in which every vehicle, service booking and repair cost is recorded and tracked. VSM Pro meets this need as a web portal accessible from any browser without extra software."
    )
    
    p_tcap = doc.add_paragraph()
    p_tcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap.paragraph_format.space_before = Pt(4)
    p_tcap.paragraph_format.space_after = Pt(3)
    r = p_tcap.add_run("Table 2.1 PROBLEMS IN THE EXISTING METHODS OF VEHICLE SERVICE MANAGEMENT")
    r.font.bold = True
    r.font.size = Pt(9.5)
    
    t21_data = [
        ("Problem", "Description", "Impact"),
        ("Scattered information", "Service history is kept on paper slips and manual logbooks.", "Vehicle owners cannot track past maintenance or verify warranty."),
        ("No online booking", "Appointments are arranged by phone calls or direct walk-ins.", "Workshop bay congestion and technician dispatch delays."),
        ("Opaque pricing", "Costs are estimated verbally without standardized base rates.", "Customer mistrust and frequent billing disputes."),
        ("No status tracking", "Customers cannot see if a vehicle is pending, in service or ready.", "Repeated phone enquiries and duplicate administrative work."),
        ("Limited administration", "Managers have no digital tool to view fleet counts or total revenue.", "Poor technician allocation and lack of operational data.")
    ]
    t21 = doc.add_table(rows=len(t21_data), cols=3)
    for r_idx, row in enumerate(t21_data):
        for c_idx, val in enumerate(row):
            t21.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t21, [1.4, 2.6, 2.4], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT], font_size=9.2, pad_v=25)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(0)
    p.add_run(
        "Problem statement: How can a secure and responsive web portal let vehicle owners register fleets, book certified services with transparent pricing, track real-time repair stages, and allow administrators to dispatch mechanics and manage repair revenue?"
    )

    # =========================================================================
    # PAGE 8: 2.2 OBJECTIVES & 2.3 SCOPE (- 3 -)
    # =========================================================================
    create_page_section("- 3 -")
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("2.2 Objectives")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run("The main objective of VSM Pro is to develop a secure, user-friendly, and responsive web application that replaces scattered paper records with a single database-driven portal. The specific objectives are:")
    
    objectives = [
        "To develop a web portal in which customers can register, log in and manage their vehicle fleets.",
        "To store users, vehicles, services and service requests in a MySQL database using PHP and PDO.",
        "To allow a customer to register vehicles with brand, model, registration number, year and fuel type.",
        "To provide service booking with transparent base prices, preferred dates, and repair descriptions.",
        "To implement live status tracking (Pending, In Progress, Completed, Cancelled) with instant pending cancellations.",
        "To provide an administrator area for managing requests, updating costs and remarks, and viewing revenue.",
        "To secure the application using password hashing, prepared statements, output escaping and role-based access control."
    ]
    for obj in objectives:
        p_obj = doc.add_paragraph(style='List Bullet')
        p_obj.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_obj.paragraph_format.line_spacing = 1.15
        p_obj.paragraph_format.space_before = Pt(1)
        p_obj.paragraph_format.space_after = Pt(2)
        r = p_obj.add_run(obj)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10.5)

    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("2.3 Scope")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.space_after = Pt(8)
    p.add_run(
        "The scope of VSM Pro is a web application through which vehicle owners and automotive workshops manage vehicle maintenance. It covers user registration and login, role-based access for customers and administrators, fleet management with full technical specs, appointment scheduling with transparent base rates, real-time ticket tracking, and administrative cost finalization. It also covers customer directory search and fleet inspection."
    )
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.space_after = Pt(8)
    p.add_run(
        "The current version does not include SMS/WhatsApp notifications, online payment gateway integration, GPS-based mechanic dispatching, or OBD-II hardware telematics. These are listed as future enhancements. The application is intended for workshop and educational use."
    )

    # =========================================================================
    # PAGE 9: 2.4 DEVELOPMENT PLAN (- 4 -)
    # =========================================================================
    create_page_section("- 4 -")
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run("2.4 Development Plan")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.space_after = Pt(8)
    p.add_run(
        "The development of VSM Pro was planned in six phases, from requirement analysis to testing. Each phase produced a defined output that was used as the input of the next phase, as shown in Table 2.2."
    )
    
    p_tcap2 = doc.add_paragraph()
    p_tcap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap2.paragraph_format.space_before = Pt(4)
    p_tcap2.paragraph_format.space_after = Pt(4)
    r = p_tcap2.add_run("Table 2.2 DEVELOPMENT PLAN OF VSM PRO")
    r.font.bold = True
    r.font.size = Pt(10)
    
    t22_data = [
        ("S.No", "Phase", "Activities", "Output"),
        ("1", "Requirement analysis", "Identified functional requirements: registration, fleet management, booking, tracking and admin dispatch. Divided users into customer and admin roles.", "List of modules and user roles"),
        ("2", "Design", "Drew system architecture, designed normalized database schema with four related tables, and planned UI with dark-sidebar theme and colored badges.", "Flowchart, ER diagram, UI mock-up"),
        ("3", "User interface development", "Built pages with HTML5, CSS3 and Bootstrap 5 using responsive cards, tables and forms. Added JavaScript for price estimation preview and live search.", "Responsive front end"),
        ("4", "Back-end and database implementation", "Created vehicle_service_db database in MySQL with seed data. Wrote PHP scripts for sessions, role checks, fleet CRUD, bookings and administration using PDO.", "Working application with database"),
        ("5", "Security hardening", "Applied password hashing, prepared statements, output escaping, CSRF tokens and role checks on every protected page.", "Secured application"),
        ("6", "Testing", "Tested the complete flow on XAMPP with valid and invalid inputs, different user roles and different screen sizes.", "Test results")
    ]
    t22 = doc.add_table(rows=len(t22_data), cols=4)
    for r_idx, row in enumerate(t22_data):
        for c_idx, val in enumerate(row):
            t22.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t22, [0.6, 1.4, 2.9, 1.5], [WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT], font_size=9.2, pad_v=25)

    # =========================================================================
    # PAGE 10: CHAPTER 3 IMPLEMENTATION (- 5 -)
    # =========================================================================
    create_page_section("- 5 -")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run("CHAPTER - 3\nIMPLEMENTATION")
    r.font.bold = True
    r.font.size = Pt(13)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "VSM Pro follows a three-layer client-server architecture. The user interacts through a web browser on desktop or mobile. The presentation layer, built with HTML5, CSS3, Bootstrap 5 and JavaScript, renders pages and sends requests to Apache. The application layer, written in PHP 8 and running on XAMPP, handles authentication, fleet operations, booking dispatch and administrative analytics. It accesses the data layer through PHP Data Objects (PDO), which sends SQL queries to the MySQL database vehicle_service_db."
    )
    
    p_f31 = doc.add_paragraph()
    p_f31.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f31.paragraph_format.space_before = Pt(4)
    p_f31.paragraph_format.space_after = Pt(2)
    if os.path.exists(fig31_path):
        p_f31.add_run().add_picture(fig31_path, width=Inches(4.8))
    p_c31 = doc.add_paragraph()
    p_c31.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c31.paragraph_format.space_before = Pt(1)
    p_c31.paragraph_format.space_after = Pt(6)
    r = p_c31.add_run("Fig 3.1 SYSTEM ARCHITECTURE OF VEHICLE SERVICE MANAGEMENT SYSTEM")
    r.font.bold = True
    r.font.size = Pt(9.5)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("3.1 Tech Stack")
    r.font.bold = True
    r.font.size = Pt(11.5)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "The technologies used in the project were selected because they are open-source, widely documented and suitable for a data-driven web application. They are explained below and summarised in Table 3.1."
    )
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run("3.1.1 HTML5")
    r.font.bold = True
    r.font.size = Pt(10.5)
    p_b = doc.add_paragraph()
    p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_b.paragraph_format.line_spacing = 1.15
    p_b.paragraph_format.space_after = Pt(0)
    p_b.add_run(
        "HyperText Markup Language 5 defines the structure of every page of the portal, including the navigation bar, forms, tables, cards and the sidebar. Semantic elements and built-in input types such as email and date make forms clear and let the browser perform basic validation before sending data to the server."
    )

    # =========================================================================
    # PAGE 11: TECH STACK CONTINUED (- 6 -)
    # =========================================================================
    create_page_section("- 6 -")
    tech_subs_pg6 = [
        ("3.1.2 CSS3 and Bootstrap 5", "Cascading Style Sheets 3 and Bootstrap 5 control the layout, colours and responsiveness. The interface uses a dark sidebar theme with high-contrast cards, modern typography and coloured status badges for pending, in progress, completed and cancelled records. Flexbox, grid and media queries let the layout adapt to desktop and mobile screens, and the sidebar collapses on small devices."),
        ("3.1.3 JavaScript", "JavaScript makes the pages interactive. It is used for client-side form validation, showing and hiding password fields, live calculation previews of service base prices upon selection, confirming vehicle deletions, and live search across the administrative queue."),
        ("3.1.4 PHP and PDO", "PHP is a server-side scripting language that runs on the Apache server and generates dynamic HTML. It provides built-in support for sessions, form handling and password hashing. PHP Data Objects (PDO) with the MySQL driver is the database access layer. Prepared statements separate the SQL command from user data and protect against SQL injection. PHP implements registration, login, fleet operations, appointment booking and all admin actions."),
        ("3.1.5 MySQL and phpMyAdmin", "MySQL is an open-source relational database management system known for reliability, constraints, indexes and transactions. The database vehicle_service_db stores four related tables. PRIMARY KEY, FOREIGN KEY and UNIQUE constraints keep the data valid, and indexes on email, registration number and status columns speed up searching. phpMyAdmin is the graphical tool used to create the database, run SQL scripts and inspect stored data."),
        ("3.1.6 Development and Testing Tools", "Visual Studio Code is the editor used to write the HTML, CSS, JavaScript and PHP files. XAMPP provides the local Apache web server that runs the PHP application from the htdocs folder. Google Chrome and its Developer Tools are used for testing, viewport inspection and debugging.")
    ]
    for h_txt, b_txt in tech_subs_pg6:
        p_h = doc.add_paragraph()
        p_h.paragraph_format.space_before = Pt(4)
        p_h.paragraph_format.space_after = Pt(2)
        r = p_h.add_run(h_txt)
        r.font.bold = True
        r.font.size = Pt(11)
        
        p_b = doc.add_paragraph()
        p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_b.paragraph_format.line_spacing = 1.15
        p_b.paragraph_format.space_after = Pt(6)
        p_b.add_run(b_txt)

    # =========================================================================
    # PAGE 12: TABLE 3.1 & 3.2 MODULES (- 7 -)
    # =========================================================================
    create_page_section("- 7 -")
    p_tcap3 = doc.add_paragraph()
    p_tcap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap3.paragraph_format.space_before = Pt(6)
    p_tcap3.paragraph_format.space_after = Pt(4)
    r = p_tcap3.add_run("Table 3.1 TECHNOLOGY STACK")
    r.font.bold = True
    r.font.size = Pt(10)
    
    t31 = doc.add_table(rows=len(t31_data), cols=2)
    for r_idx, row in enumerate(t31_data):
        for c_idx, val in enumerate(row):
            t31.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t31, [1.8, 4.6], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT], font_size=9.2, pad_v=22)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("3.2 Modules")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.space_after = Pt(8)
    p.add_run(
        "VSM Pro is divided into the modules explained in this section. The customer modules and administrator modules are separated by role, and the database and security modules support all of them."
    )
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("3.2.1 Database Module")
    r.font.bold = True
    r.font.size = Pt(11.5)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.space_after = Pt(8)
    p.add_run(
        "The database vehicle_service_db contains four related tables. The users table stores user accounts, the vehicles table stores registered customer fleets, the services table stores the service package catalog, and the service_requests table stores all appointment tickets. Cascading foreign keys ensure referential integrity. The relationships are shown in Fig 3.2, the entities are described in Table 3.2 and status values are listed in Table 3.3."
    )

    # =========================================================================
    # PAGE 13: FIG 3.2 & TABLE 3.2 (- 8 -)
    # =========================================================================
    create_page_section("- 8 -")
    p_f32 = doc.add_paragraph()
    p_f32.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f32.paragraph_format.space_before = Pt(6)
    p_f32.paragraph_format.space_after = Pt(2)
    if os.path.exists(fig32_path):
        p_f32.add_run().add_picture(fig32_path, width=Inches(4.9))
    p_c32 = doc.add_paragraph()
    p_c32.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c32.paragraph_format.space_before = Pt(1)
    p_c32.paragraph_format.space_after = Pt(8)
    r = p_c32.add_run("Fig 3.2 ENTITY RELATIONSHIP DIAGRAM OF THE DATABASE")
    r.font.bold = True
    r.font.size = Pt(9.5)
    
    p_tcap4 = doc.add_paragraph()
    p_tcap4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap4.paragraph_format.space_before = Pt(6)
    p_tcap4.paragraph_format.space_after = Pt(4)
    r = p_tcap4.add_run("Table 3.2 CORE DATA ENTITIES")
    r.font.bold = True
    r.font.size = Pt(10)
    
    t32 = doc.add_table(rows=len(t32_data), cols=2)
    for r_idx, row in enumerate(t32_data):
        for c_idx, val in enumerate(row):
            t32.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t32, [1.6, 4.8], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT], font_size=9.2, pad_v=24)

    # =========================================================================
    # PAGE 14: TABLE 3.3 & MODULES 3.2.2 TO 3.2.4 (- 9 -)
    # =========================================================================
    create_page_section("- 9 -")
    p_tcap5 = doc.add_paragraph()
    p_tcap5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap5.paragraph_format.space_before = Pt(4)
    p_tcap5.paragraph_format.space_after = Pt(3)
    r = p_tcap5.add_run("Table 3.3 STATUS VALUES OF SERVICE REQUESTS")
    r.font.bold = True
    r.font.size = Pt(9.5)
    
    t33 = doc.add_table(rows=len(t33_data), cols=3)
    for r_idx, row in enumerate(t33_data):
        for c_idx, val in enumerate(row):
            t33.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t33, [1.5, 1.2, 3.7], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT], font_size=9.2, pad_v=20)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("3.2.2 Registration and Login Module")
    r.font.bold = True
    r.font.size = Pt(11)
    p_b = doc.add_paragraph()
    p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_b.paragraph_format.line_spacing = 1.15
    p_b.paragraph_format.space_after = Pt(6)
    p_b.add_run(
        "A new user creates an account with full name, email address, phone, password and address. The password is saved as a salted hash using password_hash(). At login credentials are authenticated with password_verify(), the session is regenerated, and the user is redirected to the customer or administrator dashboard according to their role."
    )
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("3.2.3 Customer Dashboard Module")
    r.font.bold = True
    r.font.size = Pt(11)
    p_b = doc.add_paragraph()
    p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_b.paragraph_format.line_spacing = 1.15
    p_b.paragraph_format.space_after = Pt(6)
    p_b.add_run(
        "The dashboard presents a welcome message, shortcut buttons to add vehicles or book service, four metric cards (My Vehicles, Pending Requests, In Progress, Completed Services), a table of recent service appointments, and an enrolled vehicle fleet roster."
    )
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("3.2.4 Vehicle Fleet Management Module")
    r.font.bold = True
    r.font.size = Pt(11)
    p_b = doc.add_paragraph()
    p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_b.paragraph_format.line_spacing = 1.15
    p_b.paragraph_format.space_after = Pt(0)
    p_b.add_run(
        "Customers manage their personal vehicles (cars, motorcycles, electric vehicles). Customers can add, view, edit, or delete vehicles with brand, model, registration number, year and fuel type. Modal confirmations ensure safe deletions with cascading database updates."
    )

    # =========================================================================
    # PAGE 15: 3.2.5 & FIG 3.3 FLOWCHART (- 10 -)
    # =========================================================================
    create_page_section("- 10 -")
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("3.2.5 Service Booking and Pricing Estimation Module")
    r.font.bold = True
    r.font.size = Pt(11.5)
    p_b = doc.add_paragraph()
    p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_b.paragraph_format.line_spacing = 1.15
    p_b.paragraph_format.space_after = Pt(4)
    p_b.add_run(
        "The customer selects an enrolled vehicle from a dropdown, chooses a service package, selects a preferred future date, and provides maintenance instructions. A JavaScript event listener immediately updates an 'Estimated Price Preview' card showcasing the base cost. The booking is submitted to the database with status Pending. The algorithm flow is shown in Fig 3.3."
    )
    
    p_f33 = doc.add_paragraph()
    p_f33.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f33.paragraph_format.space_before = Pt(4)
    p_f33.paragraph_format.space_after = Pt(2)
    if os.path.exists(fig33_path):
        p_f33.add_run().add_picture(fig33_path, width=Inches(4.5))
    p_c33 = doc.add_paragraph()
    p_c33.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c33.paragraph_format.space_before = Pt(1)
    p_c33.paragraph_format.space_after = Pt(4)
    r = p_c33.add_run("Fig 3.3 FLOWCHART OF THE SERVICE BOOKING AND DISPATCH ALGORITHM")
    r.font.bold = True
    r.font.size = Pt(9.5)

    # =========================================================================
    # PAGE 16: FIG 3.4 WORKFLOW & MODULES 3.2.6 TO 3.2.8 (- 11 -)
    # =========================================================================
    create_page_section("- 11 -")
    p_f34 = doc.add_paragraph()
    p_f34.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_f34.paragraph_format.space_before = Pt(4)
    p_f34.paragraph_format.space_after = Pt(2)
    if os.path.exists(fig34_path):
        p_f34.add_run().add_picture(fig34_path, width=Inches(4.2))
    p_c34 = doc.add_paragraph()
    p_c34.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c34.paragraph_format.space_before = Pt(1)
    p_c34.paragraph_format.space_after = Pt(6)
    r = p_c34.add_run("Fig 3.4 TYPICAL WORKFLOW OF VSM PRO")
    r.font.bold = True
    r.font.size = Pt(9.5)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run("3.2.6 Service Request History Module")
    r.font.bold = True
    r.font.size = Pt(10.5)
    p_b = doc.add_paragraph()
    p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_b.paragraph_format.line_spacing = 1.15
    p_b.paragraph_format.space_after = Pt(4)
    p_b.add_run("Lists past and active bookings with filter pills (All, Pending, In Progress, Completed, Cancelled), total billed cost, and cancellation capabilities for pending tickets.")
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run("3.2.7 Admin Overview Dashboard Module")
    r.font.bold = True
    r.font.size = Pt(10.5)
    p_b = doc.add_paragraph()
    p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_b.paragraph_format.line_spacing = 1.15
    p_b.paragraph_format.space_after = Pt(4)
    p_b.add_run("Displays workshop metrics: total customers, fleet size, pending requests, in-progress bay tickets, completed jobs, and cumulative revenue with quick dispatch shortcuts.")
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run("3.2.8 Service Request Queue and Dispatch Module")
    r.font.bold = True
    r.font.size = Pt(10.5)
    p_b = doc.add_paragraph()
    p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_b.paragraph_format.line_spacing = 1.15
    p_b.paragraph_format.space_after = Pt(0)
    p_b.add_run("Enables administrators to filter tickets, search across clients and plates, update status, write diagnostic remarks, and assign finalized repair billing.")

    # =========================================================================
    # PAGE 17: MODULES 3.2.9, 3.2.10 & TABLE 3.4 (- 12 -)
    # =========================================================================
    create_page_section("- 12 -")
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("3.2.9 Customer Directory and Fleet Module")
    r.font.bold = True
    r.font.size = Pt(11.5)
    p_b = doc.add_paragraph()
    p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_b.paragraph_format.line_spacing = 1.2
    p_b.paragraph_format.space_after = Pt(6)
    p_b.add_run(
        "Enables workshop administrators to view all registered customers, contact information, addresses, and total fleet size, with interactive 'View Fleet' modals to inspect vehicles associated with any client."
    )
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("3.2.10 Security Module")
    r.font.bold = True
    r.font.size = Pt(11.5)
    p_b = doc.add_paragraph()
    p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_b.paragraph_format.line_spacing = 1.2
    p_b.paragraph_format.space_after = Pt(6)
    p_b.add_run(
        "Because the system manages customer personal data and billing records, security controls are built into every tier following OWASP standards as summarized in Table 3.4."
    )
    
    p_tcap6 = doc.add_paragraph()
    p_tcap6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap6.paragraph_format.space_before = Pt(4)
    p_tcap6.paragraph_format.space_after = Pt(3)
    r = p_tcap6.add_run("Table 3.4 SECURITY CONTROLS IMPLEMENTED IN THE APPLICATION")
    r.font.bold = True
    r.font.size = Pt(10)
    
    t34 = doc.add_table(rows=len(t34_data), cols=2)
    for r_idx, row in enumerate(t34_data):
        for c_idx, val in enumerate(row):
            t34.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t34, [1.8, 4.6], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT], font_size=9.2, pad_v=20)

    # =========================================================================
    # PAGE 18: CHAPTER 4 OUTCOME, FIG 4.1 & FIG 4.2 (- 13 -)
    # =========================================================================
    create_page_section("- 13 -")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run("CHAPTER - 4\nOUTCOME")
    r.font.bold = True
    r.font.size = Pt(13)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("4.1 Implementation Outcome")
    r.font.bold = True
    r.font.size = Pt(11)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run(
        "VSM Pro was successfully developed and tested on an Apache HTTP Server with PHP 8 and MySQL within XAMPP. The user interface responds smoothly across viewport sizes, providing vehicle owners and garage administrators with high-contrast, modern dashboards. All operations—from user onboarding to booking dispatch, status transitions, and fleet lookups—executed reliably."
    )
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(1)
    r = p.add_run("4.2 Module-wise Outcome with Screenshots")
    r.font.bold = True
    r.font.size = Pt(11)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.1
    p.paragraph_format.space_after = Pt(3)
    p.add_run("Public Landing Page Module. Introduces VSM Pro with key value proposition highlights (100% Transparent Pricing, 6+ Certified Services, 24/7 Online Booking), clean navigation, and a Live Fleet Tracker widget (Fig 4.1).")
    
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(fig41_path):
        p_img.add_run().add_picture(fig41_path, width=Inches(4.5))
    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c.paragraph_format.space_after = Pt(4)
    r = p_c.add_run("Fig 4.1 PUBLIC LANDING PAGE MODULE")
    r.font.bold = True
    r.font.size = Pt(9)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.1
    p.paragraph_format.space_after = Pt(3)
    p.add_run("Login Module. Centered authentication card featuring email and password input fields, role redirection, and direct link to account registration (Fig 4.2).")
    
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(fig42_path):
        p_img.add_run().add_picture(fig42_path, width=Inches(3.3))
    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_c.add_run("Fig 4.2 LOGIN MODULE")
    r.font.bold = True
    r.font.size = Pt(9)

    # =========================================================================
    # PAGE 19: FIG 4.3 & FIG 4.4 (- 14 -)
    # =========================================================================
    create_page_section("- 14 -")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Customer Dashboard Module. Provides registered customers with real-time fleet metric cards, quick-action buttons, recent bookings, and a registered vehicle roster (Fig 4.3).")
    
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(fig43_path):
        p_img.add_run().add_picture(fig43_path, width=Inches(4.5))
    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c.paragraph_format.space_after = Pt(8)
    r = p_c.add_run("Fig 4.3 CUSTOMER DASHBOARD MODULE")
    r.font.bold = True
    r.font.size = Pt(9)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Vehicle Fleet Management Module. Presents enrolled vehicles in a clean table with vehicle type badges, license registration numbers, manufacture year, fuel type, and action buttons for booking, editing, or deleting assets (Fig 4.4).")
    
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(fig44_path):
        p_img.add_run().add_picture(fig44_path, width=Inches(4.5))
    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_c.add_run("Fig 4.4 VEHICLE FLEET MANAGEMENT MODULE")
    r.font.bold = True
    r.font.size = Pt(9)

    # =========================================================================
    # PAGE 20: FIG 4.5 & FIG 4.6 (- 15 -)
    # =========================================================================
    create_page_section("- 15 -")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Service Booking Appointment Module. Streamlined appointment scheduling interface with vehicle selection, catalog dropdown, preferred service date picker, issue notes, and a live pricing estimation preview card (Fig 4.5).")
    
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(fig45_path):
        p_img.add_run().add_picture(fig45_path, width=Inches(4.5))
    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c.paragraph_format.space_after = Pt(8)
    r = p_c.add_run("Fig 4.5 SERVICE BOOKING APPOINTMENT MODULE")
    r.font.bold = True
    r.font.size = Pt(9)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Service Request History Module. Displays historical and active service bookings with status filter pills, scheduled dates, total finalized costs, and ticket detail inspection modals (Fig 4.6).")
    
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(fig46_path):
        p_img.add_run().add_picture(fig46_path, width=Inches(4.5))
    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_c.add_run("Fig 4.6 SERVICE REQUEST HISTORY MODULE")
    r.font.bold = True
    r.font.size = Pt(9)

    # =========================================================================
    # PAGE 21: FIG 4.7 & FIG 4.8 (- 16 -)
    # =========================================================================
    create_page_section("- 16 -")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Admin Dashboard Overview Module. Workshop management console showing real-time metrics for total customers, registered vehicles, active ticket counts, and total workshop revenue, accompanied by recent ticket activity (Fig 4.7).")
    
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(fig47_path):
        p_img.add_run().add_picture(fig47_path, width=Inches(4.5))
    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c.paragraph_format.space_after = Pt(8)
    r = p_c.add_run("Fig 4.7 ADMIN DASHBOARD OVERVIEW MODULE")
    r.font.bold = True
    r.font.size = Pt(9)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(4)
    p.add_run("Admin Service Request Queue Module. Centralized ticket queue with interactive status filter pills and live search bar, enabling administrators to dispatch mechanics, update repair stages, write diagnostic remarks, and assign finalized repair invoices (Fig 4.8).")
    
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(fig48_path):
        p_img.add_run().add_picture(fig48_path, width=Inches(4.5))
    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p_c.add_run("Fig 4.8 ADMIN SERVICE REQUEST QUEUE MODULE")
    r.font.bold = True
    r.font.size = Pt(9)

    # =========================================================================
    # PAGE 22: FIG 4.9 ADMIN CUSTOMER DIRECTORY (- 17 -)
    # =========================================================================
    create_page_section("- 17 -")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.2
    p.paragraph_format.space_after = Pt(6)
    p.add_run("Admin Customer Directory & Fleet Module. Enables workshop management to browse all registered clients, residential addresses, phone numbers, and associated fleet metrics. An interactive 'View Fleet' modal reveals all vehicles owned by a specific customer, assisting workshop personnel in providing personalized automotive care (Fig 4.9).")
    
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    if os.path.exists(fig49_path):
        p_img.add_run().add_picture(fig49_path, width=Inches(4.8))
    p_c = doc.add_paragraph()
    p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c.paragraph_format.space_after = Pt(6)
    r = p_c.add_run("Fig 4.9 ADMIN CUSTOMER DIRECTORY & FLEET MODULE")
    r.font.bold = True
    r.font.size = Pt(9.5)

    # =========================================================================
    # PAGE 23: 4.3 COMPARISON WITH EXISTING METHODS (- 18 -)
    # =========================================================================
    create_page_section("- 18 -")
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("4.3 Comparison with Existing Methods")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "A rigorous comparative evaluation between traditional manual workshop management techniques and VSM Pro demonstrates substantial improvements across data integrity, workflow automation, cost transparency, and customer satisfaction, as presented in Table 4.1."
    )
    
    p_tcap7 = doc.add_paragraph()
    p_tcap7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap7.paragraph_format.space_before = Pt(4)
    p_tcap7.paragraph_format.space_after = Pt(3)
    r = p_tcap7.add_run("Table 4.1 EXISTING METHODS VERSUS VSM PRO")
    r.font.bold = True
    r.font.size = Pt(10)
    
    t41 = doc.add_table(rows=len(t41_data), cols=3)
    for r_idx, row in enumerate(t41_data):
        for c_idx, val in enumerate(row):
            t41.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t41, [1.4, 2.5, 2.5], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.LEFT], font_size=9.2, pad_v=18)

    # =========================================================================
    # PAGE 24: 4.4 DISCUSSION AND LIMITATIONS (- 19 -)
    # =========================================================================
    create_page_section("- 19 -")
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("4.4 Discussion and Limitations")
    r.font.bold = True
    r.font.size = Pt(12)
    
    p_tcap8 = doc.add_paragraph()
    p_tcap8.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tcap8.paragraph_format.space_before = Pt(4)
    p_tcap8.paragraph_format.space_after = Pt(3)
    r = p_tcap8.add_run("Table 4.2 KEY OUTCOMES OF VSM PRO")
    r.font.bold = True
    r.font.size = Pt(10)
    
    t42 = doc.add_table(rows=len(t42_data), cols=3)
    for r_idx, row in enumerate(t42_data):
        for c_idx, val in enumerate(row):
            t42.rows[r_idx].cells[c_idx].paragraphs[0].text = val
    style_table(t42, [1.6, 1.2, 3.6], [WD_ALIGN_PARAGRAPH.LEFT, WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.LEFT], font_size=9.2, pad_v=20)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "The experimental validation and local deployment results establish that VSM Pro successfully eliminates traditional automotive service friction. Consolidating customer vehicles, standardized service offerings, and workshop dispatch queues into an integrated relational database reduces administrative turnaround times, prevents misplaced maintenance records, and builds trust through upfront pricing."
    )
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(0)
    p.add_run(
        "However, certain limitations exist in the current prototype. The system executes in a local XAMPP Apache development environment and requires migration to production cloud hosting for wide internet access. Customer notifications currently rely on visiting the web portal rather than automated SMS or WhatsApp messages, and repair bills are recorded administratively rather than processed via direct online credit card or UPI payment gateways."
    )

    # =========================================================================
    # PAGE 25: CHAPTER 5 CONCLUSION & FUTURE SCOPE (- 20 -)
    # =========================================================================
    create_page_section("- 20 -")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(10)
    r = p.add_run("CHAPTER - 5\nCONCLUSION")
    r.font.bold = True
    r.font.size = Pt(13)
    
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(6)
    p.add_run(
        "Vehicle Service Management System (VSM Pro) was conceived, engineered, and verified as a modern, responsive, and secure full-stack web application designed to digitize automotive maintenance operations. By pairing an intuitive HTML5, CSS3, Bootstrap 5, and vanilla JavaScript front-end with a robust PHP 8 and MySQL relational backend, the system delivers an end-to-end operational platform bridging vehicle owners and workshop administrators. Customers benefit from effortless fleet enrollment, transparent service booking with automated cost estimation, and live ticket tracking. Workshop supervisors gain deep administrative oversight through real-time operational analytics, interactive dispatch queues, and customer directories."
    )
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_after = Pt(8)
    p.add_run(
        "The project provided rigorous hands-on exposure to full-stack software development principles, including modular file architectures, relational database normalization (3NF), foreign key cascading, secure session management, and OWASP-recommended security practices (PDO prepared statements, bcrypt hashing, and HTML escaping). Comprehensive local testing across diverse user roles confirmed that VSM Pro effectively solves the communication breakdowns, lost job cards, and billing disputes endemic to conventional automotive garages."
    )
    
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)
    r = p.add_run("5.1 Future Scope")
    r.font.bold = True
    r.font.size = Pt(11.5)
    
    for item in future_items:
        p_f = doc.add_paragraph(style='List Bullet')
        p_f.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_f.paragraph_format.line_spacing = 1.12
        p_f.paragraph_format.space_before = Pt(1)
        p_f.paragraph_format.space_after = Pt(2)
        r = p_f.add_run(item)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10)

    # =========================================================================
    # PAGE 26: REFERENCES (- 21 -)
    # =========================================================================
    create_page_section("- 21 -")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(16)
    r = p.add_run("REFERENCES")
    r.font.bold = True
    r.font.size = Pt(13)
    
    for idx, ref in enumerate(references, 1):
        p_ref = doc.add_paragraph()
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.space_before = Pt(2)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.left_indent = Inches(0.35)
        p_ref.paragraph_format.first_line_indent = Inches(-0.35)
        r = p_ref.add_run(f"{idx}.\t{ref}")
        r.font.name = 'Times New Roman'
        r.font.size = Pt(10.5)

    out_proj = r"C:\Users\rohit\OneDrive\Desktop\web tech pro\Vehicle_Service_Management_System_Project_Report.docx"
    doc.save(out_proj)
    print("Word document generated at:", out_proj)

if __name__ == '__main__':
    main()
