import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import threading
from frontend import fendfile
import queue
st.set_page_config(layout="wide")

if 'receiveXY' not in st.session_state:
    st.session_state.receiveXY = "none"

if 'gets' not in st.session_state:
    st.session_state.gets = "Not Started"

if 'sets' not in st.session_state:
    st.session_state.sets = "Not Started"

if 'starttime' not in st.session_state:
    st.session_state.starttime = "0"

if 'selfstarttime' not in st.session_state:
    st.session_state.selfstarttime = "0"

if 'thread_queuegl' not in st.session_state:
    st.session_state.thread_queuegl = queue.Queue()

if 'thread_queuegs' not in st.session_state:
    st.session_state.thread_queuegs = queue.Queue()

if 'thread_queuesl' not in st.session_state:
    st.session_state.thread_queuesl = queue.Queue()

if 'thread_queuess' not in st.session_state:
    st.session_state.thread_queuess = queue.Queue()

def getcode(sq: queue.Queue, lq: queue.Queue, rid, role):
    try:
        erole = "r" if role[0]=="H" else "h"
        sq.put({"status": "showstat", "message": "Connecting"})
        print("GettingDriverloaded","https://codeshare.io/ugt"+rid+erole)
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--log-level=3")
        #options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--window-size=640,480")
        driver = webdriver.Chrome(options=options)
        driver.get("https://codeshare.io/ugt"+rid+erole)
        code_mirror_editor_div = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.CodeMirror")))
        print("GetDriverloaded","https://codeshare.io/ugt"+rid+erole)
        sq.put({"status": "showstat", "message": "Ready"})
        cur=""
        lastheartbeat=int(time.time() * 1000)
        gameon=True
        while gameon:
            initial_code = driver.execute_script("return arguments[0].CodeMirror.getValue();", code_mirror_editor_div)
            if (initial_code!=cur):
                if initial_code in [str(i) for i in range(255)]:
                    cur=initial_code
                    sq.put({"status": "running", "message": cur})
                if initial_code[:5] == "ready":
                    sq.put({"status": "starttime", "message": initial_code.split()[1]})
            try:
                message_from_thread = lq.get_nowait()
                print(f"Main: Received from queue by get thread: {message_from_thread}")
                lastheartbeat=int(message_from_thread["time"])
                if (message_from_thread["type"]=="disconnect"):
                    print(f"Disconnecting get thread: {message_from_thread}")
                    sq.put({"status": "showstat", "message": "Disconnected"})
                    driver.quit()
                    return
            except queue.Empty:
                if (int(time.time() * 1000)-lastheartbeat>5000):
                    print("Heartbeat Timeout Disconnect Get")
                    if driver is not None: driver.quit()
                    return
    except:
        print("Force disconnect get")
        if driver is not None: driver.quit()

def setcode(sq: queue.Queue, lq: queue.Queue, rid, role):
    try:
        roleshort = "h" if role[0]=="H" else "r"
        print("SettingDriverloaded","https://codeshare.io/ugt"+rid+roleshort)
        sq.put({"status": "showstat", "message": "Connecting"})
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Optional: run headless
        options.add_argument("--log-level=3")
        #options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-browser-side-navigation")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--window-size=640,480")
        driver = webdriver.Chrome(options=options)
        driver.get("https://codeshare.io/ugt"+rid+roleshort)
        code_mirror_editor_div = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.CodeMirror")))
        print("SetDriverloaded","https://codeshare.io/ugt"+rid+roleshort)
        sq.put({"status": "showstat", "message": "Ready"})
        starttime=str(int(time.time() * 1000))
        driver.execute_script("arguments[0].CodeMirror.setValue(arguments[1]);", code_mirror_editor_div, "ready "+starttime)
        sq.put({"status": "starttime", "message": starttime})
        lastheartbeat=int(time.time() * 1000)
        gameon=True
        while gameon:
            try:
                message_from_thread = lq.get_nowait()
                print(f"Main: Received from queue by big set thread: {message_from_thread}")
                lastheartbeat=int(message_from_thread["time"])
                if (message_from_thread["type"]=="move"):
                    driver.execute_script("arguments[0].CodeMirror.setValue(arguments[1]);", code_mirror_editor_div, message_from_thread["loc"])
                if (message_from_thread["type"]=="disconnect"):
                    print(f"Disconnecting set thread: {message_from_thread}")
                    sq.put({"status": "showstat", "message": "Disconnected"})
                    driver.quit()
                    gameon=False
                    return
            except queue.Empty:
                if (int(time.time() * 1000)-lastheartbeat>5000):
                    print("Heartbeat Timeout Disconnect Set")
                    if driver is not None: driver.quit()
                    return
    except:
        print("Force disconnect set")
        if driver is not None: driver.quit()

def pqget():
    try:
        while not st.session_state.thread_queuegs.empty(): #get
            message_from_thread = st.session_state.thread_queuegs.get_nowait()
            print(f"Main: Received from get queue: {message_from_thread}")
            if message_from_thread["status"]=="running":
                st.session_state.receiveXY = message_from_thread["message"]
            elif message_from_thread["status"]=="showstat":
                st.session_state.gets = message_from_thread["message"]
            elif message_from_thread["status"]=="starttime":
                if (st.session_state.selfstarttime!="0"):
                    st.session_state.starttime = str(max(int(message_from_thread["message"]),int(st.session_state.selfstarttime))+5000)
    except queue.Empty:
        pass
    try:
        while not st.session_state.thread_queuess.empty(): #set
            message_from_thread = st.session_state.thread_queuess.get_nowait()
            print(f"Main: Received from set queue: {message_from_thread}")
            if message_from_thread["status"]=="showstat":
                st.session_state.sets = message_from_thread["message"]
            elif message_from_thread["status"]=="starttime":
                st.session_state.selfstarttime = message_from_thread["message"]
    except queue.Empty:
        pass

def pqset(value):
    if value is not None:
        st.session_state.thread_queuesl.put(value)
        st.session_state.thread_queuegl.put(value)

def toXY(stri):
    return({"x": str(int(stri)//15+1),"y": str(int(stri)%15+1)})

if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
    st.session_state.room_code = ""
    st.session_state.role = ""

# --- Display the Form or Results ---
if not st.session_state.form_submitted:
    st.title("Glitch Tag")
    st.write("A game using codespace.io as a means of communication, by Ulfred and Eric")
    st.markdown("---") # A separator for visual appeal
    # Use st.form for atomic submission and to clear inputs on submit
    with st.form("room_join_form", clear_on_submit=True):
        st.write("Please enter the room details:")

        # Text input for Room Code
        room_code_input = st.text_input(
            "Room Code",
            placeholder="e.g., ABCD",
            help="Enter the unique code for the room you wish to join.",
            max_chars=5
        )

        # Selectbox for Gender
        role = st.selectbox(
            "Select Role",
            ["Hunter","Runner"],
            index=0, # Default selection: "Prefer not to say"
            help="Choose your role."
        )

        # Submit button for the form
        submit_button = st.form_submit_button("Join Room")

        # Logic when the form is submitted
        if submit_button:
            if not room_code_input:
                st.error("Please enter a Room Code.")
            else:
                # Store the submitted data in session state
                st.session_state.room_code = room_code_input
                st.session_state.role = role
                st.session_state.form_submitted = True
                st.rerun()
else:
    if 'receiveXYthread' not in st.session_state:
        st.session_state.receiveXYthread = True
        thread = threading.Thread(target=getcode, args=(st.session_state.thread_queuegs, st.session_state.thread_queuegl, st.session_state.room_code,st.session_state.role))
        thread.start()
        thread2 = threading.Thread(target=setcode, args=(st.session_state.thread_queuess, st.session_state.thread_queuesl,st.session_state.room_code,st.session_state.role))
        thread2.start()
    pqget()
    props = {'epos': toXY(st.session_state.receiveXY) if st.session_state.receiveXY!="none" else "none", 'rid': st.session_state.room_code,
             'role':st.session_state.role, "sets": st.session_state.sets, "gets": st.session_state.gets, "starttime": st.session_state.starttime}
    value = fendfile(**props,key="123")
    pqset(value)
    st.write('Received from component: ', value)