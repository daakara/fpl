#!/usr/bin/env python3
"""
Quick debug script to check available FPL data columns
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.fpl_data_service import FPLDataService

def check_available_columns():
    """Check what columns are actually available in FPL data"""
    print("🔍 Checking available FPL data columns...")
    
    try:
        service = FPLDataService()
        players_df, teams_df = service.load_fpl_data()
        
        print(f"\n📊 Players DataFrame shape: {players_df.shape}")
        print(f"📊 Teams DataFrame shape: {teams_df.shape}")
        
        print("\n🔍 Available Player Columns:")
        for i, col in enumerate(sorted(players_df.columns), 1):
            print(f"{i:2d}. {col}")
        
        print("\n🔍 Available Team Columns:")
        for i, col in enumerate(sorted(teams_df.columns), 1):
            print(f"{i:2d}. {col}")
        
        # Check for transfer-related columns
        transfer_columns = ['transfers_in_event', 'transfers_out_event', 'transfers_balance']
        print(f"\n❌ Missing Transfer Columns:")
        for col in transfer_columns:
            if col not in players_df.columns:
                print(f"   • {col}")
        
        # Check for available columns we can use instead
        available_alternatives = ['form', 'selected_by_percent', 'total_points', 'now_cost', 'minutes']
        print(f"\n✅ Available Alternative Columns:")
        for col in available_alternatives:
            if col in players_df.columns:
                print(f"   • {col} ✓")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_available_columns()
