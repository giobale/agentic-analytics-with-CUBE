#!/usr/bin/env python3
"""
ABOUTME: Minimal Python application to test CUBE API connectivity and query execution
ABOUTME: Demonstrates how to authenticate, query cubes, and export results to CSV
"""

import requests
import json
import pandas as pd
from datetime import datetime
import sys
import time
import subprocess
import re
import os

class CubeAPIClient:
    def __init__(self, base_url="http://localhost:4000", api_secret="baubeach", results_dir="results"):
        self.base_url = base_url
        self.api_secret = api_secret
        self.jwt_token = None
        self.results_dir = results_dir
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Create results directory if it doesn't exist
        os.makedirs(self.results_dir, exist_ok=True)
    
    def get_jwt_token(self):
        """Retrieve JWT token from CUBE container logs"""
        try:
            # Try to get token from container logs
            result = subprocess.run(
                ['docker-compose', 'logs', 'cube'],
                capture_output=True, text=True, check=True
            )
            
            # Look for JWT token pattern in logs
            jwt_pattern = r'eyJ[A-Za-z0-9._-]*'
            matches = re.findall(jwt_pattern, result.stdout)
            
            if matches:
                # Get the most recent token
                self.jwt_token = matches[-1]
                print(f"✅ Retrieved JWT token: {self.jwt_token[:20]}...")
                
                # Update session headers with JWT token
                self.session.headers.update({
                    'Authorization': f'Bearer {self.jwt_token}'
                })
                return True
            else:
                print("❌ No JWT token found in container logs")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to get container logs: {e}")
            return False
        except Exception as e:
            print(f"❌ Error retrieving JWT token: {e}")
            return False
    
    def test_connection(self):
        """Test basic connectivity to CUBE API"""
        try:
            response = self.session.get(f"{self.base_url}/readyz")
            response.raise_for_status()
            print("✅ Successfully connected to CUBE API")
            return True
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to CUBE API: {e}")
            return False
    
    def get_meta(self):
        """Get metadata about available cubes"""
        try:
            response = self.session.get(f"{self.base_url}/cubejs-api/v1/meta")
            response.raise_for_status()
            meta_data = response.json()
            
            if 'cubes' in meta_data:
                cube_names = [cube['name'] for cube in meta_data['cubes']]
                print(f"✅ Available cubes: {', '.join(cube_names)}")
                return meta_data
            else:
                print("❌ No cubes found in metadata")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get metadata: {e}")
            return None
    
    def execute_query(self, query):
        """Execute a CUBE query"""
        try:
            response = self.session.post(
                f"{self.base_url}/cubejs-api/v1/load",
                json={"query": query}
            )
            response.raise_for_status()
            result = response.json()
            
            if 'data' in result:
                print(f"✅ Query executed successfully, {len(result['data'])} rows returned")
                return result['data']
            else:
                print("❌ Query executed but no data returned")
                print(f"Response: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Query execution failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Error details: {e.response.text}")
            return None
    
    def save_to_csv(self, data, filename=None):
        """Save query results to CSV file in results directory"""
        if not data:
            print("❌ No data to save")
            return None
            
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"query_results_{timestamp}.csv"
        
        # Ensure filename is saved in results directory
        filepath = os.path.join(self.results_dir, filename)
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            print(f"✅ Results saved to: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Failed to save CSV: {e}")
            return None

def main():
    print("🧪 CUBE API Test Application")
    print("=" * 40)
    
    # Initialize client
    client = CubeAPIClient()
    
    # Test basic connectivity
    if not client.test_connection():
        print("Failed to connect to CUBE API. Make sure containers are running.")
        print("Run: docker-compose up -d")
        sys.exit(1)
    
    # Get JWT token for authentication
    print("\n🔐 Retrieving JWT token...")
    if not client.get_jwt_token():
        print("Failed to retrieve JWT token. Trying to access API anyway...")
        # Try with API secret as fallback
        client.session.headers.update({
            'Authorization': f'Bearer {client.api_secret}'
        })
    
    # Get metadata about available cubes
    meta_data = client.get_meta()
    if not meta_data:
        print("Failed to retrieve cube metadata. Check CUBE configuration.")
        sys.exit(1)
    
    print("\n📊 Testing Simple Count Queries")
    print("-" * 30)
    
    # Sample queries to test each cube
    test_queries = [
        {
            "name": "Events Count",
            "query": {
                "measures": ["DimEvents.count"]
            }
        },
        {
            "name": "Shops Count", 
            "query": {
                "measures": ["DimShops.count"]
            }
        },
        {
            "name": "Tickets Count",
            "query": {
                "measures": ["DimTickets.count"]
            }
        },
        {
            "name": "Orders Count and Total Value",
            "query": {
                "measures": ["FactOrders.count", "FactOrders.totalOrderValue"]
            }
        },
        {
            "name": "Orders by Payment Method",
            "query": {
                "measures": ["FactOrders.count"],
                "dimensions": ["FactOrders.paymentMethod"]
            }
        }
    ]
    
    # Execute test queries
    results = []
    for test_query in test_queries:
        print(f"\n🔍 Executing: {test_query['name']}")
        data = client.execute_query(test_query['query'])
        
        if data:
            results.append({
                "query_name": test_query['name'],
                "data": data
            })
            
            # Print first few results
            if len(data) <= 3:
                for row in data:
                    print(f"   Result: {row}")
            else:
                print(f"   First result: {data[0]}")
                print(f"   ... and {len(data)-1} more rows")
        
        # Small delay between queries
        time.sleep(0.5)
    
    # Save results to CSV files
    if results:
        print(f"\n💾 Saving {len(results)} query results to CSV files")
        print("-" * 40)
        
        for result in results:
            safe_name = result['query_name'].replace(' ', '_').replace('/', '_')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{timestamp}.csv"
            
            saved_file = client.save_to_csv(result['data'], filename)
            if saved_file:
                # Show a preview of the CSV
                try:
                    df = pd.read_csv(saved_file)
                    print(f"   📋 {saved_file}: {len(df)} rows, {len(df.columns)} columns")
                    if len(df.columns) <= 5:
                        print(f"      Columns: {list(df.columns)}")
                except Exception:
                    pass
    
    print(f"\n✨ Test completed successfully!")
    print(f"📁 All CSV files saved to: ./results/ directory")

if __name__ == "__main__":
    main()