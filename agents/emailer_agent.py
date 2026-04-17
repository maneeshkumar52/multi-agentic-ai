import smtplib
import mimetypes
from email.message import EmailMessage
from pathlib import Path
from utils import Config, Logger

class EmailerAgent:
    def __init__(self):
        self.logger = Logger("EmailerAgent")

    def send_email(self, to, subject, body, attachments=None):
        """Send email with attachments using modern EmailMessage API"""
        try:
            self.logger.log_agent_activity("EmailerAgent", f"Sending email to: {to}")

            # Create message
            msg = EmailMessage()
            msg['From'] = Config.FROM_EMAIL
            msg['To'] = to
            msg['Subject'] = subject

            # Set HTML body
            msg.set_content(body, subtype='html')

            # Filter and attach files
            if attachments:
                attachments = [a for a in attachments if a is not None and Path(a).exists()]
                for attachment in attachments:
                    self._attach_file_smtp(msg, attachment)

            # Send email
            with smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT) as server:
                server.starttls()
                server.login(Config.SMTP_USER, Config.SMTP_PASSWORD)
                server.send_message(msg)

            self.logger.log_agent_activity("EmailerAgent", f"Email sent successfully to: {to}")
            return {
                'status': 'success',
                'recipient': to,
                'attachments_count': len(attachments) if attachments else 0
            }

        except Exception as e:
            self.logger.log_error(f"Email sending failed: {e}")
            return {
                'status': 'error',
                'recipient': to,
                'error': str(e)
            }

    def send_search_results_email(self, compliance_result, recipient, attachments=None):
        """Send professional email with search results and compliance badge"""
        try:
            if not compliance_result or not compliance_result.get('approved'):
                return {
                    'status': 'error',
                    'error': 'Cannot send email: content not approved'
                }

            results = compliance_result.get('cleaned_results', [])
            ai_summary = compliance_result.get('validated_summary')
            quality_score = compliance_result.get('quality_score', 0)

            # Generate HTML body
            html_body = self._generate_html_body(compliance_result, results, ai_summary, quality_score)

            subject = f"Search Results Report - Quality Score: {quality_score:.2f}"

            return self.send_email(recipient, subject, html_body, attachments)

        except Exception as e:
            self.logger.log_error(f"Search results email failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def _generate_html_body(self, compliance_result, results, ai_summary, quality_score):
        """Generate professional HTML email body"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #1f77b4; border-bottom: 2px solid #1f77b4; padding-bottom: 20px; margin-bottom: 30px; }}
                .compliance-badge {{ background-color: #28a745; color: white; padding: 10px 20px; border-radius: 20px; display: inline-block; margin: 20px 0; }}
                .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
                .result {{ border: 1px solid #dee2e6; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .result h3 {{ margin-top: 0; color: #1f77b4; }}
                .result a {{ color: #007bff; text-decoration: none; }}
                .result a:hover {{ text-decoration: underline; }}
                .footer {{ text-align: center; color: #6c757d; font-size: 12px; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔍 Multi-Agent Search Results</h1>
                    <p>Enterprise-grade research with compliance validation</p>
                </div>

                <div class="compliance-badge">
                    ✓ Content Validated & Citation-Checked
                </div>

                <div class="summary">
                    <h2>Quality Metrics</h2>
                    <p><strong>Quality Score:</strong> {quality_score:.2f}/1.00</p>
                    <p><strong>Validated Sources:</strong> {len(results)}</p>
                    <p><strong>Compliance Status:</strong> Approved</p>
                </div>
        """

        if ai_summary:
            html += f"""
                <div class="summary">
                    <h2>AI Summary</h2>
                    <p>{ai_summary}</p>
                </div>
            """

        if results:
            html += """
                <h2>Search Results</h2>
            """

            for i, result in enumerate(results, 1):
                html += f"""
                <div class="result">
                    <h3>{i}. {result['title']}</h3>
                    <p><strong>Source:</strong> <a href="{result['url']}" target="_blank">{result['url']}</a></p>
                    <p>{result['snippet']}</p>
                </div>
                """

        html += """
                <div class="footer">
                    <p>This report was generated by the Multi-Agent Pipeline with enterprise-grade compliance validation.</p>
                    <p>For questions or concerns, please contact the system administrator.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def _attach_file_smtp(self, msg, filepath):
        """Attach file to email message"""
        try:
            path = Path(filepath)
            if not path.exists():
                return

            # Guess MIME type
            mime_type, _ = mimetypes.guess_type(str(path))
            if mime_type is None:
                mime_type = 'application/octet-stream'

            main_type, sub_type = mime_type.split('/', 1)

            # Read file
            with open(path, 'rb') as f:
                file_data = f.read()

            # Add attachment
            msg.add_attachment(
                file_data,
                maintype=main_type,
                subtype=sub_type,
                filename=path.name
            )

        except Exception as e:
            self.logger.log_error(f"Failed to attach file {filepath}: {e}")