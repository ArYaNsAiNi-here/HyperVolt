"""
Setup script to initialize Django-Q scheduled tasks for HyperVolt.
Run this after migrations to set up periodic tasks.

Usage:
    python setup_scheduled_tasks.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hypervolt_backend.settings')
django.setup()

from django_q.models import Schedule


def setup_tasks():
    """Create scheduled tasks for external API data fetching."""
    
    tasks = [
        {
            'name': 'Fetch Carbon Intensity',
            'func': 'data_pipeline.tasks.fetch_carbon_intensity',
            'schedule_type': Schedule.MINUTES,
            'minutes': 15,
            'repeats': -1,  # Infinite repeats
        },
        {
            'name': 'Fetch Weather Data',
            'func': 'data_pipeline.tasks.fetch_weather_data',
            'schedule_type': Schedule.MINUTES,
            'minutes': 15,
            'repeats': -1,
        },
        {
            'name': 'Cleanup Old Data',
            'func': 'data_pipeline.tasks.cleanup_old_data',
            'schedule_type': Schedule.DAILY,
            'repeats': -1,
        },
    ]
    
    for task_config in tasks:
        schedule, created = Schedule.objects.get_or_create(
            name=task_config['name'],
            defaults={
                'func': task_config['func'],
                'schedule_type': task_config['schedule_type'],
                'minutes': task_config.get('minutes'),
                'repeats': task_config['repeats'],
            }
        )
        
        if created:
            print(f"✓ Created scheduled task: {task_config['name']}")
        else:
            print(f"→ Task already exists: {task_config['name']}")
    
    print("\n✓ All scheduled tasks configured!")
    print("Run 'python manage.py qcluster' to start the task worker.")


if __name__ == '__main__':
    setup_tasks()
