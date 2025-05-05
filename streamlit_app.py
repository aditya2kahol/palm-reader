import streamlit as st
import base64
import os
from groq import Groq
from PIL import Image
import io

# Set page configuration
st.set_page_config(
    page_title="Palm Reading App",
    page_icon="🔮",
    layout="centered"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #9c27b0;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #6a1b9a;
        margin-bottom: 1rem;
    }
    .instruction {
        padding: 1rem;
        background-color: #4a148c;
        color: #ffffff;
        border-radius: 5px;
        margin-bottom: 1rem;
    }
    .stButton>button {
        background-color: #9c27b0;
        color: white;
        font-weight: bold;
        width: 100%;
    }
    .reading-result {
        padding: 1.5rem;
        background-color: #4a148c;
        color: #ffffff;
        border-radius: 5px;
        margin-top: 1rem;
        border-left: 5px solid #e040fb;
    }
</style>
""", unsafe_allow_html=True)

# App title
st.markdown("<h1 class='main-header'>✋ Mystic Palm Reader ✋</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Upload an image of your palm to discover more about yourself!</p>", unsafe_allow_html=True)

# Language selection for UI
ui_language = st.sidebar.radio(
    "App Language/ऐप भाषा", 
    ["English", "हिंदी (Hindi)"], 
    index=0
)

# Set UI text based on language selection
if ui_language == "हिंदी (Hindi)":
    how_it_works_title = "यह कैसे काम करता है"
    instructions_html = """
    <div class='instruction'>
    <ol>
        <li>अपनी हथेली की तस्वीर अपलोड करें या अपने कैमरे का उपयोग करके फोटो लें</li>
        <li>सुनिश्चित करें कि आपकी हथेली की रेखाएं स्पष्ट रूप से दिखाई दे रही हैं</li>
        <li>अपना व्यक्तिगत पठन प्राप्त करने के लिए 'मेरी हथेली पढ़ें' पर क्लिक करें</li>
    </ol>
    </div>
    """
    upload_title = "अपनी हथेली की छवि अपलोड करें"
    upload_option_label = "एक विकल्प चुनें:"
    upload_options = ["छवि अपलोड करें", "कैमरे से फोटो लें"]
    upload_instruction = "अपनी हथेली की एक छवि चुनें"
    camera_instruction = "अपनी हथेली की फोटो लें"
else:
    how_it_works_title = "How it works"
    instructions_html = """
    <div class='instruction'>
    <ol>
        <li>Upload an image of your palm or take a photo using your camera</li>
        <li>Make sure your palm lines are clearly visible</li>
        <li>Click on 'Read My Palm' to get your personalized reading</li>
    </ol>
    </div>
    """
    upload_title = "Upload Your Palm Image"
    upload_option_label = "Choose an option:"
    upload_options = ["Upload Image", "Take Photo with Camera"]
    upload_instruction = "Choose an image of your palm"
    camera_instruction = "Take a photo of your palm"

# Function to encode the image to base64
def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

# Function to process the image and get a palm reading
def get_palm_reading(image_bytes, language="English"):
    # Encode image to base64
    base64_image = encode_image(image_bytes)
    
    # Get API key from environment variable or Streamlit secrets
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key and 'GROQ_API_KEY' in st.secrets:
        api_key = st.secrets["GROQ_API_KEY"]
    
    if not api_key:
        st.error("GROQ API key not found. Please set the GROQ_API_KEY environment variable or in Streamlit secrets.")
        return None
    
    # Create Groq client
    client = Groq(api_key=api_key)
    
    # Prepare system prompt based on language
    system_prompt = """You are an experienced palmistry expert known for your grounded, practical approach. Analyze the provided palm image and deliver a clear, insightful, and respectful report. Your analysis should include detailed observations on the following:

- **Major Lines**: Heart Line (emotions and relationships), Head Line (intellect and mindset), Life Line (vitality and life path), and Fate Line (career and destiny).
- **Minor Lines**: Sun Line, Mercury Line, Marriage Line, Travel Lines, and other significant markings (only the ones which are visible).
- **Mounts**: Venus, Jupiter, Saturn, Sun (Apollo), Mercury, Moon, and their implications (only the ones which are visible).
- **Hand Shape & Proportions**: Indications of personality traits and innate abilities.
- **Thumb Structure**: Insights into willpower, logic, and decision-making style.
- **Marks & Symbols**: Interpretation of crosses, stars, squares, tridents, islands, breaks, and other notable features (only the ones which are visible).

Please organize your analysis in sections. If you identify any challenging signs, mention them with care and offer constructive advice or practical remedies wherever possible."""
    if language == "Hindi":
        user_prompt = "Please anlyze this palm image and give me a detailed analysis report in Hindi Language."
    else:
        user_prompt = "Please analyze this palm image and give me a detailed analysis report in English Language."
    
    try:
        # Send request to Groq API
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model="meta-llama/llama-4-maverick-17b-128e-instruct",#"meta-llama/llama-4-scout-17b-16e-instruct",
            max_completion_tokens = 1024,
            temperature = 0.5,
        )
        
        return chat_completion.choices[0].message.content
    
    except Exception as e:
        st.error(f"Error during API call: {str(e)}")
        return None

# Main app function
def main():
    st.markdown(f"<h2 class='sub-header'>{how_it_works_title}</h2>", unsafe_allow_html=True)
    st.markdown(instructions_html, unsafe_allow_html=True)
    
    # Image upload section
    st.markdown(f"<h2 class='sub-header'>{upload_title}</h2>", unsafe_allow_html=True)
    
    # Option to choose between upload and camera
    upload_option = st.radio(upload_option_label, upload_options)
    
    image_file = None
    if upload_option == upload_options[0]:  # Upload Image option
        # Support multiple image formats
        image_file = st.file_uploader(upload_instruction, 
                                      type=['jpg', 'jpeg', 'png', 'webp', 'bmp', 'tiff', 'gif'])
    else:  # Camera option
        image_file = st.camera_input(camera_instruction)
    
    # Display the uploaded image
    if image_file is not None:
        # Read the image file
        image = Image.open(image_file)
        
        # Display image with some styling
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(image, caption="Your palm image", use_container_width=True)
        
        # Language selection
        st.markdown("<h3 style='color: #9c27b0; margin-top: 1rem;'>Select Reading Language</h3>", unsafe_allow_html=True)
        language = st.selectbox(
            "Choose the language for your palm reading:",
            options=["English", "Hindi"],
            index=0,
            help="Select the language in which you want to receive your palm reading."
        )
        
        # Custom message based on language
        spinner_text = "The mystic forces are analyzing your palm..." if language == "English" else "रहस्यमय शक्तियाँ आपकी हथेली का विश्लेषण कर रही हैं..."
        satisfied_text = "Wasn't satisfied with your reading? Try again with a clearer image!" if language == "English" else "अपने पठन से संतुष्ट नहीं हैं? एक स्पष्ट छवि के साथ फिर से प्रयास करें!"
        reading_header = "Your Palm Reading" if language == "English" else "आपका हस्तरेखा पठन"
        
        # Button to get palm reading
        button_text = "✨ Read My Palm ✨" if language == "English" else "✨ मेरी हथेली पढ़ें ✨"
        if st.button(button_text):
            with st.spinner(spinner_text):
                # Convert image to bytes for processing
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format if image.format else 'JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Get the reading in the selected language
                reading = get_palm_reading(img_byte_arr, language)
                
                if reading:
                    st.markdown(f"<h2 class='sub-header'>{reading_header}</h2>", unsafe_allow_html=True)
                    st.markdown(f"<div class='reading-result'>{reading}</div>", unsafe_allow_html=True)
                    
                    # Option to get a new reading
                    st.markdown(f"<p style='text-align: center; margin-top: 1.5rem;'>{satisfied_text}</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()