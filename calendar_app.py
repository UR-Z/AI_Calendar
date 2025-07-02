import streamlit as st
import pandas as pd
import datetime
from dateutil import parser
import os
from dotenv import load_dotenv
from tools import calendar_intent_agent

import re
import json

load_dotenv()

CSV_FILE = 'calendar_events.csv'

# --- Helper Functions ---
def load_events():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df = df.sort_values('date')
        return df
    else:
        return pd.DataFrame(columns=['date', 'event'])

def save_events(df):
    df = df.sort_values('date')
    df.to_csv(CSV_FILE, index=False)

def add_event(date, event):
    df = load_events()
    df = pd.concat([df, pd.DataFrame([{'date': date, 'event': event}])], ignore_index=True)
    save_events(df)

def edit_event(index, new_date, new_event):
    df = load_events()
    df.at[index, 'date'] = new_date
    df.at[index, 'event'] = new_event
    save_events(df)

def delete_event(index):
    df = load_events()
    df = df.drop(index).reset_index(drop=True)
    save_events(df)

def extract_json_from_text(text):
    match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    try:
        return json.loads(text)
    except Exception:
        return None

# --- Streamlit UI ---
st.set_page_config(page_title="Multimodal Calendar", layout="wide")
st.title("📅 Multimodal Calendar Assistant")

col1, col2 = st.columns([2, 1])

# --- Calendar View ---
with col1:
    st.header("Month Overview")
    today = datetime.date.today()
    month_offset = st.session_state.get('month_offset', 0)
    if 'month_offset' not in st.session_state:
        st.session_state['month_offset'] = 0

    def change_month(offset):
        st.session_state['month_offset'] += offset

    # Month navigation
    prev, next = st.columns([1,1])
    with prev:
        if st.button('⬅️ Previous Month'):
            change_month(-1)
    with next:
        if st.button('Next Month ➡️'):
            change_month(1)

    # Calculate current month to display
    display_month = (today.replace(day=1) + pd.DateOffset(months=st.session_state['month_offset'])).date()
    st.subheader(display_month.strftime('%B %Y'))

    # Load and filter events for the month
    df = load_events()
    if not df.empty and pd.api.types.is_datetime64_any_dtype(df['date']):
        month_events = df[(df['date'].dt.month == display_month.month) & (df['date'].dt.year == display_month.year)]
    else:
        month_events = pd.DataFrame(columns=df.columns)

    # Render calendar grid
    import calendar
    cal = calendar.Calendar()
    month_days = list(cal.itermonthdates(display_month.year, display_month.month))
    week_rows = [month_days[i:i+7] for i in range(0, len(month_days), 7)]

    st.write("")
    for week in week_rows:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if not month_events.empty and pd.api.types.is_datetime64_any_dtype(month_events['date']):
                day_events = month_events[month_events['date'].dt.date == day]
            else:
                day_events = pd.DataFrame(columns=month_events.columns)
            label = f"{day.day}" if day.month == display_month.month else f"*{day.day}*"
            with cols[i]:
                st.markdown(f"**{label}**")
                for idx, row in day_events.iterrows():
                    st.markdown(f"- {row['event']}")

# --- Chat & Image Upload ---
with col2:
    st.header("Chat & Event Management")
    st.write("Add, edit, or delete events. Upload a fridge calendar image to extract events.")

    # Chat interface
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []

    # Load LLM prompt for chat intent extraction
    with open('calendar_prompt.txt', 'r') as f:
        CALENDAR_PROMPT = f.read()

    user_input = st.text_input("Type a command (e.g., 'Add event on July 10: Doctor appointment'):")
    if st.button("Send") and user_input:
        try:
            agent_result = calendar_intent_agent(user_input)
            agent_response = getattr(agent_result, "text", agent_result)
            llm_json = extract_json_from_text(agent_response)
            if not llm_json:
                st.session_state['chat_history'].append((user_input, "❌ LLM did not return valid JSON. Try rephrasing your request."))
            else:
                if isinstance(llm_json, dict):
                    events = [llm_json]
                else:
                    events = llm_json
                chat_response = ""
                for event_obj in events:
                    intent = event_obj.get('intent', 'unknown')
                    date_str = event_obj.get('date')
                    start_date = event_obj.get('start_date')
                    end_date = event_obj.get('end_date')
                    event = event_obj.get('event')
                    idx = event_obj.get('index')
                    if intent == 'add' and event:
                        try:
                            if start_date and end_date:
                                start = parser.parse(start_date).date()
                                end = parser.parse(end_date).date()
                                for single_date in pd.date_range(start, end):
                                    add_event(single_date.date(), event)
                                chat_response += f"✅ Added multi-day event: {event} ({start} to {end})\n"
                            elif date_str:
                                date = parser.parse(date_str).date()
                                add_event(date, event)
                                chat_response += f"✅ Added event on {date}: {event}\n"
                            else:
                                chat_response += f"❌ No date provided for event: {event}\n"
                        except Exception as e:
                            chat_response += f"❌ Could not parse date: {e}\n"
                    elif intent == 'edit' and idx is not None and event:
                        try:
                            if start_date and end_date:
                                start = parser.parse(start_date).date()
                                end = parser.parse(end_date).date()
                                edit_event(int(idx), start, event)
                                chat_response += f"✏️ Edited event {idx} to {event} ({start} to {end})\n"
                            elif date_str:
                                date = parser.parse(date_str).date()
                                edit_event(int(idx), date, event)
                                chat_response += f"✏️ Edited event {idx} to {date}: {event}\n"
                            else:
                                chat_response += f"❌ No date provided for edit event: {event}\n"
                        except Exception as e:
                            chat_response += f"❌ Could not edit event: {e}\n"
                    elif intent == 'delete' and idx is not None:
                        try:
                            delete_event(int(idx))
                            chat_response += f"🗑️ Deleted event {idx}\n"
                        except Exception as e:
                            chat_response += f"❌ Could not delete event: {e}\n"
                    elif intent == 'unknown':
                        chat_response += "❓ Command not recognized. Try: 'Add event on July 10: Doctor appointment'\n"
                st.session_state['chat_history'].append((user_input, chat_response.strip()))
        except Exception as e:
            st.session_state['chat_history'].append((user_input, f"❌ Agent error: {e}"))

    # Display chat history
    for user, resp in st.session_state['chat_history'][-10:]:
        st.markdown(f"**You:** {user}")
        st.markdown(f"**Bot:** {resp}")

    # Image upload
    st.subheader("Upload Fridge Calendar Image")
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        if st.button("Extract Events from Image"):
            file_bytes = uploaded_file.read()
            files = [{
                'name': uploaded_file.name,
                'content': file_bytes.encode('base64') if isinstance(file_bytes, str) else file_bytes,
            }]
            import base64
            files[0]['content'] = base64.b64encode(file_bytes).decode('utf-8')
            prompt = CALENDAR_PROMPT + "\nExtract all events from this image."
            try:
                agent_result = calendar_intent_agent(prompt)
                agent_response = getattr(agent_result, "text", agent_result)
                llm_json = extract_json_from_text(agent_response)
                if not llm_json:
                    st.error("LLM did not return valid JSON for image extraction.")
                else:
                    if isinstance(llm_json, dict):
                        events = [llm_json]
                    else:
                        events = llm_json
                    added = 0
                    for event_obj in events:
                        intent = event_obj.get('intent', 'unknown')
                        event = event_obj.get('event')
                        date_str = event_obj.get('date')
                        start_date = event_obj.get('start_date')
                        end_date = event_obj.get('end_date')
                        if intent == 'add' and event:
                            try:
                                if start_date and end_date:
                                    start = parser.parse(start_date).date()
                                    end = parser.parse(end_date).date()
                                    for single_date in pd.date_range(start, end):
                                        add_event(single_date.date(), event)
                                        added += 1
                                elif date_str:
                                    date = parser.parse(date_str).date()
                                    add_event(date, event)
                                    added += 1
                            except Exception:
                                continue
                    st.success(f"Extracted and added {added} events from image.")
            except Exception as e:
                st.error(f"Failed to extract events: {e}")

# --- Event Table ---
st.subheader("All Events (sorted by date)")
df = load_events()
st.dataframe(df.reset_index().rename(columns={'index':'ID'})) 