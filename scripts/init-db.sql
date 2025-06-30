-- Initialize Marketing Automation Database
-- This script sets up initial data for demos and testing

-- Create extensions if using PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Insert sample campaigns for demo
INSERT INTO campaigns (campaign_id, name, platform, status, budget, start_date, created_at)
VALUES 
    ('dd_search_001', 'DoorDash Search - Food Delivery', 'google_ads', 'active', 15000.00, CURRENT_DATE - INTERVAL '30 days', CURRENT_TIMESTAMP),
    ('dd_display_002', 'DoorDash Display - Brand Awareness', 'google_ads', 'active', 10000.00, CURRENT_DATE - INTERVAL '30 days', CURRENT_TIMESTAMP),
    ('dd_social_003', 'DoorDash Social - New User Acquisition', 'facebook_ads', 'active', 20000.00, CURRENT_DATE - INTERVAL '30 days', CURRENT_TIMESTAMP),
    ('dd_video_004', 'DoorDash Video - Restaurant Partners', 'facebook_ads', 'active', 8000.00, CURRENT_DATE - INTERVAL '30 days', CURRENT_TIMESTAMP),
    ('dd_retarget_005', 'DoorDash Retargeting - Cart Abandoners', 'google_ads', 'active', 5000.00, CURRENT_DATE - INTERVAL '30 days', CURRENT_TIMESTAMP)
ON CONFLICT (campaign_id) DO NOTHING;

-- Insert sample performance metrics
INSERT INTO performance_metrics (campaign_id, date_recorded, impressions, clicks, conversions, revenue, cost, is_automated, automation_applied)
SELECT 
    c.id,
    CURRENT_DATE - INTERVAL '1 day',
    CASE 
        WHEN c.campaign_id = 'dd_search_001' THEN 850000
        WHEN c.campaign_id = 'dd_display_002' THEN 2000000
        WHEN c.campaign_id = 'dd_social_003' THEN 1500000
        WHEN c.campaign_id = 'dd_video_004' THEN 500000
        WHEN c.campaign_id = 'dd_retarget_005' THEN 250000
    END,
    CASE 
        WHEN c.campaign_id = 'dd_search_001' THEN 17000
        WHEN c.campaign_id = 'dd_display_002' THEN 20000
        WHEN c.campaign_id = 'dd_social_003' THEN 30000
        WHEN c.campaign_id = 'dd_video_004' THEN 5000
        WHEN c.campaign_id = 'dd_retarget_005' THEN 10000
    END,
    CASE 
        WHEN c.campaign_id = 'dd_search_001' THEN 425
        WHEN c.campaign_id = 'dd_display_002' THEN 800
        WHEN c.campaign_id = 'dd_social_003' THEN 1200
        WHEN c.campaign_id = 'dd_video_004' THEN 100
        WHEN c.campaign_id = 'dd_retarget_005' THEN 800
    END,
    CASE 
        WHEN c.campaign_id = 'dd_search_001' THEN 21250.00
        WHEN c.campaign_id = 'dd_display_002' THEN 40000.00
        WHEN c.campaign_id = 'dd_social_003' THEN 60000.00
        WHEN c.campaign_id = 'dd_video_004' THEN 5000.00
        WHEN c.campaign_id = 'dd_retarget_005' THEN 40000.00
    END,
    CASE 
        WHEN c.campaign_id = 'dd_search_001' THEN 14500.00
        WHEN c.campaign_id = 'dd_display_002' THEN 9800.00
        WHEN c.campaign_id = 'dd_social_003' THEN 19500.00
        WHEN c.campaign_id = 'dd_video_004' THEN 7800.00
        WHEN c.campaign_id = 'dd_retarget_005' THEN 4800.00
    END,
    false,
    NULL
FROM campaigns c
WHERE c.campaign_id IN ('dd_search_001', 'dd_display_002', 'dd_social_003', 'dd_video_004', 'dd_retarget_005');

-- Insert sample automation tasks
INSERT INTO automation_tasks (task_type, task_name, status, manual_duration_minutes, automated_duration_seconds, hourly_rate, created_at, completed_at)
VALUES 
    ('performance_analysis', 'Weekly Campaign Analysis', 'completed', 480, 30, 75.00, CURRENT_TIMESTAMP - INTERVAL '7 days', CURRENT_TIMESTAMP - INTERVAL '7 days' + INTERVAL '30 seconds'),
    ('budget_optimization', 'Q4 Budget Reallocation', 'completed', 180, 45, 100.00, CURRENT_TIMESTAMP - INTERVAL '3 days', CURRENT_TIMESTAMP - INTERVAL '3 days' + INTERVAL '45 seconds'),
    ('report_generation', 'Monthly Executive Report', 'completed', 600, 120, 75.00, CURRENT_TIMESTAMP - INTERVAL '1 day', CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '2 minutes')
ON CONFLICT DO NOTHING;

-- Insert sample ROI tracking
INSERT INTO roi_tracking (period_start, period_end, tasks_automated, total_time_saved_hours, labor_cost_saved, roi_percentage, created_at)
VALUES 
    (CURRENT_DATE - INTERVAL '30 days', CURRENT_DATE, 15, 87.5, 6562.50, 428.75, CURRENT_TIMESTAMP)
ON CONFLICT DO NOTHING;