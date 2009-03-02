#!/usr/bin/pyton
""""
 take a mysql schema file and extract table col names

"""
import sys
import re

def read_file(file_ob):
    # read the mysql schema file into a single txet blob
    f = open(file_ob,'r')
    schema_content = f.read()
    f.close()
    return schema_content

def strip_comments(infile):
    comment1 = re.compile("\/\*.*\*\/\;") 
    # detects comments of the form /* comment */;
    return comment1.sub('',infile)

def strip_newlines(infile):
    newline = re.compile("\n") 
    # detects comments of the form /* comment */;
    return newline.sub('',infile)    
    
def parse_commands(infile):
    # splits mysql commands into a list of commands
    # assumes that each command ends with ';'
    l_commands = infile.split(";")
    return l_commands
        
def get_create_table_commands(l_commands):
    create_table = re.compile("\A(CREATE TABLE)",re.IGNORECASE) 
    # detects comments of the form /* comment */;
    l_create_tables = []
    for command in l_commands:
        if create_table.match(command):
            l_create_tables.append(command)
    return  l_create_tables       
        
def get_table_name(create_command):
    # dumb function, assumes table name is the 3rd word in the command
    words = create_command.split()
    table_name = words[2]
    return table_name

def get_table_names(l_create_tables):
    l_table_names = []
    for command in l_create_tables:
        table_name = get_table_name(command)
        l_table_names.append(table_name)
    return l_table_names

def get_col_names(create_command):
    # this is an add hoc function that is very fragile
    l_cols  = []
    command_parts = create_command.split(',')
    first_part = command_parts[0]
    col_parts = command_parts[1:]
    #
    # deal with the first col
    first_col_part = first_part.split("(")[1] # CREATE TABLE 'name' ( this bit here
    first_col = first_col_part.split()[0]
    l_cols.append(first_col)
    # 
    # deal with the other cols
    # want to stop processing if the command line has got any of the following:
    #  PRIMARY KEY
    #  UNIQUE KEY
    #  KEY
    command_length = len(col_parts) # in case there are no keys defined we need a halting condition
    mysql_keys = re.compile("(PRIMARY KEY|UNIQUE KEY|KEY)",re.IGNORECASE)
    current_col_candidate = col_parts[0]
    current_length = 0
    x = 0
    while (not mysql_keys.search(current_col_candidate) )and (x != command_length):
        col = col_parts[x].split()[0]
        l_cols.append(col)  

        # stop overrunning the end of the cols index
        if x < command_length - 1:
            current_col_candidate = col_parts[x+1]
        else:
            pass
        x = x + 1
    return l_cols
        
def get_all_col_names(l_create_tables):
    for create_command in l_create_tables:
        table_name = get_table_name(create_command)
        l_cols = get_col_names(create_command)
        print table_name, l_cols
        
def get_table_cols_dict(l_create_tables):
    table_cols = {}
    for command in l_create_tables:
        table_name = get_table_name(command)
        cols = get_col_names(command)
        table_cols[table_name] = cols
    return table_cols
        
def main():
    file_ob = sys.argv[1]
    schema = read_file(file_ob)
    schema_no_comments = strip_comments(schema)
    schema_no_neline = strip_newlines(schema_no_comments)
    l_commands = parse_commands(schema_no_neline)
    l_create_tables = get_create_table_commands(l_commands)
    table_cols = get_table_cols_dict(l_create_tables)
    print table_cols

if __name__ == "__main__":
    main()