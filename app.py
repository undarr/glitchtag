import streamlit as st
import streamlit.components.v1 as components
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import threading
import sys
from frontend import fendfile
from datetime import datetime
import queue
st.set_page_config(layout="wide")

if 'codeshare' not in st.session_state:
    st.session_state.codeshare = "123"

if 'thread_queue' not in st.session_state:
    st.session_state.thread_queue = queue.Queue()

if 'thread_queue2' not in st.session_state:
    st.session_state.thread_queue2 = queue.Queue()

def getcode(q: queue.Queue):
    print("GettingDriverloaded")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Optional: run headless
    options.add_argument("--log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--window-size=640,480")
    driver = webdriver.Chrome(options=options)
    driver.get("https://codeshare.io/ueue")
    code_mirror_editor_div = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.CodeMirror")))
    cur = ""
    print("GetDriverloaded")
    while True:
        initial_code = driver.execute_script("return arguments[0].CodeMirror.getValue();", code_mirror_editor_div)
        if (initial_code!=cur):
            if initial_code in [str(i) for i in range(255)]:
                cur=initial_code
                q.put({"status": "running", "message": cur})
                print("Added new")
                #time.sleep(0.1)

def setcode(q: queue.Queue):
    print("SettingDriverloaded")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Optional: run headless
    options.add_argument("--log-level=3")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-browser-side-navigation")
    options.add_argument("--disable-features=VizDisplayCompositor")
    options.add_argument("--window-size=640,480")
    driver = webdriver.Chrome(options=options)
    driver.get("https://codeshare.io/ueues")
    code_mirror_editor_div = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.CodeMirror")))
    cur = ""
    print("SetDriverloaded")
    while True:
        try:
            while not q.empty():
                message_from_thread = q.get_nowait()
                print(f"Main: Received from queue by thread: {message_from_thread}")
                if (message_from_thread["message"]):
                    driver.execute_script("arguments[0].CodeMirror.setValue(arguments[1]);", code_mirror_editor_div, message_from_thread["message"])
        except queue.Empty:
            pass # Queue is empty, nothing to process

if 'codesharethread' not in st.session_state:
    st.session_state.codesharethread = False
    thread = threading.Thread(target=getcode, args=(st.session_state.thread_queue,))
    thread.start()
    thread2 = threading.Thread(target=setcode, args=(st.session_state.thread_queue2,))
    thread2.start()
    st.success("Thread started. Updates should appear live.")

if 'startloc' not in st.session_state:
    st.session_state.startloc = "0"

def pqget():
    try:
        while not st.session_state.thread_queue.empty():
            message_from_thread = st.session_state.thread_queue.get_nowait()
            print(f"Main: Received from queue: {message_from_thread}")
            st.session_state.codeshare = message_from_thread["message"]
    except queue.Empty:
        pass # Queue is empty, nothing to process

def pqset(value):
    st.session_state.thread_queue2.put({"status": "running", "message": value})

def toXY(stri):
    return({"x": str(int(stri)//15+1),"y": str(int(stri)%15+1)})
pqget()
props = {'runner': toXY(st.session_state.codeshare)}
value = fendfile(**props,key="123")
pqset(value)
st.header('Streamlit4')
st.write('Received from component: ', value)
