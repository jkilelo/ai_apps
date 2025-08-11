"""
Test Reporting Components for UI Testing Framework v2
"""

from .html_reporter import HTMLReporter
from .pdf_reporter import PDFReporter
from .failure_analyzer import FailureAnalyzer
from .metrics_dashboard import MetricsDashboard

__all__ = [
    'HTMLReporter',
    'PDFReporter',
    'FailureAnalyzer',
    'MetricsDashboard',
]