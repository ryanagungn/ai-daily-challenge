import sqlite3

def fetch_user_profile(user_id, default_roles=[]):
    # Issue 1 (Code Smell): Mutable default argument
    # Issue 2 (Security): SQL Injection vulnerability via string formatting
    db = sqlite3.connect("production.db")
    cursor = db.cursor()
    
    query = "SELECT id, name, email, role FROM users WHERE id = '%s'" % user_id
    cursor.execute(query)
    record = cursor.fetchone()
    
    # Issue 3 (Resource Leak): Database connection is not closed (missing try-finally or context manager)
    return record

def find_common_elements(list1, list2):
    # Issue 4 (Performance): Inefficient O(N*M) nested loop search instead of set intersection O(N+M)
    common = []
    for item1 in list1:
        for item2 in list2:
            if item1 == item2 and item1 not in common:
                common.append(item1)
    return common

def parse_config(config_str):
    # Issue 5 (Security): Insecure eval on untrusted user input
    return eval(config_str)
