"""Professional marketing report generation with visualizations"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import base64
from io import BytesIO
import asyncio
from decimal import Decimal

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
import numpy as np

from .database import (
    db, Campaign, AutomationTask, PerformanceMetrics, 
    ROITracking, AIDecisionHistory, TaskType
)
from .database_utils import generate_roi_report


class ReportType:
    """Report type constants"""
    WEEKLY_SUMMARY = "weekly_summary"
    CAMPAIGN_OPTIMIZATION = "campaign_optimization"
    ROI_ANALYSIS = "roi_analysis"
    EXECUTIVE_DASHBOARD = "executive_dashboard"


class ChartGenerator:
    """Generate Plotly charts for reports"""
    
    # Professional color palette
    COLORS = {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e',
        'success': '#2ca02c',
        'danger': '#d62728',
        'warning': '#ff9800',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#343a40'
    }
    
    CHART_LAYOUT = {
        'font': {'family': 'Arial, sans-serif', 'size': 12},
        'margin': {'l': 50, 'r': 50, 't': 50, 'b': 50},
        'paper_bgcolor': 'white',
        'plot_bgcolor': 'white',
        'showlegend': True,
        'hovermode': 'x unified'
    }
    
    @staticmethod
    def performance_trend_chart(data: List[Dict[str, Any]], metrics: List[str]) -> str:
        """Create a performance trend line chart"""
        df = pd.DataFrame(data)
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('Campaign Performance Metrics', 'Conversion Metrics'),
            row_heights=[0.6, 0.4]
        )
        
        # Top chart - Traffic metrics
        if 'impressions' in metrics:
            fig.add_trace(
                go.Scatter(
                    x=df['date'], y=df['impressions'],
                    name='Impressions',
                    line=dict(color=ChartGenerator.COLORS['primary'], width=2)
                ),
                row=1, col=1
            )
        
        if 'clicks' in metrics:
            fig.add_trace(
                go.Scatter(
                    x=df['date'], y=df['clicks'],
                    name='Clicks',
                    line=dict(color=ChartGenerator.COLORS['secondary'], width=2),
                    yaxis='y2'
                ),
                row=1, col=1
            )
        
        # Bottom chart - Conversion metrics
        if 'conversions' in metrics:
            fig.add_trace(
                go.Bar(
                    x=df['date'], y=df['conversions'],
                    name='Conversions',
                    marker_color=ChartGenerator.COLORS['success']
                ),
                row=2, col=1
            )
        
        fig.update_layout(
            **ChartGenerator.CHART_LAYOUT,
            title='Performance Trend Analysis',
            height=600,
            yaxis2=dict(
                title='Clicks',
                overlaying='y',
                side='right'
            )
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Impressions", row=1, col=1)
        fig.update_yaxes(title_text="Conversions", row=2, col=1)
        
        return fig.to_html(div_id="performance-trend", include_plotlyjs='cdn')
    
    @staticmethod
    def roi_breakdown_chart(roi_data: Dict[str, Any]) -> str:
        """Create ROI breakdown pie chart"""
        labels = ['Labor Cost Saved', 'Performance Value Added', 'Automation Cost']
        values = [
            roi_data.get('labor_cost_saved', 0),
            roi_data.get('performance_value_added', 0),
            abs(roi_data.get('automation_cost', 0))
        ]
        
        fig = go.Figure(data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(
                    colors=[ChartGenerator.COLORS['success'], 
                           ChartGenerator.COLORS['info'], 
                           ChartGenerator.COLORS['warning']]
                ),
                textposition='inside',
                textinfo='percent+label'
            )
        ])
        
        fig.update_layout(
            **ChartGenerator.CHART_LAYOUT,
            title='ROI Breakdown',
            height=400,
            annotations=[
                dict(
                    text=f"ROI<br>{roi_data.get('roi_percentage', 0):.1f}%",
                    x=0.5, y=0.5,
                    font_size=20,
                    showarrow=False
                )
            ]
        )
        
        return fig.to_html(div_id="roi-breakdown", include_plotlyjs='cdn')
    
    @staticmethod
    def time_savings_chart(task_data: List[Dict[str, Any]]) -> str:
        """Create time savings bar chart by task type"""
        df = pd.DataFrame(task_data)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['task_type'],
            y=df['manual_hours'],
            name='Manual Time',
            marker_color=ChartGenerator.COLORS['danger'],
            text=df['manual_hours'].round(1),
            textposition='auto'
        ))
        
        fig.add_trace(go.Bar(
            x=df['task_type'],
            y=df['automated_hours'],
            name='Automated Time',
            marker_color=ChartGenerator.COLORS['success'],
            text=df['automated_hours'].round(1),
            textposition='auto'
        ))
        
        fig.update_layout(
            **ChartGenerator.CHART_LAYOUT,
            title='Time Savings by Task Type',
            xaxis_title='Task Type',
            yaxis_title='Hours',
            barmode='group',
            height=400
        )
        
        return fig.to_html(div_id="time-savings", include_plotlyjs='cdn')
    
    @staticmethod
    def campaign_performance_heatmap(performance_data: List[Dict[str, Any]]) -> str:
        """Create heatmap of campaign performance metrics"""
        campaigns = list(set(p['campaign_name'] for p in performance_data))
        metrics = ['CTR', 'Conversion Rate', 'ROAS', 'CPA']
        
        # Create matrix
        z_data = []
        for campaign in campaigns:
            campaign_metrics = []
            for metric in metrics:
                values = [p[metric.lower().replace(' ', '_')] for p in performance_data 
                         if p['campaign_name'] == campaign]
                avg_value = np.mean(values) if values else 0
                campaign_metrics.append(avg_value)
            z_data.append(campaign_metrics)
        
        fig = go.Figure(data=go.Heatmap(
            z=z_data,
            x=metrics,
            y=campaigns,
            colorscale='RdYlGn',
            text=np.round(z_data, 2),
            texttemplate='%{text}',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            **ChartGenerator.CHART_LAYOUT,
            title='Campaign Performance Heatmap',
            height=400
        )
        
        return fig.to_html(div_id="performance-heatmap", include_plotlyjs='cdn')
    
    @staticmethod
    def ai_decision_success_gauge(success_rate: float) -> str:
        """Create gauge chart for AI decision success rate"""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=success_rate,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "AI Decision Success Rate"},
            delta={'reference': 80, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1},
                'bar': {'color': ChartGenerator.COLORS['primary']},
                'steps': [
                    {'range': [0, 50], 'color': ChartGenerator.COLORS['danger']},
                    {'range': [50, 80], 'color': ChartGenerator.COLORS['warning']},
                    {'range': [80, 100], 'color': ChartGenerator.COLORS['success']}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            **ChartGenerator.CHART_LAYOUT,
            height=300
        )
        
        return fig.to_html(div_id="ai-success-gauge", include_plotlyjs='cdn')


class ReportGenerator:
    """Generate professional marketing reports"""
    
    def __init__(self, template_dir: Optional[str] = None):
        if not template_dir:
            template_dir = Path(__file__).parent / 'templates'
        
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        
        # Add custom filters
        self.env.filters['currency'] = self._currency_filter
        self.env.filters['percentage'] = self._percentage_filter
        self.env.filters['number'] = self._number_filter
        
        self.chart_generator = ChartGenerator()
    
    @staticmethod
    def _currency_filter(value: Union[float, Decimal]) -> str:
        """Format currency values"""
        return f"${float(value):,.2f}"
    
    @staticmethod
    def _percentage_filter(value: float) -> str:
        """Format percentage values"""
        return f"{value:.1f}%"
    
    @staticmethod
    def _number_filter(value: Union[int, float]) -> str:
        """Format large numbers with commas"""
        if isinstance(value, float):
            return f"{value:,.1f}"
        return f"{value:,}"
    
    async def generate_weekly_summary(
        self,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> Dict[str, str]:
        """Generate weekly performance summary report"""
        if not end_date:
            end_date = start_date + timedelta(days=7)
        
        # Gather data
        with db.get_session() as session:
            # Get campaigns
            campaigns = session.query(Campaign).filter(
                Campaign.created_at <= end_date
            ).all()
            
            # Get performance metrics
            performance_metrics = session.query(PerformanceMetrics).filter(
                PerformanceMetrics.metric_date >= start_date,
                PerformanceMetrics.metric_date <= end_date
            ).all()
            
            # Get automation tasks
            automation_tasks = session.query(AutomationTask).filter(
                AutomationTask.completed_at >= start_date,
                AutomationTask.completed_at <= end_date,
                AutomationTask.status == 'completed'
            ).all()
            
            # Get AI decisions
            ai_decisions = session.query(AIDecisionHistory).filter(
                AIDecisionHistory.decision_timestamp >= start_date,
                AIDecisionHistory.decision_timestamp <= end_date
            ).all()
        
        # Calculate summary metrics
        total_impressions = sum(m.impressions for m in performance_metrics)
        total_clicks = sum(m.clicks for m in performance_metrics)
        total_conversions = sum(m.conversions for m in performance_metrics)
        total_revenue = sum(float(m.revenue) for m in performance_metrics)
        total_cost = sum(float(m.cost) for m in performance_metrics)
        
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        overall_roas = (total_revenue / total_cost) if total_cost > 0 else 0
        
        # Time and cost savings
        total_time_saved = sum(t.time_saved_minutes for t in automation_tasks) / 60
        total_cost_saved = sum(float(t.cost_saved) for t in automation_tasks)
        
        # Prepare performance trend data
        perf_by_date = {}
        for metric in performance_metrics:
            date_str = metric.metric_date.strftime('%Y-%m-%d')
            if date_str not in perf_by_date:
                perf_by_date[date_str] = {
                    'date': date_str,
                    'impressions': 0,
                    'clicks': 0,
                    'conversions': 0,
                    'revenue': 0
                }
            perf_by_date[date_str]['impressions'] += metric.impressions
            perf_by_date[date_str]['clicks'] += metric.clicks
            perf_by_date[date_str]['conversions'] += metric.conversions
            perf_by_date[date_str]['revenue'] += float(metric.revenue)
        
        performance_trend_data = list(perf_by_date.values())
        
        # Generate charts
        charts = {
            'performance_trend': self.chart_generator.performance_trend_chart(
                performance_trend_data,
                ['impressions', 'clicks', 'conversions']
            ),
            'ai_success_gauge': self.chart_generator.ai_decision_success_gauge(
                self._calculate_ai_success_rate(ai_decisions)
            )
        }
        
        # Prepare template data
        template_data = {
            'report_title': 'Weekly Performance Summary',
            'period': {
                'start': start_date.strftime('%B %d, %Y'),
                'end': end_date.strftime('%B %d, %Y')
            },
            'summary_metrics': {
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'total_conversions': total_conversions,
                'total_revenue': total_revenue,
                'avg_ctr': avg_ctr,
                'avg_conversion_rate': avg_conversion_rate,
                'overall_roas': overall_roas
            },
            'automation_metrics': {
                'tasks_completed': len(automation_tasks),
                'time_saved_hours': total_time_saved,
                'cost_saved': total_cost_saved,
                'ai_decisions_made': len(ai_decisions)
            },
            'top_campaigns': self._get_top_campaigns(performance_metrics),
            'charts': charts,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Generate HTML
        template = self.env.get_template('weekly_summary.html')
        html_content = template.render(**template_data)
        
        # Generate PDF
        pdf_content = self._generate_pdf(html_content)
        
        return {
            'html': html_content,
            'pdf': base64.b64encode(pdf_content).decode('utf-8') if pdf_content else None
        }
    
    async def generate_campaign_optimization_report(
        self,
        campaign_id: int,
        period_days: int = 30
    ) -> Dict[str, str]:
        """Generate campaign optimization report"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        with db.get_session() as session:
            # Get campaign
            campaign = session.query(Campaign).filter_by(id=campaign_id).first()
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            # Get performance metrics
            performance_metrics = session.query(PerformanceMetrics).filter(
                PerformanceMetrics.campaign_id == campaign_id,
                PerformanceMetrics.metric_date >= start_date
            ).order_by(PerformanceMetrics.metric_date).all()
            
            # Get AI decisions
            ai_decisions = session.query(AIDecisionHistory).filter(
                AIDecisionHistory.campaign_id == campaign_id,
                AIDecisionHistory.decision_timestamp >= start_date
            ).all()
            
            # Get automation tasks
            automation_tasks = session.query(AutomationTask).filter(
                AutomationTask.campaign_id == campaign_id,
                AutomationTask.completed_at >= start_date,
                AutomationTask.status == 'completed'
            ).all()
        
        # Calculate optimization metrics
        optimization_metrics = self._calculate_optimization_metrics(
            performance_metrics, ai_decisions
        )
        
        # Prepare performance data for heatmap
        performance_data = [
            {
                'campaign_name': campaign.name,
                'ctr': m.ctr,
                'conversion_rate': m.conversion_rate,
                'roas': m.roas,
                'cpa': float(m.cpa) if m.cpa else 0
            }
            for m in performance_metrics
        ]
        
        # Generate charts
        charts = {
            'performance_heatmap': self.chart_generator.campaign_performance_heatmap(
                performance_data
            ),
            'performance_trend': self.chart_generator.performance_trend_chart(
                [m.to_dict() for m in performance_metrics],
                ['clicks', 'conversions']
            )
        }
        
        # Prepare optimization recommendations
        recommendations = self._generate_optimization_recommendations(
            campaign, performance_metrics, ai_decisions
        )
        
        template_data = {
            'report_title': 'Campaign Optimization Report',
            'campaign': campaign.to_dict(),
            'period_days': period_days,
            'optimization_metrics': optimization_metrics,
            'ai_decisions': [d.to_dict() for d in ai_decisions[-5:]],  # Last 5 decisions
            'recommendations': recommendations,
            'charts': charts,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        template = self.env.get_template('campaign_optimization.html')
        html_content = template.render(**template_data)
        pdf_content = self._generate_pdf(html_content)
        
        return {
            'html': html_content,
            'pdf': base64.b64encode(pdf_content).decode('utf-8') if pdf_content else None
        }
    
    async def generate_roi_analysis(
        self,
        start_date: datetime,
        end_date: datetime,
        campaign_id: Optional[int] = None
    ) -> Dict[str, str]:
        """Generate ROI analysis report"""
        # Get ROI data
        roi_data = generate_roi_report(start_date, end_date, campaign_id)
        
        # Prepare task breakdown data for chart
        task_breakdown_data = []
        for task in roi_data['task_breakdown']:
            task_breakdown_data.append({
                'task_type': task['task_type'].replace('_', ' ').title(),
                'manual_hours': task['time_saved_hours'] * 1.2,  # Estimate manual time
                'automated_hours': task['time_saved_hours'] * 0.2,  # 20% of manual
                'cost_saved': task['cost_saved']
            })
        
        # Generate charts
        charts = {
            'roi_breakdown': self.chart_generator.roi_breakdown_chart(
                roi_data['roi_metrics']
            ),
            'time_savings': self.chart_generator.time_savings_chart(
                task_breakdown_data
            )
        }
        
        # Calculate projections
        monthly_projection = self._calculate_roi_projections(roi_data, 30)
        annual_projection = self._calculate_roi_projections(roi_data, 365)
        
        template_data = {
            'report_title': 'ROI Analysis Report',
            'period': roi_data['period'],
            'roi_metrics': roi_data['roi_metrics'],
            'automation_summary': roi_data['automation_summary'],
            'task_breakdown': task_breakdown_data,
            'insights': roi_data['insights'],
            'projections': {
                'monthly': monthly_projection,
                'annual': annual_projection
            },
            'charts': charts,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        template = self.env.get_template('roi_analysis.html')
        html_content = template.render(**template_data)
        pdf_content = self._generate_pdf(html_content)
        
        return {
            'html': html_content,
            'pdf': base64.b64encode(pdf_content).decode('utf-8') if pdf_content else None
        }
    
    async def generate_executive_dashboard(
        self,
        period_days: int = 30
    ) -> Dict[str, str]:
        """Generate executive dashboard with high-level insights"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        # Get comprehensive data
        with db.get_session() as session:
            # Overall metrics
            total_campaigns = session.query(Campaign).count()
            active_campaigns = session.query(Campaign).filter_by(status='active').count()
            
            # Aggregate performance
            performance_metrics = session.query(PerformanceMetrics).filter(
                PerformanceMetrics.metric_date >= start_date
            ).all()
            
            # Automation metrics
            automation_summary = db.get_automation_summary(period_days)
            
            # ROI tracking
            roi_records = session.query(ROITracking).filter(
                ROITracking.period_start >= start_date
            ).all()
        
        # Calculate KPIs
        kpis = {
            'total_revenue': sum(float(m.revenue) for m in performance_metrics),
            'total_cost': sum(float(m.cost) for m in performance_metrics),
            'overall_roas': 0,
            'time_saved_hours': automation_summary['total_time_saved_hours'],
            'cost_saved': automation_summary['total_cost_saved'],
            'efficiency_gain': automation_summary['average_efficiency_gain'],
            'ai_success_rate': automation_summary['ai_decision_success_rate']
        }
        
        if kpis['total_cost'] > 0:
            kpis['overall_roas'] = kpis['total_revenue'] / kpis['total_cost']
        
        # Top performing campaigns
        campaign_performance = {}
        for metric in performance_metrics:
            if metric.campaign_id not in campaign_performance:
                campaign_performance[metric.campaign_id] = {
                    'revenue': 0,
                    'conversions': 0,
                    'roas': []
                }
            campaign_performance[metric.campaign_id]['revenue'] += float(metric.revenue)
            campaign_performance[metric.campaign_id]['conversions'] += metric.conversions
            if metric.roas:
                campaign_performance[metric.campaign_id]['roas'].append(metric.roas)
        
        # Sort by revenue
        top_campaigns = sorted(
            [
                {
                    'campaign_id': cid,
                    'revenue': data['revenue'],
                    'conversions': data['conversions'],
                    'avg_roas': np.mean(data['roas']) if data['roas'] else 0
                }
                for cid, data in campaign_performance.items()
            ],
            key=lambda x: x['revenue'],
            reverse=True
        )[:5]
        
        # Generate trend data
        daily_metrics = self._aggregate_daily_metrics(performance_metrics)
        
        # Generate charts
        charts = {
            'performance_trend': self.chart_generator.performance_trend_chart(
                daily_metrics,
                ['impressions', 'clicks', 'conversions']
            ),
            'ai_success_gauge': self.chart_generator.ai_decision_success_gauge(
                kpis['ai_success_rate']
            )
        }
        
        # Key insights
        insights = self._generate_executive_insights(
            kpis, automation_summary, roi_records
        )
        
        template_data = {
            'report_title': 'Executive Dashboard',
            'period_days': period_days,
            'kpis': kpis,
            'campaign_stats': {
                'total': total_campaigns,
                'active': active_campaigns
            },
            'top_campaigns': top_campaigns,
            'automation_summary': automation_summary,
            'insights': insights,
            'charts': charts,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        template = self.env.get_template('executive_dashboard.html')
        html_content = template.render(**template_data)
        pdf_content = self._generate_pdf(html_content)
        
        return {
            'html': html_content,
            'pdf': base64.b64encode(pdf_content).decode('utf-8') if pdf_content else None
        }
    
    def _generate_pdf(self, html_content: str) -> bytes:
        """Convert HTML to PDF"""
        try:
            # Add CSS for PDF generation
            css = CSS(string='''
                @page {
                    size: A4;
                    margin: 1cm;
                }
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                }
                .page-break {
                    page-break-after: always;
                }
            ''')
            
            # Generate PDF
            pdf_file = BytesIO()
            HTML(string=html_content).write_pdf(pdf_file, stylesheets=[css])
            pdf_file.seek(0)
            
            return pdf_file.read()
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return None
    
    def _calculate_ai_success_rate(self, ai_decisions: List[AIDecisionHistory]) -> float:
        """Calculate AI decision success rate"""
        if not ai_decisions:
            return 0
        
        successful = sum(1 for d in ai_decisions 
                        if d.success_score and d.success_score >= 80)
        total = sum(1 for d in ai_decisions if d.success_score is not None)
        
        return (successful / total * 100) if total > 0 else 0
    
    def _get_top_campaigns(
        self, 
        performance_metrics: List[PerformanceMetrics], 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top performing campaigns"""
        campaign_totals = {}
        
        for metric in performance_metrics:
            if metric.campaign_id not in campaign_totals:
                campaign_totals[metric.campaign_id] = {
                    'campaign_id': metric.campaign_id,
                    'revenue': 0,
                    'conversions': 0,
                    'impressions': 0
                }
            
            campaign_totals[metric.campaign_id]['revenue'] += float(metric.revenue)
            campaign_totals[metric.campaign_id]['conversions'] += metric.conversions
            campaign_totals[metric.campaign_id]['impressions'] += metric.impressions
        
        # Sort by revenue
        sorted_campaigns = sorted(
            campaign_totals.values(),
            key=lambda x: x['revenue'],
            reverse=True
        )
        
        return sorted_campaigns[:limit]
    
    def _calculate_optimization_metrics(
        self,
        performance_metrics: List[PerformanceMetrics],
        ai_decisions: List[AIDecisionHistory]
    ) -> Dict[str, Any]:
        """Calculate optimization impact metrics"""
        if not performance_metrics:
            return {}
        
        # Separate pre and post optimization metrics
        optimization_date = None
        if ai_decisions:
            # Find first implemented decision
            for decision in sorted(ai_decisions, key=lambda x: x.decision_timestamp):
                if decision.was_implemented:
                    optimization_date = decision.implemented_at
                    break
        
        if not optimization_date:
            optimization_date = performance_metrics[len(performance_metrics)//2].metric_date
        
        pre_optimization = [m for m in performance_metrics if m.metric_date < optimization_date]
        post_optimization = [m for m in performance_metrics if m.metric_date >= optimization_date]
        
        # Calculate averages
        pre_metrics = {
            'avg_ctr': np.mean([m.ctr for m in pre_optimization]) if pre_optimization else 0,
            'avg_conversion_rate': np.mean([m.conversion_rate for m in pre_optimization]) if pre_optimization else 0,
            'avg_cpa': np.mean([float(m.cpa) for m in pre_optimization if m.cpa]) if pre_optimization else 0,
            'avg_roas': np.mean([m.roas for m in pre_optimization]) if pre_optimization else 0
        }
        
        post_metrics = {
            'avg_ctr': np.mean([m.ctr for m in post_optimization]) if post_optimization else 0,
            'avg_conversion_rate': np.mean([m.conversion_rate for m in post_optimization]) if post_optimization else 0,
            'avg_cpa': np.mean([float(m.cpa) for m in post_optimization if m.cpa]) if post_optimization else 0,
            'avg_roas': np.mean([m.roas for m in post_optimization]) if post_optimization else 0
        }
        
        # Calculate improvements
        improvements = {}
        for metric in ['avg_ctr', 'avg_conversion_rate', 'avg_roas']:
            if pre_metrics[metric] > 0:
                improvement = ((post_metrics[metric] - pre_metrics[metric]) / pre_metrics[metric]) * 100
                improvements[f"{metric}_improvement"] = improvement
        
        # CPA should decrease
        if pre_metrics['avg_cpa'] > 0:
            improvements['avg_cpa_improvement'] = ((pre_metrics['avg_cpa'] - post_metrics['avg_cpa']) / pre_metrics['avg_cpa']) * 100
        
        return {
            'pre_optimization': pre_metrics,
            'post_optimization': post_metrics,
            'improvements': improvements,
            'optimization_date': optimization_date.strftime('%Y-%m-%d')
        }
    
    def _generate_optimization_recommendations(
        self,
        campaign: Campaign,
        performance_metrics: List[PerformanceMetrics],
        ai_decisions: List[AIDecisionHistory]
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        recommendations = []
        
        # Analyze recent performance
        if performance_metrics:
            recent_metrics = performance_metrics[-7:]  # Last 7 days
            avg_ctr = np.mean([m.ctr for m in recent_metrics])
            avg_conversion_rate = np.mean([m.conversion_rate for m in recent_metrics])
            
            # CTR recommendations
            if avg_ctr < 2.0:
                recommendations.append({
                    'type': 'warning',
                    'title': 'Low Click-Through Rate',
                    'description': f'CTR is {avg_ctr:.1f}%, below industry standard of 2%',
                    'action': 'Consider refreshing ad creative or refining targeting'
                })
            
            # Conversion rate recommendations
            if avg_conversion_rate < 3.0:
                recommendations.append({
                    'type': 'warning',
                    'title': 'Low Conversion Rate',
                    'description': f'Conversion rate is {avg_conversion_rate:.1f}%, below target of 3%',
                    'action': 'Review landing page experience and offer relevance'
                })
        
        # AI decision recommendations
        successful_decisions = [d for d in ai_decisions if d.success_score and d.success_score >= 80]
        if len(successful_decisions) < len(ai_decisions) * 0.7:
            recommendations.append({
                'type': 'info',
                'title': 'AI Decision Performance',
                'description': 'Less than 70% of AI decisions meeting success criteria',
                'action': 'Review AI decision parameters and confidence thresholds'
            })
        
        # Budget recommendations
        if campaign.budget:
            total_spend = sum(float(m.cost) for m in performance_metrics)
            budget_utilization = (total_spend / float(campaign.budget)) * 100
            
            if budget_utilization < 80:
                recommendations.append({
                    'type': 'info',
                    'title': 'Budget Underutilization',
                    'description': f'Only {budget_utilization:.1f}% of budget used',
                    'action': 'Consider increasing bids or expanding targeting'
                })
        
        return recommendations
    
    def _calculate_roi_projections(
        self,
        current_roi_data: Dict[str, Any],
        projection_days: int
    ) -> Dict[str, Any]:
        """Calculate ROI projections"""
        current_days = current_roi_data['period']['days']
        
        # Simple linear projection
        daily_rate = {
            'time_saved': current_roi_data['roi_metrics']['total_time_saved_hours'] / current_days,
            'cost_saved': current_roi_data['roi_metrics']['total_cost_saved'] / current_days,
            'tasks_automated': current_roi_data['roi_metrics']['tasks_automated'] / current_days
        }
        
        return {
            'period_days': projection_days,
            'projected_time_saved': daily_rate['time_saved'] * projection_days,
            'projected_cost_saved': daily_rate['cost_saved'] * projection_days,
            'projected_tasks': int(daily_rate['tasks_automated'] * projection_days),
            'confidence': 'medium'  # Could be calculated based on variance
        }
    
    def _aggregate_daily_metrics(
        self,
        performance_metrics: List[PerformanceMetrics]
    ) -> List[Dict[str, Any]]:
        """Aggregate metrics by day"""
        daily_data = {}
        
        for metric in performance_metrics:
            date_str = metric.metric_date.strftime('%Y-%m-%d')
            if date_str not in daily_data:
                daily_data[date_str] = {
                    'date': date_str,
                    'impressions': 0,
                    'clicks': 0,
                    'conversions': 0,
                    'revenue': 0,
                    'cost': 0
                }
            
            daily_data[date_str]['impressions'] += metric.impressions
            daily_data[date_str]['clicks'] += metric.clicks
            daily_data[date_str]['conversions'] += metric.conversions
            daily_data[date_str]['revenue'] += float(metric.revenue)
            daily_data[date_str]['cost'] += float(metric.cost)
        
        return sorted(daily_data.values(), key=lambda x: x['date'])
    
    def _generate_executive_insights(
        self,
        kpis: Dict[str, Any],
        automation_summary: Dict[str, Any],
        roi_records: List[ROITracking]
    ) -> List[Dict[str, Any]]:
        """Generate executive-level insights"""
        insights = []
        
        # ROI insight
        if kpis['cost_saved'] > 0:
            insights.append({
                'type': 'success',
                'icon': 'trending_up',
                'title': 'Strong ROI Performance',
                'description': f"Marketing automation delivered ${kpis['cost_saved']:,.2f} in cost savings with {kpis['time_saved_hours']:.1f} hours saved"
            })
        
        # Efficiency insight
        if kpis['efficiency_gain'] > 50:
            insights.append({
                'type': 'success',
                'icon': 'speed',
                'title': 'High Efficiency Gains',
                'description': f"Automation improved task efficiency by {kpis['efficiency_gain']:.1f}%, significantly reducing manual workload"
            })
        
        # AI performance insight
        if kpis['ai_success_rate'] > 80:
            insights.append({
                'type': 'info',
                'icon': 'psychology',
                'title': 'AI Decision Making',
                'description': f"AI decisions achieving {kpis['ai_success_rate']:.1f}% success rate, driving consistent optimization improvements"
            })
        
        # Revenue impact
        if kpis['overall_roas'] > 3:
            insights.append({
                'type': 'success',
                'icon': 'attach_money',
                'title': 'Revenue Performance',
                'description': f"Campaigns achieving {kpis['overall_roas']:.1f}x ROAS, exceeding industry benchmarks"
            })
        
        return insights


# Convenience function to create report generator
def create_report_generator(template_dir: Optional[str] = None) -> ReportGenerator:
    """Create and return a report generator instance"""
    return ReportGenerator(template_dir)