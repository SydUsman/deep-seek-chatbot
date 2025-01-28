import streamlit as st
from openai import OpenAI

# Track chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! How can I help you today?"}
    ]

api_key = st.secrets["api_key"]

def extract_think_content(response: str) -> tuple:
    """
    Extracts content between <think> and </think> tags and the remaining response.
    """
    think_start = response.find("<think>")
    think_end = response.find("</think>")
    
    if think_start != -1 and think_end != -1:
        think_content = response[think_start + len("<think>") : think_end].strip()
        remaining_response = response[:think_start] + response[think_end + len("</think>") :].strip()
        return think_content, remaining_response
    return None, response

def deepseek_chat(api_key: str, messages: list) -> str:
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        response = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[{"role": "system", "content": "You are a helpful assistant"}, *messages],
            stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error occurred: {str(e)}")
        return ""

def main():
    st.header('DeepSeek - Powered by GROQ')   
    st.markdown("Developed by Syed Usman Hassan - [LinkedIn](https://www.linkedin.com/in/syed-usman-hassan-naqvi/)")
    
    
    # Sidebar with user guide
    with st.sidebar:
        st.header("🤖 DeepSeek Chatbot")        
        st.markdown("""         
        - This is a custom chatbot powered by GROQ.
        - Click 'Reset Chat' to start a new conversation.
               
        """)
        
        if st.button("Reset Chat"):
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! How can I help you today?"}
            ]
            st.rerun()
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Handle user input
    if prompt := st.chat_input("What's on your mind?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.write(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = deepseek_chat(api_key, st.session_state.messages)
                
                # Extract <think> content and remaining response
                think_content, remaining_response = extract_think_content(response)
                
                # Display thinking process in a div-like container
                if think_content:
                    st.markdown(
                        f'<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-bottom: 10px;">'
                        f'<strong>Thinking:</strong><br>{think_content}'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                
                # Display the remaining response
                st.write(remaining_response)
                
                # Append the full response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()