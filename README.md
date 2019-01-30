# CM Test Runner

This is a test runner for API testing & unit testing available for django projects

## Getting Started
python3 is needed for this package
```
pip install cmtestrunner
```
### Prerequisites
```
TEST_PAYLOAD_PATH = test payload directory
TEST_DATA_PATH = test data directory
TEST_RUNNER = 'cmtestrunner.CMTestRunner'
TEST_APPS => list of apps to be tested 
```
set these variables in django settings file

### Available APIs
```
TestRunner =>  'import as  from cmtestrunner import TestRunner'
```
```
parse_list_string
```
```  
request_response_formatter
```
``` 
process_request_response
```
```
set_lang_header
```
```
set_auth_header
```
