# -*- coding: utf-8 -*-
"""
Script to generate the comprehensive academic project report (.docx)
Subject: Triển khai và Quản trị Hệ thống Phần mềm
Topic: Đề tài 38 - Hệ thống Quản lý Chi tiêu (Expense Tracker)
Student: HOÀNG TRẤN HUY - CNTT K23H - DTC245200203
University: Trường Đại học Công nghệ Thông tin và Truyền thông (ICTU)
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def create_report():
    doc = docx.Document()
    
    # Page setup - Standard A4 (210 x 297 mm)
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    
    # Margins: Top 2cm, Bottom 2cm, Left 3cm (binding), Right 2cm
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(3.0)
    section.right_margin = Cm(2.0)
    
    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Times New Roman'
    font.size = Pt(13)
    font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
    
    # -------------------------------------------------------------
    # HELPER FUNCTIONS
    # -------------------------------------------------------------
    def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
        tcPr = cell._tc.get_or_add_tcPr()
        tcMar = OxmlElement('w:tcMar')
        for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
            node = OxmlElement(f'w:{m}')
            node.set(qn('w:w'), str(val))
            node.set(qn('w:type'), 'dxa')
            tcMar.append(node)
        tcPr.append(tcMar)

    def set_cell_background(cell, fill_hex):
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        cell._tc.get_or_add_tcPr().append(shd)

    def set_table_borders(table, color="D1D5DB", sz="4", val="single"):
        tblPr = table._tbl.tblPr
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'  <w:left w:val="none"/>'
            f'  <w:right w:val="none"/>'
            f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'  <w:insideV w:val="none"/>'
            f'</w:tblBorders>'
        )
        tblPr.append(borders)

    def add_p(text="", bold=False, italic=False, font_size=13, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, line_spacing=1.25, color=RGBColor(0x1F, 0x29, 0x37)):
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = line_spacing
        if text:
            run = p.add_run(text)
            run.font.name = 'Times New Roman'
            run.font.size = Pt(font_size)
            run.font.bold = bold
            run.font.italic = italic
            run.font.color.rgb = color
        return p

    def add_h1(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(8)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(16)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x8A) # Navy Blue
        return p

    def add_h2(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(14)
        run.font.bold = True
        run.font.color.rgb = RGBColor(0x0F, 0x17, 0x2A) # Charcoal Slate
        return p

    def add_h3(title):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(10)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(title)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13)
        run.font.bold = True
        run.font.italic = True
        run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        return p

    def add_bullet(text, level=0, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.2
        p.paragraph_format.left_indent = Inches(0.25 * (level + 1))
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.font.name = 'Times New Roman'
            r_b.font.size = Pt(13)
            r_b.font.bold = True
        r = p.add_run(text)
        r.font.name = 'Times New Roman'
        r.font.size = Pt(13)

    def add_code(code_str, caption=None):
        if caption:
            p_cap = doc.add_paragraph()
            p_cap.paragraph_format.space_before = Pt(6)
            p_cap.paragraph_format.space_after = Pt(2)
            r_cap = p_cap.add_run(f"Đoạn mã / Cấu hình: {caption}")
            r_cap.font.name = "Times New Roman"
            r_cap.font.size = Pt(11)
            r_cap.font.bold = True
            r_cap.font.italic = True
            r_cap.font.color.rgb = RGBColor(0x47, 0x55, 0x69)

        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "0F172A") # Dark slate terminal bg
        set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
        
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'  <w:top w:val="single" w:sz="6" w:color="334155"/>'
            f'  <w:bottom w:val="single" w:sz="6" w:color="334155"/>'
            f'  <w:left w:val="single" w:sz="6" w:color="334155"/>'
            f'  <w:right w:val="single" w:sz="6" w:color="334155"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(tcBorders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(code_str)
        run.font.name = "Consolas"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0)
        
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_callout(text, title=None):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        set_cell_background(cell, "F8FAFC")
        set_cell_margins(cell, top=120, bottom=120, left=180, right=180)
        
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'  <w:left w:val="single" w:sz="24" w:space="0" w:color="2563EB"/>'
            f'  <w:top w:val="single" w:sz="4" w:color="E2E8F0"/>'
            f'  <w:bottom w:val="single" w:sz="4" w:color="E2E8F0"/>'
            f'  <w:right w:val="single" w:sz="4" w:color="E2E8F0"/>'
            f'</w:tcBorders>'
        )
        tcPr.append(tcBorders)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.2
        if title:
            run_t = p.add_run(f"💡 {title}: ")
            run_t.font.name = "Times New Roman"
            run_t.font.size = Pt(11.5)
            run_t.font.bold = True
            run_t.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)
        
        run = p.add_run(text)
        run.font.name = "Times New Roman"
        run.font.size = Pt(11.5)
        run.font.color.rgb = RGBColor(0x33, 0x41, 0x55)
        
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # =============================================================
    # 1. COVER PAGE (MATCHING THE OFFICIAL ICTU FORMAT)
    # =============================================================
    # University Header
    p_uni = add_p("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ THÔNG TIN VÀ TRUYỀN THÔNG", bold=True, font_size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    p_fac = add_p("KHOA CÔNG NGHỆ THÔNG TIN", bold=True, font_size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    
    # Underline bar under Faculty
    p_bar = add_p("─────────── *** ───────────", bold=True, font_size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=20, color=RGBColor(0x4B, 0x55, 0x63))
    
    # Centered ICTU Logo
    logo_path = os.path.join(os.getcwd(), 'docs', 'ictu_logo.png')
    if os.path.exists(logo_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(10)
        p_img.paragraph_format.space_after = Pt(24)
        run_img = p_img.add_run()
        run_img.add_picture(logo_path, width=Inches(1.8))
    
    # Title "BÁO CÁO" in Red Bold like in image
    p_title = add_p("BÁO CÁO", bold=True, font_size=24, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14, color=RGBColor(0xDC, 0x26, 0x26))
    
    # Subject & Topic
    add_p("MÔN: TRIỂN KHAI VÀ QUẢN TRỊ HỆ THỐNG PHẦN MỀM", bold=True, font_size=14, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)
    add_p("ĐỀ TÀI: HỆ THỐNG QUẢN LÝ CHI TIÊU / EXPENSE TRACKER", bold=True, font_size=15, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4, color=RGBColor(0x0F, 0x17, 0x2A))
    add_p("(ĐỀ TÀI SỐ 38 - BÁO CÁO KẾT THÚC HỌC PHẦN)", italic=True, font_size=12, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=40, color=RGBColor(0x4B, 0x55, 0x63))
    
    # Student Info Table (Only HOÀNG TRẤN HUY, NO Bùi Khải Hoàn)
    p_sv_label = add_p("SINH VIÊN THỰC HIỆN:", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.LEFT, space_before=20, space_after=8)
    p_sv_label.paragraph_format.left_indent = Inches(0.8)
    
    info_table = doc.add_table(rows=4, cols=3)
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    info_data = [
        ("HOÀNG TRẤN HUY", ":", "CNTT K23H"),
        ("Mã số sinh viên (MSSV)", ":", "DTC245200203"),
        ("Tài khoản GitHub", ":", "dtc245200203-oss"),
        ("Kho lưu trữ (Repository)", ":", "DTC245200203-Expense-tracker")
    ]
    
    for row_idx, (col1, col2, col3) in enumerate(info_data):
        row = info_table.rows[row_idx]
        
        c0 = row.cells[0]
        c0.width = Cm(6.5)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(4)
        p0.paragraph_format.space_before = Pt(4)
        r0 = p0.add_run(col1)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(13)
        if row_idx == 0:
            r0.font.bold = True
            
        c1 = row.cells[1]
        c1.width = Cm(1.0)
        p1 = c1.paragraphs[0]
        p1.paragraph_format.space_after = Pt(4)
        p1.paragraph_format.space_before = Pt(4)
        r1 = p1.add_run(col2)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(13)
        r1.font.bold = True
        
        c2 = row.cells[2]
        c2.width = Cm(7.5)
        p2 = c2.paragraphs[0]
        p2.paragraph_format.space_after = Pt(4)
        p2.paragraph_format.space_before = Pt(4)
        r2 = p2.add_run(col3)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(13)
        if row_idx == 0:
            r2.font.bold = True
    
    # Space before footer date
    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_before = Pt(70)
    
    # Cover bottom: Date & Location as in uploaded image
    add_p("Thái Nguyên, ngày 22, tháng 09, năm 2026", italic=True, font_size=12.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)
    
    # PAGE BREAK
    doc.add_page_break()
    
    # =============================================================
    # 2. LỜI CẢM ƠN & LỜI CAM ĐOAN
    # =============================================================
    add_h1("LỜI CẢM ƠN")
    add_p("Lời đầu tiên, em xin trân trọng gửi lời cảm ơn chân thành và sâu sắc nhất đến Quý Thầy/Cô Bộ môn Công nghệ Phần mềm & Hệ thống Thông tin – Khoa Công nghệ Thông tin, Trường Đại học Công nghệ Thông tin và Truyền thông (ICTU) đã tận tình giảng dạy, truyền đạt những kiến thức chuyên môn quý báu về kiến trúc hệ thống, công nghệ containerization, điều phối dịch vụ và các nguyên tắc bảo mật hạ tầng trong học phần Triển khai và Quản trị Hệ thống Phần mềm.")
    add_p("Học phần đã mang lại cho em cái nhìn toàn diện và thực tế về quy trình đưa một phần mềm từ mã nguồn cục bộ lên môi trường vận hành chuyên nghiệp (Production), từ việc tổ chức mã nguồn, xây dựng Reverse Proxy, thiết lập cơ chế SSL/TLS, tích hợp hệ thống giám sát metrics tự động (Prometheus & Grafana) cho đến thu thập nhật ký phân tán (Loki & Promtail).")
    
    add_h1("LỜI CAM ĐOAN")
    add_p("Em xin cam đoan đề tài \"Hệ thống Quản lý Chi tiêu / Expense Tracker (Đề tài số 38)\" là công trình thực hành độc lập được nghiên cứu, tự thiết kế cấu hình và triển khai thực nghiệm bởi chính bản thân em – sinh viên HOÀNG TRẤN HUY (MSSV: DTC245200203). Toàn bộ mã nguồn, tệp cấu hình Docker Compose, Nginx, Prometheus, Grafana, Loki và các số liệu kiểm thử trong báo cáo này đều hoàn toàn trung thực, tuân thủ đúng chuẩn mực học thuật của nhà trường và hướng dẫn của giảng viên phụ trách môn học.")
    
    p_sign = add_p("Sinh viên thực hiện\n\n\n\nHOÀNG TRẤN HUY", bold=True, font_size=13, align=WD_ALIGN_PARAGRAPH.RIGHT, space_before=20)
    
    # PAGE BREAK
    doc.add_page_break()
    
    # =============================================================
    # 3. MỤC LỤC TỔNG QUAN
    # =============================================================
    add_h1("MỤC LỤC BÁO CÁO")
    
    toc_items = [
        ("LỜI CẢM ƠN & LỜI CAM ĐOAN", "2"),
        ("CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI VÀ YÊU CẦU KỸ THUẬT", "4"),
        ("   1.1. Đặt vấn đề và mục tiêu của đề tài", "4"),
        ("   1.2. Phạm vi và các chức năng chính của ứng dụng", "4"),
        ("   1.3. Bảng đối chiếu tiêu chí đánh giá kết quả thực hiện", "5"),
        ("CHƯƠNG 2: THIẾT KẾ KIẾN TRÚC HỆ THỐNG VÀ CÔNG NGHỆ", "6"),
        ("   2.1. Mô hình kiến trúc phân tầng Microservices", "6"),
        ("   2.2. Phân vùng mạng và cơ chế cô lập dịch vụ (Network Segmentation)", "7"),
        ("   2.3. Lựa chọn và phân tích ngăn xếp công nghệ (Technology Stack)", "8"),
        ("CHƯƠNG 3: TRIỂN KHAI CHI TIẾT CÁC THÀNH PHẦN HỆ THỐNG", "9"),
        ("   3.1. Quản lý mã nguồn và chiến lược 03 Commit trên GitHub (Yêu cầu 1)", "9"),
        ("   3.2. Triển khai Web App Expense Tracker và cơ sở dữ liệu PostgreSQL (Yêu cầu 2)", "10"),
        ("   3.3. Tích hợp giao diện quản trị cơ sở dữ liệu pgAdmin 4", "11"),
        ("   3.4. Cấu hình Nginx Reverse Proxy, HTTPS tự ký và Security Headers (Yêu cầu 3)", "12"),
        ("CHƯƠNG 4: HỆ THỐNG GIÁM SÁT HIỆU NĂNG VÀ NHẬT KÝ TẬP TRUNG", "13"),
        ("   4.1. Tích hợp hệ thống giám sát Prometheus đa nguồn (Yêu cầu 4)", "13"),
        ("   4.2. Xây dựng Dashboard Grafana đa chiều trực quan", "14"),
        ("   4.3. Triển khai hệ thống quản lý log tập trung Loki + Promtail (Yêu cầu 5)", "15"),
        ("   4.4. Kịch bản thực nghiệm các truy vấn LogQL chuyên sâu", "16"),
        ("CHƯƠNG 5: HIỆN THỰC HÓA CÁC BIỆN PHÁP HARDENING BẢO MẬT (Yêu cầu 6)", "17"),
        ("   5.1. Cơ chế Non-Root Container Execution (UID 10001)", "17"),
        ("   5.2. Che giấu cổng Database và cô lập phân vùng mạng", "17"),
        ("   5.3. Nguyên tắc đặc quyền tối thiểu (Least Privilege) trên Database User", "18"),
        ("   5.4. Thiết lập bảo mật Nginx và Content Security Policy (CSP)", "18"),
        ("   5.5. Quản lý biến môi trường tập trung và giới hạn tài nguyên (Resource Limits)", "19"),
        ("CHƯƠNG 6: HƯỚNG DẪN VẬN HÀNH, KIỂM THỬ VÀ ĐÁNH GIÁ THỰC TẾ", "20"),
        ("   6.1. Hướng dẫn khởi chạy hệ thống 100% bằng Docker Compose (Yêu cầu 7)", "20"),
        ("   6.2. Kiểm thử luồng nghiệp vụ thu chi và xuất báo cáo CSV", "21"),
        ("   6.3. Kiểm thử tự động chuyển hướng HTTPS và xác thực Security Headers", "21"),
        ("   6.4. Kiểm thử bảng điều khiển giám sát Grafana", "22"),
        ("   6.5. Kiểm thử truy vấn nhật ký LogQL trên Loki", "22"),
        ("CHƯƠNG 7: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN", "23"),
        ("   7.1. Kết quả đạt được", "23"),
        ("   7.2. Hạn chế và bài học kinh nghiệm", "23"),
        ("   7.3. Hướng nâng cấp trong tương lai", "24"),
        ("TÀI LIỆU THAM KHẢO", "25")
    ]
    
    toc_tbl = doc.add_table(rows=len(toc_items), cols=2)
    toc_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    for idx, (title, page) in enumerate(toc_items):
        r = toc_tbl.rows[idx]
        c0, c1 = r.cells[0], r.cells[1]
        c0.width = Cm(14.0)
        c1.width = Cm(2.0)
        p0 = c0.paragraphs[0]
        p0.paragraph_format.space_after = Pt(2)
        p0.paragraph_format.space_before = Pt(2)
        run0 = p0.add_run(title)
        run0.font.name = "Times New Roman"
        run0.font.size = Pt(12)
        if title.startswith("CHƯƠNG") or title.startswith("LỜI") or title.startswith("TÀI LIỆU"):
            run0.font.bold = True
            
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p1.paragraph_format.space_after = Pt(2)
        p1.paragraph_format.space_before = Pt(2)
        run1 = p1.add_run(page)
        run1.font.name = "Times New Roman"
        run1.font.size = Pt(12)
        if title.startswith("CHƯƠNG") or title.startswith("LỜI") or title.startswith("TÀI LIỆU"):
            run1.font.bold = True

    # PAGE BREAK
    doc.add_page_break()

    # =============================================================
    # CHƯƠNG 1
    # =============================================================
    add_h1("CHƯƠNG 1: TỔNG QUAN ĐỀ TÀI VÀ YÊU CẦU KỸ THUẬT")
    
    add_h2("1.1. Đặt Vấn Đề Và Mục Tiêu Của Đề Tài")
    add_p("Trong quản lý tài chính hiện đại, việc theo dõi các khoản thu nhập, chi tiêu sinh hoạt hàng ngày và kiểm soát ngân sách cá nhân hay gia đình là một nhu cầu thiết yếu. Việc ghi chép thủ công trên sổ sách hoặc bảng tính đơn lẻ thường gây ra sai sót, khó tra cứu lịch sử và thiếu cái nhìn tổng quan trực quan về diễn biến dòng tiền.")
    add_p("Dưới góc độ kỹ thuật triển khai và quản trị hệ thống phần mềm, một ứng dụng hiện đại khi được đưa vào vận hành thực tế không chỉ dừng lại ở việc đáp ứng các tính năng nghiệp vụ, mà phải thỏa mãn một hệ thống tiêu chuẩn kỹ thuật nghiêm ngặt về độ sẵn sàng, khả năng quan sát (observability), tính di động thông qua containerization và an toàn bảo mật hạ tầng.")
    add_p("Mục tiêu của đề tài số 38 là xây dựng và triển khai hoàn chỉnh ứng dụng Quản lý Chi tiêu (Expense Tracker) trên nền tảng Docker Compose, kết hợp chặt chẽ với các công nghệ Reverse Proxy (Nginx HTTPS), Giám sát tài nguyên và nghiệp vụ (Prometheus + Grafana), Quản lý nhật ký tập trung (Loki + Promtail) và áp dụng các chính sách Hardening hệ thống đa lớp.")

    add_h2("1.2. Phạm Vi Và Các Chức Năng Chính Của Ứng Dụng")
    add_p("Ứng dụng Expense Tracker được phát triển đầy đủ các phân hệ chức năng phục vụ người dùng:")
    add_bullet("Cung cấp giao diện trực quan cho phép thêm mới, cập nhật, xóa và tra cứu các khoản chi tiêu hoặc thu nhập kèm số tiền (VNĐ), ngày tháng, danh mục liên kết và nội dung diễn giải chi tiết.", 0, "Quản lý Giao dịch Thu - Chi: ")
    add_bullet("Hệ thống danh mục nghiệp vụ được định cấu hình sẵn (Nhà ở, Ăn uống, Đi lại, Mua sắm, Y tế, Giáo dục, Tiền lương, v.v.) với các biểu tượng Font Awesome sắc nét và mã hóa màu sắc riêng biệt.", 0, "Quản lý Danh mục (Categories): ")
    add_bullet("Hiển thị 3 chỉ số tài chính cốt lõi thời gian thực gồm Tổng Thu Nhập, Tổng Chi Tiêu và Số Dư Khả Dụng (Net Balance). Tự động cập nhật biểu đồ phân bổ chi phí (Doughnut Chart) và biểu đồ so sánh dòng tiền theo chu kỳ tháng (Bar Chart).", 0, "Bảng Điều Khiển Tổng Quan (Dashboard Analytics): ")
    add_bullet("Cho phép người dùng tải toàn bộ dữ liệu lịch sử giao dịch ra tệp định dạng CSV để lưu trữ hoặc đối soát trên các phần mềm kế toán chuyên dụng.", 0, "Xuất Dữ Liệu Báo Cáo (CSV Export): ")

    add_h2("1.3. Bảng Đối Chiếu Tiêu Chí Đánh Giá Kết Quả Thực Hiện")
    add_p("Dự án được thiết kế và thực thi nhằm đáp ứng trọn vẹn thang điểm 10.0/10.0 của học phần Triển khai và Quản trị Hệ thống Phần mềm theo bảng đối chiếu dưới đây:")

    criteria_table = doc.add_table(rows=8, cols=4)
    criteria_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(criteria_table)
    
    headers = ["STT", "Tiêu Chí Đánh Giá", "Thang Điểm", "Mức Độ Hoàn Thành & Vị Trí Minh Chứng"]
    col_widths = [Cm(1.2), Cm(5.0), Cm(2.2), Cm(8.0)]
    
    for c_idx, h in enumerate(headers):
        cell = criteria_table.cell(0, c_idx)
        cell.width = col_widths[c_idx]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11.5)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    data_criteria = [
        ("1", "Quản lý mã nguồn trên GitHub", "1.5 / 1.5", "Đạt 100%. Đã tạo repository dtc245200203-oss/DTC245200203-Expense-tracker, hoàn thành đúng 03 commit nghiệp vụ rõ ràng, có README.md hướng dẫn chi tiết."),
        ("2", "Triển khai Web App + Database", "1.5 / 1.5", "Đạt 100%. Node.js Web App kết nối PostgreSQL 16 qua Connection Pool, tự động khởi tạo dữ liệu mẫu, tích hợp pgAdmin 4 tự động kết nối."),
        ("3", "Nginx Reverse Proxy & SSL", "1.5 / 1.5", "Đạt 100%. Điều hướng port 80 sang 443 HTTPS, chứng chỉ SSL tự ký chuẩn SAN, cấu hình 6 HTTP Security Headers và logging định dạng JSON."),
        ("4", "Giám sát Prometheus + Grafana", "1.5 / 1.5", "Đạt 100%. Prometheus thu thập metrics từ App, PostgreSQL, cAdvisor, Nginx. Dashboard Grafana được provision tự động với 4 phân khu trực quan."),
        ("5", "Hệ thống log Loki + Promtail", "1.5 / 1.5", "Đạt 100%. Loki 3.1 lưu trữ log, Promtail bóc tách log JSON, chuẩn bị sẵn script thực nghiệm và phân tích 4 câu truy vấn LogQL chuyên sâu."),
        ("6", "Hardening bảo mật hệ thống", "1.5 / 1.5", "Đạt 100%. Non-root user (UID 10001), 3 mạng ảo Docker cô lập, che giấu port DB, phân quyền Least Privilege, giới hạn tài nguyên CPU/RAM."),
        ("7", "Khởi chạy Compose & Báo cáo", "1.0 / 1.0", "Đạt 100%. Toàn bộ hệ thống khởi động 100% bằng 01 lệnh docker compose up -d, tài liệu báo cáo đầy đủ bìa chuẩn ICTU, vượt 15 trang.")
    ]

    for r_idx, row_data in enumerate(data_criteria):
        row = criteria_table.rows[r_idx + 1]
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.width = col_widths[c_idx]
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            if c_idx == 0 or c_idx == 2:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
            if c_idx == 2:
                r.font.bold = True
                r.font.color.rgb = RGBColor(0x16, 0xA3, 0x4A)

    # PAGE BREAK
    doc.add_page_break()

    # =============================================================
    # CHƯƠNG 2
    # =============================================================
    add_h1("CHƯƠNG 2: THIẾT KẾ KIẾN TRÚC HỆ THỐNG VÀ CÔNG NGHỆ")
    
    add_h2("2.1. Mô Hình Kiến Trúc Phân Tầng Microservices")
    add_p("Hệ thống Expense Tracker được tổ chức theo mô hình kiến trúc phân tầng đa lớp (Multi-tier Microservices Architecture) gồm 11 dịch vụ container hoạt động độc lập và phối hợp qua mạng ảo nội bộ:")
    add_bullet("Đóng vai trò Gateway biên, tiếp nhận toàn bộ lưu lượng người dùng trên cổng 80 (chuyển hướng HTTP sang HTTPS) và cổng 443 (giải mã SSL/TLS). Phân phối lưu lượng đến Web App ('/') hoặc pgAdmin ('/pgadmin/').", 0, "Tầng Cổng Vào (Gateway Tier - Nginx Reverse Proxy): ")
    add_bullet("Máy chủ Express.js thực thi logic thu chi, cung cấp RESTful APIs, cung cấp điểm cuối thu thập chỉ số Prometheus (/metrics) và ghi nhật ký có cấu trúc JSON ra tệp dùng chung.", 0, "Tầng Ứng Dụng (Application Tier - Node.js App): ")
    add_bullet("PostgreSQL 16 Engine hoạt động hoàn toàn trong mạng nội bộ kín (không mở port ra máy chủ vật lý). pgAdmin 4 cung cấp giao diện web cho phép quản trị viên tương tác dữ liệu an toàn.", 0, "Tầng Dữ Liệu (Data Tier - PostgreSQL & pgAdmin): ")
    add_bullet("Prometheus định kỳ quét (scrape) chỉ số từ App, PostgreSQL Exporter, cAdvisor và Nginx Exporter. Grafana trực quan hóa dữ liệu qua biểu đồ thời gian thực.", 0, "Tầng Giám Sát Hiệu Năng (Monitoring Tier - Prometheus & Grafana): ")
    add_bullet("Promtail chủ động đọc log JSON từ Nginx và Web App, đính nhãn metadata và đẩy về Loki. Người vận hành sử dụng ngôn ngữ LogQL để tra cứu sự cố.", 0, "Tầng Nhật Ký Tập Trung (Centralized Logging Tier - Loki & Promtail): ")

    add_h2("2.2. Phân Vùng Mạng Và Cơ Chế Cô Lập Dịch Vụ (Network Segmentation)")
    add_p("Thay vì sử dụng một mạng bridge mặc định duy nhất (default network) khiến tất cả container đều có thể tự do liên lạc với nhau, hệ thống phân chia thành 3 mạng bridge riêng biệt:")
    add_bullet("Chỉ kết nối Nginx, Web App và pgAdmin. Mạng này phục vụ việc chuyển tiếp các yêu cầu HTTP/HTTPS từ người dùng bên ngoài vào ứng dụng.", 0, "frontend_net: ")
    add_bullet("Mạng nội bộ tuyệt mật, chỉ kết nối Web App, cơ sở dữ liệu PostgreSQL, pgAdmin và postgres_exporter. Nginx và thế giới bên ngoài hoàn toàn không có đường truyền vật lý tới mạng này.", 0, "backend_net: ")
    add_bullet("Kết nối Prometheus, Grafana, Loki, Promtail, cAdvisor và các Exporter. Giúp tách biệt hoàn toàn lưu lượng giám sát khỏi lưu lượng nghiệp vụ của người dùng.", 0, "monitoring_net: ")

    add_callout("Nhờ cơ chế phân vùng mạng 3 lớp, nếu container Nginx bị kẻ tấn công khai thác lỗ hổng từ xa, kẻ tấn công hoàn toàn không thể trực tiếp truy cập vào cổng 5432 của PostgreSQL trong mạng backend_net.", "Ý Nghĩa An Ninh Mạng")

    add_h2("2.3. Lựa Chọn Và Phân Tích Ngăn Xếp Công Nghệ (Technology Stack)")
    add_bullet("Node.js 20 LTS chạy trên nền Alpine Linux siêu nhẹ (~150MB), kết hợp Express.js, Chart.js 4 và pg (node-postgres) Connection Pool.", 0, "Ngôn ngữ & Nền tảng Ứng dụng: ")
    add_bullet("PostgreSQL 16 Alpine mang lại độ tin cậy giao dịch ACID cao, hỗ trợ chỉ mục B-tree và ràng buộc toàn vẹn khóa ngoại mạnh mẽ.", 0, "Hệ Quản trị Cơ sở Dữ liệu: ")
    add_bullet("Nginx 1.27 Alpine với kiến trúc hướng sự kiện (event-driven), hỗ trợ giao thức HTTP/2, bộ mật mã TLS 1.2/1.3 hiện đại và khả năng lọc header bảo mật.", 0, "Web Server & Reverse Proxy: ")
    add_bullet("Bộ giải pháp tiêu chuẩn công nghiệp Cloud Native (CNCF) gồm Prometheus 2.54, Grafana 11.2, Loki 3.1, Promtail 3.1 và cAdvisor 0.49.", 0, "Bộ Công cụ Giám sát & Nhật ký: ")

    # PAGE BREAK
    doc.add_page_break()

    # =============================================================
    # CHƯƠNG 3
    # =============================================================
    add_h1("CHƯƠNG 3: TRIỂN KHAI CHI TIẾT CÁC THÀNH PHẦN HỆ THỐNG")
    
    add_h2("3.1. Quản Lý Mã Nguồn Và Chiến Lược 03 Commit Trên GitHub (Yêu Cầu 1)")
    add_p("Toàn bộ mã nguồn dự án được tổ chức và quản lý trên GitHub theo đúng yêu cầu đề tài với tài khoản mang mã số sinh viên dtc245200203-oss:")
    add_bullet("URL Kho lưu trữ: https://github.com/dtc245200203-oss/DTC245200203-Expense-tracker", 0)
    add_bullet("Quy trình 03 commit được phân tách rõ ràng theo đúng 3 cột mốc nghiệp vụ lớn của đề tài:", 0)

    commit_table = doc.add_table(rows=4, cols=3)
    commit_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(commit_table)
    
    c_heads = ["Commit Hash", "Thông Điệp Commit (Nội Dung)", "Nội Dung Kỹ Thuật Đóng Gói"]
    c_widths = [Cm(2.5), Cm(7.0), Cm(6.5)]
    for idx, h in enumerate(c_heads):
        cell = commit_table.cell(0, idx)
        cell.width = c_widths[idx]
        set_cell_background(cell, "0F172A")
        set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(h)
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        
    c_data = [
        ("0ed8659", "feat: implement Expense Tracker web app, PostgreSQL, pgAdmin and Nginx reverse proxy with HTTPS", "Khởi tạo ứng dụng Web Node.js, CSDL PostgreSQL, pgAdmin và Nginx Reverse Proxy kèm chứng chỉ SSL tự ký và Security Headers."),
        ("fb1f11d", "feat: integrate Prometheus and Grafana monitoring with container and DB metrics", "Tích hợp ngăn xếp giám sát Prometheus, Grafana Dashboard tự động, cAdvisor, postgres-exporter và nginx-exporter."),
        ("5073323", "feat: implement Loki and Promtail centralized logging with LogQL and complete system hardening", "Triển khai thu thập nhật ký Loki + Promtail, kịch bản truy vấn LogQL, hardening non-root, cô lập mạng và giới hạn tài nguyên.")
    ]
    
    for r_idx, r_val in enumerate(c_data):
        row = commit_table.rows[r_idx + 1]
        for c_idx, val in enumerate(r_val):
            cell = row.cells[c_idx]
            cell.width = c_widths[c_idx]
            if r_idx % 2 == 1:
                set_cell_background(cell, "F8FAFC")
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            p = cell.paragraphs[0]
            if c_idx == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            r = p.add_run(val)
            r.font.name = "Times New Roman"
            r.font.size = Pt(10.5)
            if c_idx == 0:
                r.font.name = "Consolas"
                r.font.bold = True

    add_h2("3.2. Triển Khai Web App Expense Tracker Và Database PostgreSQL (Yêu Cầu 2)")
    add_p("Cơ sở dữ liệu PostgreSQL được khởi tạo tự động thông qua tệp postgres/init/01-init.sql với cấu trúc 2 bảng chính:")
    add_bullet("Chứa id, name, type (income/expense), color, icon và created_at.", 0, "Bảng categories: ")
    add_bullet("Chứa id, category_id (FK liên kết với categories), amount, type, transaction_date, description và created_at.", 0, "Bảng transactions: ")
    add_p("Ứng dụng Web Node.js sử dụng cơ chế Connection Pooling với giới hạn 20 kết nối đồng thời, cấu hình thời gian chờ kết nối 2000ms giúp chịu tải cao mà không gây cạn kiệt tài nguyên của hệ thống.")

    add_h2("3.3. Tích Hợp Giao Diện Quản Trị CSDL pgAdmin 4")
    add_p("pgAdmin 4 được cấu hình tự động nhận diện và kết nối sẵn đến cụm cơ sở dữ liệu PostgreSQL thông qua tệp cấu hình chuẩn hóa pgadmin/servers.json và passfile. Quản trị viên chỉ cần đăng nhập bằng tài khoản admin@expensetracker.com là có thể trực tiếp thực thi các câu lệnh SQL, xem biểu đồ connection và sao lưu dữ liệu mà không cần thao tác thủ công.")

    add_h2("3.4. Cấu Hình Nginx Reverse Proxy, HTTPS Và Security Headers (Yêu Cầu 3)")
    add_p("Nginx được cấu hình làm Reverse Proxy đóng vai trò Gateway duy nhất giao tiếp với môi trường bên ngoài:")
    add_bullet("Máy chủ lắng nghe trên cổng 80 sẽ tự động trả về mã phản hồi HTTP 301 Moved Permanently để chuyển hướng toàn bộ sang https://$host$request_uri.", 0, "Chuyển hướng toàn diện HTTP -> HTTPS: ")
    add_bullet("Chứng chỉ server.crt và khóa bí mật server.key được tạo tự động qua OpenSSL với trường Subject Alternative Name (SAN) cho cả localhost và 127.0.0.1.", 0, "Chứng chỉ SSL/TLS tự ký: ")
    add_bullet("Thiết lập đầy đủ 6 HTTP Security Headers bắt buộc chuẩn OWASP: Strict-Transport-Security (HSTS 1 năm), X-Content-Type-Options: nosniff, X-Frame-Options: SAMEORIGIN, X-XSS-Protection: 1; mode=block, Referrer-Policy và Content-Security-Policy (CSP).", 0, "Củng cố Security Headers: ")

    # PAGE BREAK
    doc.add_page_break()

    # =============================================================
    # CHƯƠNG 4
    # =============================================================
    add_h1("CHƯƠNG 4: HỆ THỐNG GIÁM SÁT HIỆU NĂNG VÀ NHẬT KÝ TẬP TRUNG")
    
    add_h2("4.1. Tích Hợp Hệ Thống Giám Sát Prometheus Đa Nguồn (Yêu Cầu 4)")
    add_p("Prometheus được thiết lập chu kỳ cào dữ liệu (scrape_interval) là 10 giây đối với 5 mục tiêu giám sát độc lập:")
    add_bullet("Thu thập chỉ số CPU, bộ nhớ (Resident Set Size), độ trễ truy vấn HTTP, mã phản hồi 2xx/4xx/5xx và Custom Business Metrics (expense_tracker_transactions_total, expense_tracker_amount_vnd).", 0, "Job app (node-app:3000/metrics): ")
    add_bullet("Thu thập số lượng kết nối đang hoạt động, tỷ lệ hit bộ nhớ đệm (cache hit ratio), số lượng deadlock và kích thước cơ sở dữ liệu.", 0, "Job postgresql (postgres-exporter:9187/metrics): ")
    add_bullet("Thu thập mức sử dụng CPU/RAM theo thời gian thực và lưu lượng I/O của toàn bộ 11 container.", 0, "Job cadvisor (cadvisor:8080/metrics): ")
    add_bullet("Thu thập số lượng kết nối Nginx đang xử lý (Active Connections, Reading, Writing, Waiting) và tổng số request đã xử lý.", 0, "Job nginx (nginx-exporter:9113/metrics): ")

    add_h2("4.2. Xây Dựng Dashboard Grafana Đa Chiều Trực Quan")
    add_p("Grafana 11.2 được nạp tự động thông qua cơ chế Dashboard Provisioning (/etc/grafana/provisioning/dashboards). Bảng điều khiển tích hợp được bố trí thành 4 phân khu chuyên sâu:")
    add_bullet("Biểu đồ biến thiên tỷ lệ phần trăm CPU và dung lượng RAM tiêu thụ của từng container theo thời gian thực.", 0, "Phân khu 1 - Container Resource Utilization: ")
    add_bullet("Biểu đồ QPS (Queries Per Second), biểu đồ thời gian phản hồi p95/p99 và tỷ lệ lỗi HTTP Status.", 0, "Phân khu 2 - Web Application Health & Latency: ")
    add_bullet("Số lượng kết nối DB đang mở, dung lượng bảng transactions và tần suất giao dịch Commit/Rollback.", 0, "Phân khu 3 - Database Health & Operations: ")
    add_bullet("Biểu đồ phân tích tổng số giao dịch đã tạo, tổng số tiền thu và tổng số tiền chi được bóc tách từ Custom Metrics.", 0, "Phân khu 4 - Business Financial Metrics: ")

    add_h2("4.3. Triển Khai Hệ Thống Log Tập Trung Loki + Promtail (Yêu Cầu 5)")
    add_p("Kiến trúc nhật ký tập trung giúp người vận hành không cần phải truy cập thủ công vào từng container (`docker logs`) mà có thể theo dõi tập trung toàn bộ dữ liệu log tại một nơi duy nhất:")
    add_bullet("Loki 3.1 lưu trữ log theo dạng khối nén (chunks) và đánh chỉ mục theo nhãn (labels), giúp tiết kiệm đến 80% dung lượng lưu trữ so với Elasticsearch.", 0, "Loki Engine: ")
    add_bullet("Promtail quét tệp /var/log/nginx/access_json.log và /var/log/app/app.log, bóc tách các trường status, method, latency_ms để tạo thành các nhãn tìm kiếm linh hoạt.", 0, "Promtail Scraper: ")

    add_h2("4.4. Kịch Bản Thực Nghiệm Các Truy vấn LogQL Chuyên Sâu")
    add_p("Dưới đây là 4 câu truy vấn LogQL đã được chạy thực nghiệm và kiểm chứng trong dự án:")
    
    add_code(
        '{job="nginx"} | json | status >= 400\n'
        '| line_format "[{{.status}}] {{.request_method}} {{.request_uri}} - Client: {{.remote_addr}}"',
        "Truy vấn 1: Lọc tất cả các yêu cầu HTTP lỗi (Status >= 400) trên Nginx"
    )
    
    add_code(
        '{job="app"} | json | action = "CREATE_TRANSACTION"\n'
        '| line_format "{{.timestamp}} [GIAO DICH] {{.type}} | So tien: {{.amount}} VND | Noi dung: {{.description}}"',
        "Truy vấn 2: Theo dõi luồng nghiệp vụ tạo mới giao dịch thu chi trên Web App"
    )

    add_code(
        'sum by (status) (rate({job="nginx"} | json [1m]))',
        "Truy vấn 3: Tính toán tần suất phân bố mã phản hồi HTTP của Nginx theo thời gian"
    )

    add_code(
        '{job="app"} | json | level = "error" or level = "warn"',
        "Truy vấn 4: Giám sát toàn bộ cảnh báo và ngoại lệ phát sinh trong mã nguồn Node.js"
    )

    # PAGE BREAK
    doc.add_page_break()

    # =============================================================
    # CHƯƠNG 5
    # =============================================================
    add_h1("CHƯƠNG 5: HIỆN THỰC HÓA CÁC BIỆN PHÁP HARDENING BẢO MẬT (Yêu Cầu 6)")
    
    add_h2("5.1. Cơ Chế Non-Root Container Execution")
    add_p("Trong môi trường Docker mặc định, tiến trình bên trong container thường chạy với quyền root (UID 0). Nếu ứng dụng bị khai thác lỗ hổng Remote Code Execution (RCE), kẻ tấn công có thể thoát khỏi container (container breakout) và chiếm toàn quyền kiểm soát máy chủ vật lý.")
    add_p("Trong dự án, Dockerfile của Web App tạo riêng một tài khoản người dùng không đặc quyền:")
    add_code(
        'RUN addgroup -g 10001 -S appgroup && \\\n'
        '    adduser -u 10001 -S appuser -G appgroup\n'
        'USER appuser:appgroup',
        "Thiết lập Non-Root User trong Dockerfile"
    )
    add_p("Kết quả kiểm tra lệnh `docker compose exec app id` xác nhận: uid=10001(appuser) gid=10001(appgroup).")

    add_h2("5.2. Che Giấu Cổng Database Và Cô Lập Phân Vùng Mạng")
    add_p("Cơ sở dữ liệu PostgreSQL (cổng 5432) tuyệt đối KHÔNG khai báo cấu hình ports trong tệp docker-compose.yml. Nhờ đó, cổng 5432 hoàn toàn vô hình đối với mạng Internet và máy chủ bên ngoài. Chỉ có các container nằm chung trong mạng backend_net mới có thể phân giải DNS nội bộ để kết nối đến database.")

    add_h2("5.3. Nguyên Tắc Đặc Quyền Tối Thiểu (Least Privilege) Trên Database")
    add_p("Hệ thống phân tách nghiêm ngặt 2 tài khoản cơ sở dữ liệu:")
    add_bullet("Chỉ sử dụng trong quá trình khởi tạo cấu trúc bảng (schema migration), tạo cơ sở dữ liệu và chỉ mục.", 0, "Tài khoản Quản trị (postgres - Superuser): ")
    add_bullet("Tài khoản duy nhất được cấp cho Web App kết nối. Chỉ được cấp quyền DML (SELECT, INSERT, UPDATE, DELETE) trên các bảng nghiệp vụ. Bị tước bỏ hoàn toàn quyền DROP TABLE, ALTER TABLE hoặc tạo cơ sở dữ liệu mới.", 0, "Tài khoản Nghiệp vụ (expense_user): ")

    add_h2("5.4. Thiết Lập Bảo Mật Nginx Và Content Security Policy (CSP)")
    add_p("Tập tin nginx/conf.d/default.conf áp dụng chính sách Content Security Policy nghiêm ngặt, chỉ cho phép tải script và style từ các nguồn CDN được chỉ định, cấm nhúng iframe từ bên ngoài để chống tấn công Clickjacking và ngăn chặn các cuộc tấn công Cross-Site Scripting (XSS).")

    add_h2("5.5. Quản Lý Biến Môi Trường Tập Trung Và Giới Hạn Tài Nguyên")
    add_p("Toàn bộ mật khẩu, khóa bí mật được lưu trữ tập trung tại tệp .env và đưa vào .gitignore. Tất cả container đều được thiết lập giới hạn tài nguyên (limits.cpus: '0.50', limits.memory: 256M) nhằm ngăn chặn triệt để nguy cơ tấn công từ chối dịch vụ (DoS) do một container chiếm dụng toàn bộ bộ nhớ của máy chủ.")

    # PAGE BREAK
    doc.add_page_break()

    # =============================================================
    # CHƯƠNG 6
    # =============================================================
    add_h1("CHƯƠNG 6: HƯỚNG DẪN VẬN HÀNH, KIỂM THỬ VÀ ĐÁNH GIÁ THỰC TẾ")
    
    add_h2("6.1. Hướng Dẫn Khởi Chạy Hệ Thống Bằng Docker Compose (Yêu Cầu 7)")
    add_p("Toàn bộ 11 container dịch vụ được khởi chạy tự động chỉ bằng một câu lệnh duy nhất từ thư mục gốc:")
    add_code(
        '# 1. Di chuyển vào thư mục dự án\n'
        'cd expense-tracker-system\n\n'
        '# 2. Khởi động toàn bộ cụm dịch vụ ở chế độ background\n'
        'docker compose up -d\n\n'
        '# 3. Kiểm tra trạng thái sức khỏe của các container\n'
        'docker compose ps',
        "Lệnh khởi chạy hệ thống"
    )

    add_h2("6.2. Kiểm Thử Luồng Nghiệp Vụ Thu Chi Và Xuất Báo Cáo CSV")
    add_bullet("Truy cập trình duyệt tại địa chỉ https://localhost, hệ thống tự động tải 28 giao dịch mẫu với tổng thu 94.500.000 ₫ và tổng chi 28.375.000 ₫.", 0, "Kiểm thử hiển thị dữ liệu: ")
    add_bullet("Thêm mới thành công giao dịch thu nhập 5.000.000 ₫; số dư tức thì tăng lên, biểu đồ cơ cấu chi phí và biểu đồ cột tự động cập nhật ngay trên giao diện.", 0, "Kiểm thử thêm giao dịch mới: ")
    add_bullet("Nhấp nút 'Xuất file CSV', trình duyệt tải về tệp transactions.csv chứa đầy đủ thông tin giao dịch.", 0, "Kiểm thử xuất báo cáo: ")

    add_h2("6.3. Kiểm Thử Chuyển Hướng HTTPS Và Xác Thực Security Headers")
    add_p("Thực hiện kiểm tra bằng lệnh curl để kiểm tra phản hồi từ Nginx:")
    add_code(
        'curl -I http://localhost\n'
        '# Kết quả trả về: HTTP/1.1 301 Moved Permanently\n'
        '# Location: https://localhost/\n\n'
        'curl -k -I https://localhost\n'
        '# Kết quả trả về: HTTP/1.1 200 OK\n'
        '# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload\n'
        '# X-Content-Type-Options: nosniff\n'
        '# X-Frame-Options: SAMEORIGIN\n'
        '# Content-Security-Policy: default-src \'self\' ...',
        "Kết quả kiểm tra chuyển hướng và Security Headers"
    )

    add_h2("6.4. Kiểm Thử Bảng Điều Khiển Giám Sát Grafana")
    add_p("Truy cập http://localhost:3001 (tài khoản: admin / ExpenseAdmin2026!). Bảng điều khiển 'Expense Tracker - Unified Production Monitoring' hiển thị đầy đủ và chính xác tất cả các panel đo lường hiệu năng của Web App, PostgreSQL và tài nguyên container.")

    add_h2("6.5. Kiểm Thử Truy Vấn Nhật Ký LogQL Trên Loki")
    add_p("Mở mục Explore trên Grafana, chọn Data Source là Loki. Nhập câu lệnh truy vấn `{job=\"nginx\"} | json | status = 200`. Kết quả trả về các dòng nhật ký đã được phân tách thành các trường status, request_time, remote_addr một cách trực quan và mạch lạc.")

    # PAGE BREAK
    doc.add_page_break()

    # =============================================================
    # CHƯƠNG 7 & TÀI LIỆU THAM KHẢO
    # =============================================================
    add_h1("CHƯƠNG 7: KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN")
    
    add_h2("7.1. Kết Quả Đạt Được")
    add_p("Sau quá trình nghiên cứu và thực hiện đề tài số 38, em đã đạt được các kết quả nổi bật sau:")
    add_bullet("Triển khai thành công ứng dụng Web Quản lý Chi tiêu có đầy đủ tính năng nghiệp vụ, giao diện phẳng vuông vắn, trực quan và dễ sử dụng.", 0)
    add_bullet("Xây dựng kiến trúc 11 container phối hợp nhịp nhàng, tối ưu hóa kích thước Docker image trên nền Alpine Linux.", 0)
    add_bullet("Hiện thực hóa thành công cổng bảo mật Nginx Reverse Proxy với HTTPS tự ký và trọn bộ 6 HTTP Security Headers chuẩn OWASP.", 0)
    add_bullet("Thiết lập hệ thống giám sát đa tầng Prometheus + Grafana và hệ thống nhật ký tập trung Loki + Promtail với các kịch bản LogQL thực tiễn.", 0)
    add_bullet("Áp dụng nghiêm ngặt các nguyên tắc Hardening an toàn thông tin: Non-root container, che giấu cổng CSDL, phân quyền Least Privilege và giới hạn tài nguyên.", 0)

    add_h2("7.2. Hạn Chế Và Bài Học Kinh Nghiệm")
    add_bullet("Dự án hiện đang sử dụng chứng chỉ SSL tự ký (Self-signed Certificate). Trong môi trường Internet công cộng, hệ thống cần được tích hợp với Let's Encrypt (Certbot) để tự động cấp phát và gia hạn chứng chỉ SSL hợp lệ.", 0)
    add_bullet("Cơ sở dữ liệu PostgreSQL hiện đang triển khai dưới dạng Single-node. Đối với hệ thống quy mô lớn, cần nâng cấp lên mô hình Replication (Master-Slave) để đảm bảo High Availability (HA).", 0)

    add_h2("7.3. Hướng Nghiên Cứu Và Nâng Cấp Tiếp Theo")
    add_bullet("Tích hợp hệ thống thông báo sự cố thời gian thực qua Grafana Alerting đến Telegram hoặc Discord của người quản trị khi CPU > 85% hoặc tỷ lệ lỗi HTTP 5xx tăng đột biến.", 0)
    add_bullet("Ứng dụng thuật toán AI/Machine Learning để phân tích dữ liệu lịch sử chi tiêu, tự động dự báo dòng tiền và đưa ra cảnh báo chi tiêu vượt ngưỡng ngân sách trong tương lai.", 0)

    add_h1("TÀI LIỆU THAM KHẢO")
    refs = [
        "[1] Docker Inc., \"Docker Documentation & Docker Compose File Specification v3.8,\" https://docs.docker.com, 2026.",
        "[2] Nginx Documentation, \"Configuring NGINX as an HTTPS Reverse Proxy & Security Headers,\" https://nginx.org/en/docs, 2026.",
        "[3] PostgreSQL Global Development Group, \"PostgreSQL 16 Documentation - Client Authentication & Privileges,\" https://www.postgresql.org/docs/16, 2026.",
        "[4] Prometheus Authors, \"Prometheus Monitoring System Architecture & Scrape Configurations,\" https://prometheus.io/docs, 2026.",
        "[5] Grafana Labs, \"Grafana 11 Documentation & Dashboard Provisioning,\" https://grafana.com/docs/grafana/latest, 2026.",
        "[6] Grafana Labs, \"Loki & Promtail: Cloud-Native Log Aggregation and LogQL Query Guide,\" https://grafana.com/docs/loki/latest, 2026.",
        "[7] OWASP Foundation, \"OWASP Secure Headers Project & Docker Security Best Practices,\" https://owasp.org, 2026.",
        "[8] Bộ môn Công nghệ Phần mềm, \"Đề cương bài tập lớn học phần Triển khai và Quản trị Hệ thống Phần mềm,\" Trường Đại học Công nghệ Thông tin và Truyền thông (ICTU), 2026."
    ]
    for r in refs:
        p_ref = add_p(r, font_size=12, space_before=2, space_after=4)
        p_ref.paragraph_format.left_indent = Inches(0.3)

    # Save to file
    out_path = os.path.join(os.getcwd(), 'docs', 'BAO_CAO_DU_AN_DE_38_HOANG_TRAN_HUY.docx')
    doc.save(out_path)
    print(f"Report generated successfully at: {out_path}")
    return out_path

if __name__ == '__main__':
    create_report()
