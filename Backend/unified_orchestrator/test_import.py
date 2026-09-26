print("Starting imports...")

try:
    print("Importing PyPDF2...")
    import PyPDF2
    print("Importing json, re, sys, os...")
    import json
    import re
    import sys
    import os
    print("Importing llama_cpp...")
    from llama_cpp import Llama
    print("Importing requests...")
    import requests
    print("Importing streamlit...")
    import streamlit as st
    print("Importing classifier...")
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
    import classifier
    print("Done importing classifier.")
except Exception as e:
    print(f"Error: {e}")

print("Done with tests.")
