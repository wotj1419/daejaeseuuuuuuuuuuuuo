import os
import re

def check_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    template_match = re.search(r'<template>(.*)</template>', content, re.DOTALL)
    if not template_match:
        return
    
    template = template_match.group(1)
    
    # Strip comments
    template = re.sub(r'<!--.*?-->', '', template, flags=re.DOTALL)
    
    # Find all tags
    # Handle self-closing tags like <input />, <img /> etc.
    # Void elements in HTML
    void_elements = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
    
    tag_pattern = re.compile(r'<(/?)([a-zA-Z0-9-]+)([^>]*?)(/?)>')
    
    stack = []
    lines = template.split('\n')
    
    # Track line numbers
    pos = 0
    for line_num, line in enumerate(lines, 1):
        for match in tag_pattern.finditer(line):
            is_closing = match.group(1) == '/'
            tag_name = match.group(2).lower()
            is_self_closing = match.group(4) == '/' or tag_name in void_elements
            
            if is_self_closing:
                if is_closing:
                    print(f"[{file_path}:{line_num}] Invalid self-closing closing tag </{tag_name}/>")
                continue
            
            if is_closing:
                if not stack:
                    print(f"[{file_path}:{line_num}] Unexpected closing tag </{tag_name}> (no opening tag)")
                else:
                    top_name, top_line = stack.pop()
                    if top_name != tag_name:
                        print(f"[{file_path}:{line_num}] Mismatched tag: expected </{top_name}> (from line {top_line}), found </{tag_name}>")
                        # recover
                        # stack.append((top_name, top_line)) # Don't push back, just keep going
            else:
                stack.append((tag_name, line_num))
    
    for name, line in stack:
        print(f"[{file_path}:{line}] Unclosed tag <{name}>")

def main():
    root_dir = r'frontend\src'
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.vue'):
                check_file(os.path.join(root, file))

if __name__ == '__main__':
    main()
