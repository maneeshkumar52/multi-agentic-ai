import uuid
import datetime
from utils import Logger
from agents import WebSearchAgent, ComplianceGuardAgent, DocumentFormatterAgent, EmailerAgent

class PipelineOrchestrator:
    def __init__(self):
        self.logger = Logger("PipelineOrchestrator")

        # Initialize all agents
        try:
            self.web_search_agent = WebSearchAgent()
            self.compliance_guard = ComplianceGuardAgent()
            self.document_formatter = DocumentFormatterAgent()
            self.emailer_agent = EmailerAgent()

            self.logger.log_agent_activity("PipelineOrchestrator", "All agents initialized successfully")
        except Exception as e:
            self.logger.log_error(f"Agent initialization failed: {e}")
            raise

    def validate_configuration(self):
        """Validate system configuration before running pipeline"""
        from utils import Config

        errors = []

        # Check basic config
        config_errors = Config.validate()
        errors.extend(config_errors)

        # Check Azure OpenAI (optional)
        if not Config.is_azure_openai_configured():
            self.logger.log_agent_activity("PipelineOrchestrator", "Azure OpenAI not configured - AI summaries disabled")

        # Check output directory
        if not Config.OUTPUT_DIR.exists():
            try:
                Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create output directory: {e}")

        return errors

    def run_pipeline(self, query, num_results=5, send_email=False, recipient_email=None, filename_prefix='search_report'):
        """Execute the complete multi-agent pipeline"""
        pipeline_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()

        self.logger.log_agent_activity("PipelineOrchestrator", f"Starting pipeline {pipeline_id} for query: {query}")

        try:
            # Validate configuration
            config_errors = self.validate_configuration()
            if config_errors:
                return {
                    'pipeline_id': pipeline_id,
                    'timestamp': timestamp,
                    'query': query,
                    'status': 'error',
                    'error': 'Configuration validation failed',
                    'config_errors': config_errors
                }

            stages = {}

            # STAGE 1: Web Search
            self.logger.log_agent_activity("PipelineOrchestrator", "Stage 1: Web Search")
            web_result = self.web_search_agent.search(query, num_results)
            stages['web_search'] = web_result

            if web_result['status'] != 'success':
                return {
                    'pipeline_id': pipeline_id,
                    'timestamp': timestamp,
                    'query': query,
                    'status': 'error',
                    'stage': 'web_search',
                    'error': 'Web search failed',
                    'stages': stages
                }

            # STAGE 2: Compliance Guard (CRITICAL)
            self.logger.log_agent_activity("PipelineOrchestrator", "Stage 2: Compliance Validation")
            compliance_result = self.compliance_guard.validate(web_result)
            stages['compliance_guard'] = compliance_result

            if not compliance_result['approved']:
                self.logger.log_agent_activity("PipelineOrchestrator", f"Pipeline rejected: {compliance_result['issues']}")
                return {
                    'pipeline_id': pipeline_id,
                    'timestamp': timestamp,
                    'query': query,
                    'status': 'rejected',
                    'stage': 'compliance_guard',
                    'issues': compliance_result['issues'],
                    'quality_score': compliance_result['quality_score'],
                    'stages': stages,
                    'compliance_passed': False
                }

            # STAGE 3: Document Formatting
            self.logger.log_agent_activity("PipelineOrchestrator", "Stage 3: Document Formatting")
            doc_result = self.document_formatter.format_documents(
                compliance_result,  # Pass validated content
                query,
                filename_prefix
            )
            stages['document_formatting'] = doc_result

            # STAGE 4: Email (optional)
            email_result = None
            if send_email and recipient_email:
                self.logger.log_agent_activity("PipelineOrchestrator", "Stage 4: Email Delivery")
                email_result = self.emailer_agent.send_search_results_email(
                    compliance_result,  # Pass validated content
                    recipient_email,
                    doc_result.get('files_created', [])
                )
                stages['email'] = email_result

            # Determine overall status
            if doc_result['status'] == 'success':
                status = 'success'
            else:
                status = 'partial_success'

            result = {
                'pipeline_id': pipeline_id,
                'timestamp': timestamp,
                'query': query,
                'status': status,
                'stages': stages,
                'compliance_passed': True
            }

            self.logger.log_agent_activity("PipelineOrchestrator", f"Pipeline {pipeline_id} completed: {status}")
            return result

        except Exception as e:
            self.logger.log_error(f"Pipeline execution failed: {e}")
            return {
                'pipeline_id': pipeline_id,
                'timestamp': timestamp,
                'query': query,
                'status': 'error',
                'error': str(e),
                'stages': stages if 'stages' in locals() else {}
            }

    def get_pipeline_summary(self, result):
        """Generate a human-readable summary of pipeline results"""
        if not result:
            return "No pipeline result available"

        summary = []
        summary.append(f"Pipeline ID: {result.get('pipeline_id', 'Unknown')}")
        summary.append(f"Query: {result.get('query', 'Unknown')}")
        summary.append(f"Status: {result.get('status', 'Unknown')}")
        summary.append(f"Timestamp: {result.get('timestamp', 'Unknown')}")

        stages = result.get('stages', {})
        if stages:
            summary.append("\nStages:")

            if 'web_search' in stages:
                ws = stages['web_search']
                summary.append(f"  Web Search: {ws.get('status', 'Unknown')} ({ws.get('total_results', 0)} results)")

            if 'compliance_guard' in stages:
                cg = stages['compliance_guard']
                summary.append(f"  Compliance Guard: {'Approved' if cg.get('approved') else 'Rejected'} (Score: {cg.get('quality_score', 0):.2f})")

            if 'document_formatting' in stages:
                df = stages['document_formatting']
                files = df.get('files_created', [])
                summary.append(f"  Document Formatting: {df.get('status', 'Unknown')} ({len(files)} files)")

            if 'email' in stages:
                em = stages['email']
                summary.append(f"  Email: {em.get('status', 'Unknown')}")

        if result.get('compliance_passed'):
            summary.append("\n✓ Pipeline completed with compliance validation")
        else:
            issues = result.get('issues', [])
            if issues:
                summary.append(f"\n✗ Pipeline rejected: {', '.join(issues)}")

        return '\n'.join(summary)