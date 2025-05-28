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

def my_threaded_function(q: queue.Queue):
    print("Thread: Started")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Optional: run headless
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)
    driver.get("https://codeshare.io/ueue")
    code_mirror_editor_div = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.CodeMirror")))
    cur = ""
    print("Driverloaded")
    while True:
        initial_code = driver.execute_script("return arguments[0].CodeMirror.getValue();", code_mirror_editor_div)
        if (initial_code!=cur):
            cur=initial_code
            q.put({"status": "running", "message": cur})
            print("Added new")
        #time.sleep(0.1)
    q.put({"status": "progress", "message": "56"})
    time.sleep(3) # Simulate more work
    q.put({"status": "completed", "message": "67"})
    print("Thread: Finished and put final message in queue")

if 'codeshareget' not in st.session_state:
    st.session_state.codeshareget = False
    thread = threading.Thread(target=my_threaded_function, args=(st.session_state.thread_queue,))
    thread.start()
    st.success("Thread started. Updates should appear live.")

def pq():
    try:
        while not st.session_state.thread_queue.empty():
            message_from_thread = st.session_state.thread_queue.get_nowait()
            print(f"Main: Received from queue: {message_from_thread}")
            st.session_state.codeshare = message_from_thread["message"]
    except queue.Empty:
        pass # Queue is empty, nothing to process

def toXY(stri):
    return({"x": str(int(stri)//15+1),"y": str(int(stri)%15+1)})
pq()
props = {'runner': toXY(st.session_state.codeshare)}
value = fendfile(**props,key="123")
st.header('Streamlit')
st.write('Received from component: ', value)
