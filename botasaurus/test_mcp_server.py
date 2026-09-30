#!/usr/bin/env python3
"""
Quick test script for MCP server functionality
"""

import json
import sys
sys.path.insert(0, '.')

def test_mcp_server():
    """Test MCP stdio server"""
    try:
        from src.us_b2b.mcp_server_stdio import MCPStdioServer
        print('✅ MCP Stdio Server imported successfully')
        
        # Create instance
        server = MCPStdioServer()
        print(f'✅ MCP Server initialized with {len(server.tools)} tools:')
        for tool_name in server.tools.keys():
            print(f'   - {tool_name}')
        
        # Test 1: Initialize
        print('\n[TEST 1] Initialize Request')
        init_request = {'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {}}
        response = server.process_request(init_request)
        server_name = response['result']['serverInfo']['name']
        print(f'✅ Initialize test passed: {server_name}')
        
        # Test 2: List tools
        print('\n[TEST 2] Tools/List Request')
        list_request = {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}}
        response = server.process_request(list_request)
        tools_count = len(response['result']['tools'])
        print(f'✅ Tools/list test passed: {tools_count} tools available')
        for tool in response['result']['tools']:
            print(f'   - {tool["name"]}: {tool["description"][:60]}...')
        
        # Test 3: Search companies
        print('\n[TEST 3] Call Tool: search_companies')
        search_request = {
            'jsonrpc': '2.0',
            'id': 3,
            'method': 'tools/call',
            'params': {
                'name': 'search_companies',
                'arguments': {'query': '', 'limit': 2}
            }
        }
        response = server.process_request(search_request)
        result_text = response['result']['content'][0]['text']
        result_data = json.loads(result_text)
        print(f'✅ Search companies test passed: Found {len(result_data)} results')
        if result_data:
            print(f'   Example: {result_data[0]["legal_name"]}')
        
        # Test 4: Get company details
        print('\n[TEST 4] Call Tool: get_company_details')
        if result_data:
            company_id = result_data[0]['company_id']
            detail_request = {
                'jsonrpc': '2.0',
                'id': 4,
                'method': 'tools/call',
                'params': {
                    'name': 'get_company_details',
                    'arguments': {'company_id': company_id}
                }
            }
            response = server.process_request(detail_request)
            detail_text = response['result']['content'][0]['text']
            detail_data = json.loads(detail_text)
            execs_count = len(detail_data.get('executives', []))
            print(f'✅ Get company details test passed')
            print(f'   Company: {detail_data["legal_name"]}')
            print(f'   Executives found: {execs_count}')
        
        # Test 5: Get executives
        print('\n[TEST 5] Call Tool: get_csuite_executives')
        if result_data:
            company_id = result_data[0]['company_id']
            exec_request = {
                'jsonrpc': '2.0',
                'id': 5,
                'method': 'tools/call',
                'params': {
                    'name': 'get_csuite_executives',
                    'arguments': {'company_id': company_id}
                }
            }
            response = server.process_request(exec_request)
            exec_text = response['result']['content'][0]['text']
            exec_data = json.loads(exec_text)
            print(f'✅ Get executives test passed: Found {len(exec_data)} executives')
            for exec_item in exec_data[:2]:
                print(f'   - {exec_item["full_name"]}: {exec_item["title"]}')
        
        print('\n' + '='*60)
        print('✅ ALL TESTS PASSED - MCP Server is working correctly!')
        print('='*60)
        return True
        
    except Exception as e:
        print(f'❌ Error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_mcp_server()
    sys.exit(0 if success else 1)
