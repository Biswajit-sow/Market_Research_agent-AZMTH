from fpdf import FPDF
import time
import os
import re

class ReportService:
    @staticmethod
    def clean_text_for_pdf(text):
        if not text:
            return "Analysis content currently unavailable."

        
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        
        text = text.replace('**', '').replace('###', '').replace('##', '').replace('*', '').replace('#', '')

        
        replacements = {
            '\u2013': '-', '\u2014': '-', '\u2018': "'", '\u2019': "'",
            '\u201c': '"', '\u201d': '"', '\u2022': '-', '\u2026': '...'
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
       
        return text.encode('ascii', 'ignore').decode('ascii').strip()

    @staticmethod
    def create_pdf(analysis_text):
        content = ReportService.clean_text_for_pdf(analysis_text)
        timestamp = int(time.time())
        filename = f"Strategy_Report_{timestamp}.pdf"
        filepath = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), filename)

        
        PAGE_W      = 210   
        LEFT_M      = 20
        RIGHT_M     = 20
        TOP_M       = 20
        BOTTOM_M    = 20
        
        EFF_W       = PAGE_W - LEFT_M - RIGHT_M   # 170 mm

        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_margins(left=LEFT_M, top=TOP_M, right=RIGHT_M)
        pdf.set_auto_page_break(auto=True, margin=BOTTOM_M)
        pdf.add_page()

        
        def reset_x():
            """Snap cursor back to left margin before every multi_cell."""
            pdf.set_x(LEFT_M)

        
        pdf.set_fill_color(15, 23, 42)
        pdf.rect(0, 0, PAGE_W, 45, 'F')

        pdf.set_y(15)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", 'B', 18)
        reset_x()
        pdf.multi_cell(w=EFF_W, h=10, text="MARKET INTELLIGENCE STRATEGY", align='C')

        pdf.set_font("Helvetica", 'I', 8)
        reset_x()
        pdf.multi_cell(w=EFF_W, h=8, text=f"Document ID: {timestamp} | Direct Asset Dispatch", align='C')

        pdf.set_y(55)
        pdf.set_text_color(30, 41, 59)

        
        paragraphs = content.split('\n')

        for para in paragraphs:
            line = para.strip()

            if not line:
                pdf.ln(5)
                continue

           
            is_header = (
                len(line) < 80
                and (
                    line.endswith(':')
                    or line.isupper()
                    or (line[0].isdigit() and len(line) > 2 and line[1] == '.')
                )
            )

            if is_header:
                pdf.ln(2)
                pdf.set_font("Helvetica", 'B', 11)
                pdf.set_text_color(37, 99, 235)   # Corporate Blue
                reset_x()
                pdf.multi_cell(w=EFF_W, h=8, text=line, align='L')

                
                line_y = pdf.get_y()
                pdf.set_draw_color(226, 232, 240)
                pdf.line(LEFT_M, line_y, LEFT_M + 30, line_y)

                pdf.set_text_color(30, 41, 59)
                pdf.ln(2)
            else:
                pdf.set_font("Helvetica", '', 10)
                pdf.set_text_color(30, 41, 59)
                reset_x()
                pdf.multi_cell(w=EFF_W, h=6, text=line, align='L')
                pdf.ln(1)

        
        try:
            pdf.output(filepath)
            return filepath
        except Exception as e:
            print(f"Server-Side Rendering Exception: {e}")
            raise e





        
'''
    @staticmethod
    def create_pdf(analysis_text):
        clean_content = ReportService.clean_text_for_pdf(analysis_text)
        
        timestamp = int(time.time())
        filename = f"Strategy_Report_{timestamp}.pdf"
        
        # Dynamic path handling
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(current_dir)
        filepath = os.path.join(project_root, filename)

        # Standard Portrait A4 configuration



        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_margins(left=20, top=20, right=20) # 20mm professional margins
        pdf.set_auto_page_break(auto=True, margin=25)
        pdf.add_page()
        
        # CORPORATE HEADER BACKGROUND
        pdf.set_fill_color(15, 23, 42) # Slate-900 (Navy)
        pdf.rect(0, 0, 210, 45, 'F')
        
        # HEADER TEXT (White)
        pdf.set_y(15)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", 'B', 22)
        pdf.cell(0, 10, "STRATEGIC INTELLIGENCE REPORT", ln=True, align='C')
        
        pdf.set_font("Helvetica", 'I', 10)
        pdf.set_y(26)
        pdf.cell(0, 10, f"Generated Strategy ID: {timestamp} | Direct Competitive Research", ln=True, align='C')
        
        # Space below header
        pdf.set_y(55)
        


        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        
        # CORPORATE IDENTITY HEADER
        pdf.set_fill_color(15, 23, 42)
        pdf.rect(0, 0, 210, 38, 'F')
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", 'B', 16)
        pdf.cell(0, 15, "PROPRIETARY MARKET INTELLIGENCE DOCUMENT", ln=True, align='C')
        pdf.set_font("Helvetica", 'I', 8)
        pdf.cell(0, 5, f"Report ID: {timestamp} | Classification: Confidential Strategic Asset", ln=True, align='C')
        
        pdf.ln(25)
        pdf.set_text_color(30, 41, 59)
        # CONTENT ENGINE
        # Splitting into blocks helps distinguish headers from body text
        blocks = clean_content.split('\n')
        
        for block in blocks:
            trimmed = block.strip()
            if not trimmed:
                pdf.ln(4)
                continue
                
            # DESIGN LOGIC: If block is a Header (all caps, or ends in colon, or numbered)
            is_header = len(trimmed) < 100 and (trimmed.endswith(':') or trimmed.isupper() or (trimmed[0].isdigit() and '.' in trimmed[:3]))
            
            if is_header:
                pdf.ln(5) # Top spacing for sections
                pdf.set_font("Helvetica", 'B', 12)
                pdf.set_text_color(37, 99, 235) # High-Impact Blue (Corporate blue)
                
                # '0' width auto-wraps within margins
                pdf.multi_cell(0, 8, trimmed, align='L')
                
                # Visual separator line under headers
                pdf.set_draw_color(226, 232, 240) # Slate-200 (light gray)
                pdf.line(20, pdf.get_y(), 190, pdf.get_y())
                
                pdf.set_font("Helvetica", '', 10) # Reset to body text style
                pdf.set_text_color(30, 41, 59)    # Slate-700
                pdf.ln(2)
            else:
                # DESIGN LOGIC: Body Paragraphs
                pdf.set_font("Helvetica", '', 10)
                pdf.set_text_color(51, 65, 85)
                # Setting width to 0 ensures full alignment with the right margin
                pdf.multi_cell(0, 6, trimmed, align='L')
                pdf.ln(1) # Subtle space between wrapped blocks
            
        try:
            pdf.output(filepath)
            return filepath
        except Exception as e:
            print(f"Error during PDF export: {e}")
            raise e

            '''

    