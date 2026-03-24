"""
╔═══════════════════════════════════════════════════════════════════╗
║  JOBPILOT — PDF Generator Service                                ║
║                                                                   ║
║  Converts tailored resume/cover letter content into PDF files.    ║
║  Uses Jinja2 templates + WeasyPrint for HTML-to-PDF conversion.   ║
║                                                                   ║
║  TWO RESUME TEMPLATES:                                            ║
║  1. Original Style — matches Rishi's current LaTeX-like format   ║
║  2. Clean Template — modern, clean professional layout            ║
║                                                                   ║
║  USAGE:                                                           ║
║    from services.pdf_generator import pdf_generator               ║
║    path = await pdf_generator.generate_resume_pdf(content, ...)  ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
from datetime import datetime
from typing import Optional
from jinja2 import Environment, FileSystemLoader
from utils.logger import logger
from utils.helpers import sanitize_filename

# Directory paths
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
RESUME_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "resumes")
COVER_LETTER_OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cover_letters")


class PDFGeneratorService:
    """
    Generates PDF documents from structured content using HTML templates.
    
    The flow is:
    1. Take structured content (from AI service)
    2. Render it into an HTML template (Jinja2)
    3. Convert HTML to PDF (WeasyPrint)
    4. Save to data/ directory
    """

    def __init__(self):
        """Set up Jinja2 template environment."""
        self.env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=True,
        )
        # Ensure output directories exist
        os.makedirs(RESUME_OUTPUT_DIR, exist_ok=True)
        os.makedirs(COVER_LETTER_OUTPUT_DIR, exist_ok=True)

    async def generate_resume_pdf(
        self,
        content: dict,
        template_style: str,
        job_title: str,
        company_name: str,
        candidate_name: str = "Rishi Raj",
    ) -> str:
        """
        Generate a resume PDF from tailored content.
        
        Args:
            content: Structured resume dict (from resume_tailor)
            template_style: "original" or "clean"
            job_title: For the filename
            company_name: For the filename
            candidate_name: Candidate's name for the resume header
        
        Returns:
            str: File path to the generated PDF
        """
        try:
            # Select template based on style
            template_file = (
                "resume_original.html" if template_style == "original"
                else "resume_clean.html"
            )
            template = self.env.get_template(template_file)

            # Render HTML with the tailored content
            html_content = template.render(
                name=candidate_name,
                summary=content.get("professional_summary", ""),
                skills=content.get("skills_reordered", []),
                experience=content.get("experience", []),
                education=content.get("education", {}),
                achievements=content.get("achievements", []),
            )

            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_company = sanitize_filename(company_name)
            safe_title = sanitize_filename(job_title)
            filename = f"resume_{safe_company}_{safe_title}_{template_style}_{timestamp}.pdf"
            filepath = os.path.join(RESUME_OUTPUT_DIR, filename)

            # Convert HTML to PDF using WeasyPrint
            # NOTE: WeasyPrint must be installed with its system dependencies
            # On Ubuntu: apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
            try:
                from weasyprint import HTML
                HTML(string=html_content).write_pdf(filepath)
            except ImportError:
                # Fallback: save as HTML if WeasyPrint not installed
                filepath = filepath.replace(".pdf", ".html")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.warning(
                    "WeasyPrint not installed — saved as HTML. "
                    "Install with: pip install weasyprint"
                )

            logger.info(f"Resume PDF generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise

    async def generate_cover_letter_pdf(
        self,
        content: dict,
        job_title: str,
        company_name: str,
        candidate_name: str = "Rishi Raj",
    ) -> str:
        """
        Generate a cover letter PDF.
        
        Args:
            content: Cover letter dict (from cover_letter_service)
            job_title: For the filename
            company_name: For the filename
            candidate_name: For the header
        
        Returns:
            str: File path to the generated PDF
        """
        try:
            # Simple, clean cover letter HTML
            html_content = f"""<!DOCTYPE html>
<html>
<head>
<style>
    body {{
        font-family: 'Georgia', 'Times New Roman', serif;
        max-width: 700px; margin: 40px auto; padding: 40px;
        line-height: 1.7; color: #1a1a1a; font-size: 11pt;
    }}
    .header {{ margin-bottom: 30px; }}
    .header h1 {{ font-size: 16pt; margin: 0; color: #0a0a0a; }}
    .header p {{ margin: 2px 0; color: #444; font-size: 10pt; }}
    .date {{ margin: 20px 0; color: #555; font-size: 10pt; }}
    .greeting {{ margin-bottom: 15px; }}
    .body p {{ margin-bottom: 15px; text-align: justify; }}
    .closing {{ margin-top: 30px; }}
</style>
</head>
<body>
    <div class="header">
        <h1>{candidate_name}</h1>
        <p>rishiraj727909.work@gmail.com | +91-8210239176</p>
    </div>
    <div class="date">{datetime.now().strftime('%B %d, %Y')}</div>
    <div class="greeting">{content.get('greeting', 'Dear Hiring Manager,')}</div>
    <div class="body">
        {''.join(f'<p>{para}</p>' for para in content.get('body', '').split(chr(10)+chr(10)) if para.strip())}
    </div>
    <div class="closing">{content.get('closing', f'Best regards,<br>{candidate_name}').replace(chr(10), '<br>')}</div>
</body>
</html>"""

            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_company = sanitize_filename(company_name)
            filename = f"cover_letter_{safe_company}_{timestamp}.pdf"
            filepath = os.path.join(COVER_LETTER_OUTPUT_DIR, filename)

            try:
                from weasyprint import HTML
                HTML(string=html_content).write_pdf(filepath)
            except ImportError:
                filepath = filepath.replace(".pdf", ".html")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.warning("WeasyPrint not installed — saved as HTML.")

            logger.info(f"Cover letter PDF generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Cover letter PDF generation failed: {e}")
            raise


# ─────────────────────────────────────
# Singleton instance
# ─────────────────────────────────────
pdf_generator = PDFGeneratorService()
