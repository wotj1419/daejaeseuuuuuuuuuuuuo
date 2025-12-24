import os
import re
import sys

def check_tags(file_content):
    # Extract template section
    template_match = re.search(r'<template>(.*)</template>', file_content, re.DOTALL)
    if not template_match:
        return []
    
    template = template_match.group(1)
    
    # regex for tags, including attributes and self-closing
    # group 1: opening tag name
    # group 2: self-closing marker (/)
    # group 3: closing tag name
    tag_regex = re.compile(r'<([a-zA-Z0-9-]+)(?:[^>]*?(/)?)>|</([a-zA-Z0-9-]+)>')
    
    void_elements = {'br', 'hr', 'img', 'input', 'link', 'meta', 'area', 'base', 'col', 'embed', 'param', 'source', 'track', 'wbr'}
    
    stack = []
    errors = []
    
    for match in tag_regex.finditer(template):
        opening_name, self_closing, closing_name = match.groups()
        
        if opening_name:
            if opening_name.lower() in void_elements or self_closing:
                continue
            stack.append((opening_name, match.start()))
        elif closing_name:
            if not stack:
                errors.append(f"Closing tag </{closing_name}> at {match.start()} has no opening tag.")
                continue
            
            top_name, top_start = stack.pop()
            if top_name != closing_name:
                errors.append(f"Mismatched tag: Opening <{top_name}> at {top_start}, Closing </{closing_name}> at {match.start()}.")
                # Attempt to recover by popping until we find a match or empty
                while stack and stack[-1][0] != closing_name:
                    stack.pop()
                if stack:
                    stack.pop()
    
    for name, start in stack:
        errors.append(f"Unclosed tag <{name}> starting at {start}.")
    
    return errors

if __name__ == '__main__':
    path = r'c:\Users\SSAFY\Desktop\SSAFY_GD\daejaeseuuuuuuuuuuuuo\frontend\src\views\boards\FriendBoardView.vue'
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    errs = check_tags(content)
    if errs:
        for e in errs:
            print(e)
    else:
        print("No issues found in template.")
