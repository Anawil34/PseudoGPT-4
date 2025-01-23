import streamlit as st
import src.scraper as sc
import src.ai as ai
import src.prompt as pr

limit_api_called = 5
limit_words = 1000
full_unknown_bulletpoint = ""
all_article = ""
behavior_prompt = ""
n_pages = 3
n_results = 5


def btnClearMsg():
    del st.session_state.messages[:]


def sendChatToGPT(prompt, showInput=True, showOutput=True):
    st.session_state.messages.append(
        {"role": "user", "content": prompt, "show": showInput})
    response = ai.chatWithChatGPT(
        st.session_state.model, st.session_state.messages)
    st.session_state.messages.append(
        {"role": "assistant", "content": response, "show": showOutput})
    sum_token = ai.calculate_sum_token(prompt, response)
    st.session_state.tokenCount += sum_token
    return response


def remindBot():
    response = sendChatToGPT(pr.remind_bot, False, True)
    return response


if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello Human, How can I help you", "show": True}]
if "tokenCount" not in st.session_state:
    st.session_state["tokenCount"] = 0
if "topic" not in st.session_state:
    st.session_state["topic"] = ""
if "model" not in st.session_state:
    st.session_state.model = "gpt-3.5-turbo-0301"
if "role" not in st.session_state:
    st.session_state.role = ""


with st.sidebar:
    st.header("Required Input")
    with st.form("input_form"):
        api_key = st.text_input("API_KEY:")
        model_options = ["gpt-3.5-turbo", "o1-mini", "gpt-4o-mini"]
        st.session_state.model = st.selectbox("Select Model:", model_options)

        role_options = ["Researcher", "Tech Engineer", "Software Engineer",
                        "Marketing Director", "Actuary", "News Reporter", "Other"]
        selected_option = st.selectbox("Select role:", role_options)
        if selected_option == "Other":
            role = st.text_input("Enter the role", key="text_input_key")
        else:
            role = selected_option
        topic = st.text_input("Please input research the topic: ")
        submitted = st.form_submit_button("Submit")
    st.header("Optional Input")
    with st.form("optional_input_form"):
        n_pages = st.slider('number of page searched:', 1, 10, n_pages)
        n_results = st.slider('number of result provide to the model', 1, 10, n_results)
        st.form_submit_button('Submit')

    bot_behaviors = st.multiselect('Bot behavior',
                                   ['normal', 'make_assumption'], ['normal'])
    st.write(
        f"Current Token Used: {st.session_state.tokenCount}")
    st.write(
        f"Current Price: {st.session_state.tokenCount * 0.002 * 35 / 1000} Baht")

st.title("💬 Psudo GPT-4 (WebScraper AI)")
st.markdown(
    "This AI is Using Webscraper to retrieve the top 5 google search based on the subject provided and assist you based on the data gathered. (use remind button when the Bot started to hallucinate)")

if submitted and topic and topic != '' and topic != st.session_state.topic:
    ai.setAPI(api_key=api_key)
    # role = ai.get_suitable_role(topic)
    with st.spinner("Fetching......"):
        del st.session_state.messages[:]
        google_links = sc.perform_google_search(topic, n_pages=n_pages, n_results=n_results)

        for link in google_links:
            article = sc.get_article_from_url(link["url"])
            if article:
                all_article += link["title"] + '\n' + article + '\n'

        batches_list = list(ai.extract_paragraph_batches(
            paragraph=all_article, batch_size=limit_words))

        for i, batch_paragraph in enumerate(batches_list):
            if i >= limit_api_called:
                break
            unknown_summary = ai.get_bulletpoint_unknown_knowledge(
                topic, role, batch_paragraph)
            full_unknown_bulletpoint += unknown_summary + "\n"
            st.session_state.tokenCount += ai.calculate_sum_token(
                batch_paragraph, unknown_summary)

        learn_unknown_prompt = pr.learn_unknown_knowledge.format(
            topic=topic, role=role)

        sendChatToGPT(learn_unknown_prompt, False, False)
        sendChatToGPT(full_unknown_bulletpoint +
                      "\n after reading this you will keep playing as Bob as in the hypothesis scenario", False, True)

        st.session_state.topic = topic

for msg in st.session_state.messages:
    if msg["show"]:
        st.chat_message(msg["role"]).write(msg["content"])

col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    st.button("clear messages", on_click=btnClearMsg)
with col2:
    st.button("Remind Bot", on_click=remindBot)

if prompt := st.chat_input():
    if not st.session_state.topic:
        st.info("please enter the topic first before continue")
        st.stop()
    for selected_behavior in bot_behaviors:
        if selected_behavior == "normal":
            behavior_prompt += "Bob, "
        if selected_behavior == "make_assumption":
            behavior_prompt += "remember we are in hypothesis scenario, give assumption and opinion as neccesary. "
    st.chat_message("user").write(prompt)
    response = sendChatToGPT(behavior_prompt+prompt)
    st.chat_message("assistant").write(response)

# st.write(st.session_state.messages)
token_price = st.session_state.tokenCount * 0.002 * 35 / 1000
