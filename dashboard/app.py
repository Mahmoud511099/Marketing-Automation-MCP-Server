"""
Simple Web Dashboard for Marketing Automation MCP
Shows real-time metrics and ROI tracking
"""

from flask import Flask, render_template, jsonify
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import json

app = Flask(__name__)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///marketing_automation.db')
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

# Import models (simplified for dashboard)
from src.database import Campaign, AutomationTask, PerformanceMetrics, ROITracking

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """Get current metrics"""
    session = Session()
    try:
        # Get summary metrics
        total_campaigns = session.query(Campaign).count()
        total_tasks = session.query(AutomationTask).count()
        
        # Calculate time saved (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_tasks = session.query(AutomationTask).filter(
            AutomationTask.created_at >= thirty_days_ago
        ).all()
        
        total_time_saved = sum(task.time_saved_minutes or 0 for task in recent_tasks)
        total_cost_saved = sum(task.cost_saved or 0 for task in recent_tasks)
        
        # Get performance improvements
        automated_metrics = session.query(PerformanceMetrics).filter(
            PerformanceMetrics.is_automated == True
        ).all()
        
        manual_metrics = session.query(PerformanceMetrics).filter(
            PerformanceMetrics.is_automated == False
        ).all()
        
        avg_automated_roi = sum(m.roas or 0 for m in automated_metrics) / max(len(automated_metrics), 1)
        avg_manual_roi = sum(m.roas or 0 for m in manual_metrics) / max(len(manual_metrics), 1)
        roi_improvement = ((avg_automated_roi - avg_manual_roi) / max(avg_manual_roi, 1)) * 100
        
        return jsonify({
            'total_campaigns': total_campaigns,
            'total_automations': total_tasks,
            'time_saved_hours': total_time_saved / 60,
            'cost_saved': total_cost_saved,
            'roi_improvement': roi_improvement,
            'last_updated': datetime.now().isoformat()
        })
    finally:
        session.close()

@app.route('/api/campaigns')
def get_campaigns():
    """Get campaign data"""
    session = Session()
    try:
        campaigns = session.query(Campaign).all()
        campaign_data = []
        
        for campaign in campaigns:
            # Get latest metrics
            latest_metric = session.query(PerformanceMetrics).filter(
                PerformanceMetrics.campaign_id == campaign.id
            ).order_by(PerformanceMetrics.date_recorded.desc()).first()
            
            if latest_metric:
                campaign_data.append({
                    'name': campaign.name,
                    'platform': campaign.platform,
                    'budget': float(campaign.budget or 0),
                    'roi': float(latest_metric.roas or 0),
                    'conversions': latest_metric.conversions or 0,
                    'is_automated': latest_metric.is_automated
                })
        
        return jsonify(campaign_data)
    finally:
        session.close()

@app.route('/api/timeline')
def get_timeline():
    """Get automation timeline"""
    session = Session()
    try:
        # Get recent automation tasks
        recent_tasks = session.query(AutomationTask).order_by(
            AutomationTask.created_at.desc()
        ).limit(20).all()
        
        timeline_data = []
        for task in recent_tasks:
            timeline_data.append({
                'timestamp': task.created_at.isoformat(),
                'task_type': task.task_type.value if task.task_type else 'Unknown',
                'task_name': task.task_name,
                'time_saved': task.time_saved_minutes or 0,
                'cost_saved': task.cost_saved or 0,
                'status': task.status.value if task.status else 'Unknown'
            })
        
        return jsonify(timeline_data)
    finally:
        session.close()

@app.route('/api/roi_trend')
def get_roi_trend():
    """Get ROI trend over time"""
    session = Session()
    try:
        # Get ROI tracking data
        roi_data = session.query(ROITracking).order_by(
            ROITracking.period_start
        ).limit(12).all()
        
        trend_data = []
        for roi in roi_data:
            trend_data.append({
                'period': roi.period_start.strftime('%Y-%m'),
                'roi_percentage': float(roi.roi_percentage or 0),
                'time_saved_hours': float(roi.total_time_saved_hours or 0),
                'cost_saved': float(roi.labor_cost_saved or 0)
            })
        
        return jsonify(trend_data)
    finally:
        session.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)