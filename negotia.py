import os
import streamlit as st
from langchain_groq import ChatGroq
import dotenv

# Configure Streamlit page
st.set_page_config(page_title="Negotia")

# Hide Streamlit's default menu bar
st.markdown("""
    <style>
    .css-1v0mbdj.e16nr0p30 {
        visibility: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# Load environment variables
dotenv.load_dotenv()

# Default model and temperature settings
DEFAULT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_TEMPERATURE = 0.7
API_KEY = os.getenv("GROQ_API_KEY", "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")

# Groq Integration
def initialize_groq(api_key, model_name=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE):
    try:
        return ChatGroq(
            api_key=api_key,
            model_name=model_name,
            temperature=temperature
        )
    except Exception as e:
        st.error(f"Groq initialization error: {e}")
        return None

# Generate negotiation scenario using LLM
def generate_scenario(groq_chat):
    prompt = """
    Generate a unique negotiation scenario. Provide a brief description of the scenario including the parties involved, 
    their initial offers, and what they are negotiating for. Ensure there are no typos and use clear, 
    professional language no italic fonts. make sure you pick the side for which the player is playing.
    Just type the entire thing in text your response should not cause any issue for the UI
    do not use symbols in your response
    """
    try:
        response = groq_chat.invoke([{"role": "user", "content": prompt}])
        return response.content
    except Exception as e:
        st.error(f"Scenario generation error: {e}")
        return "A Marketing firm has contacted an Instagram influencer with 10 million followers and a 30% engagement rate for sponsorship. They are ready to pay $10,000, but she wants $15,000."

# Main Streamlit app
def main():
    st.title("Negotiation Game")

    # Initialize Groq
    groq_chat = initialize_groq(API_KEY)
    if not groq_chat:
        return

    # Game modes
    game_modes = ["One-shot Negotiation", "Multi-shot Negotiation"]
    selected_mode = st.selectbox("Select the game mode:", game_modes)

    # Generate scenario
    selected_scenario = generate_scenario(groq_chat)
    st.markdown(f"**Scenario:** {selected_scenario}")

    # Player's initial offer
    player_offer = st.text_input("Enter your initial negotiation statement:")

    if player_offer:
        if selected_mode == "One-shot Negotiation":
            # Construct the prompt for one-shot negotiation
            prompt = f"""
            You are an AI negotiator.
            Scenario: {selected_scenario}
            Player's statement: "{player_offer}"
            Respond as the other party in the negotiation.
            Mention the player's side
            no italic fonts. make sure you pick the side for which the player is playing.
    Just type the entire thing in text your response should not cause any issue for the UI
    do not use symbols in your response
            """

            # Generate the AI response
            with st.spinner("Generating AI response..."):
                try:
                    response = groq_chat.invoke([{"role": "user", "content": prompt}])
                    ai_response = response.content
                    # Display response
                    st.markdown(f"**AI Response:** {ai_response}")
                except Exception as e:
                    st.error(f"Response generation error: {e}")

        elif selected_mode == "Multi-shot Negotiation":
            # Multi-shot negotiation variables
            negotiation_history = []

            # Function to perform multi-shot negotiation
            def multi_shot_negotiation(player_offer, selected_scenario):
                negotiation_history.append(f"Player: {player_offer}")

                while True:
                    # Construct the prompt for multi-shot negotiation
                    prompt = f"""
                    You are an AI negotiator.
                    Scenario: {selected_scenario}
                    {' '.join([f'{h}' for h in negotiation_history])}
                    Respond as the other party in the negotiation. No symbols only text. Pick the side of user
                    """

                    # Generate the AI response
                    try:
                        response = groq_chat.invoke([{"role": "user", "content": prompt}])
                        ai_response = response.content

                        # Add AI response to the negotiation history
                        negotiation_history.append(f"AI: {ai_response}")
                        st.markdown(f"**AI Response:** {ai_response}")

                        # Check if the negotiation should be closed
                        if "acceptable" in ai_response.lower() or "agreed" in ai_response.lower():
                            st.success("Negotiation successful! Starting a new scenario...")
                            new_scenario = generate_scenario(groq_chat)
                            st.markdown(f"**New Scenario:** {new_scenario}")
                            negotiation_history.clear()
                            break

                        # Player's counter-statement
                        player_counter_offer = st.text_input("Enter your counter-negotiation statement:", key=len(negotiation_history))
                        if not player_counter_offer:
                            break
                        negotiation_history.append(f"Player: {player_counter_offer}")
                    except Exception as e:
                        st.error(f"Response generation error: {e}")
                        break

            # Start multi-shot negotiation
            multi_shot_negotiation(player_offer, selected_scenario)

if __name__ == "__main__":
    main()