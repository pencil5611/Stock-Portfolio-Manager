import streamlit as st
import pandas as pd
from features.portfolio_manager import render_portfolio_manager

def show():
    render_portfolio_manager()