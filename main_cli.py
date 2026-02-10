#!/usr/bin/env python3
"""
Command Line Interface for Drone Operations Agent
"""

import sys
import os
import click
from datetime import datetime
from typing import Optional

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.sheets_manager import GoogleSheetsManager
from modules.data_models import Pilot, Drone, Mission

@click.group()
def cli():
    """Drone Operations Coordinator AI Agent CLI"""
    pass

@cli.command()
def status():
    """Show current system status"""
    manager = GoogleSheetsManager()
    status = manager.get_status()

    click.echo("🚁 Drone Operations Agent Status")
    click.echo("=" * 50)

    for sheet_name, data in status.items():
        click.echo(f"\n📊 {sheet_name.upper().replace('_', ' ')}:")
        click.echo(f"   Records: {data['records']}")
        click.echo(f"   Last Sync: {data['last_sync']}")
        click.echo(f"   Columns: {', '.join(data['columns'][:5])}...")

@cli.command()
@click.argument('pilot_id')
@click.argument('new_status')
def update_pilot(pilot_id, new_status):
    """Update pilot status"""
    manager = GoogleSheetsManager()

    valid_statuses = ['Available', 'On Leave', 'Unavailable', 'On Assignment']
    if new_status not in valid_statuses:
        click.echo(f"❌ Invalid status. Choose from: {', '.join(valid_statuses)}")
        return

    success = manager.update_record('pilot_roster', pilot_id, {'status': new_status})
    if success:
        click.echo(f"✅ Updated pilot {pilot_id} to {new_status}")
    else:
        click.echo(f"❌ Failed to update pilot {pilot_id}")

@cli.command()
def conflicts():
    """Check for conflicts"""
    manager = GoogleSheetsManager()

    # Get all data
    pilots_df = manager.get_sheet_data('pilot_roster')
    drones_df = manager.get_sheet_data('drone_fleet')
    missions_df = manager.get_sheet_data('missions')

    if pilots_df.empty or drones_df.empty or missions_df.empty:
        click.echo("❌ No data loaded. Check your sheet connections.")
        return

    click.echo("🔍 Checking for conflicts...")
    click.echo("=" * 50)

    conflicts_found = False

    # Check double bookings
    for _, mission in missions_df.iterrows():
        if mission['assigned_pilot'] and mission['assigned_pilot'] != 'None':
            # Find other missions with same pilot
            other_missions = missions_df[
                (missions_df['assigned_pilot'] == mission['assigned_pilot']) &
                (missions_df['mission_id'] != mission['mission_id'])
            ]

            for _, other in other_missions.iterrows():
                # Check date overlap
                mission_start = pd.to_datetime(mission['start_date'])
                mission_end = pd.to_datetime(mission['end_date'])
                other_start = pd.to_datetime(other['start_date'])
                other_end = pd.to_datetime(other['end_date'])

                if max(mission_start, other_start) <= min(mission_end, other_end):
                    click.echo(f"🚨 DOUBLE BOOKING: Pilot {mission['assigned_pilot']}")
                    click.echo(f"   Mission 1: {mission['mission_id']} ({mission['start_date']} to {mission['end_date']})")
                    click.echo(f"   Mission 2: {other['mission_id']} ({other['start_date']} to {other['end_date']})")
                    click.echo()
                    conflicts_found = True

    # Check skill mismatches
    for _, mission in missions_df.iterrows():
        if mission['assigned_pilot'] and mission['assigned_pilot'] != 'None':
            pilot = pilots_df[pilots_df['pilot_id'] == mission['assigned_pilot']]
            if not pilot.empty:
                pilot_skills = str(pilot.iloc[0]['skills']).split(',')
                required_skills = str(mission['required_skills']).split(',')

                missing_skills = [s for s in required_skills if s.strip() not in pilot_skills]
                if missing_skills:
                    click.echo(f"⚠️  SKILL MISMATCH: Pilot {mission['assigned_pilot']}")
                    click.echo(f"   Mission: {mission['mission_id']}")
                    click.echo(f"   Missing skills: {', '.join(missing_skills)}")
                    click.echo()
                    conflicts_found = True

    if not conflicts_found:
        click.echo("✅ No conflicts found!")

@cli.command()
@click.option('--mission-id', required=True, help='Mission ID to assign')
@click.option('--pilot-id', help='Specific pilot ID to assign')
def assign(mission_id, pilot_id):
    """Assign resources to a mission"""
    manager = GoogleSheetsManager()

    missions_df = manager.get_sheet_data('missions')
    pilots_df = manager.get_sheet_data('pilot_roster')
    drones_df = manager.get_sheet_data('drone_fleet')

    # Find mission
    mission = missions_df[missions_df['mission_id'] == mission_id]
    if mission.empty:
        click.echo(f"❌ Mission {mission_id} not found")
        return

    mission = mission.iloc[0]

    if pilot_id:
        # Assign specific pilot
        pilot = pilots_df[pilots_df['pilot_id'] == pilot_id]
        if pilot.empty:
            click.echo(f"❌ Pilot {pilot_id} not found")
            return

        # Check availability
        if pilot.iloc[0]['status'] != 'Available':
            click.echo(f"❌ Pilot {pilot_id} is not available")
            return

        # Update mission
        success = manager.update_record('missions', mission_id,
                                       {'assigned_pilot': pilot_id})
        if success:
            click.echo(f"✅ Assigned pilot {pilot_id} to mission {mission_id}")
        else:
            click.echo(f"❌ Failed to assign pilot")
    else:
        # Auto-assign best pilot
        click.echo(f"🔍 Finding best pilot for mission {mission_id}...")
        # Implement auto-assignment logic here
        click.echo("Auto-assignment feature coming soon!")

if __name__ == '__main__':
    cli()
