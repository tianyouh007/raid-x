"""
Basic tests for RAID-X framework
"""

import pytest
import json
import os

def test_config_loading():
    """Test configuration file loading"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
    
    assert os.path.exists(config_path), "Config file should exist"
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    assert 'framework' in config
    assert 'infrastructure' in config
    assert 'compliance_rules' in config
    assert config['framework']['name'] == 'RAID-X'

def test_lambda_functions_exist():
    """Test that all Lambda function directories exist"""
    lambda_dir = os.path.join(os.path.dirname(__file__), '..', 'lambda_functions')
    
    expected_functions = ['r3_engine', 'arsm', 'tad_x', 'data_ingestion', 'orchestrator']
    
    for func in expected_functions:
        func_dir = os.path.join(lambda_dir, func)
        assert os.path.exists(func_dir), f"Lambda function directory {func} should exist"
        
        main_file = os.path.join(func_dir, 'main.py')
        assert os.path.exists(main_file), f"Main file for {func} should exist"

def test_stack_files_exist():
    """Test that all stack files exist"""
    stack_dir = os.path.join(os.path.dirname(__file__), '..', 'raid_x_stack')
    
    expected_files = [
        'raid_x_stack.py',
        'infrastructure.py',
        'lambda_construct.py',
        'stepfunctions_construct.py',
        'api_construct.py'
    ]
    
    for file in expected_files:
        file_path = os.path.join(stack_dir, file)
        assert os.path.exists(file_path), f"Stack file {file} should exist"

if __name__ == '__main__':
    pytest.main([__file__])
